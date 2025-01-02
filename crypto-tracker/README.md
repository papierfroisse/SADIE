# Crypto Tracker

Une application web pour suivre les prix des cryptomonnaies en temps réel, avec des graphiques en chandeliers et des données provenant de Binance et Kraken.

## Fonctionnalités

- Authentification avec Google ou email/mot de passe via Firebase
- Affichage des prix en temps réel
- Graphiques en chandeliers avec différents intervalles de temps
- Support de plusieurs exchanges (Binance, Kraken)
- Mode sombre/clair
- Interface responsive

## Technologies utilisées

- React
- TypeScript
- Firebase (Authentication)
- Styled Components
- Lightweight Charts
- Formik & Yup
- Axios

## Installation

1. Clonez le dépôt :
```bash
git clone https://github.com/votre-username/crypto-tracker.git
cd crypto-tracker
```

2. Installez les dépendances :
```bash
npm install
```

3. Créez un fichier `.env` à la racine du projet avec vos identifiants Firebase :
```env
VITE_FIREBASE_API_KEY=votre-api-key
VITE_FIREBASE_AUTH_DOMAIN=votre-auth-domain
VITE_FIREBASE_PROJECT_ID=votre-project-id
VITE_FIREBASE_STORAGE_BUCKET=votre-storage-bucket
VITE_FIREBASE_MESSAGING_SENDER_ID=votre-messaging-sender-id
VITE_FIREBASE_APP_ID=votre-app-id
```

4. Démarrez le serveur de développement :
```bash
npm run dev
```

## Scripts disponibles

- `npm run dev` : Lance le serveur de développement
- `npm run build` : Compile l'application pour la production
- `npm run preview` : Prévisualise la version de production

## Structure du projet

```
crypto-tracker/
├── src/
│   ├── components/     # Composants React
│   ├── services/       # Services (API calls)
│   ├── hooks/          # Custom hooks
│   ├── config/         # Configuration (Firebase)
│   └── ...
├── public/            # Fichiers statiques
└── ...
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request. 