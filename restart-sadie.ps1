rite-Host "RedÃ©marrage du conteneur SADIE Frontend..." -ForegroundColor Cyan

# ArrÃªt du conteneur frontend
Write-Host "1. ArrÃªt du conteneur..." -ForegroundColor Yellow
docker stop sadie-frontend

# Suppression du conteneur
Write-Host "2. Suppression du conteneur..." -ForegroundColor Yellow
docker rm sadie-frontend

# RedÃ©marrage avec docker-compose
Write-Host "3. RedÃ©marrage du conteneur avec docker-compose..." -ForegroundColor Yellow
docker-compose up -d frontend

# Attente pour le dÃ©marrage
Write-Host "4. Attente du dÃ©marrage du serveur (60 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 60

# VÃ©rification de l'Ã©tat
Write-Host "5. VÃ©rification de l'Ã©tat du serveur..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri http://localhost:3000 -Method HEAD -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "`nLe serveur frontend est opÃ©rationnel! (StatusCode: $($response.StatusCode))" -ForegroundColor Green
        Write-Host "AccÃ©dez Ã  l'application via: http://localhost:3000" -ForegroundColor Cyan
    } else {
        Write-Host "`nLe serveur a rÃ©pondu avec le code $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "`nImpossible de se connecter au serveur: $_" -ForegroundColor Red
    Write-Host "VÃ©rifiez les logs du conteneur avec: docker logs sadie-frontend" -ForegroundColor Yellow
}

Write-Host "`nConsultez les logs pour plus de dÃ©tails: docker logs sadie-frontend" -ForegroundColor Magenta 