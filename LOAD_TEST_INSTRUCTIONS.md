# Load Testing Instructions

## Quick Start Guide

To fill in the load testing results table in README.md, follow these steps:

### Prerequisites

1. Ensure your API is running:
   ```bash
   # Option 1: Using Docker Compose
   docker-compose up
   
   # Option 2: Directly
   uvicorn api.app:app --host 0.0.0.0 --port 8000
   ```

2. Install Locust (if not already installed):
   ```bash
   pip install locust
   ```

### Running Load Tests

#### Test with 1 Container

1. Start API with 1 container:
   ```bash
   docker-compose up
   ```

2. Run tests for different user counts:

   **10 users (Light Load):**
   ```bash
   locust --headless -u 10 -r 2 -t 60s --host http://localhost:8000 --html results/10_users_1_container.html --csv results/10_users_1_container
   ```

   **50 users (Medium Load):**
   ```bash
   locust --headless -u 50 -r 5 -t 120s --host http://localhost:8000 --html results/50_users_1_container.html --csv results/50_users_1_container
   ```

   **100 users (Heavy Load):**
   ```bash
   locust --headless -u 100 -r 10 -t 180s --host http://localhost:8000 --html results/100_users_1_container.html --csv results/100_users_1_container
   ```

#### Test with Multiple Containers

1. Modify `docker-compose.yml` to scale containers:
   ```bash
   # For 3 containers
   docker-compose up --scale api=3
   
   # For 5 containers
   docker-compose up --scale api=5
   ```

2. Run the same test commands as above, but update the output filenames:
   ```bash
   # Example for 3 containers, 50 users
   locust --headless -u 50 -r 5 -t 120s --host http://localhost:8000 --html results/50_users_3_containers.html --csv results/50_users_3_containers
   ```

### Extracting Results

After each test, check the CSV files in the `results/` directory:

- `results/*_stats.csv` - Contains RPS, median, 95th percentile, 99th percentile, max response times
- `results/*_failures.csv` - Contains failure counts

Or use the HTML reports which show all metrics visually.

### Using the PowerShell Script

Alternatively, use the provided script:

```powershell
.\run_load_tests.ps1
```

This will run all test scenarios automatically and save results to the `results/` directory.

### Filling in the README Table

Once you have results, update the table in README.md (lines 266-274) with:

- **RPS**: Requests per second (from stats CSV)
- **Median (ms)**: Median response time
- **95th %ile (ms)**: 95th percentile response time
- **99th %ile (ms)**: 99th percentile response time
- **Max (ms)**: Maximum response time
- **Failures**: Number of failed requests

### Example Results Format

```
| Container Count | Users | RPS | Median (ms) | 95th %ile (ms) | 99th %ile (ms) | Max (ms) | Failures |
| --------------- | ----- | --- | ----------- | -------------- | -------------- | -------- | -------- |
| 1               | 10    | 5.2 | 180         | 350            | 450            | 1200     | 0        |
| 1               | 50    | 8.5 | 250         | 500            | 800            | 2000     | 2        |
```

### Notes

- Run each test for at least 60-120 seconds for reliable results
- Make sure the API is fully loaded before starting tests
- Test during off-peak hours if using shared resources
- Multiple container tests require a load balancer (consider using nginx or similar)

