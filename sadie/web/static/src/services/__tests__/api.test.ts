import { Alert } from '../../types';
import { AlerteApi, versAlerte, versAlerteApi } from '../api';

/**
 * L'API renvoie les alertes en snake_case (`notification_type`, `created_at`)
 * alors que le front travaille en camelCase (`notificationType`, `createdAt`).
 * Ces tests verrouillent la traduction : sans elle, `alert.createdAt` valait
 * `undefined` et l'affichage de la liste plantait sur une date invalide, et un
 * envoi en camelCase était rejeté en 422 par le modèle FastAPI.
 */
describe('traduction du contrat des alertes', () => {
  const alerteApi: AlerteApi = {
    id: 'a1',
    symbol: 'BTCUSDT',
    type: 'price',
    condition: 'above',
    value: 50000,
    notification_type: 'email',
    triggered: true,
    created_at: 1700000000000,
    triggered_at: 1700000060000,
  };

  it("traduit le snake_case de l'API vers le domaine du front", () => {
    const attendu: Alert = {
      id: 'a1',
      symbol: 'BTCUSDT',
      type: 'price',
      condition: 'above',
      value: 50000,
      notificationType: 'email',
      triggered: true,
      createdAt: 1700000000000,
      triggeredAt: 1700000060000,
    };

    expect(versAlerte(alerteApi)).toEqual(attendu);
  });

  it('remplace un horodatage absent au lieu de produire une date invalide', () => {
    const sansDate = versAlerte({ ...alerteApi, created_at: null, triggered_at: null });

    expect(Number.isFinite(sansDate.createdAt)).toBe(true);
    expect(sansDate.triggeredAt).toBeUndefined();
  });

  it("traduit une alerte du domaine vers le payload attendu par l'API", () => {
    const payload = versAlerteApi({
      symbol: 'ETHUSDT',
      type: 'volume',
      condition: 'below',
      value: 10,
      notificationType: 'browser',
      triggered: false,
      createdAt: 1700000000000,
    });

    expect(payload).toEqual({
      symbol: 'ETHUSDT',
      type: 'volume',
      condition: 'below',
      value: 10,
      notification_type: 'browser',
    });
  });

  it("normalise un type de notification inconnu vers 'browser'", () => {
    expect(versAlerte({ ...alerteApi, notification_type: 'sms' }).notificationType).toBe('browser');
  });
});