import { useState, useRef, useEffect } from 'react';
import { MessageCircle } from 'lucide-react';
import Message from './components/Message';
import MessageInput from './components/MessageInput';
import TypingIndicator from './components/TypingIndicator';
import { chatAPI } from './services/api';

function App() {
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text) => {
    const userMsg = { id: Date.now(), role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await chatAPI.sendMessage(text, conversationId);
      if (!conversationId) setConversationId(res.conversation_id);
      
      setMessages(prev => [...prev, {
        id: res.message_id,
        role: 'assistant',
        content: res.content,
        agent_type: res.agent
      }]);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '20px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px'
      }}>
        <MessageCircle size={28} />
        <h1 style={{ margin: 0 }}>AI Customer Support</h1>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '24px', background: '#F9FAFB' }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '50px' }}>
            <h2>Welcome!</h2>
            <p>Ask me anything about orders, billing, or support.</p>
          </div>
        ) : (
          <>
            {messages.map(msg => <Message key={msg.id} message={msg} />)}
            {isLoading && <TypingIndicator />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      <MessageInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}

export default App;