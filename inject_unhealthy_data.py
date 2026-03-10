import requests
import datetime
import time

# Configuration
API_URL = "https://dimas.rulsit.com/api/log"
LOCATION = "Pedesaan"
START_DATE = datetime.datetime(2026, 3, 10, 14, 0, 0)
DAYS_AHEAD = 7
READINGS_PER_DAY = 4  # Every 6 hours

def inject_data():
    print(f"🚀 Injecting simulation data for {LOCATION}")
    print(f"Target API: {API_URL}")
    print(f"Timerange: {START_DATE} to {START_DATE + datetime.timedelta(days=DAYS_AHEAD)}")
    
    total_readings = DAYS_AHEAD * READINGS_PER_DAY
    
    for i in range(total_readings):
        # Progress (0.0 to 1.0)
        progress = i / (total_readings - 1)
        
        if LOCATION == "Perkotaan":
            # Hazardous trend
            co2 = 400 + (progress * 5600)
            co = 2 + (progress * 38)
            status = "Hazardous Simulation"
        else:
            # Safe/Good trend
            co2 = 380 + (progress * 50)
            co = 1.2 + (progress * 1.5)
            status = "Safe Simulation"
        
        # Calculate timestamp
        current_time = START_DATE + datetime.timedelta(hours=i * (24 / READINGS_PER_DAY))
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        data = {
            "co2_ppm": round(co2, 2),
            "co_ppm": round(co, 2),
            "mq7_detected": co > 9 if LOCATION == "Perkotaan" else False,
            "location": LOCATION,
            "status": status,
            "timestamp": timestamp_str
        }
        
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code in [200, 201, 210]:
                print(f"✅ [{i+1}/{total_readings}] {timestamp_str}: CO2={data['co2_ppm']}, CO={data['co_ppm']} (Success)")
            else:
                print(f"❌ [{i+1}/{total_readings}] {timestamp_str}: Error {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
            break

    print(f"\n✨ Done! {LOCATION} data has been updated.")
    print("Refresh your browser to see the 'Survival Analysis' update.")

if __name__ == "__main__":
    inject_data()
