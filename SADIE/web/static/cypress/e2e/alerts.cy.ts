/// <reference types="cypress" />

describe('Alertes', () => {
  beforeEach(() => {
    cy.visit('/alerts');
  });

  it('devrait afficher la liste des alertes', () => {
    cy.get('[data-testid=alerts-list]').should('exist');
  });

  it('devrait pouvoir créer une nouvelle alerte', () => {
    const symbol = 'BTCUSDT';
    const price = 50000;
    
    cy.createAlert(symbol, price);
    
    cy.get('[data-testid=alert-item]').should('have.length.at.least', 1);
    cy.get('[data-testid=alert-symbol]').should('contain', symbol);
    cy.get('[data-testid=alert-price]').should('contain', price);
  });

  it('devrait pouvoir supprimer une alerte', () => {
    cy.createAlert('ETHUSDT', 3000);
    cy.get('[data-testid=alert-item]').should('exist');
    
    cy.get('[data-testid=delete-alert-button]').first().click();
    cy.get('[data-testid=confirm-delete-button]').click();
    
    cy.get('[data-testid=alert-item]').should('not.exist');
  });
}); 
