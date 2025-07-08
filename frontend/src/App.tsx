import React, { useState } from 'react';
import { Box, Button, Container, TextField, Typography, Paper, List, ListItem, ListItemIcon, ListItemText } from '@mui/material';
import { Chat } from './Chat';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

const EXAMPLE_PROMPTS = [
  'Show me my top 5 cross-sell opportunities and why.',
  'Which accounts are most likely to buy Product X and why?',
  'Why is Account Y a good upsell target for Product Z?',
  'What are the top cross-sell opportunities in my territory?',
  'Which accounts are at risk of churn and why?',
  'What should I do next for Account Z?',
  'Generate a personalized pitch for Acme Corp for Product Y.',
  'Why did the model score Account X low for Product Y?',
  'What features are driving the upsell score for Account A?',
  'Show me all accounts with high cross-sell potential for Product Z in the healthcare segment.',
  'Summarize my top opportunities and risks for this quarter.'
];

const App: React.FC = () => {
  const [userId, setUserId] = useState('');
  const [input, setInput] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      setUserId(input.trim());
      setSubmitted(true);
    }
  };

  return (
    <Container maxWidth="sm" sx={{ py: 6 }}>
      <Typography variant="h4" align="center" gutterBottom>
        Sales/CS PTB Agent
      </Typography>
      <Paper sx={{ p: 2, mb: 4, background: '#f5f7fa' }} elevation={1}>
        <Typography variant="subtitle1" sx={{ mb: 1 }}>
          Example questions you can ask:
        </Typography>
        <List dense>
          {EXAMPLE_PROMPTS.map((prompt, idx) => (
            <ListItem key={idx}>
              <ListItemIcon>
                <HelpOutlineIcon color="primary" />
              </ListItemIcon>
              <ListItemText primary={prompt} />
            </ListItem>
          ))}
        </List>
      </Paper>
      {!userId && !submitted ? (
        <Paper sx={{ p: 4, mt: 6 }} elevation={3}>
          <form onSubmit={handleSubmit}>
            <Typography variant="h6" gutterBottom>
              Enter your User ID to start
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
              <TextField
                label="User ID"
                value={input}
                onChange={e => setInput(e.target.value)}
                fullWidth
                autoFocus
              />
              <Button type="submit" variant="contained" size="large" disabled={!input.trim()}>
                Start
              </Button>
            </Box>
          </form>
        </Paper>
      ) : (
        <Box sx={{ mt: 4 }}>
          <Chat userId={userId} />
        </Box>
      )}
    </Container>
  );
};

export default App;
