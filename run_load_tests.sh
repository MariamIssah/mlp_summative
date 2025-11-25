#!/bin/bash
# Load Testing Script for Vegetable Classification API
# This script runs different load test scenarios using Locust

HOST="${HOST:-http://localhost:8000}"

echo "=========================================="
echo "Vegetable Classification API Load Testing"
echo "=========================================="
echo "Host: $HOST"
echo ""

# Function to run a test scenario
run_test() {
    local name=$1
    local users=$2
    local spawn_rate=$3
    local duration=$4
    local output_file=$5
    
    echo "Running: $name"
    echo "Users: $users | Spawn Rate: $spawn_rate/s | Duration: $duration"
    echo "----------------------------------------"
    
    locust --headless \
        -u $users \
        -r $spawn_rate \
        -t $duration \
        --host $HOST \
        -f locustfile.py \
        --html "results/${output_file}.html" \
        --csv "results/${output_file}" \
        --loglevel INFO
    
    echo "Results saved to: results/${output_file}.html"
    echo ""
}

# Create results directory
mkdir -p results

# Scenario 1: Light Load (10 users)
echo "Scenario 1: Light Load Test"
run_test "Light Load" 10 2 "60s" "light_load"

# Scenario 2: Medium Load (50 users)
echo "Scenario 2: Medium Load Test"
run_test "Medium Load" 50 5 "120s" "medium_load"

# Scenario 3: Heavy Load (100 users)
echo "Scenario 3: Heavy Load Test"
run_test "Heavy Load" 100 10 "180s" "heavy_load"

# Scenario 4: Stress Test (200 users)
echo "Scenario 4: Stress Test"
run_test "Stress Test" 200 20 "300s" "stress_test"

echo "=========================================="
echo "All load tests completed!"
echo "Check the 'results' directory for detailed reports."
echo "=========================================="

