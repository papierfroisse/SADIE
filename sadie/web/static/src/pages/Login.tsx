import React, { useState } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Paper, 
  Container,
  Snackbar,
  Alert,
  Link,
  Divider,
  CircularProgress
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { styled } from '@mui/material/styles';

// Service API pour la connexion
import { loginUser } from '../services/api';

const StyledPaper = styled(Paper)(({ theme }) => ({
  marginTop: theme.spacing(8),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  padding: theme.spacing(4),
  borderRadius: theme.spacing(1),
  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)'
}));

const LockIconWrapper = styled('div')(({ theme }) => ({
  margin: theme.spacing(1),
  backgroundColor: theme.palette.primary.main,
  borderRadius: '50%',
  padding: theme.spacing(1),
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  color: theme.palette.primary.contrastText
}));

const LoginForm = styled('form')(({ theme }) => ({
  width: '100%',
  marginTop: theme.spacing(1),
}));

const SubmitButton = styled(Button)(({ theme }) => ({
  margin: theme.spacing(3, 0, 2),
  padding: theme.spacing(1.2),
}));

interface LocationState {
  from?: string;
}

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  
  const state = location.state as LocationState;
  const from = state?.from || '/';

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!username || !password) {
      setError('Veuillez saisir votre nom d\'utilisateur et mot de passe');
      return;
    }
    
    setLoading(true);
    try {
      const response = await loginUser(username, password);
      
      if (response.access_token) {
        // Stocker le token dans localStorage
        localStorage.setItem('auth_token', response.access_token);
        localStorage.setItem('username', username);
        
        // Rediriger vers la page d'origine ou le dashboard
        navigate(from, { replace: true });
      } else {
        setError('Erreur d\'authentification');
      }
    } catch (err) {
      setError('Identifiants invalides. Veuillez réessayer.');
      console.error('Erreur de connexion:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseError = () => {
    setError('');
  };

  return (
    <Container component="main" maxWidth="xs">
      <StyledPaper elevation={6}>
        <LockIconWrapper>
          <LockOutlinedIcon />
        </LockIconWrapper>
        <Typography component="h1" variant="h5">
          Connexion à SADIE
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1, mb: 3, textAlign: 'center' }}>
          Plateforme d'analyse de marché et backtesting
        </Typography>
        
        <Divider sx={{ width: '100%', mb: 3 }} />
        
        <LoginForm onSubmit={handleLogin} noValidate>
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            id="username"
            label="Nom d'utilisateur"
            name="username"
            autoComplete="username"
            autoFocus
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="password"
            label="Mot de passe"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <SubmitButton
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Se connecter'}
          </SubmitButton>
          
          <Box mt={2} display="flex" justifyContent="flex-end">
            <Link href="#" variant="body2">
              Mot de passe oublié?
            </Link>
          </Box>
        </LoginForm>
      </StyledPaper>
      
      <Box mt={2} textAlign="center">
        <Typography variant="body2" color="textSecondary">
          Vous n'avez pas de compte ? 
          <Link href="/register" variant="body2" sx={{ ml: 1 }}>
            Créer un compte
          </Link>
        </Typography>
      </Box>
      
      <Snackbar open={!!error} autoHideDuration={6000} onClose={handleCloseError}>
        <Alert onClose={handleCloseError} severity="error">
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Login; 