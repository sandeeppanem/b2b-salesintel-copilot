import React, { useRef, useState } from 'react';
import {
  Avatar,
  Box,
  Button,
  CircularProgress,
  Paper,
  TextField,
  Typography,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import PersonIcon from '@mui/icons-material/Person';
import SmartToyIcon from '@mui/icons-material/SmartToy';

interface Message {
  sender: 'user' | 'agent';
  text: string;
}

interface ChatProps {
  userId: string;
}

export const Chat: React.FC<ChatProps> = ({ userId }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      sender: 'agent',
      text: 'Hi! Ask me anything about your sales and customer success opportunities.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setMessages((msgs) => [...msgs, { sender: 'user', text: input }]);
    setLoading(true);
    setError(null);
    const userMessage = input;
    setInput('');
    try {
      // Prepare last 10 messages as history for backend
      const historyForBackend = messages.slice(-10).map(m => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage, user_id: userId, history: historyForBackend }),
      });
      const data = await res.json();
      setMessages((msgs) => [
        ...msgs,
        { sender: 'agent', text: data.response || 'Sorry, I could not get an answer.' },
      ]);
    } catch (err: any) {
      setError('Failed to get response from the agent.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 0, maxWidth: 600, mx: 'auto', display: 'flex', flexDirection: 'column', height: 600 }}>
      <Box sx={{ flex: 1, overflowY: 'auto', p: 2, bgcolor: '#f7f7fa' }}>
        {messages.map((msg, idx) => (
          <Box key={idx} sx={{ display: 'flex', mb: 2, flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row', alignItems: 'flex-end' }}>
            <Avatar sx={{ bgcolor: msg.sender === 'user' ? 'primary.main' : 'secondary.main', ml: msg.sender === 'user' ? 2 : 0, mr: msg.sender === 'agent' ? 2 : 0 }}>
              {msg.sender === 'user' ? <PersonIcon /> : <SmartToyIcon />}
            </Avatar>
            <Box
              sx={{
                bgcolor: msg.sender === 'user' ? 'primary.light' : 'grey.200',
                color: msg.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                px: 2,
                py: 1,
                borderRadius: 2,
                maxWidth: '75%',
                boxShadow: 1,
                whiteSpace: 'pre-line',
              }}
            >
              <Typography variant="body1">{msg.text}</Typography>
            </Box>
          </Box>
        ))}
        <div ref={chatEndRef} />
      </Box>
      {error && <Box sx={{ color: 'red', px: 2, pb: 1 }}>{error}</Box>}
      <Box sx={{ display: 'flex', alignItems: 'center', p: 2, borderTop: '1px solid #eee', bgcolor: '#fff' }}>
        <TextField
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question..."
          fullWidth
          multiline
          minRows={1}
          maxRows={4}
          disabled={loading}
          sx={{ mr: 2 }}
        />
        <Button
          variant="contained"
          endIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
          onClick={handleSend}
          disabled={loading || !input.trim()}
          sx={{ minWidth: 48, minHeight: 48 }}
        >
          {!loading && <span style={{ display: 'none' }}>Send</span>}
        </Button>
      </Box>
    </Paper>
  );
}; 