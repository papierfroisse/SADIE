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
import { useNavigate } from 'react-router-dom';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import { styled } from '@mui/material/styles';

// Service API pour l'inscription
import { registerUser, RegisterData } from '../services/api';

const StyledPaper = styled(Paper)(({ theme }) => ({
  marginTop: theme.spacing(8),
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  padding: theme.spacing(4),
  borderRadius: theme.spacing(1),
  boxShadow: '0 8px 24px rgba(0, 0, 0, 0.12)'
}));

const IconWrapper = styled('div')(({ theme }) => ({
  margin: theme.spacing(1),
  backgroundColor: theme.palette.primary.main,
  borderRadius: '50%',
  padding: theme.spacing(1),
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  color: theme.palette.primary.contrastText
}));

const RegisterForm = styled('form')(({ theme }) => ({
  width: '100%',
  marginTop: theme.spacing(1),
}));

const SubmitButton = styled(Button)(({ theme }) => ({
  margin: theme.spacing(3, 0, 2),
  padding: theme.spacing(1.2),
}));

const Register: React.FC = () => {
  const [formData, setFormData] = useState<RegisterData>({
    username: '',
    password: '',
    email: '',
    full_name: ''
  });
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleRegister = async (event: React.FormEvent) => {
    event.preventDefault();
    
    // Validation
    if (!formData.username || !formData.password || !formData.email) {
      setError('Veuillez remplir tous les champs obligatoires');
      return;
    }
    
    if (formData.password !== confirmPassword) {
      setError('Les mots de passe ne correspondent pas');
      return;
    }
    
    setLoading(true);
    try {
      const response = await registerUser(formData);
      
      if (response.success) {
        setSuccess('Compte créé avec succès! Vous allez être redirigé vers la page de connexion.');
        setTimeout(() => {
          navigate('/login');
        }, 2000);
      } else {
        setError(response.message || 'Erreur lors de l\'inscription');
      }
    } catch (err) {
      setError('Erreur lors de l\'inscription. Veuillez réessayer.');
      console.error('Erreur d\'inscription:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCloseError = () => {
    setError('');
  };

  const handleCloseSuccess = () => {
    setSuccess('');
  };

  return (
    <Container component="main" maxWidth="xs">
      <StyledPaper elevation={6}>
        <IconWrapper>
          <PersonAddIcon />
        </IconWrapper>
        <Typography component="h1" variant="h5">
          Créer un compte SADIE
        </Typography>
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1, mb: 3, textAlign: 'center' }}>
          Plateforme d'analyse de marché et backtesting
        </Typography>
        
        <Divider sx={{ width: '100%', mb: 3 }} />
        
        <RegisterForm onSubmit={handleRegister} noValidate>
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
            value={formData.username}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="email"
            label="Adresse email"
            type="email"
            id="email"
            autoComplete="email"
            value={formData.email}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            fullWidth
            name="full_name"
            label="Nom complet"
            id="full_name"
            autoComplete="name"
            value={formData.full_name}
            onChange={handleChange}
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
            autoComplete="new-password"
            value={formData.password}
            onChange={handleChange}
          />
          <TextField
            variant="outlined"
            margin="normal"
            required
            fullWidth
            name="confirmPassword"
            label="Confirmer le mot de passe"
            type="password"
            id="confirmPassword"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />
          <SubmitButton
            type="submit"
            fullWidth
            variant="contained"
            color="primary"
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'S\'inscrire'}
          </SubmitButton>
          
          <Box mt={2} display="flex" justifyContent="flex-end">
            <Link href="/login" variant="body2">
              Déjà un compte? Se connecter
            </Link>
          </Box>
        </RegisterForm>
      </StyledPaper>
      
      <Snackbar open={!!error} autoHideDuration={6000} onClose={handleCloseError}>
        <Alert onClose={handleCloseError} severity="error">
          {error}
        </Alert>
      </Snackbar>
      
      <Snackbar open={!!success} autoHideDuration={6000} onClose={handleCloseSuccess}>
        <Alert onClose={handleCloseSuccess} severity="success">
          {success}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Register; 