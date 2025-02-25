/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable<Subject = any> {
    /**
     * Connexion à l'application
     * @example
     * cy.login('user@example.com', 'password123')
     */
    login(email: string, password: string): Chainable<void>;

    /**
     * Création d'une alerte
     * @example
     * cy.createAlert('BTCUSDT', 50000)
     */
    createAlert(symbol: string, price: number): Chainable<void>;

    /**
     * Monte un composant React pour les tests de composants
     * @example
     * cy.mount(<MyComponent />)
     */
    mount: typeof mount;
  }
} 