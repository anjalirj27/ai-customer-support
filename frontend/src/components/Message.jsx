import { User, Bot } from 'lucide-react';

const Message = ({ message }) => {
  const isUser = message.role === 'user';

  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '16px',
      gap: '12px'
    }}>
      {!isUser && (
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          background: '#4F46E5',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Bot size={20} color="white" />
        </div>
      )}

      <div style={{
        maxWidth: '70%',
        padding: '12px 16px',
        borderRadius: '12px',
        background: isUser ? '#4F46E5' : 'white',
        color: isUser ? 'white' : '#1F2937'
      }}>
        {message.content}
        {message.agent_type && (
          <div style={{ fontSize: '11px', opacity: 0.7, marginTop: '8px' }}>
            Agent: {message.agent_type}
          </div>
        )}
      </div>

      {isUser && (
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          background: '#10B981',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <User size={20} color="white" />
        </div>
      )}
    </div>
  );
};

export default Message;