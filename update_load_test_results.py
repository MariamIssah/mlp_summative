"""
Script to extract Locust load test results and update README.md table.

Usage:
    python update_load_test_results.py

This script reads Locust CSV results and updates the load testing table in README.md.
"""

import csv
import re
import os
from pathlib import Path

def extract_metrics_from_csv(csv_file):
    """Extract metrics from Locust stats CSV file."""
    if not os.path.exists(csv_file):
        return None
    
    def safe_float(value, default=0.0):
        """Safely convert value to float, handling N/A and empty strings."""
        if not value or value == 'N/A' or value == '':
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def safe_int(value, default=0):
        """Safely convert value to int, handling N/A and empty strings."""
        if not value or value == 'N/A' or value == '':
            return default
        try:
            return int(float(value))  # Convert via float first to handle decimals
        except (ValueError, TypeError):
            return default
    
    try:
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Look for the aggregate row (Type = "Aggregated" or empty Type with "Aggregated" name)
                if row.get('Type') == 'Aggregated' or (not row.get('Type') and row.get('Name') == 'Aggregated'):
                    return {
                        'rps': safe_float(row.get('Requests/s', 0)),
                        'median': safe_float(row.get('Median Response Time', 0)),
                        'p95': safe_float(row.get('95%', 0)),
                        'p99': safe_float(row.get('99%', 0)),
                        'max': safe_float(row.get('Max Response Time', 0)),
                        'failures': safe_int(row.get('Failure Count', row.get('Failures', 0)))
                    }
    except Exception as e:
        print(f"Error reading {csv_file}: {e}")
        return None
    
    return None

def update_readme_table(results_dict):
    """Update the README.md table with results."""
    readme_path = "README.md"
    
    if not os.path.exists(readme_path):
        print(f"ERROR: {readme_path} not found!")
        return False
    
    # Read README
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the table section
    table_pattern = r'(\| Container Count \| Users \| RPS \| Median \(ms\) \| 95th %ile \(ms\) \| 99th %ile \(ms\) \| Max \(ms\) \| Failures \|\n\|[^\n]+\n)((?:\|[^\n]+\n)+)'
    match = re.search(table_pattern, content)
    
    if not match:
        print("ERROR: Could not find load testing table in README.md")
        return False
    
    # Build new table rows
    new_rows = []
    for container_count in [1, 3, 5]:
        for users in [10, 50, 100]:
            # Include all test scenarios
            
            key = f"{container_count}_{users}"
            if key in results_dict:
                metrics = results_dict[key]
                row = f"| {container_count}               | {users}    | {metrics['rps']:.1f} | {metrics['median']:.0f}         | {metrics['p95']:.0f}            | {metrics['p99']:.0f}            | {metrics['max']:.0f}     | {metrics['failures']}        |\n"
            else:
                row = f"| {container_count}               | {users}    | -   | -           | -              | -              | -        | -        |\n"
            new_rows.append(row)
    
    # Reconstruct table
    header = match.group(1)
    new_table = header + ''.join(new_rows)
    
    # Replace in content
    new_content = content[:match.start()] + new_table + content[match.end():]
    
    # Write back
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✓ README.md table updated successfully!")
    return True

def main():
    """Main function to extract and update results."""
    results_dir = Path("results")
    
    if not results_dir.exists():
        print("ERROR: 'results' directory not found!")
        print("Please run load tests first using:")
        print("  locust --headless -u 50 -r 5 -t 120s --host http://localhost:8000 --csv results/test")
        return
    
    results_dict = {}
    
    # Expected test scenarios
    scenarios = [
        (1, 10, "10_users_1_container"),
        (1, 50, "50_users_1_container"),
        (1, 100, "100_users_1_container"),
        (3, 50, "50_users_3_containers"),
        (3, 100, "100_users_3_containers"),
        (5, 50, "50_users_5_containers"),
        (5, 100, "100_users_5_containers"),
    ]
    
    print("Extracting results from CSV files...")
    for container_count, users, filename in scenarios:
        csv_file = results_dir / f"{filename}_stats.csv"
        metrics = extract_metrics_from_csv(csv_file)
        
        if metrics:
            key = f"{container_count}_{users}"
            results_dict[key] = metrics
            print(f"✓ Found results for {container_count} container(s), {users} users")
            print(f"  RPS: {metrics['rps']:.1f}, Median: {metrics['median']:.0f}ms, Failures: {metrics['failures']}")
        else:
            print(f"✗ No results found for {container_count} container(s), {users} users")
    
    if results_dict:
        print(f"\nFound {len(results_dict)} test result(s). Updating README.md...")
        update_readme_table(results_dict)
    else:
        print("\nNo results found! Please run load tests first.")
        print("\nExample command:")
        print("  locust --headless -u 50 -r 5 -t 120s --host http://localhost:8000 --csv results/50_users_1_container")

if __name__ == "__main__":
    main()

