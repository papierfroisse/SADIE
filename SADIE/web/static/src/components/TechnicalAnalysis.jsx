import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
  Container, Row, Col, Form, Button, Card, Tabs, Tab, Alert, Spinner
} from 'react-bootstrap';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend,
} from 'chart.js';
import { format } from 'date-fns';

// Enregistrer les composants ChartJS
ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend
);

const TechnicalAnalysis = () => {
  // États pour les données et les paramètres
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [symbol, setSymbol] = useState('BTCUSDT');
  const [timeframe, setTimeframe] = useState('4h');
  const [data, setData] = useState([]);
  const [indicators, setIndicators] = useState([]);
  const [availableIndicators, setAvailableIndicators] = useState([]);
  const [selectedIndicator, setSelectedIndicator] = useState('rsi');
  const [indicatorParams, setIndicatorParams] = useState({});
  const [results, setResults] = useState({});
  const [patternResults, setPatternResults] = useState({});
  const [supResResults, setSupResResults] = useState({});
  const [activeTab, setActiveTab] = useState('indicators');
  const chartRef = useRef(null);

  // Charger les indicateurs disponibles au chargement
  useEffect(() => {
    const fetchAvailableIndicators = async () => {
      try {
        const response = await axios.get('/api/technical/indicators');
        setAvailableIndicators(response.data);
      } catch (err) {
        console.error('Erreur lors du chargement des indicateurs disponibles:', err);
        setError('Impossible de charger les indicateurs disponibles.');
      }
    };

    fetchAvailableIndicators();
  }, []);

  // Récupérer les données historiques
  const fetchHistoricalData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/data/historical`, {
        params: { symbol, timeframe, limit: 100 }
      });
      
      if (response.data && response.data.success) {
        setData(response.data.data);
      } else {
        setError('Données non disponibles pour ce symbole/timeframe.');
      }
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err);
      setError(`Erreur: ${err.response?.data?.error || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculer l'indicateur sélectionné
  const calculateIndicator = async () => {
    if (data.length === 0) {
      setError('Veuillez d\'abord charger des données historiques.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/technical/indicator', {
        data,
        indicator: selectedIndicator,
        parameters: indicatorParams
      });

      if (response.data && response.data.success) {
        setResults(prevResults => ({
          ...prevResults,
          [selectedIndicator]: response.data.data
        }));
        
        if (!indicators.includes(selectedIndicator)) {
          setIndicators([...indicators, selectedIndicator]);
        }
      } else {
        setError(`Erreur: ${response.data.error}`);
      }
    } catch (err) {
      console.error('Erreur lors du calcul de l\'indicateur:', err);
      setError(`Erreur: ${err.response?.data?.error || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Détecter les patterns
  const detectPatterns = async () => {
    if (data.length === 0) {
      setError('Veuillez d\'abord charger des données historiques.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/technical/patterns', {
        data,
        pattern_types: ['candlestick']
      });

      if (response.data && response.data.success) {
        setPatternResults(response.data.data);
      } else {
        setError(`Erreur: ${response.data.error}`);
      }
    } catch (err) {
      console.error('Erreur lors de la détection des patterns:', err);
      setError(`Erreur: ${err.response?.data?.error || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Calculer les niveaux de support et résistance
  const calculateSupportResistance = async () => {
    if (data.length === 0) {
      setError('Veuillez d\'abord charger des données historiques.');
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('/api/technical/support-resistance', {
        data,
        window_size: 10,
        sensitivity: 0.01
      });

      if (response.data && response.data.success) {
        setSupResResults(response.data.data);
      } else {
        setError(`Erreur: ${response.data.error}`);
      }
    } catch (err) {
      console.error('Erreur lors du calcul des niveaux:', err);
      setError(`Erreur: ${err.response?.data?.error || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Préparer les données du graphique
  const prepareChartData = () => {
    if (data.length === 0) return null;

    const labels = data.map(item => 
      format(new Date(item.timestamp), 'yyyy-MM-dd HH:mm')
    );

    const datasets = [
      {
        label: 'Prix',
        data: data.map(item => item.close),
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
      }
    ];

    // Ajouter les indicateurs sélectionnés
    indicators.forEach(indicator => {
      if (results[indicator]) {
        const indicatorData = results[indicator];
        
        if (indicator === 'rsi') {
          datasets.push({
            label: 'RSI',
            data: indicatorData.rsi,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.5)',
            yAxisID: 'rsi'
          });
        } else if (indicator === 'macd') {
          datasets.push({
            label: 'MACD',
            data: indicatorData.macd,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.5)',
            yAxisID: 'macd'
          });
          datasets.push({
            label: 'Signal',
            data: indicatorData.signal,
            borderColor: 'rgb(255, 159, 64)',
            backgroundColor: 'rgba(255, 159, 64, 0.5)',
            yAxisID: 'macd'
          });
        } else if (indicator === 'bollinger_bands') {
          datasets.push({
            label: 'Bande supérieure',
            data: indicatorData.upper,
            borderColor: 'rgba(255, 99, 132, 0.8)',
            backgroundColor: 'rgba(0, 0, 0, 0)',
            borderDash: [5, 5],
          });
          datasets.push({
            label: 'Bande moyenne',
            data: indicatorData.middle,
            borderColor: 'rgba(54, 162, 235, 0.8)',
            backgroundColor: 'rgba(0, 0, 0, 0)',
            borderDash: [5, 5],
          });
          datasets.push({
            label: 'Bande inférieure',
            data: indicatorData.lower,
            borderColor: 'rgba(75, 192, 192, 0.8)',
            backgroundColor: 'rgba(0, 0, 0, 0)',
            borderDash: [5, 5],
          });
        } else if (indicator === 'sma' || indicator === 'ema') {
          datasets.push({
            label: indicator.toUpperCase(),
            data: indicatorData[indicator],
            borderColor: 'rgb(153, 102, 255)',
            backgroundColor: 'rgba(153, 102, 255, 0.5)',
          });
        }
      }
    });

    return { labels, datasets };
  };

  // Options du graphique
  const chartOptions = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: `${symbol} - ${timeframe}`,
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Prix'
        }
      },
      rsi: {
        type: 'linear',
        display: indicators.includes('rsi'),
        position: 'right',
        min: 0,
        max: 100,
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'RSI'
        }
      },
      macd: {
        type: 'linear',
        display: indicators.includes('macd'),
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        title: {
          display: true,
          text: 'MACD'
        }
      }
    },
  };

  // Rendu des paramètres d'indicateur
  const renderIndicatorParams = () => {
    switch (selectedIndicator) {
      case 'rsi':
        return (
          <Form.Group className="mb-3">
            <Form.Label>Période</Form.Label>
            <Form.Control 
              type="number" 
              value={indicatorParams.period || 14}
              onChange={(e) => setIndicatorParams({ ...indicatorParams, period: parseInt(e.target.value) })}
            />
          </Form.Group>
        );
      case 'macd':
        return (
          <>
            <Form.Group className="mb-3">
              <Form.Label>Période courte</Form.Label>
              <Form.Control 
                type="number" 
                value={indicatorParams.short_period || 12}
                onChange={(e) => setIndicatorParams({ 
                  ...indicatorParams, 
                  short_period: parseInt(e.target.value) 
                })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Période longue</Form.Label>
              <Form.Control 
                type="number" 
                value={indicatorParams.long_period || 26}
                onChange={(e) => setIndicatorParams({ 
                  ...indicatorParams, 
                  long_period: parseInt(e.target.value) 
                })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Période du signal</Form.Label>
              <Form.Control 
                type="number" 
                value={indicatorParams.signal_period || 9}
                onChange={(e) => setIndicatorParams({ 
                  ...indicatorParams, 
                  signal_period: parseInt(e.target.value) 
                })}
              />
            </Form.Group>
          </>
        );
      case 'bollinger_bands':
        return (
          <>
            <Form.Group className="mb-3">
              <Form.Label>Période</Form.Label>
              <Form.Control 
                type="number" 
                value={indicatorParams.period || 20}
                onChange={(e) => setIndicatorParams({ 
                  ...indicatorParams, 
                  period: parseInt(e.target.value) 
                })}
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Écart type</Form.Label>
              <Form.Control 
                type="number" 
                step="0.1"
                value={indicatorParams.std_dev || 2.0}
                onChange={(e) => setIndicatorParams({ 
                  ...indicatorParams, 
                  std_dev: parseFloat(e.target.value) 
                })}
              />
            </Form.Group>
          </>
        );
      case 'sma':
      case 'ema':
        return (
          <Form.Group className="mb-3">
            <Form.Label>Période</Form.Label>
            <Form.Control 
              type="number" 
              value={indicatorParams.period || 20}
              onChange={(e) => setIndicatorParams({ 
                ...indicatorParams, 
                period: parseInt(e.target.value) 
              })}
            />
          </Form.Group>
        );
      default:
        return null;
    }
  };

  // Affichage des patterns détectés
  const renderPatterns = () => {
    if (!patternResults || Object.keys(patternResults).length === 0) {
      return <Alert variant="info">Aucun pattern détecté ou analyse non effectuée.</Alert>;
    }

    return (
      <Card>
        <Card.Body>
          <Card.Title>Patterns détectés</Card.Title>
          <ul>
            {Object.entries(patternResults).map(([pattern, occurrences]) => (
              <li key={pattern}>
                <strong>{pattern}:</strong> Détecté aux positions {Array.isArray(occurrences) 
                  ? occurrences.join(', ') 
                  : JSON.stringify(occurrences)}
              </li>
            ))}
          </ul>
        </Card.Body>
      </Card>
    );
  };

  // Affichage des niveaux de support et résistance
  const renderSupportResistance = () => {
    if (!supResResults || !supResResults.support || !supResResults.resistance) {
      return <Alert variant="info">Niveaux non calculés ou analyse non effectuée.</Alert>;
    }

    return (
      <Card>
        <Card.Body>
          <Card.Title>Niveaux de Support et Résistance</Card.Title>
          <Card.Subtitle className="mb-3">Support</Card.Subtitle>
          <ul>
            {supResResults.support.map((level, index) => (
              <li key={`support-${index}`}>Niveau: {level.toFixed(2)}</li>
            ))}
          </ul>
          <Card.Subtitle className="mb-3">Résistance</Card.Subtitle>
          <ul>
            {supResResults.resistance.map((level, index) => (
              <li key={`resistance-${index}`}>Niveau: {level.toFixed(2)}</li>
            ))}
          </ul>
        </Card.Body>
      </Card>
    );
  };

  // Supprimer un indicateur
  const removeIndicator = (indicator) => {
    setIndicators(indicators.filter(ind => ind !== indicator));
  };

  // Affichage des indicateurs actifs
  const renderActiveIndicators = () => {
    if (indicators.length === 0) {
      return <Alert variant="info">Aucun indicateur actif.</Alert>;
    }

    return (
      <Card>
        <Card.Body>
          <Card.Title>Indicateurs actifs</Card.Title>
          <ul>
            {indicators.map(indicator => (
              <li key={indicator} className="d-flex justify-content-between align-items-center mb-2">
                {indicator.toUpperCase()}
                <Button 
                  variant="outline-danger" 
                  size="sm"
                  onClick={() => removeIndicator(indicator)}
                >
                  ✕
                </Button>
              </li>
            ))}
          </ul>
        </Card.Body>
      </Card>
    );
  };

  return (
    <Container fluid className="mt-4 mb-5">
      <h2 className="mb-4">Analyse Technique</h2>
      
      {error && <Alert variant="danger">{error}</Alert>}
      
      <Row className="mb-4">
        <Col md={6}>
          <Card>
            <Card.Body>
              <Card.Title>Données historiques</Card.Title>
              <Form>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Symbole</Form.Label>
                      <Form.Control 
                        type="text" 
                        value={symbol} 
                        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Timeframe</Form.Label>
                      <Form.Select 
                        value={timeframe} 
                        onChange={(e) => setTimeframe(e.target.value)}
                      >
                        <option value="1m">1 minute</option>
                        <option value="5m">5 minutes</option>
                        <option value="15m">15 minutes</option>
                        <option value="1h">1 heure</option>
                        <option value="4h">4 heures</option>
                        <option value="1d">1 jour</option>
                        <option value="1w">1 semaine</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>
                <Button 
                  variant="primary" 
                  onClick={fetchHistoricalData}
                  disabled={isLoading}
                >
                  {isLoading ? <Spinner size="sm" animation="border" /> : null}
                  {' '}Charger les données
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
        <Col md={6}>
          {renderActiveIndicators()}
        </Col>
      </Row>

      <Row className="mb-4">
        <Col>
          <Card>
            <Card.Body>
              <Card.Title>Graphique</Card.Title>
              {data.length > 0 ? (
                <Line 
                  ref={chartRef}
                  options={chartOptions} 
                  data={prepareChartData() || { labels: [], datasets: [] }} 
                />
              ) : (
                <Alert variant="info">Chargez des données pour afficher le graphique.</Alert>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Body>
              <Tabs
                activeKey={activeTab}
                onSelect={(key) => setActiveTab(key)}
                className="mb-3"
              >
                <Tab eventKey="indicators" title="Indicateurs">
                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label>Indicateur</Form.Label>
                        <Form.Select 
                          value={selectedIndicator} 
                          onChange={(e) => {
                            setSelectedIndicator(e.target.value);
                            setIndicatorParams({});
                          }}
                        >
                          {availableIndicators.map(ind => (
                            <option key={ind} value={ind}>{ind.toUpperCase()}</option>
                          ))}
                        </Form.Select>
                      </Form.Group>
                      {renderIndicatorParams()}
                      <Button 
                        variant="success" 
                        onClick={calculateIndicator}
                        disabled={isLoading || data.length === 0}
                        className="mb-3"
                      >
                        {isLoading ? <Spinner size="sm" animation="border" /> : null}
                        {' '}Calculer l'indicateur
                      </Button>
                    </Col>
                  </Row>
                </Tab>
                <Tab eventKey="patterns" title="Patterns">
                  <Row>
                    <Col md={6}>
                      <Button 
                        variant="success" 
                        onClick={detectPatterns}
                        disabled={isLoading || data.length === 0}
                        className="mb-3"
                      >
                        {isLoading ? <Spinner size="sm" animation="border" /> : null}
                        {' '}Détecter les patterns
                      </Button>
                    </Col>
                    <Col md={6}>
                      {renderPatterns()}
                    </Col>
                  </Row>
                </Tab>
                <Tab eventKey="levels" title="Support/Résistance">
                  <Row>
                    <Col md={6}>
                      <Button 
                        variant="success" 
                        onClick={calculateSupportResistance}
                        disabled={isLoading || data.length === 0}
                        className="mb-3"
                      >
                        {isLoading ? <Spinner size="sm" animation="border" /> : null}
                        {' '}Calculer les niveaux
                      </Button>
                    </Col>
                    <Col md={6}>
                      {renderSupportResistance()}
                    </Col>
                  </Row>
                </Tab>
              </Tabs>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default TechnicalAnalysis; 