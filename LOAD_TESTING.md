# Load Testing Guide

This guide explains how to perform load testing on the Vegetable Classification API using Locust.

## Prerequisites

1. Install Locust:

   ```bash
   pip install locust
   ```

   Or install all requirements:

   ```bash
   pip install -r requirements.txt
   ```

2. Ensure your API is running:
   ```bash
   uvicorn api.app:app --host 0.0.0.0 --port 8000
   ```

## Quick Start

### Interactive Mode (Web UI)

1. Start Locust with web UI:

   ```bash
   locust --host http://localhost:8000
   ```

2. Open your browser to `http://localhost:8089`

3. Configure test parameters:

   - **Number of users**: Total concurrent users
   - **Spawn rate**: Users spawned per second
   - **Host**: API base URL (default: http://localhost:8000)

4. Click "Start Swarming" to begin the test

5. Monitor real-time statistics:
   - Request rates
   - Response times (min, max, median, 95th percentile)
   - Failure rates
   - Number of requests per second

### Headless Mode (Command Line)

Run tests without the web UI:

```bash
locust --headless -u 100 -r 10 -t 60s --host http://localhost:8000
```

Parameters:

- `-u, --users`: Number of concurrent users (e.g., 100)
- `-r, --spawn-rate`: Users spawned per second (e.g., 10)
- `-t, --run-time`: Test duration (e.g., 60s, 5m, 1h)
- `--host`: Base URL of your API

### Generate HTML Reports

Save results to HTML and CSV files:

```bash
locust --headless -u 100 -r 10 -t 60s --host http://localhost:8000 \
    --html results/load_test.html \
    --csv results/load_test
```

This creates:

- `results/load_test.html`: Interactive HTML report
- `results/load_test_stats.csv`: Request statistics
- `results/load_test_failures.csv`: Failed requests
- `results/load_test_exceptions.csv`: Exceptions

## Test Scenarios

### Scenario 1: Light Load

Test with 10 concurrent users:

```bash
locust --headless -u 10 -r 2 -t 60s --host http://localhost:8000 \
    --html results/light_load.html --csv results/light_load
```

### Scenario 2: Medium Load

Test with 50 concurrent users:

```bash
locust --headless -u 50 -r 5 -t 120s --host http://localhost:8000 \
    --html results/medium_load.html --csv results/medium_load
```

### Scenario 3: Heavy Load

Test with 100 concurrent users:

```bash
locust --headless -u 100 -r 10 -t 180s --host http://localhost:8000 \
    --html results/heavy_load.html --csv results/heavy_load
```

### Scenario 4: Stress Test

Test with 200 concurrent users:

```bash
locust --headless -u 200 -r 20 -t 300s --host http://localhost:8000 \
    --html results/stress_test.html --csv results/stress_test
```

## Running Automated Test Suite

### Windows (PowerShell)

```powershell
.\run_load_tests.ps1 -Host http://localhost:8000
```

### Linux/Mac (Bash)

```bash
chmod +x run_load_tests.sh
./run_load_tests.sh
```

Or set a custom host:

```bash
HOST=http://your-api-url:8000 ./run_load_tests.sh
```

## Testing with Docker Containers

To test with different numbers of Docker containers:

1. **Single Container**:

   ```bash
   docker run -p 8000:8000 your-image
   locust --headless -u 50 -r 5 -t 60s --host http://localhost:8000
   ```

2. **Multiple Containers** (using Docker Compose):

   ```yaml
   # docker-compose.yml
   version: "3.8"
   services:
     api:
       image: your-image
       deploy:
         replicas: 3 # Test with 3 containers
       ports:
         - "8000-8002:8000"
   ```

   Then run Locust against a load balancer or test each container individually.

3. **Record Results for Each Configuration**:
   - 1 container: `results/1_container.html`
   - 3 containers: `results/3_containers.html`
   - 5 containers: `results/5_containers.html`

## Understanding Results

### Key Metrics to Record

1. **Response Time**:

   - Median response time
   - 95th percentile response time
   - 99th percentile response time
   - Maximum response time

2. **Throughput**:

   - Requests per second (RPS)
   - Total requests completed

3. **Error Rate**:

   - Percentage of failed requests
   - Number of exceptions

4. **Latency**:
   - Time to first byte
   - Total request duration

### Example Results Table

| Container Count | Users | RPS | Median (ms) | 95th %ile (ms) | Failures |
| --------------- | ----- | --- | ----------- | -------------- | -------- |
| 1               | 50    | 12  | 450         | 1200           | 0%       |
| 3               | 50    | 35  | 180         | 450            | 0%       |
| 5               | 50    | 58  | 120         | 280            | 0%       |
| 1               | 100   | 15  | 800         | 2500           | 2%       |
| 3               | 100   | 42  | 250         | 650            | 0%       |
| 5               | 100   | 70  | 150         | 400            | 0%       |

## Tips

1. **Start Small**: Begin with low user counts and gradually increase
2. **Monitor Resources**: Watch CPU, memory, and network usage during tests
3. **Test Predictions Only**: For high-volume testing, use `PredictionOnlyUser` class
4. **Avoid Retraining in Load Tests**: The retrain endpoint is expensive; use sparingly
5. **Warm Up**: Allow a few seconds for the model to load before starting tests
6. **Test Different Times**: Run tests at different times to account for variability

## Troubleshooting

### No test images found

Ensure `data/test` directory exists with vegetable class folders and images.

### Connection refused

Verify your API is running and accessible at the specified host.

### High failure rates

- Reduce the number of concurrent users
- Increase spawn rate (gradual ramp-up)
- Check API server logs for errors
- Verify model file exists and is loaded correctly

### Timeout errors

- Increase timeout values in locustfile.py
- Check if the API is overloaded
- Verify network connectivity

## For Assignment Submission

Include the following in your README:

1. **Load Test Results**: Screenshots or tables showing latency/response times
2. **Container Comparison**: Results for 1, 3, and 5 containers (or similar)
3. **Analysis**: Brief explanation of how the system scales with more containers
4. **Locust Configuration**: Mention the locustfile.py and test scenarios used

Example section for README:

```markdown
## Load Testing Results

We performed load testing using Locust with different numbers of Docker containers.
Results show improved response times and throughput with increased container count.

[Include tables/charts here]
```
