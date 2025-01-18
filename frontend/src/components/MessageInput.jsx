import { useState } from 'react';
import { Send } from 'lucide-react';

const MessageInput = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim()) {
      onSend(message);
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{
      display: 'flex',
      gap: '8px',
      padding: '16px',
      background: 'white',
      borderTop: '1px solid #E5E7EB'
    }}>
      <input
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="Type your message..."
        disabled={disabled}
        style={{
          flex: 1,
          padding: '12px 16px',
          border: '1px solid #E5E7EB',
          borderRadius: '8px',
          fontSize: '14px'
        }}
      />
      <button type="submit" disabled={disabled || !message.trim()} style={{
        padding: '12px 20px',
        background: '#4F46E5',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        cursor: 'pointer',
        display: 'flex',
        gap: '8px'
      }}>
        <Send size={18} />
        Send
      </button>
    </form>
  );
};

export default MessageInput;