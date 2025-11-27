"""
Locust Load Testing Script for Vegetable Classification API

This script simulates a flood of requests to test the model's performance
under different load conditions. It tests both prediction and retraining endpoints.

Usage:
    # Run with web UI (default: http://localhost:8089)
    locust

    # Run headless (no UI)
    locust --headless -u 100 -r 10 -t 60s --host http://localhost:8000

    # Run with specific number of users and spawn rate
    locust -u 50 -r 5 --host http://localhost:8000

Parameters:
    -u, --users: Number of concurrent users
    -r, --spawn-rate: Users spawned per second
    -t, --run-time: Test duration (e.g., 60s, 5m)
    --host: Base URL of the API
"""

from locust import HttpUser, task, between
import os
import random
from pathlib import Path


class VegetableAPITestUser(HttpUser):
    """
    Simulates a user making requests to the Vegetable Classification API.
    """
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a simulated user starts. Loads test images."""
        # Find test images from the data directory
        self.test_images = self._load_test_images()
        if not self.test_images:
            print("WARNING: No test images found! Please ensure data/test directory exists.")
    
    def _load_test_images(self):
        """Load sample images from the test directory for prediction testing."""
        test_dir = Path("data/test")
        images = []
        
        if not test_dir.exists():
            # Try alternative path
            test_dir = Path("../data/test")
        
        if test_dir.exists():
            # Get images from all vegetable class folders
            for class_folder in test_dir.iterdir():
                if class_folder.is_dir():
                    for img_file in class_folder.glob("*.jpg"):
                        images.append(str(img_file))
                        if len(images) >= 50:  # Limit to 50 images for performance
                            break
                    if len(images) >= 50:
                        break
        
        return images
    
    @task(3)
    def predict_image(self):
        """
        Test the /predict endpoint with image upload.
        Weight: 3 (runs 3x more often than retrain)
        """
        if not self.test_images:
            # If no images found, skip this task
            return
        
        # Select a random test image
        image_path = random.choice(self.test_images)
        
        with open(image_path, "rb") as img_file:
            files = {"file": (os.path.basename(image_path), img_file, "image/jpeg")}
            
            with self.client.post(
                "/predict",
                files=files,
                catch_response=True,
                name="Predict Image"
            ) as response:
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if "prediction" in data:
                            response.success()
                        else:
                            response.failure(f"Unexpected response: {data}")
                    except Exception as e:
                        response.failure(f"Failed to parse response: {str(e)}")
                elif response.status_code == 500:
                    response.failure(f"Server error: {response.text}")
                else:
                    response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(0)  # Disable retraining during load tests to get cleaner prediction metrics
    def retrain_model(self):
        """
        Test the /retrain endpoint with multiple image uploads.
        Weight: 0 (disabled during load tests to avoid skewing results)
        Retraining takes 30-90 seconds and skews response time metrics.
        """
        # Disabled for load testing - retraining skews results
        pass
    
    @task(1)
    def health_check(self):
        """
        Test the root endpoint for health checks.
        Weight: 1
        """
        with self.client.get("/", name="Health Check", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


# Optional: Add a class for testing only predictions (lighter load)
class PredictionOnlyUser(HttpUser):
    """
    Lightweight user that only tests prediction endpoint.
    Use this for high-volume prediction testing.
    """
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Load test images."""
        test_dir = Path("data/test")
        self.test_images = []
        
        if not test_dir.exists():
            test_dir = Path("../data/test")
        
        if test_dir.exists():
            for class_folder in test_dir.iterdir():
                if class_folder.is_dir():
                    for img_file in class_folder.glob("*.jpg"):
                        self.test_images.append(str(img_file))
                        if len(self.test_images) >= 20:
                            break
                    if len(self.test_images) >= 20:
                        break
    
    @task
    def predict_image(self):
        """Only test prediction endpoint."""
        if not self.test_images:
            return
        
        image_path = random.choice(self.test_images)
        
        with open(image_path, "rb") as img_file:
            files = {"file": (os.path.basename(image_path), img_file, "image/jpeg")}
            
            with self.client.post(
                "/predict",
                files=files,
                catch_response=True,
                name="Predict Image"
            ) as response:
                if response.status_code == 200 and "prediction" in response.json():
                    response.success()
                else:
                    response.failure(f"Prediction failed: {response.status_code}")

