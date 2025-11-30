Param(
  [string]$ContainerName = "pg-postgis",
  [string]$PostgresPassword = "yourpassword",
  [string]$Database = "osm",
  [int]$HostPort = 5434,
  [string]$Image = "postgis/postgis:15-3.4"
)

function Fail($msg) { Write-Error $msg; exit 1 }

# Verify Docker exists
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Fail "Docker CLI not found. Please install Docker Desktop and retry."
}

# Build single-line docker run command string and execute
$cmd = "docker run -d --name $ContainerName -e POSTGRES_PASSWORD=$PostgresPassword -e POSTGRES_DB=$Database -p $HostPort:5432 $Image"
Write-Host "Executing: $cmd"
$runOut = Invoke-Expression $cmd 2>&1
if ($LASTEXITCODE -ne 0) { Fail "docker run failed. Details: $runOut" }

Write-Host "Container started. You can now enable extensions:"
Write-Host " docker exec $ContainerName psql -U postgres -d $Database -c \"CREATE EXTENSION IF NOT EXISTS postgis;\""
Write-Host " docker exec $ContainerName psql -U postgres -d $Database -c \"CREATE EXTENSION IF NOT EXISTS hstore;\""

Write-Host "Update your .env with:"
Write-Host "PGHOST=localhost"; Write-Host "PGPORT=$HostPort"; Write-Host "PGUSER=postgres"; Write-Host "PGPASSWORD=$PostgresPassword"; Write-Host "PGDATABASE=$Database";