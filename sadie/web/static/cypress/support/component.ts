import { mount } from '@cypress/react';
import './commands';

// Configuration globale pour les tests de composants
Cypress.Commands.add('mount', mount);

declare global {
  namespace Cypress {
    interface Chainable {
      mount: typeof mount;
    }
  }
} 