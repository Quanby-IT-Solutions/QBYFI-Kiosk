// utils/apiClient.ts

export async function apiRequest(endpoint: string, options = {}) {
    try {
      const response = await fetch(endpoint, options);
      if (!response.ok) {
        throw new Error(`Failed to fetch ${endpoint}: ${response.statusText}`);
      }
      return await response.json();
    } catch (error) {
      console.error(`Error in apiRequest for ${endpoint}:`, error);
      throw error;
    }
  }
  