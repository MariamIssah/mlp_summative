# Load Testing Script for Vegetable Classification API (PowerShell)
# This script runs different load test scenarios using Locust

param(
    [string]$ApiHost = "http://localhost:8000"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Vegetable Classification API Load Testing" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "API Host: $ApiHost" -ForegroundColor Yellow
Write-Host ""

# Function to run a test scenario
function Run-Test {
    param(
        [string]$Name,
        [int]$Users,
        [int]$SpawnRate,
        [string]$Duration,
        [string]$OutputFile
    )
    
    Write-Host "Running: $Name" -ForegroundColor Green
    Write-Host "Users: $Users | Spawn Rate: $SpawnRate/s | Duration: $Duration" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Gray
    
    locust --headless `
        -u $Users `
        -r $SpawnRate `
        -t $Duration `
        --host $ApiHost `
        -f locustfile.py `
        --html "results/${OutputFile}.html" `
        --csv "results/${OutputFile}" `
        --loglevel INFO
    
    Write-Host "Results saved to: results/${OutputFile}.html" -ForegroundColor Green
    Write-Host ""
}

# Create results directory
if (-not (Test-Path "results")) {
    New-Item -ItemType Directory -Path "results" | Out-Null
}

# Scenario 1: Light Load (10 users) - 1 container
Write-Host "Scenario 1: Light Load Test (1 container, 10 users)" -ForegroundColor Cyan
Run-Test -Name "Light Load" -Users 10 -SpawnRate 2 -Duration "120s" -OutputFile "10_users_1_container"

# Scenario 2: Medium Load (50 users) - 1 container
Write-Host "Scenario 2: Medium Load Test (1 container, 50 users)" -ForegroundColor Cyan
Run-Test -Name "Medium Load" -Users 50 -SpawnRate 5 -Duration "180s" -OutputFile "50_users_1_container"

# Scenario 3: Heavy Load (100 users) - 1 container
Write-Host "Scenario 3: Heavy Load Test (1 container, 100 users)" -ForegroundColor Cyan
Run-Test -Name "Heavy Load" -Users 100 -SpawnRate 10 -Duration "240s" -OutputFile "100_users_1_container"

# Note: For multiple containers (3, 5), you'll need to:
# 1. Scale docker-compose: docker-compose up --scale api=3
# 2. Run tests manually with updated filenames, or modify this script

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "All load tests completed!" -ForegroundColor Green
Write-Host "Check the 'results' directory for detailed reports." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

