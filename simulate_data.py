import requests
import time
import random
from datetime import datetime

# Configuration
API_URL = "https://dimas.rulsit.com/api/log"
LOCATIONS = ["Perkotaan", "Pedesaan"]
DURATION_SECONDS = 10
TOTAL_READINGS = 20

def simulate():
    print(f"Starting simulation. Target: {API_URL}")
    for i in range(TOTAL_READINGS):
        location = random.choice(LOCATIONS)
        
        # Generate some realistic data
        if location == "Perkotaan":
            co2 = random.uniform(400, 800)
            co = random.uniform(2, 10)
        else:
            co2 = random.uniform(350, 450)
            co = random.uniform(0.5, 2.5)
            
        data = {
            "co2_ppm": co2,
            "co_ppm": co,
            "mq7_detected": co > 15,
            "location": location,
            "status": "Simulated"
        }
        
        try:
            print(f"[{i+1}/{TOTAL_READINGS}] Sending data for {location}: CO2={co2:.2f}, CO={co:.2f}...")
            response = requests.post(API_URL, json=data)
            print(f"Response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Error sending data: {e}")
            
        if i < TOTAL_READINGS - 1:
            print(f"Waiting {DURATION_SECONDS} seconds...")
            time.sleep(DURATION_SECONDS)

    print("Simulation complete.")

if __name__ == "__main__":
    simulate()
