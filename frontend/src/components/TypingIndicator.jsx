import { Bot } from 'lucide-react';
import { useState, useEffect } from 'react';

const TypingIndicator = () => {
  const [text, setText] = useState('Analyzing query');
  
  const phrases = [
    'Analyzing query',
    'Routing to specialist',
    'Searching database',
    'Generating response',
  ];
  
  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % phrases.length;
      setText(phrases[i]);
    }, 1200);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ display: 'flex', gap: '12px', marginBottom: '16px' }}>
      <div style={{
        width: '32px', height: '32px', borderRadius: '50%',
        background: '#4F46E5', display: 'flex',
        alignItems: 'center', justifyContent: 'center'
      }}>
        <Bot size={20} color="white" />
      </div>
      <div style={{
        padding: '12px 16px', borderRadius: '12px',
        background: 'white', display: 'flex', gap: '8px',
        alignItems: 'center'
      }}>
        <span style={{ fontSize: '14px', color: '#6B7280' }}>
          {text}...
        </span>
      </div>
    </div>
  );
};

export default TypingIndicator;