Write-Host "Redémarrage du conteneur SADIE Frontend..." -ForegroundColor Cyan

# Arrêt du conteneur frontend
Write-Host "1. Arrêt du conteneur..." -ForegroundColor Yellow
docker stop sadie-frontend

# Suppression du conteneur
Write-Host "2. Suppression du conteneur..." -ForegroundColor Yellow
docker rm sadie-frontend

# Redémarrage avec docker-compose
Write-Host "3. Redémarrage du conteneur avec docker-compose..." -ForegroundColor Yellow
docker-compose up -d frontend

# Attente pour le démarrage
Write-Host "4. Attente du démarrage du serveur (60 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# Vérification de l'état
Write-Host "5. Vérification de l'état du serveur..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri http://localhost:3000 -Method HEAD -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "`nLe serveur frontend est opérationnel! (StatusCode: $($response.StatusCode))" -ForegroundColor Green
        Write-Host "Accédez à l'application via: http://localhost:3000" -ForegroundColor Cyan
    } else {
        Write-Host "`nLe serveur a répondu avec le code $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "`nImpossible de se connecter au serveur: $_" -ForegroundColor Red
    Write-Host "Vérifiez les logs du conteneur avec: docker logs sadie-frontend" -ForegroundColor Yellow
}

Write-Host "`nConsultez les logs pour plus de détails: docker logs sadie-frontend" -ForegroundColor Magenta 