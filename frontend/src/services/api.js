import axios from 'axios';

const API_BASE_URL = 'https://your-railway-url.railway.app';

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