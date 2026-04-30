import requests
import json
import datetime
import sqlite3
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'backend_laravel', 'database', 'database.sqlite')
API_URL = "http://127.0.0.1:8000/api/log"

# The user's JSON data (168 hourly records from March 1 to March 7, 2026)
data_json = [
  {"Waktu": "3/1/26 0:00", "Data Aktual (PPM)": "500", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 1:00", "Data Aktual (PPM)": "504", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 2:00", "Data Aktual (PPM)": "512", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 3:00", "Data Aktual (PPM)": "503", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 4:00", "Data Aktual (PPM)": "476", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 5:00", "Data Aktual (PPM)": "535", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 6:00", "Data Aktual (PPM)": "487", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 7:00", "Data Aktual (PPM)": "528", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 8:00", "Data Aktual (PPM)": "594", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 9:00", "Data Aktual (PPM)": "589", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 10:00", "Data Aktual (PPM)": "543", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 11:00", "Data Aktual (PPM)": "584", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 12:00", "Data Aktual (PPM)": "550", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 13:00", "Data Aktual (PPM)": "575", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 14:00", "Data Aktual (PPM)": "567", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 15:00", "Data Aktual (PPM)": "590", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 16:00", "Data Aktual (PPM)": "595", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 17:00", "Data Aktual (PPM)": "602", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 18:00", "Data Aktual (PPM)": "544", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 19:00", "Data Aktual (PPM)": "536", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 20:00", "Data Aktual (PPM)": "552", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 21:00", "Data Aktual (PPM)": "560", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 22:00", "Data Aktual (PPM)": "543", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/1/26 23:00", "Data Aktual (PPM)": "515", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 0:00", "Data Aktual (PPM)": "490", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 1:00", "Data Aktual (PPM)": "507", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 2:00", "Data Aktual (PPM)": "517", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 3:00", "Data Aktual (PPM)": "510", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 4:00", "Data Aktual (PPM)": "488", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 5:00", "Data Aktual (PPM)": "511", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 6:00", "Data Aktual (PPM)": "520", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 7:00", "Data Aktual (PPM)": "487", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 8:00", "Data Aktual (PPM)": "594", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 9:00", "Data Aktual (PPM)": "601", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 10:00", "Data Aktual (PPM)": "605", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 11:00", "Data Aktual (PPM)": "592", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 12:00", "Data Aktual (PPM)": "605", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 13:00", "Data Aktual (PPM)": "576", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 14:00", "Data Aktual (PPM)": "610", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 15:00", "Data Aktual (PPM)": "563", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 16:00", "Data Aktual (PPM)": "572", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 17:00", "Data Aktual (PPM)": "582", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 18:00", "Data Aktual (PPM)": "545", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 19:00", "Data Aktual (PPM)": "523", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 20:00", "Data Aktual (PPM)": "537", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 21:00", "Data Aktual (PPM)": "543", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 22:00", "Data Aktual (PPM)": "525", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/2/26 23:00", "Data Aktual (PPM)": "532", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 0:00", "Data Aktual (PPM)": "518", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 1:00", "Data Aktual (PPM)": "523", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 2:00", "Data Aktual (PPM)": "520", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 3:00", "Data Aktual (PPM)": "505", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 4:00", "Data Aktual (PPM)": "520", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 5:00", "Data Aktual (PPM)": "515", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 6:00", "Data Aktual (PPM)": "526", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 7:00", "Data Aktual (PPM)": "508", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 8:00", "Data Aktual (PPM)": "611", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 9:00", "Data Aktual (PPM)": "612", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 10:00", "Data Aktual (PPM)": "583", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 11:00", "Data Aktual (PPM)": "610", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 12:00", "Data Aktual (PPM)": "586", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 13:00", "Data Aktual (PPM)": "603", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 14:00", "Data Aktual (PPM)": "597", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 15:00", "Data Aktual (PPM)": "565", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 16:00", "Data Aktual (PPM)": "552", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 17:00", "Data Aktual (PPM)": "583", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 18:00", "Data Aktual (PPM)": "543", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 19:00", "Data Aktual (PPM)": "538", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 20:00", "Data Aktual (PPM)": "541", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 21:00", "Data Aktual (PPM)": "539", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 22:00", "Data Aktual (PPM)": "567", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/3/26 23:00", "Data Aktual (PPM)": "521", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 0:00", "Data Aktual (PPM)": "516", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 1:00", "Data Aktual (PPM)": "522", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 2:00", "Data Aktual (PPM)": "501", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 3:00", "Data Aktual (PPM)": "528", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 4:00", "Data Aktual (PPM)": "534", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 5:00", "Data Aktual (PPM)": "509", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 6:00", "Data Aktual (PPM)": "503", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 7:00", "Data Aktual (PPM)": "503", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 8:00", "Data Aktual (PPM)": "615", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 9:00", "Data Aktual (PPM)": "556", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 10:00", "Data Aktual (PPM)": "577", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 11:00", "Data Aktual (PPM)": "597", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 12:00", "Data Aktual (PPM)": "580", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 13:00", "Data Aktual (PPM)": "582", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 14:00", "Data Aktual (PPM)": "612", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 15:00", "Data Aktual (PPM)": "592", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 16:00", "Data Aktual (PPM)": "556", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 17:00", "Data Aktual (PPM)": "577", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 18:00", "Data Aktual (PPM)": "538", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 19:00", "Data Aktual (PPM)": "539", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 20:00", "Data Aktual (PPM)": "567", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 21:00", "Data Aktual (PPM)": "565", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 22:00", "Data Aktual (PPM)": "518", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/4/26 23:00", "Data Aktual (PPM)": "487", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 0:00", "Data Aktual (PPM)": "520", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 1:00", "Data Aktual (PPM)": "520", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 2:00", "Data Aktual (PPM)": "509", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 3:00", "Data Aktual (PPM)": "522", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 4:00", "Data Aktual (PPM)": "505", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 5:00", "Data Aktual (PPM)": "487", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 6:00", "Data Aktual (PPM)": "499", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 7:00", "Data Aktual (PPM)": "533", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 8:00", "Data Aktual (PPM)": "542", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 9:00", "Data Aktual (PPM)": "581", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 10:00", "Data Aktual (PPM)": "576", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 11:00", "Data Aktual (PPM)": "619", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 12:00", "Data Aktual (PPM)": "552", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 13:00", "Data Aktual (PPM)": "616", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 14:00", "Data Aktual (PPM)": "571", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 15:00", "Data Aktual (PPM)": "637", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 16:00", "Data Aktual (PPM)": "612", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 17:00", "Data Aktual (PPM)": "611", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 18:00", "Data Aktual (PPM)": "548", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 19:00", "Data Aktual (PPM)": "545", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 20:00", "Data Aktual (PPM)": "545", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 21:00", "Data Aktual (PPM)": "561", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 22:00", "Data Aktual (PPM)": "541", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/5/26 23:00", "Data Aktual (PPM)": "498", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 0:00", "Data Aktual (PPM)": "541", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 1:00", "Data Aktual (PPM)": "498", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 2:00", "Data Aktual (PPM)": "509", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 3:00", "Data Aktual (PPM)": "521", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 4:00", "Data Aktual (PPM)": "524", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 5:00", "Data Aktual (PPM)": "522", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 6:00", "Data Aktual (PPM)": "501", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 7:00", "Data Aktual (PPM)": "515", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 8:00", "Data Aktual (PPM)": "598", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 9:00", "Data Aktual (PPM)": "580", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 10:00", "Data Aktual (PPM)": "580", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 11:00", "Data Aktual (PPM)": "569", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 12:00", "Data Aktual (PPM)": "560", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 13:00", "Data Aktual (PPM)": "564", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 14:00", "Data Aktual (PPM)": "587", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 15:00", "Data Aktual (PPM)": "614", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 16:00", "Data Aktual (PPM)": "555", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 17:00", "Data Aktual (PPM)": "573", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 18:00", "Data Aktual (PPM)": "523", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 19:00", "Data Aktual (PPM)": "533", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 20:00", "Data Aktual (PPM)": "557", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 21:00", "Data Aktual (PPM)": "539", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 22:00", "Data Aktual (PPM)": "537", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/6/26 23:00", "Data Aktual (PPM)": "512", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 0:00", "Data Aktual (PPM)": "551", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 1:00", "Data Aktual (PPM)": "517", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 2:00", "Data Aktual (PPM)": "516", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 3:00", "Data Aktual (PPM)": "518", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 4:00", "Data Aktual (PPM)": "524", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 5:00", "Data Aktual (PPM)": "511", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 6:00", "Data Aktual (PPM)": "501", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 7:00", "Data Aktual (PPM)": "524", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 8:00", "Data Aktual (PPM)": "621", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 9:00", "Data Aktual (PPM)": "630", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 10:00", "Data Aktual (PPM)": "552", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 11:00", "Data Aktual (PPM)": "616", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 12:00", "Data Aktual (PPM)": "594", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 13:00", "Data Aktual (PPM)": "607", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 14:00", "Data Aktual (PPM)": "577", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 15:00", "Data Aktual (PPM)": "606", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 16:00", "Data Aktual (PPM)": "634", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 17:00", "Data Aktual (PPM)": "612", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 18:00", "Data Aktual (PPM)": "529", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 19:00", "Data Aktual (PPM)": "553", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 20:00", "Data Aktual (PPM)": "535", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 21:00", "Data Aktual (PPM)": "566", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 22:00", "Data Aktual (PPM)": "556", "Status Kualitas Udara": "Sedang"},
  {"Waktu": "3/7/26 23:00", "Data Aktual (PPM)": "505", "Status Kualitas Udara": "Sedang"}
]

# 1. Clear database
print("Clearing database...")
conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()
cursor.execute("DELETE FROM sensor_readings")
conn.commit()
conn.close()

# 2. Inject for both locations
locations = ["Perkotaan", "Pedesaan"]
total_injected = 0

print(f"Injecting {len(data_json)} records for each location...")

for loc in locations:
    print(f"-> Injecting for {loc}...")
    for item in data_json:
        try:
            dt = datetime.datetime.strptime(item["Waktu"], "%m/%d/%y %H:%M")
            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            continue
            
        co2 = float(item["Data Aktual (PPM)"])
        
        data = {
            "co2_ppm": round(co2, 2),
            "co_ppm": 2.00,
            "mq7_detected": False,
            "location": loc,
            "status": item["Status Kualitas Udara"],
            "timestamp": timestamp_str
        }
        
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code in [200, 201, 210]:
                total_injected += 1
        except:
            break

print(f"Done! Successfully injected {total_injected} records in total.")
