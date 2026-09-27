/// <reference types="cypress" />

import './commands';

// Configuration globale pour les tests e2e
beforeEach(() => {
  // Reset l'état de l'application avant chaque test
  cy.clearLocalStorage();
  cy.clearCookies();
});

// Gestion des erreurs non capturées
Cypress.on('uncaught:exception', () => {
  // Retourner false empêche Cypress d'échouer le test
  return false;
}); 