"""
Helper script to extract load test results from Locust CSV files
and format them for the README.
"""

import csv
import os
from pathlib import Path

def extract_metrics(csv_file):
    """Extract key metrics from Locust stats CSV file"""
    if not os.path.exists(csv_file):
        return None
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['Type'] == 'Aggregated':
                return {
                    'rps': float(row.get('Requests/s', 0)),
                    'median': float(row.get('Median response time', 0)),
                    'p95': float(row.get('95%', 0)),
                    'p99': float(row.get('99%', 0)),
                    'max': float(row.get('Max response time', 0)),
                    'failures': int(row.get('Failures', 0)),
                    'total_requests': int(row.get('Request Count', 0))
                }
    return None

def main():
    results_dir = Path("results")
    if not results_dir.exists():
        print("Results directory not found. Run load tests first.")
        return
    
    print("Load Test Results Summary")
    print("=" * 80)
    print(f"{'Test':<20} {'RPS':<10} {'Median (ms)':<15} {'95th %ile (ms)':<15} {'99th %ile (ms)':<15} {'Max (ms)':<15} {'Failures':<10}")
    print("-" * 80)
    
    test_files = [
        ("light_load", "Light Load (10 users)"),
        ("medium_load", "Medium Load (50 users)"),
        ("heavy_load", "Heavy Load (100 users)"),
        ("stress_test", "Stress Test (200 users)")
    ]
    
    for file_prefix, test_name in test_files:
        csv_file = results_dir / f"{file_prefix}_stats.csv"
        metrics = extract_metrics(csv_file)
        
        if metrics:
            print(f"{test_name:<20} {metrics['rps']:<10.2f} {metrics['median']:<15.2f} {metrics['p95']:<15.2f} {metrics['p99']:<15.2f} {metrics['max']:<15.2f} {metrics['failures']:<10}")
        else:
            print(f"{test_name:<20} {'N/A':<10} {'N/A':<15} {'N/A':<15} {'N/A':<15} {'N/A':<15} {'N/A':<10}")
    
    print("\nTo update README, copy the metrics from the table above.")

if __name__ == "__main__":
    main()

