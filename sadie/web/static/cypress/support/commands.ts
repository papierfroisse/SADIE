/// <reference types="cypress" />
/// <reference types="@testing-library/cypress" />

export {};

declare global {
  namespace Cypress {
    interface Chainable<Subject = any> {
      /**
       * Connexion à l'application
       * @example cy.login('user@example.com', 'password123')
       */
      login(email: string, password: string): Chainable<void>;

      /**
       * Création d'une alerte
       * @example cy.createAlert('BTCUSDT', 50000)
       */
      createAlert(symbol: string, price: number): Chainable<void>;
    }
  }
}

// Commandes personnalisées
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login');
  cy.get('[data-testid=email-input]').type(email);
  cy.get('[data-testid=password-input]').type(password);
  cy.get('[data-testid=login-button]').click();
});

Cypress.Commands.add('createAlert', (symbol: string, price: number) => {
  cy.visit('/alerts');
  cy.get('[data-testid=new-alert-button]').click();
  cy.get('[data-testid=symbol-input]').type(symbol);
  cy.get('[data-testid=price-input]').type(price.toString());
  cy.get('[data-testid=create-alert-button]').click();
});

// Déclaration des types pour TypeScript
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      createAlert(symbol: string, price: number): Chainable<void>;
    }
  }
} 