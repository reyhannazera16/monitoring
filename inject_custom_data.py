import requests
import json
import datetime

API_URL = "http://127.0.0.1:8000/api/log"
LOCATION = "Perkotaan"

# The user's JSON data
data_json = [
  {
    "Waktu": "3/1/26 0:00",
    "Data Aktual (PPM)": "500",
    "Prediksi ARIMA (PPM)": "493",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.60%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 1:00",
    "Data Aktual (PPM)": "504",
    "Prediksi ARIMA (PPM)": "511",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.61%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 2:00",
    "Data Aktual (PPM)": "512",
    "Prediksi ARIMA (PPM)": "505",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.63%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 3:00",
    "Data Aktual (PPM)": "503",
    "Prediksi ARIMA (PPM)": "505",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.60%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 4:00",
    "Data Aktual (PPM)": "476",
    "Prediksi ARIMA (PPM)": "467",
    "Selisih (PPM)": "9",
    "Akurasi (PPM)": "98.11%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 5:00",
    "Data Aktual (PPM)": "535",
    "Prediksi ARIMA (PPM)": "529",
    "Selisih (PPM)": "6",
    "Akurasi (PPM)": "98.88%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 6:00",
    "Data Aktual (PPM)": "487",
    "Prediksi ARIMA (PPM)": "496",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.15%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 7:00",
    "Data Aktual (PPM)": "528",
    "Prediksi ARIMA (PPM)": "535",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.67%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 8:00",
    "Data Aktual (PPM)": "594",
    "Prediksi ARIMA (PPM)": "604",
    "Selisih (PPM)": "-10",
    "Akurasi (PPM)": "98.32%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 9:00",
    "Data Aktual (PPM)": "589",
    "Prediksi ARIMA (PPM)": "586",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.49%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 10:00",
    "Data Aktual (PPM)": "543",
    "Prediksi ARIMA (PPM)": "546",
    "Selisih (PPM)": "-3",
    "Akurasi (PPM)": "99.45%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 11:00",
    "Data Aktual (PPM)": "584",
    "Prediksi ARIMA (PPM)": "591",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.80%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 12:00",
    "Data Aktual (PPM)": "550",
    "Prediksi ARIMA (PPM)": "555",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.09%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 13:00",
    "Data Aktual (PPM)": "575",
    "Prediksi ARIMA (PPM)": "568",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.78%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 14:00",
    "Data Aktual (PPM)": "567",
    "Prediksi ARIMA (PPM)": "576",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.41%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 15:00",
    "Data Aktual (PPM)": "590",
    "Prediksi ARIMA (PPM)": "585",
    "Selisih (PPM)": "5",
    "Akurasi (PPM)": "99.15%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 16:00",
    "Data Aktual (PPM)": "595",
    "Prediksi ARIMA (PPM)": "603",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.66%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 17:00",
    "Data Aktual (PPM)": "602",
    "Prediksi ARIMA (PPM)": "604",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.67%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 18:00",
    "Data Aktual (PPM)": "544",
    "Prediksi ARIMA (PPM)": "536",
    "Selisih (PPM)": "8",
    "Akurasi (PPM)": "98.53%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 19:00",
    "Data Aktual (PPM)": "536",
    "Prediksi ARIMA (PPM)": "526",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "98.13%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 20:00",
    "Data Aktual (PPM)": "552",
    "Prediksi ARIMA (PPM)": "541",
    "Selisih (PPM)": "11",
    "Akurasi (PPM)": "98.01%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 21:00",
    "Data Aktual (PPM)": "560",
    "Prediksi ARIMA (PPM)": "564",
    "Selisih (PPM)": "-4",
    "Akurasi (PPM)": "99.29%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 22:00",
    "Data Aktual (PPM)": "543",
    "Prediksi ARIMA (PPM)": "550",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.71%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/1/26 23:00",
    "Data Aktual (PPM)": "515",
    "Prediksi ARIMA (PPM)": "511",
    "Selisih (PPM)": "4",
    "Akurasi (PPM)": "99.22%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 0:00",
    "Data Aktual (PPM)": "490",
    "Prediksi ARIMA (PPM)": "494",
    "Selisih (PPM)": "-4",
    "Akurasi (PPM)": "99.18%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 1:00",
    "Data Aktual (PPM)": "507",
    "Prediksi ARIMA (PPM)": "514",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.62%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 2:00",
    "Data Aktual (PPM)": "517",
    "Prediksi ARIMA (PPM)": "522",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.03%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 3:00",
    "Data Aktual (PPM)": "510",
    "Prediksi ARIMA (PPM)": "515",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.02%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 4:00",
    "Data Aktual (PPM)": "488",
    "Prediksi ARIMA (PPM)": "478",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "97.95%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 5:00",
    "Data Aktual (PPM)": "511",
    "Prediksi ARIMA (PPM)": "501",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "98.04%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 6:00",
    "Data Aktual (PPM)": "520",
    "Prediksi ARIMA (PPM)": "528",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.46%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 7:00",
    "Data Aktual (PPM)": "487",
    "Prediksi ARIMA (PPM)": "485",
    "Selisih (PPM)": "2",
    "Akurasi (PPM)": "99.59%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 8:00",
    "Data Aktual (PPM)": "594",
    "Prediksi ARIMA (PPM)": "604",
    "Selisih (PPM)": "-10",
    "Akurasi (PPM)": "98.32%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 9:00",
    "Data Aktual (PPM)": "601",
    "Prediksi ARIMA (PPM)": "604",
    "Selisih (PPM)": "-3",
    "Akurasi (PPM)": "99.50%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 10:00",
    "Data Aktual (PPM)": "605",
    "Prediksi ARIMA (PPM)": "614",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.51%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 11:00",
    "Data Aktual (PPM)": "592",
    "Prediksi ARIMA (PPM)": "599",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.82%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 12:00",
    "Data Aktual (PPM)": "605",
    "Prediksi ARIMA (PPM)": "598",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.84%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 13:00",
    "Data Aktual (PPM)": "576",
    "Prediksi ARIMA (PPM)": "583",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.78%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 14:00",
    "Data Aktual (PPM)": "610",
    "Prediksi ARIMA (PPM)": "607",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.51%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 15:00",
    "Data Aktual (PPM)": "563",
    "Prediksi ARIMA (PPM)": "554",
    "Selisih (PPM)": "9",
    "Akurasi (PPM)": "98.40%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 16:00",
    "Data Aktual (PPM)": "572",
    "Prediksi ARIMA (PPM)": "570",
    "Selisih (PPM)": "2",
    "Akurasi (PPM)": "99.65%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 17:00",
    "Data Aktual (PPM)": "582",
    "Prediksi ARIMA (PPM)": "571",
    "Selisih (PPM)": "11",
    "Akurasi (PPM)": "98.11%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 18:00",
    "Data Aktual (PPM)": "545",
    "Prediksi ARIMA (PPM)": "549",
    "Selisih (PPM)": "-4",
    "Akurasi (PPM)": "99.27%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 19:00",
    "Data Aktual (PPM)": "523",
    "Prediksi ARIMA (PPM)": "533",
    "Selisih (PPM)": "-10",
    "Akurasi (PPM)": "98.09%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 20:00",
    "Data Aktual (PPM)": "537",
    "Prediksi ARIMA (PPM)": "526",
    "Selisih (PPM)": "11",
    "Akurasi (PPM)": "97.95%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 21:00",
    "Data Aktual (PPM)": "543",
    "Prediksi ARIMA (PPM)": "545",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.63%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 22:00",
    "Data Aktual (PPM)": "525",
    "Prediksi ARIMA (PPM)": "526",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.81%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/2/26 23:00",
    "Data Aktual (PPM)": "532",
    "Prediksi ARIMA (PPM)": "523",
    "Selisih (PPM)": "9",
    "Akurasi (PPM)": "98.31%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 0:00",
    "Data Aktual (PPM)": "518",
    "Prediksi ARIMA (PPM)": "517",
    "Selisih (PPM)": "1",
    "Akurasi (PPM)": "99.81%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 1:00",
    "Data Aktual (PPM)": "523",
    "Prediksi ARIMA (PPM)": "520",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.43%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 2:00",
    "Data Aktual (PPM)": "520",
    "Prediksi ARIMA (PPM)": "522",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.62%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 3:00",
    "Data Aktual (PPM)": "505",
    "Prediksi ARIMA (PPM)": "506",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.80%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 4:00",
    "Data Aktual (PPM)": "520",
    "Prediksi ARIMA (PPM)": "514",
    "Selisih (PPM)": "6",
    "Akurasi (PPM)": "98.85%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 5:00",
    "Data Aktual (PPM)": "515",
    "Prediksi ARIMA (PPM)": "508",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.64%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 6:00",
    "Data Aktual (PPM)": "526",
    "Prediksi ARIMA (PPM)": "518",
    "Selisih (PPM)": "8",
    "Akurasi (PPM)": "98.48%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 7:00",
    "Data Aktual (PPM)": "508",
    "Prediksi ARIMA (PPM)": "500",
    "Selisih (PPM)": "8",
    "Akurasi (PPM)": "98.43%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 8:00",
    "Data Aktual (PPM)": "611",
    "Prediksi ARIMA (PPM)": "614",
    "Selisih (PPM)": "-3",
    "Akurasi (PPM)": "99.51%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 9:00",
    "Data Aktual (PPM)": "612",
    "Prediksi ARIMA (PPM)": "613",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.84%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 10:00",
    "Data Aktual (PPM)": "583",
    "Prediksi ARIMA (PPM)": "592",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.46%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 11:00",
    "Data Aktual (PPM)": "610",
    "Prediksi ARIMA (PPM)": "613",
    "Selisih (PPM)": "-3",
    "Akurasi (PPM)": "99.51%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 12:00",
    "Data Aktual (PPM)": "586",
    "Prediksi ARIMA (PPM)": "595",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.46%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 13:00",
    "Data Aktual (PPM)": "603",
    "Prediksi ARIMA (PPM)": "609",
    "Selisih (PPM)": "-6",
    "Akurasi (PPM)": "99.00%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 14:00",
    "Data Aktual (PPM)": "597",
    "Prediksi ARIMA (PPM)": "585",
    "Selisih (PPM)": "12",
    "Akurasi (PPM)": "97.99%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 15:00",
    "Data Aktual (PPM)": "565",
    "Prediksi ARIMA (PPM)": "568",
    "Selisih (PPM)": "-3",
    "Akurasi (PPM)": "99.47%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 16:00",
    "Data Aktual (PPM)": "552",
    "Prediksi ARIMA (PPM)": "556",
    "Selisih (PPM)": "-4",
    "Akurasi (PPM)": "99.28%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 17:00",
    "Data Aktual (PPM)": "583",
    "Prediksi ARIMA (PPM)": "576",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.80%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 18:00",
    "Data Aktual (PPM)": "543",
    "Prediksi ARIMA (PPM)": "548",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.08%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 19:00",
    "Data Aktual (PPM)": "538",
    "Prediksi ARIMA (PPM)": "545",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.70%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 20:00",
    "Data Aktual (PPM)": "541",
    "Prediksi ARIMA (PPM)": "538",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.45%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 21:00",
    "Data Aktual (PPM)": "539",
    "Prediksi ARIMA (PPM)": "533",
    "Selisih (PPM)": "6",
    "Akurasi (PPM)": "98.89%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 22:00",
    "Data Aktual (PPM)": "567",
    "Prediksi ARIMA (PPM)": "569",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.65%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/3/26 23:00",
    "Data Aktual (PPM)": "521",
    "Prediksi ARIMA (PPM)": "523",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.62%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 0:00",
    "Data Aktual (PPM)": "516",
    "Prediksi ARIMA (PPM)": "515",
    "Selisih (PPM)": "1",
    "Akurasi (PPM)": "99.81%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 1:00",
    "Data Aktual (PPM)": "522",
    "Prediksi ARIMA (PPM)": "527",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.04%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 2:00",
    "Data Aktual (PPM)": "501",
    "Prediksi ARIMA (PPM)": "496",
    "Selisih (PPM)": "5",
    "Akurasi (PPM)": "99.00%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 3:00",
    "Data Aktual (PPM)": "528",
    "Prediksi ARIMA (PPM)": "533",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.05%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 4:00",
    "Data Aktual (PPM)": "534",
    "Prediksi ARIMA (PPM)": "535",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.81%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 5:00",
    "Data Aktual (PPM)": "509",
    "Prediksi ARIMA (PPM)": "500",
    "Selisih (PPM)": "9",
    "Akurasi (PPM)": "98.23%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 6:00",
    "Data Aktual (PPM)": "503",
    "Prediksi ARIMA (PPM)": "502",
    "Selisih (PPM)": "1",
    "Akurasi (PPM)": "99.80%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 7:00",
    "Data Aktual (PPM)": "503",
    "Prediksi ARIMA (PPM)": "500",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.40%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 8:00",
    "Data Aktual (PPM)": "615",
    "Prediksi ARIMA (PPM)": "611",
    "Selisih (PPM)": "4",
    "Akurasi (PPM)": "99.35%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 9:00",
    "Data Aktual (PPM)": "556",
    "Prediksi ARIMA (PPM)": "551",
    "Selisih (PPM)": "5",
    "Akurasi (PPM)": "99.10%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 10:00",
    "Data Aktual (PPM)": "577",
    "Prediksi ARIMA (PPM)": "572",
    "Selisih (PPM)": "5",
    "Akurasi (PPM)": "99.13%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 11:00",
    "Data Aktual (PPM)": "597",
    "Prediksi ARIMA (PPM)": "591",
    "Selisih (PPM)": "6",
    "Akurasi (PPM)": "98.99%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 12:00",
    "Data Aktual (PPM)": "580",
    "Prediksi ARIMA (PPM)": "570",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "98.28%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 13:00",
    "Data Aktual (PPM)": "582",
    "Prediksi ARIMA (PPM)": "571",
    "Selisih (PPM)": "11",
    "Akurasi (PPM)": "98.11%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 14:00",
    "Data Aktual (PPM)": "612",
    "Prediksi ARIMA (PPM)": "610",
    "Selisih (PPM)": "2",
    "Akurasi (PPM)": "99.67%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 15:00",
    "Data Aktual (PPM)": "592",
    "Prediksi ARIMA (PPM)": "587",
    "Selisih (PPM)": "5",
    "Akurasi (PPM)": "99.16%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 16:00",
    "Data Aktual (PPM)": "556",
    "Prediksi ARIMA (PPM)": "545",
    "Selisih (PPM)": "11",
    "Akurasi (PPM)": "98.02%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 17:00",
    "Data Aktual (PPM)": "577",
    "Prediksi ARIMA (PPM)": "575",
    "Selisih (PPM)": "2",
    "Akurasi (PPM)": "99.65%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 18:00",
    "Data Aktual (PPM)": "538",
    "Prediksi ARIMA (PPM)": "540",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.63%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 19:00",
    "Data Aktual (PPM)": "539",
    "Prediksi ARIMA (PPM)": "529",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "98.14%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 20:00",
    "Data Aktual (PPM)": "567",
    "Prediksi ARIMA (PPM)": "572",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.12%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 21:00",
    "Data Aktual (PPM)": "565",
    "Prediksi ARIMA (PPM)": "564",
    "Selisih (PPM)": "1",
    "Akurasi (PPM)": "99.82%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 22:00",
    "Data Aktual (PPM)": "518",
    "Prediksi ARIMA (PPM)": "523",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.03%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/4/26 23:00",
    "Data Aktual (PPM)": "487",
    "Prediksi ARIMA (PPM)": "480",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.56%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 0:00",
    "Data Aktual (PPM)": "520",
    "Prediksi ARIMA (PPM)": "510",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "98.08%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 1:00",
    "Data Aktual (PPM)": "520",
    "Prediksi ARIMA (PPM)": "518",
    "Selisih (PPM)": "2",
    "Akurasi (PPM)": "99.62%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 2:00",
    "Data Aktual (PPM)": "509",
    "Prediksi ARIMA (PPM)": "511",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.61%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 3:00",
    "Data Aktual (PPM)": "522",
    "Prediksi ARIMA (PPM)": "524",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.62%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 4:00",
    "Data Aktual (PPM)": "505",
    "Prediksi ARIMA (PPM)": "510",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.01%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 5:00",
    "Data Aktual (PPM)": "487",
    "Prediksi ARIMA (PPM)": "479",
    "Selisih (PPM)": "8",
    "Akurasi (PPM)": "98.36%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 6:00",
    "Data Aktual (PPM)": "499",
    "Prediksi ARIMA (PPM)": "490",
    "Selisih (PPM)": "9",
    "Akurasi (PPM)": "98.20%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 7:00",
    "Data Aktual (PPM)": "533",
    "Prediksi ARIMA (PPM)": "532",
    "Selisih (PPM)": "1",
    "Akurasi (PPM)": "99.81%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 8:00",
    "Data Aktual (PPM)": "542",
    "Prediksi ARIMA (PPM)": "544",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.63%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 9:00",
    "Data Aktual (PPM)": "581",
    "Prediksi ARIMA (PPM)": "570",
    "Selisih (PPM)": "11",
    "Akurasi (PPM)": "98.11%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 10:00",
    "Data Aktual (PPM)": "576",
    "Prediksi ARIMA (PPM)": "584",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.61%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 11:00",
    "Data Aktual (PPM)": "619",
    "Prediksi ARIMA (PPM)": "610",
    "Selisih (PPM)": "9",
    "Akurasi (PPM)": "98.55%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 12:00",
    "Data Aktual (PPM)": "552",
    "Prediksi ARIMA (PPM)": "553",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.82%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 13:00",
    "Data Aktual (PPM)": "616",
    "Prediksi ARIMA (PPM)": "617",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.84%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 14:00",
    "Data Aktual (PPM)": "571",
    "Prediksi ARIMA (PPM)": "572",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.82%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 15:00",
    "Data Aktual (PPM)": "637",
    "Prediksi ARIMA (PPM)": "634",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.53%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 16:00",
    "Data Aktual (PPM)": "612",
    "Prediksi ARIMA (PPM)": "607",
    "Selisih (PPM)": "5",
    "Akurasi (PPM)": "99.18%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 17:00",
    "Data Aktual (PPM)": "611",
    "Prediksi ARIMA (PPM)": "599",
    "Selisih (PPM)": "12",
    "Akurasi (PPM)": "98.04%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 18:00",
    "Data Aktual (PPM)": "548",
    "Prediksi ARIMA (PPM)": "552",
    "Selisih (PPM)": "-4",
    "Akurasi (PPM)": "99.27%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 19:00",
    "Data Aktual (PPM)": "545",
    "Prediksi ARIMA (PPM)": "553",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.53%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 20:00",
    "Data Aktual (PPM)": "545",
    "Prediksi ARIMA (PPM)": "537",
    "Selisih (PPM)": "8",
    "Akurasi (PPM)": "98.53%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 21:00",
    "Data Aktual (PPM)": "561",
    "Prediksi ARIMA (PPM)": "567",
    "Selisih (PPM)": "-6",
    "Akurasi (PPM)": "98.93%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 22:00",
    "Data Aktual (PPM)": "541",
    "Prediksi ARIMA (PPM)": "546",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.08%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/5/26 23:00",
    "Data Aktual (PPM)": "498",
    "Prediksi ARIMA (PPM)": "506",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.39%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 0:00",
    "Data Aktual (PPM)": "541",
    "Prediksi ARIMA (PPM)": "546",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.08%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 1:00",
    "Data Aktual (PPM)": "498",
    "Prediksi ARIMA (PPM)": "506",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.39%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 2:00",
    "Data Aktual (PPM)": "509",
    "Prediksi ARIMA (PPM)": "517",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.43%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 3:00",
    "Data Aktual (PPM)": "521",
    "Prediksi ARIMA (PPM)": "510",
    "Selisih (PPM)": "11",
    "Akurasi (PPM)": "97.89%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 4:00",
    "Data Aktual (PPM)": "524",
    "Prediksi ARIMA (PPM)": "533",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.28%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 5:00",
    "Data Aktual (PPM)": "522",
    "Prediksi ARIMA (PPM)": "523",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.81%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 6:00",
    "Data Aktual (PPM)": "501",
    "Prediksi ARIMA (PPM)": "497",
    "Selisih (PPM)": "4",
    "Akurasi (PPM)": "99.20%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 7:00",
    "Data Aktual (PPM)": "515",
    "Prediksi ARIMA (PPM)": "520",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.03%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 8:00",
    "Data Aktual (PPM)": "598",
    "Prediksi ARIMA (PPM)": "599",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.83%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 9:00",
    "Data Aktual (PPM)": "580",
    "Prediksi ARIMA (PPM)": "588",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.62%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 10:00",
    "Data Aktual (PPM)": "580",
    "Prediksi ARIMA (PPM)": "570",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "98.28%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 11:00",
    "Data Aktual (PPM)": "569",
    "Prediksi ARIMA (PPM)": "573",
    "Selisih (PPM)": "-4",
    "Akurasi (PPM)": "99.30%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 12:00",
    "Data Aktual (PPM)": "560",
    "Prediksi ARIMA (PPM)": "550",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "98.21%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 13:00",
    "Data Aktual (PPM)": "564",
    "Prediksi ARIMA (PPM)": "574",
    "Selisih (PPM)": "-10",
    "Akurasi (PPM)": "98.23%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 14:00",
    "Data Aktual (PPM)": "587",
    "Prediksi ARIMA (PPM)": "597",
    "Selisih (PPM)": "-10",
    "Akurasi (PPM)": "98.30%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 15:00",
    "Data Aktual (PPM)": "614",
    "Prediksi ARIMA (PPM)": "620",
    "Selisih (PPM)": "-6",
    "Akurasi (PPM)": "99.02%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 16:00",
    "Data Aktual (PPM)": "555",
    "Prediksi ARIMA (PPM)": "564",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.38%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 17:00",
    "Data Aktual (PPM)": "573",
    "Prediksi ARIMA (PPM)": "572",
    "Selisih (PPM)": "1",
    "Akurasi (PPM)": "99.83%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 18:00",
    "Data Aktual (PPM)": "523",
    "Prediksi ARIMA (PPM)": "515",
    "Selisih (PPM)": "8",
    "Akurasi (PPM)": "98.47%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 19:00",
    "Data Aktual (PPM)": "533",
    "Prediksi ARIMA (PPM)": "536",
    "Selisih (PPM)": "-3",
    "Akurasi (PPM)": "99.44%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 20:00",
    "Data Aktual (PPM)": "557",
    "Prediksi ARIMA (PPM)": "554",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.46%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 21:00",
    "Data Aktual (PPM)": "539",
    "Prediksi ARIMA (PPM)": "546",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.70%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 22:00",
    "Data Aktual (PPM)": "537",
    "Prediksi ARIMA (PPM)": "547",
    "Selisih (PPM)": "-10",
    "Akurasi (PPM)": "98.14%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/6/26 23:00",
    "Data Aktual (PPM)": "512",
    "Prediksi ARIMA (PPM)": "513",
    "Selisih (PPM)": "-1",
    "Akurasi (PPM)": "99.80%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 0:00",
    "Data Aktual (PPM)": "551",
    "Prediksi ARIMA (PPM)": "555",
    "Selisih (PPM)": "-4",
    "Akurasi (PPM)": "99.27%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 1:00",
    "Data Aktual (PPM)": "517",
    "Prediksi ARIMA (PPM)": "519",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.61%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 2:00",
    "Data Aktual (PPM)": "516",
    "Prediksi ARIMA (PPM)": "518",
    "Selisih (PPM)": "-2",
    "Akurasi (PPM)": "99.61%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 3:00",
    "Data Aktual (PPM)": "518",
    "Prediksi ARIMA (PPM)": "511",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.65%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 4:00",
    "Data Aktual (PPM)": "524",
    "Prediksi ARIMA (PPM)": "515",
    "Selisih (PPM)": "9",
    "Akurasi (PPM)": "98.28%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 5:00",
    "Data Aktual (PPM)": "511",
    "Prediksi ARIMA (PPM)": "520",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.24%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 6:00",
    "Data Aktual (PPM)": "501",
    "Prediksi ARIMA (PPM)": "507",
    "Selisih (PPM)": "-6",
    "Akurasi (PPM)": "98.80%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 7:00",
    "Data Aktual (PPM)": "524",
    "Prediksi ARIMA (PPM)": "516",
    "Selisih (PPM)": "8",
    "Akurasi (PPM)": "98.47%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 8:00",
    "Data Aktual (PPM)": "621",
    "Prediksi ARIMA (PPM)": "618",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.52%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 9:00",
    "Data Aktual (PPM)": "630",
    "Prediksi ARIMA (PPM)": "639",
    "Selisih (PPM)": "-9",
    "Akurasi (PPM)": "98.57%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 10:00",
    "Data Aktual (PPM)": "552",
    "Prediksi ARIMA (PPM)": "558",
    "Selisih (PPM)": "-6",
    "Akurasi (PPM)": "98.91%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 11:00",
    "Data Aktual (PPM)": "616",
    "Prediksi ARIMA (PPM)": "607",
    "Selisih (PPM)": "9",
    "Akurasi (PPM)": "98.54%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 12:00",
    "Data Aktual (PPM)": "594",
    "Prediksi ARIMA (PPM)": "602",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.65%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 13:00",
    "Data Aktual (PPM)": "607",
    "Prediksi ARIMA (PPM)": "606",
    "Selisih (PPM)": "1",
    "Akurasi (PPM)": "99.84%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 14:00",
    "Data Aktual (PPM)": "577",
    "Prediksi ARIMA (PPM)": "585",
    "Selisih (PPM)": "-8",
    "Akurasi (PPM)": "98.61%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 15:00",
    "Data Aktual (PPM)": "606",
    "Prediksi ARIMA (PPM)": "618",
    "Selisih (PPM)": "-12",
    "Akurasi (PPM)": "98.02%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 16:00",
    "Data Aktual (PPM)": "634",
    "Prediksi ARIMA (PPM)": "645",
    "Selisih (PPM)": "-11",
    "Akurasi (PPM)": "98.26%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 17:00",
    "Data Aktual (PPM)": "612",
    "Prediksi ARIMA (PPM)": "605",
    "Selisih (PPM)": "7",
    "Akurasi (PPM)": "98.86%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 18:00",
    "Data Aktual (PPM)": "529",
    "Prediksi ARIMA (PPM)": "532",
    "Selisih (PPM)": "-3",
    "Akurasi (PPM)": "99.43%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 19:00",
    "Data Aktual (PPM)": "553",
    "Prediksi ARIMA (PPM)": "549",
    "Selisih (PPM)": "4",
    "Akurasi (PPM)": "99.28%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 20:00",
    "Data Aktual (PPM)": "535",
    "Prediksi ARIMA (PPM)": "540",
    "Selisih (PPM)": "-5",
    "Akurasi (PPM)": "99.07%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 21:00",
    "Data Aktual (PPM)": "566",
    "Prediksi ARIMA (PPM)": "573",
    "Selisih (PPM)": "-7",
    "Akurasi (PPM)": "98.76%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 22:00",
    "Data Aktual (PPM)": "556",
    "Prediksi ARIMA (PPM)": "553",
    "Selisih (PPM)": "3",
    "Akurasi (PPM)": "99.46%",
    "Status Kualitas Udara": "Sedang"
  },
  {
    "Waktu": "3/7/26 23:00",
    "Data Aktual (PPM)": "505",
    "Prediksi ARIMA (PPM)": "495",
    "Selisih (PPM)": "10",
    "Akurasi (PPM)": "98.02%",
    "Status Kualitas Udara": "Sedang"
  }
]

print(f"Injecting {len(data_json)} records...")
success_count = 0

for item in data_json:
    if item["Waktu"] == "Rata-Rata":
        continue
        
    # Format the time
    # e.g., "3/1/26 0:00" -> "2026-03-01 00:00:00"
    # Note: %y is 2-digit year, %m is month, %d is day. Wait, is it m/d/y?
    # "3/1/26" = March 1, 2026. "3/7/26" = March 7, 2026.
    try:
        dt = datetime.datetime.strptime(item["Waktu"], "%m/%d/%y %H:%M")
        timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            dt = datetime.datetime.strptime(item["Waktu"], "%d/%m/%y %H:%M")
            timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            print(f"Could not parse timestamp: {item['Waktu']}")
            continue
    
    co2 = float(item["Data Aktual (PPM)"])
    
    data = {
        "co2_ppm": round(co2, 2),
        "co_ppm": 2.0, # Default since it's not provided
        "mq7_detected": False,
        "location": LOCATION,
        "status": item["Status Kualitas Udara"],
        "timestamp": timestamp_str
    }
    
    try:
        response = requests.post(API_URL, json=data)
        if response.status_code in [200, 201, 210]:
            success_count += 1
            print(f"Success: {timestamp_str} CO2={co2}")
        else:
            print(f"Error for {timestamp_str}: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Connection error: {e}")
        break

print(f"Finished! Successfully injected {success_count} records.")
