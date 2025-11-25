# Load Testing Instructions

## Quick Start Guide

### Prerequisites
1. Ensure your API is running on `http://localhost:8000`
2. Install Locust: `pip install locust`
3. Ensure test images exist in `data/test/` directory

### Step 1: Run Basic Load Tests

**Option A: Using the automated script (Windows)**
```powershell
.\run_load_tests.ps1
```

**Option B: Manual testing (recommended for first time)**

Start with a simple test to verify everything works:

```powershell
# Interactive mode - opens web UI
locust --host http://localhost:8000
```

Then open `http://localhost:8089` in your browser and:
1. Set Number of users: 10
2. Set Spawn rate: 2
3. Click "Start Swarming"
4. Let it run for 60 seconds
5. Note the metrics from the Statistics tab

### Step 2: Run Headless Tests for Documentation

Run these tests one at a time and record the results:

```powershell
# Create results directory
mkdir results

# Light Load - 10 users
locust --headless -u 10 -r 2 -t 60s --host http://localhost:8000 --html results/light_load.html --csv results/light_load

# Medium Load - 50 users  
locust --headless -u 50 -r 5 -t 120s --host http://localhost:8000 --html results/medium_load.html --csv results/medium_load

# Heavy Load - 100 users
locust --headless -u 100 -r 10 -t 180s --host http://localhost:8000 --html results/heavy_load.html --csv results/heavy_load
```

### Step 3: Extract Results

After running tests, use the helper script to extract metrics:

```powershell
python extract_load_test_results.py
```

Or manually check the HTML reports in the `results/` folder.

### Step 4: Record Results in README

Update the table in README.md with your actual results. Key metrics to record:
- **RPS**: Requests per second (from Statistics)
- **Median**: Median response time in milliseconds
- **95th %ile**: 95th percentile response time
- **99th %ile**: 99th percentile response time  
- **Max**: Maximum response time
- **Failures**: Number of failed requests

### Step 5: Test with Multiple Containers (Optional)

To test scaling with multiple containers:

1. Update `docker-compose.yml` to add replicas
2. Restart with multiple containers
3. Run the same load tests
4. Compare performance

## Understanding the Results

- **RPS (Requests per Second)**: Higher is better - shows throughput
- **Response Times**: Lower is better - shows latency
- **95th/99th Percentile**: Important for understanding worst-case performance
- **Failures**: Should be 0% for good performance

## Troubleshooting

- **No test images found**: Ensure `data/test/` directory exists with image files
- **Connection refused**: Make sure API is running on port 8000
- **High failure rates**: Reduce number of users or increase spawn rate gradually

