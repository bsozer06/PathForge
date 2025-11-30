Param(
  [string]$ContainerName = "pg-postgis",
  [string]$PostgresPassword = "yourpassword",
  [string]$Database = "osm",
  [int]$HostPort = 5432,
  [string]$Image = "postgis/postgis:15-3.4"
)

Write-Host "Pulling image $Image ..."
docker pull $Image | Out-Null

if ((docker ps -a --format "{{.Names}}" | Where-Object { $_ -eq $ContainerName })) {
  Write-Host "Container $ContainerName already exists. Restarting..."
  docker restart $ContainerName | Out-Null
} else {
  Write-Host "Creating container $ContainerName ..."
  docker run -d --name $ContainerName `
    -e POSTGRES_PASSWORD=$PostgresPassword `
    -e POSTGRES_DB=$Database `
    -p $HostPort:5432 `
    $Image | Out-Null
}

Write-Host "Waiting for PostgreSQL to accept connections..."
$maxAttempts = 30
for ($i=0; $i -lt $maxAttempts; $i++) {
  try {
    docker exec $ContainerName pg_isready -U postgres | Out-Null
    if ($LASTEXITCODE -eq 0) { break }
  } catch {}
  Start-Sleep -Seconds 2
}

if ($i -ge $maxAttempts) {
  Write-Error "PostgreSQL did not become ready in time."; exit 1
}

Write-Host "Enabling extensions in database $Database ..."
docker exec $ContainerName psql -U postgres -d $Database -c "CREATE EXTENSION IF NOT EXISTS postgis;" | Out-Null
# hstore is optional but useful for osm2pgsql
docker exec $ContainerName psql -U postgres -d $Database -c "CREATE EXTENSION IF NOT EXISTS hstore;" | Out-Null

Write-Host "PostGIS container is ready: name=$ContainerName, port=$HostPort, db=$Database"
Write-Host "Update your .env with:"
Write-Host "PGHOST=localhost"; Write-Host "PGPORT=$HostPort"; Write-Host "PGUSER=postgres"; Write-Host "PGPASSWORD=$PostgresPassword"; Write-Host "PGDATABASE=$Database";