 Script d'installation de PostgreSQL et TimescaleDB pour Windows
# Ã€ exÃ©cuter en tant qu'administrateur

# Configuration
$POSTGRES_VERSION = "14"
$TIMESCALEDB_VERSION = "2.10.1"
$POSTGRES_PASSWORD = "postgres"

# TÃ©lÃ©chargement et installation de PostgreSQL
Write-Host "TÃ©lÃ©chargement de PostgreSQL $POSTGRES_VERSION..."
$POSTGRES_URL = "https://get.enterprisedb.com/postgresql/postgresql-$POSTGRES_VERSION.10-1-windows-x64.exe"
$POSTGRES_INSTALLER = "postgresql_installer.exe"
Invoke-WebRequest -Uri $POSTGRES_URL -OutFile $POSTGRES_INSTALLER

Write-Host "Installation de PostgreSQL..."
Start-Process -Wait -FilePath ".\$POSTGRES_INSTALLER" -ArgumentList "--mode unattended --superpassword $POSTGRES_PASSWORD"
Remove-Item $POSTGRES_INSTALLER

# Ajout de PostgreSQL au PATH
$env:Path += ";C:\Program Files\PostgreSQL\$POSTGRES_VERSION\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path, [System.EnvironmentVariableTarget]::Machine)

# TÃ©lÃ©chargement et installation de TimescaleDB
Write-Host "TÃ©lÃ©chargement de TimescaleDB $TIMESCALEDB_VERSION..."
$TIMESCALEDB_URL = "https://github.com/timescale/timescaledb/releases/download/$TIMESCALEDB_VERSION/timescaledb-postgresql-$POSTGRES_VERSION-windows-amd64.zip"
$TIMESCALEDB_ZIP = "timescaledb.zip"
Invoke-WebRequest -Uri $TIMESCALEDB_URL -OutFile $TIMESCALEDB_ZIP

Write-Host "Installation de TimescaleDB..."
Expand-Archive -Path $TIMESCALEDB_ZIP -DestinationPath "C:\Program Files\PostgreSQL\$POSTGRES_VERSION"
Remove-Item $TIMESCALEDB_ZIP

# Configuration de PostgreSQL pour TimescaleDB
$POSTGRESQL_CONF = "C:\Program Files\PostgreSQL\$POSTGRES_VERSION\data\postgresql.conf"
Add-Content -Path $POSTGRESQL_CONF -Value "shared_preload_libraries = 'timescaledb'"

# RedÃ©marrage du service PostgreSQL
Write-Host "RedÃ©marrage du service PostgreSQL..."
Restart-Service postgresql-x64-$POSTGRES_VERSION

Write-Host "Installation terminÃ©e !"
Write-Host "Vous pouvez maintenant crÃ©er la base de donnÃ©es avec : psql -U postgres -f scripts/create_database.sql" 