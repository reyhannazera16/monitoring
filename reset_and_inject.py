"""
Reset & Inject - Data Kualitas Udara 1-7 Maret 2026
- STEP 1: Hapus semua data dari https://dimas.rulsit.com/api
- STEP 2: Inject ulang data lengkap 1-7 Maret (per jam)
"""
import requests
import sys
import os
from datetime import datetime

# Import data dari inject_specific_data.py yang sudah ada
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from inject_specific_data import CO_DATA, CO2_DATA

BASE_URL = "https://dimas.rulsit.com/api"


def parse_date(s):
    return datetime.strptime(s, "%m/%d/%y %H:%M").strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# STEP 1: HAPUS SEMUA DATA
# ============================================================
def delete_all_data():
    print("=" * 55)
    print("STEP 1: Menghapus semua data dari database...")
    print("=" * 55)

    deleted = 0
    page = 1

    while True:
        try:
            r = requests.get(
                f"{BASE_URL}/sensor-readings",
                params={"page": page},
                timeout=15
            )
            if r.status_code != 200:
                print(f"  ⚠  Gagal ambil halaman {page}: HTTP {r.status_code}")
                break

            j = r.json()
            # Support paginated (Laravel) response
            items = j.get("data", [])
            if isinstance(items, dict):          # nested pagination
                items = items.get("data", [])
            if not items:
                break

            for item in items:
                rid = item.get("id")
                if not rid:
                    continue
                dr = requests.delete(
                    f"{BASE_URL}/sensor-readings/{rid}",
                    timeout=10
                )
                if dr.status_code in [200, 204]:
                    deleted += 1
                    if deleted % 20 == 0:
                        print(f"  🗑  Dihapus {deleted} record...")
                else:
                    print(f"  ⚠  Gagal hapus id={rid}: HTTP {dr.status_code}")

            # Cek apakah masih ada halaman berikutnya
            next_url = j.get("next_page_url") or (
                j.get("data", {}).get("next_page_url") if isinstance(j.get("data"), dict) else None
            )
            if not next_url:
                break
            page += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            break

    print(f"  ✅ Total dihapus: {deleted} record\n")


# ============================================================
# STEP 2: INJECT DATA BARU (1-7 Maret, per jam)
# ============================================================
def inject_data():
    print("=" * 55)
    print("STEP 2: Inject data 1-7 Maret 2026 (per jam)...")
    print("=" * 55)

    # Gabungkan CO & CO2 per timestamp, per lokasi
    # Perkotaan = Data Aktual (R) / Data Aktual (PPM)
    # Pedesaan  = Prediksi ARIMA (P) / Prediksi ARIMA (PPM)
    urban = {}   # Perkotaan
    rural = {}   # Pedesaan

    for row in CO_DATA:
        ts = parse_date(row["Waktu"])
        urban.setdefault(ts, {"timestamp": ts, "location": "Perkotaan", "co2_ppm": 0.0, "co_ppm": 0.0})
        rural.setdefault(ts, {"timestamp": ts, "location": "Pedesaan",  "co2_ppm": 0.0, "co_ppm": 0.0})
        urban[ts]["co_ppm"] = float(row["Aktual (R)"])
        rural[ts]["co_ppm"] = float(row["Prediksi ARIMA (P)"])

    for row in CO2_DATA:
        ts = parse_date(row["Waktu"])
        urban.setdefault(ts, {"timestamp": ts, "location": "Perkotaan", "co2_ppm": 0.0, "co_ppm": 0.0})
        rural.setdefault(ts, {"timestamp": ts, "location": "Pedesaan",  "co2_ppm": 0.0, "co_ppm": 0.0})
        urban[ts]["co2_ppm"] = float(row["Data Aktual (PPM)"])
        rural[ts]["co2_ppm"] = float(row["Prediksi ARIMA (PPM)"])

    all_records = sorted(
        list(urban.values()) + list(rural.values()),
        key=lambda x: x["timestamp"]
    )

    print(f"  📦 Total record akan diinjeksi: {len(all_records)}")
    print(f"  📅 Range: 1 Maret 2026 – 7 Maret 2026 (24 jam/hari)")
    print(f"  📍 Lokasi: Perkotaan (Aktual) + Pedesaan (Prediksi ARIMA)\n")

    success = 0
    fail = 0
    for i, record in enumerate(all_records, 1):
        try:
            r = requests.post(f"{BASE_URL}/log", json=record, timeout=10)
            if r.status_code in [200, 201, 210]:
                success += 1
                if success % 20 == 0:
                    print(f"  ✅ Injected {success}/{len(all_records)}")
            else:
                fail += 1
                print(f"  ❌ [{i}] {record['timestamp']} [{record['location']}]: "
                      f"HTTP {r.status_code} - {r.text[:60]}")
        except Exception as e:
            fail += 1
            print(f"  ❌ [{i}] Error: {e}")

    print(f"\n  ✨ Selesai! Berhasil: {success} | Gagal: {fail}")


# ============================================================
if __name__ == "__main__":
    print("\n🚀 RESET & INJECT - Data Kualitas Udara 1-7 Maret 2026")
    print("=" * 55)
    delete_all_data()
    inject_data()
    print("\n✅ Done! Refresh dashboard untuk melihat data terbaru.")
