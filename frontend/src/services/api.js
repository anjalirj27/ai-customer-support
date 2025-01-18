import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

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