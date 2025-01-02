import React, { useState } from 'react';
import { signInWithEmailAndPassword, signInWithPopup } from 'firebase/auth';
import { auth, googleProvider } from '../../config/firebase';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import styled from 'styled-components';
import { FaGoogle } from 'react-icons/fa';

const LoginContainer = styled.div`
  max-width: 400px;
  margin: 40px auto;
  padding: 20px;
  background: ${({ theme }) => theme.cardBackground};
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Title = styled.h2`
  text-align: center;
  color: ${({ theme }) => theme.textPrimary};
  margin-bottom: 24px;
`;

const Input = styled(Field)`
  width: 100%;
  padding: 10px;
  margin-bottom: 16px;
  border: 1px solid ${({ theme }) => theme.border};
  border-radius: 4px;
  background: ${({ theme }) => theme.inputBackground};
  color: ${({ theme }) => theme.textPrimary};
`;

const Button = styled.button`
  width: 100%;
  padding: 12px;
  background: ${({ theme }) => theme.accent};
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  margin-bottom: 16px;

  &:hover {
    opacity: 0.9;
  }

  &:disabled {
    background: ${({ theme }) => theme.buttonBackground};
    cursor: not-allowed;
  }
`;

const GoogleButton = styled(Button)`
  background: #4285f4;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

const ErrorMessage = styled.div`
  color: ${({ theme }) => theme.errorColor};
  margin-bottom: 16px;
  font-size: 14px;
`;

const LinkText = styled.p`
  text-align: center;
  color: ${({ theme }) => theme.textSecondary};
  margin-top: 16px;

  a {
    color: ${({ theme }) => theme.accent};
    cursor: pointer;
  }
`;

const validationSchema = Yup.object().shape({
  email: Yup.string()
    .email('Email invalide')
    .required('Email requis'),
  password: Yup.string()
    .min(6, 'Le mot de passe doit contenir au moins 6 caractères')
    .required('Mot de passe requis'),
});

interface LoginProps {
  onSwitchToRegister: () => void;
}

const Login: React.FC<LoginProps> = ({ onSwitchToRegister }) => {
  const [error, setError] = useState<string>('');

  const handleGoogleLogin = async () => {
    try {
      console.log('Starting Google login process...');
      
      const result = await signInWithPopup(auth, googleProvider);
      console.log('Google login successful:', result.user);
    } catch (error: any) {
      console.error('Google login error:', error);
      console.error('Error code:', error.code);
      console.error('Error message:', error.message);
      
      let errorMessage = 'Une erreur est survenue lors de la connexion.';
      
      switch (error.code) {
        case 'auth/popup-blocked':
          errorMessage = 'Le popup de connexion a été bloqué. Veuillez autoriser les popups pour ce site.';
          break;
        case 'auth/popup-closed-by-user':
          errorMessage = 'La fenêtre de connexion a été fermée avant la fin du processus.';
          break;
        case 'auth/cancelled-popup-request':
          errorMessage = 'La demande de connexion précédente est toujours en cours.';
          break;
        case 'auth/redirect-cancelled-by-user':
          errorMessage = 'La redirection a été annulée.';
          break;
        case 'auth/redirect-operation-pending':
          errorMessage = 'Une redirection est déjà en cours.';
          break;
        default:
          errorMessage = error.message;
      }
      
      setError(errorMessage);
    }
  };

  return (
    <LoginContainer>
      <Title>Connexion</Title>
      <Formik
        initialValues={{ email: '', password: '' }}
        validationSchema={validationSchema}
        onSubmit={async (values, { setSubmitting }) => {
          try {
            await signInWithEmailAndPassword(auth, values.email, values.password);
          } catch (error: any) {
            setError(error.message);
          }
          setSubmitting(false);
        }}
      >
        {({ errors, touched, isSubmitting }) => (
          <Form>
            <Input
              type="email"
              name="email"
              placeholder="Email"
            />
            {errors.email && touched.email && (
              <ErrorMessage>{errors.email}</ErrorMessage>
            )}

            <Input
              type="password"
              name="password"
              placeholder="Mot de passe"
            />
            {errors.password && touched.password && (
              <ErrorMessage>{errors.password}</ErrorMessage>
            )}

            {error && <ErrorMessage>{error}</ErrorMessage>}

            <Button type="submit" disabled={isSubmitting}>
              Se connecter
            </Button>
          </Form>
        )}
      </Formik>

      <GoogleButton onClick={handleGoogleLogin}>
        <FaGoogle />
        Se connecter avec Google
      </GoogleButton>

      <LinkText>
        Pas encore de compte ?{' '}
        <a onClick={onSwitchToRegister}>S'inscrire</a>
      </LinkText>
    </LoginContainer>
  );
};

export default Login; 