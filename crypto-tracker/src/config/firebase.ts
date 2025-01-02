import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
};

// Vérification de la configuration
Object.entries(firebaseConfig).forEach(([key, value]) => {
  if (!value) {
    console.error(`Missing Firebase config value for: ${key}`);
  }
});

console.log('Firebase Config:', {
  ...firebaseConfig,
  apiKey: firebaseConfig.apiKey ? '***' : undefined
});

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// Configuration du provider Google
const googleProvider = new GoogleAuthProvider();

// Ajout des scopes nécessaires
googleProvider.addScope('email');
googleProvider.addScope('profile');

// Configuration de base
const baseConfig = {
  prompt: 'select_account'
};

// En développement, on utilise localhost
if (import.meta.env.DEV) {
  console.log('Development mode - configuring for localhost');
  auth.useDeviceLanguage();
  // Ne pas modifier authDomain ici
}

export { auth, googleProvider }; 