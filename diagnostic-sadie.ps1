rite-Host "Diagnostic complet de SADIE..." -ForegroundColor Cyan

# 1. Vérification des conteneurs
Write-Host "Vérification des conteneurs Docker..." -ForegroundColor Yellow
docker ps -a | Select-String "sadie"

# 2. Vérification des ressources
Write-Host "Utilisation des ressources..." -ForegroundColor Yellow
docker stats --no-stream

# 3. Vérification des logs
Write-Host "Derniers logs du frontend..." -ForegroundColor Yellow
docker logs sadie-frontend --tail 30

# 4. Vérification des dépendances
Write-Host "Audit des dépendances npm..." -ForegroundColor Yellow
docker exec sadie-frontend npm outdated

# 5. Vérification de l'espace disque
Write-Host "Espace disque disponible..." -ForegroundColor Yellow
Get-PSDrive C | Format-Table -AutoSize

Write-Host "Diagnostic terminé!" -ForegroundColor Green
