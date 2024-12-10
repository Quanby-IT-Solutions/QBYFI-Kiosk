import { AnimatePresence } from 'framer-motion';
import HomePage from './home/page';

export default function Home() {
  return (
    <AnimatePresence>
      <HomePage />
    </AnimatePresence>
  );
}
