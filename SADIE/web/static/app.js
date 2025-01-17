// Configuration des graphiques
const priceData = {
    x: [],
    y: [],
    type: 'scatter',
    name: 'Prix',
    line: {
        color: '#3B82F6',
        width: 2
    }
};

const volumeData = {
    x: [],
    y: [],
    type: 'bar',
    name: 'Volume',
    marker: {
        color: '#10B981'
    }
};

// Configuration des graphiques Plotly
const priceLayout = {
    title: 'Prix BTC/USDT',
    xaxis: { 
        title: 'Temps',
        gridcolor: '#E5E7EB'
    },
    yaxis: { 
        title: 'Prix',
        gridcolor: '#E5E7EB'
    },
    paper_bgcolor: 'white',
    plot_bgcolor: 'white',
    margin: { t: 30 }
};

const volumeLayout = {
    title: 'Volume des Trades',
    xaxis: { 
        title: 'Temps',
        gridcolor: '#E5E7EB'
    },
    yaxis: { 
        title: 'Volume',
        gridcolor: '#E5E7EB'
    },
    paper_bgcolor: 'white',
    plot_bgcolor: 'white',
    margin: { t: 30 }
};

// Initialisation des graphiques
Plotly.newPlot('price-chart', [priceData], priceLayout);
Plotly.newPlot('volume-chart', [volumeData], volumeLayout);

// Connexion WebSocket
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function() {
    console.log('Connexion WebSocket établie');
};

ws.onclose = function() {
    console.log('Connexion WebSocket fermée');
};

ws.onerror = function(error) {
    console.error('Erreur WebSocket:', error);
};

// Gestion des messages WebSocket
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    // Mise à jour des graphiques
    Plotly.extendTraces('price-chart', {
        x: [[data.timestamp]],
        y: [[data.price]]
    }, [0]);
    
    Plotly.extendTraces('volume-chart', {
        x: [[data.timestamp]],
        y: [[data.volume]]
    }, [0]);
    
    // Limitation du nombre de points affichés
    if (priceData.x.length > 100) {
        Plotly.relayout('price-chart', {
            xaxis: {
                range: [priceData.x[priceData.x.length - 100], priceData.x[priceData.x.length - 1]]
            }
        });
    }
    
    // Mise à jour des statistiques
    updateStats(data);
};

// Mise à jour des statistiques
function updateStats(data) {
    document.getElementById('last-price').textContent = 
        data.price.toFixed(2) + ' USDT';
    document.getElementById('volume-24h').textContent = 
        data.volume_24h.toFixed(2) + ' BTC';
    document.getElementById('trades-per-sec').textContent = 
        data.trades_per_sec.toFixed(1);
    
    const change = data.change_24h;
    const changeElement = document.getElementById('change-24h');
    changeElement.textContent = change.toFixed(2) + '%';
    changeElement.className = change >= 0 ? 'positive' : 'negative';
} 