/**
 * Configuration Jest pour le projet SADIE
 * 
 * Cette configuration est optimisée pour tester des composants React
 * avec TypeScript, et inclut la configuration de la couverture de code.
 */

module.exports = {
  // Répertoire racine pour la résolution des modules
  roots: ['<rootDir>/src'],

  // Chemins de recherche pour les modules
  modulePaths: ['<rootDir>/src'],

  // Résolution des extensions de fichiers
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],

  // Environnement de test (jsdom pour les tests de composants React)
  testEnvironment: 'jsdom',

  // Modèles de chemins pour les fichiers de test
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js|jsx)',
    '**/?(*.)+(spec|test).+(ts|tsx|js|jsx)',
  ],

  // Transformations des fichiers
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.(js|jsx)$': 'babel-jest',
  },

  // Configuration de la couverture de code
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.tsx',
    '!src/serviceWorker.ts',
    '!src/reportWebVitals.ts',
    '!src/setupTests.ts',
    '!src/mocks/**',
    '!src/**/*.stories.*',
  ],

  // Seuils de couverture de code
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70,
    },
  },

  // Répertoire de sortie des rapports de couverture
  coverageDirectory: 'coverage',

  // Format des rapports de couverture
  coverageReporters: ['text', 'lcov', 'json-summary'],

  // Mocks pour les extensions de fichiers statiques
  moduleNameMapper: {
    '\\.(jpg|jpeg|png|gif|svg|webp|ico)$': '<rootDir>/src/tests/mocks/fileMock.js',
    '\\.(css|scss|sass|less)$': '<rootDir>/src/tests/mocks/styleMock.js',
  },

  // Setup de l'environnement de test
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],

  // Afficher un résumé des tests
  verbose: true,

  // Temporisation des tests pour éviter les timeouts sur les CI lentes
  testTimeout: 30000,

  // Ignorer certains répertoires pour les transformations
  transformIgnorePatterns: [
    '/node_modules/(?!(@material-ui|recharts|d3-.*)/)',
  ],

  // Réglages de Jest Watch
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname',
  ],

  // Répertoire global de cache
  cacheDirectory: '<rootDir>/.jest-cache',
  
  // Réglages pour la détection des fuites de mémoire
  detectLeaks: false,
  detectOpenHandles: false,
}; 