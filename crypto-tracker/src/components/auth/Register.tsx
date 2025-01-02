import React, { useState } from 'react';
import { createUserWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../../config/firebase';
import { Formik, Form, Field } from 'formik';
import * as Yup from 'yup';
import styled from 'styled-components';

const RegisterContainer = styled.div`
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
  username: Yup.string()
    .min(3, 'Le nom d\'utilisateur doit contenir au moins 3 caractères')
    .required('Nom d\'utilisateur requis'),
  email: Yup.string()
    .email('Email invalide')
    .required('Email requis'),
  password: Yup.string()
    .min(8, 'Le mot de passe doit contenir au moins 8 caractères')
    .matches(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Le mot de passe doit contenir au moins une majuscule, une minuscule, un chiffre et un caractère spécial'
    )
    .required('Mot de passe requis'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password')], 'Les mots de passe ne correspondent pas')
    .required('Confirmation du mot de passe requise'),
});

interface RegisterProps {
  onSwitchToLogin: () => void;
}

const Register: React.FC<RegisterProps> = ({ onSwitchToLogin }) => {
  const [error, setError] = useState<string>('');

  return (
    <RegisterContainer>
      <Title>Inscription</Title>
      <Formik
        initialValues={{
          username: '',
          email: '',
          password: '',
          confirmPassword: ''
        }}
        validationSchema={validationSchema}
        onSubmit={async (values, { setSubmitting }) => {
          try {
            await createUserWithEmailAndPassword(auth, values.email, values.password);
            // Ici, vous pouvez ajouter des informations supplémentaires de l'utilisateur dans Firestore
          } catch (error: any) {
            setError(error.message);
          }
          setSubmitting(false);
        }}
      >
        {({ errors, touched, isSubmitting }) => (
          <Form>
            <Input
              type="text"
              name="username"
              placeholder="Nom d'utilisateur"
            />
            {errors.username && touched.username && (
              <ErrorMessage>{errors.username}</ErrorMessage>
            )}

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

            <Input
              type="password"
              name="confirmPassword"
              placeholder="Confirmer le mot de passe"
            />
            {errors.confirmPassword && touched.confirmPassword && (
              <ErrorMessage>{errors.confirmPassword}</ErrorMessage>
            )}

            {error && <ErrorMessage>{error}</ErrorMessage>}

            <Button type="submit" disabled={isSubmitting}>
              S'inscrire
            </Button>
          </Form>
        )}
      </Formik>

      <LinkText>
        Déjà un compte ?{' '}
        <a onClick={onSwitchToLogin}>Se connecter</a>
      </LinkText>
    </RegisterContainer>
  );
};

export default Register; 