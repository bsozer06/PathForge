Param(
  [string]$NetworkName = "pathforge-net",
  [string]$ContainerName = "pg-postgis-5434",
  [string]$DbName = "osm",
  [string]$PostgresPassword = "StrongP@ssw0rd",
  [int]$HostPort = 5434,
  [string]$PostgisImage = "postgis/postgis:15-3.4",
  [string]$Osm2pgsqlImage = "iboates/osm2pgsql:latest",
  [string]$Workdir = (Get-Location).Path,
  [string]$PbfFile = "turkey-latest.osm.pbf",
  [switch]$SkipImport = $false,
  [switch]$SkipRoads = $false
)

$ErrorActionPreference = "Stop"

function Fail($msg) { Write-Error $msg; exit 1 }

# Verify Docker CLI
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Fail "Docker CLI not found. Please install/launch Docker Desktop and retry."
}

Write-Host "Ensuring Docker network '$NetworkName' exists ..."
$netExists = docker network ls --format "{{.Name}}" | Where-Object { $_ -eq $NetworkName }
if (-not $netExists) {
  docker network create $NetworkName | Out-Null
}

Write-Host "Starting PostGIS container '$ContainerName' on network '$NetworkName' ..."
$exists = docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }
if ($exists) {
  $running = docker ps --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName }
  if (-not $running) { docker start $ContainerName | Out-Null }
  # Ensure correct network connection
  docker network connect $NetworkName $ContainerName 2>$null
} else {
  docker run -d --name $ContainerName --network $NetworkName `
    -e POSTGRES_PASSWORD=$PostgresPassword -e POSTGRES_DB=$DbName `
    -p $HostPort:5432 $PostgisImage | Out-Null
}

Write-Host "Waiting for PostgreSQL readiness ..."
$maxAttempts = 60
for ($i=0; $i -lt $maxAttempts; $i++) {
  $ready = docker exec $ContainerName pg_isready -U postgres 2>&1
  if ($LASTEXITCODE -eq 0) { break }
  Start-Sleep -Seconds 2
}
if ($i -ge $maxAttempts) { Fail "PostgreSQL did not become ready in time." }

Write-Host "Enabling extensions (postgis, hstore) ..."
$extOut1 = docker exec $ContainerName psql -U postgres -d $DbName -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>&1
if ($LASTEXITCODE -ne 0) { Fail "Failed to enable postgis: $extOut1" }
$extOut2 = docker exec $ContainerName psql -U postgres -d $DbName -c "CREATE EXTENSION IF NOT EXISTS hstore;" 2>&1
if ($LASTEXITCODE -ne 0) { Fail "Failed to enable hstore: $extOut2" }

if (-not $SkipImport) {
  $pbfPath = Join-Path $Workdir $PbfFile
  if (-not (Test-Path $pbfPath)) {
    Fail "PBF file not found at '$pbfPath'. Download it first or pass -PbfFile path."
  }
  Write-Host "Importing OSM data from '$pbfPath' ..."
  $volume = "$Workdir:/data"
  $imp = docker run --rm --network $NetworkName -v "$volume" `
    -e PGPASSWORD=$PostgresPassword $Osm2pgsqlImage `
    osm2pgsql -d $DbName -U postgres --host $ContainerName --port 5432 `
    --create --slim --hstore --latlong "/data/$PbfFile" 2>&1
  if ($LASTEXITCODE -ne 0) { Fail "osm2pgsql import failed: $imp" }
}

if (-not $SkipRoads) {
  Write-Host "Creating roads table ..."
  docker exec $ContainerName sh -c "mkdir -p /data" | Out-Null
  $roadsLocal = Join-Path $Workdir "scripts\roads.sql"
  if (-not (Test-Path $roadsLocal)) { Fail "roads.sql not found at '$roadsLocal'" }
  docker cp $roadsLocal "$ContainerName:/data/roads.sql"
  $roadsOut = docker exec $ContainerName psql -U postgres -d $DbName -f /data/roads.sql 2>&1
  if ($LASTEXITCODE -ne 0) { Fail "Applying roads.sql failed: $roadsOut" }
}

Write-Host "Verifying roads count ..."
$cntOut = docker exec $ContainerName psql -U postgres -d $DbName -c "SELECT COUNT(*) FROM roads;" 2>&1
Write-Host $cntOut

Write-Host "Done. Update your .env if needed:"
Write-Host "PGHOST=localhost"; Write-Host "PGPORT=$HostPort"; Write-Host "PGUSER=postgres"; Write-Host "PGPASSWORD=$PostgresPassword"; Write-Host "PGDATABASE=$DbName";
