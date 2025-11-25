# Load Testing Script for Vegetable Classification API (PowerShell)
# This script runs different load test scenarios using Locust

param(
    [string]$Host = "http://localhost:8000"
)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Vegetable Classification API Load Testing" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Host: $Host" -ForegroundColor Yellow
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
        --host $Host `
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

# Scenario 1: Light Load (10 users)
Write-Host "Scenario 1: Light Load Test" -ForegroundColor Cyan
Run-Test -Name "Light Load" -Users 10 -SpawnRate 2 -Duration "60s" -OutputFile "light_load"

# Scenario 2: Medium Load (50 users)
Write-Host "Scenario 2: Medium Load Test" -ForegroundColor Cyan
Run-Test -Name "Medium Load" -Users 50 -SpawnRate 5 -Duration "120s" -OutputFile "medium_load"

# Scenario 3: Heavy Load (100 users)
Write-Host "Scenario 3: Heavy Load Test" -ForegroundColor Cyan
Run-Test -Name "Heavy Load" -Users 100 -SpawnRate 10 -Duration "180s" -OutputFile "heavy_load"

# Scenario 4: Stress Test (200 users)
Write-Host "Scenario 4: Stress Test" -ForegroundColor Cyan
Run-Test -Name "Stress Test" -Users 200 -SpawnRate 20 -Duration "300s" -OutputFile "stress_test"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "All load tests completed!" -ForegroundColor Green
Write-Host "Check the 'results' directory for detailed reports." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan

