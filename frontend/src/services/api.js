import axios from 'axios';

// Override with VITE_API_URL (see .env.example); defaults to the hosted backend.
const API_URL = import.meta.env.VITE_API_URL || 'https://web-production-b46fb.up.railway.app';

const api = axios.create({
  baseURL: API_URL,
  timeout: 60000, // LLM calls can be slow, but should not hang forever
});

/** Turn an axios error into a message that is safe to show to the user. */
export const getErrorMessage = (err) => {
  if (err.response?.status === 429) {
    return 'You are sending messages too quickly. Please wait a moment and try again.';
  }
  if (err.response?.status === 422) {
    return 'Your message could not be sent. Please check it and try again.';
  }
  if (err.code === 'ECONNABORTED') {
    return 'The request timed out. Please try again.';
  }
  if (!err.response) {
    return 'Unable to reach the server. Please check your connection and try again.';
  }
  return 'Something went wrong on our side. Please try again.';
};

export const chatAPI = {
  sendMessage: async (message, conversationId) => {
    const res = await api.post('/api/chat/messages', {
      message,
      conversation_id: conversationId,
    });
    return res.data;
  },
};

export default api;
