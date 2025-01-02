import React, { useState } from 'react';
import styled from 'styled-components';
import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from 'firebase/auth';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import { FaGoogle } from 'react-icons/fa';
import { auth } from '../../config/firebase';

interface LoginProps {
  onSwitchToRegister: () => void;
}

const LoginContainer = styled.div`
  background-color: ${({ theme }) => theme.background};
  border: 1px solid ${({ theme }) => theme.textSecondary};
  border-radius: 8px;
  padding: 2rem;
  width: 100%;
  max-width: 400px;
`;

const Title = styled.h1`
  text-align: center;
  margin-bottom: 2rem;
  color: ${({ theme }) => theme.accent};
`;

const Input = styled(Field)`
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: 1px solid ${({ theme }) => theme.textSecondary};
  border-radius: 4px;
  background-color: transparent;
  color: ${({ theme }) => theme.textPrimary};
  
  &:focus {
    outline: none;
    border-color: ${({ theme }) => theme.accent};
  }
`;

const Button = styled.button`
  width: 100%;
  padding: 0.75rem;
  margin-bottom: 1rem;
  border: none;
  border-radius: 4px;
  background-color: ${({ theme }) => theme.accent};
  color: white;
  cursor: pointer;
  font-weight: 500;
  
  &:hover {
    opacity: 0.9;
  }
  
  &:disabled {
    background-color: ${({ theme }) => theme.textSecondary};
    cursor: not-allowed;
  }
`;

const GoogleButton = styled(Button)`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background-color: #4285f4;
`;

const ErrorMessage = styled.div`
  color: #f44336;
  margin-bottom: 1rem;
  font-size: 0.875rem;
`;

const LinkText = styled.p`
  text-align: center;
  margin-top: 1rem;
  
  span {
    color: ${({ theme }) => theme.accent};
    cursor: pointer;
    
    &:hover {
      text-decoration: underline;
    }
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

const Login: React.FC<LoginProps> = ({ onSwitchToRegister }) => {
  const [error, setError] = useState('');

  const handleGoogleLogin = async () => {
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    } catch (error: any) {
      console.error('Google login error:', error);
      setError(error.message);
    }
  };

  const handleSubmit = async (values: { email: string; password: string }) => {
    try {
      await signInWithEmailAndPassword(auth, values.email, values.password);
    } catch (error: any) {
      console.error('Login error:', error);
      setError(error.message);
    }
  };

  return (
    <LoginContainer>
      <Title>Crypto Tracker</Title>
      <GoogleButton type="button" onClick={handleGoogleLogin}>
        <FaGoogle size={20} />
        Continuer avec Google
      </GoogleButton>
      
      <Formik
        initialValues={{ email: '', password: '' }}
        validationSchema={validationSchema}
        onSubmit={handleSubmit}
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
      
      <LinkText>
        Pas encore de compte ?{' '}
        <span onClick={onSwitchToRegister}>S'inscrire</span>
      </LinkText>
    </LoginContainer>
  );
};

export default Login; 