from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import OPi.GPIO as GPIO
import time
import json

app = Flask(__name__)
socketio = SocketIO(app)

GPIO.setmode(GPIO.BOARD)

COIN_SENSOR_PIN = 3  # GPIO pin connected to the coin acceptor
ENABLE_PIN = 5

coin_count = 0  # Total value of coins inserted
pulse_count = 0  # To count pulses for determining coin type
last_pulse_time = time.time()  # Tracks the time of the last pulse

# Load vouchers from JSON file
def load_vouchers():
    try:
        with open("vouchers.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: vouchers.json file not found!")
        return {}

vouchers = load_vouchers()

def coin_inserted(channel):
    global last_pulse_time, pulse_count, coin_count
    current_time = time.time()
    pulse_count += 1
    last_pulse_time = current_time

# Set up the GPIO pin for the coin sensor
GPIO.setup(COIN_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(ENABLE_PIN, GPIO.OUT)
GPIO.output(ENABLE_PIN, GPIO.LOW)

# Add event detection for coin insertion
GPIO.add_event_detect(COIN_SENSOR_PIN, GPIO.RISING, callback=coin_inserted, bouncetime=50)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('start_coin_acceptance')
def start_coin_acceptance():
    global pulse_count, coin_count, last_pulse_time

    GPIO.output(ENABLE_PIN, GPIO.HIGH)
    print("Waiting for coins to be inserted...")
    emit('message', {'status':'Coin acceptance started'})

    try:
        while True:
            current_time = time.time()
            if pulse_count > 0 and current_time - last_pulse_time > 0.5:
                if pulse_count == 1:
                    coin_value = 1
                    print("1 peso inserted")
                elif pulse_count == 5:
                    coin_value = 5
                elif pulse_count == 10:
                    coin_value = 10
                else:
                    coin_value = 0

                coin_count += coin_value
                print(f"Current total: {coin_count} pesos")
                
                pulse_count = 0
                
                emit('coin_update', {'coin_count': coin_count}, broadcast=True)
                
                """
				user_input = input("Done inserting coin? y/n: ").strip().lower()
				if user_input == "y":
					break
				elif user_input == "n":
					continue"""
		
            socketio.sleep(0.1)

    except KeyboardInterrupt:
        GPIO.cleanup()

    return jsonify({'message': 'Coin acceptance completed', 'coin_count': coin_count})
    
@socketio.on('finish_insertion')
def finish_insertion():
	global coin_count
	GPIO.output(ENABLE_PIN, GPIO.LOW)
	emit('message', {'status': 'Coin insertion finished', 'coin_count':coin_count})
	
	if str(coin_count) in vouchers and vouchers[str(coin_count)]:
		voucher_code = vouchers[str(coin_count)].pop(0)
		emit('voucher_dispensed', {'voucher_code':voucher_code})
	else:
		emit('voucher_dispensed', {'voucher_code': 'No vouchers available for this amount'})
        
if __name__ == '__main__':
	socketio.run(app, host = "0.0.0.0", port=5000, debug=True)
