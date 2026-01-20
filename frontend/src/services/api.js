import axios from 'axios';

const api = axios.create({
  baseURL: 'https://web-production-b46fb.up.railway.app', // Railway backend
});

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
