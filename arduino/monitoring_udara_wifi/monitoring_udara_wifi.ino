// Library untuk koneksi WiFi ESP8266
#include <ESP8266WiFi.h>

// Library untuk melakukan HTTP request
#include <ESP8266HTTPClient.h>

// Library client dasar untuk koneksi jaringan
#include <WiFiClient.h>

// Library komunikasi I2C
#include <Wire.h>

// Library LCD I2C
#include <LiquidCrystal_I2C.h>

// Library untuk membuat dan membaca JSON
#include <ArduinoJson.h>

// Library fungsi matematika
#include <math.h>

/* ================= WIFI CONFIG ================= */

// Nama WiFi yang akan digunakan
const char* ssid = "YOUR_WIFI_SSID";          

// Password WiFi
const char* password = "YOUR_WIFI_PASSWORD";  

/* ================= SERVER CONFIG ================= */

// URL API tujuan upload data
const char* serverUrl = "https://dimas.rulsit.com/api/log";

// Lokasi monitoring
const char* location = "Perkotaan";

/* ================= PIN CONFIG ================= */

// Pin analog MQ135
#define MQ135_AOUT A0

// Pin digital MQ7
#define MQ7_DOUT   D6

// Pin buzzer
#define BUZZER_PIN D7

// Pin indikator WiFi (opsional)
#define WIFI_INDICATOR D0

/* ================= LCD CONFIG ================= */

// Membuat object LCD I2C alamat 0x27 ukuran 16x2
LiquidCrystal_I2C lcd(0x27, 16, 2);

/* ================= MQ135 CONFIG ================= */

// Nilai resistor beban MQ135
#define RL_MQ135 10.0

// Nilai R0 default (dipakai jika kalibrasi gagal)
#define MQ135_DEFAULT_R0 9.83

// Rasio Rs/R0 pada udara bersih KHUSUS kurva CO2 (400 ppm atmosfer = ratio 0.641)
// Rumus: 400 = 116.6 * ratio^(-2.769) -> ratio = 0.641
#define MQ135_CLEAN_AIR_RATIO 0.641

// Nilai maksimum ADC ESP8266
#define ADC_MAX 1023.0

// Tegangan kerja sensor
#define VCC 5.0

// Konstanta rumus MQ135
#define MQ135_A 116.6020682

// Konstanta rumus MQ135
#define MQ135_B -2.769034857

// ADC minimum valid (hindari spike 0 dan pembacaan tidak stabil)
// ADC < 50 menghasilkan resistansi sangat besar -> ratio sangat besar -> ppm ~0
#define MQ135_MIN_ADC_VALID 50

// Batas atas nilai ppm
#define MQ135_MAX_PPM 5000.0

// Jumlah sampel kalibrasi startup
#define MQ135_CALIBRATION_SAMPLES 80

// Faktor smoothing EMA
#define MQ135_EMA_ALPHA 0.25

// Jumlah sampel digital MQ7 untuk stabilisasi pembacaan
#define MQ7_SAMPLES 21

// Faktor smoothing estimasi CO dari MQ7
#define MQ7_EMA_ALPHA 0.20

/* ================= THRESHOLD ================= */

// Batas warning kualitas udara
#define MQ135_WARNING 1000

// Batas bahaya kualitas udara
#define MQ135_DANGER  2000

/* ================= VARIABLE ================= */

// Variabel penyimpanan nilai ppm MQ135 (default 400 ppm = CO2 atmosfer normal)
float mq135_ppm = 400.0;

// Nilai R0 aktual hasil kalibrasi runtime
float mq135_r0 = MQ135_DEFAULT_R0;

// Status deteksi MQ7
bool mq7_detected = false;

// Rasio pembacaan HIGH MQ7 untuk estimasi kestabilan sinyal
float mq7_high_ratio = 0.0;

// Estimasi CO berbasis tren deteksi MQ7
float mq7_estimated_co_ppm = 2.5;

// Status warning
bool warningState = false;

// Status koneksi WiFi
bool wifiConnected = false;

// Timer pembacaan sensor
unsigned long tSensor = 0;

// Timer update LCD
unsigned long tLCD = 0;

// Timer buzzer
unsigned long tBuzzer = 0;

// Timer upload data
unsigned long tUpload = 0;

/* ================= SETUP ================= */

// Fungsi setup dijalankan sekali saat board menyala
void setup() {

  // Memulai serial monitor
  Serial.begin(115200);

  // Delay awal
  delay(500);

  // Set pin MQ7 sebagai input
  pinMode(MQ7_DOUT, INPUT);

  // Set pin buzzer sebagai output
  pinMode(BUZZER_PIN, OUTPUT);

  // Memastikan buzzer mati saat awal
  digitalWrite(BUZZER_PIN, LOW);

  // Memulai komunikasi I2C
  // D2 = SDA
  // D1 = SCL
  Wire.begin(D2, D1);

  // Inisialisasi LCD
  lcd.init();

  // Menyalakan backlight LCD
  lcd.backlight();

  // Membersihkan LCD
  lcd.clear();

  // Menampilkan teks pada LCD baris pertama
  lcd.setCursor(0,0);
  lcd.print("Air Quality");

  // Menampilkan teks pada LCD baris kedua
  lcd.setCursor(0,1);
  lcd.print("Connecting WiFi");

  // Menampilkan informasi awal di serial monitor
  Serial.println("================================");

  // Menampilkan judul project
  Serial.println(" AIR QUALITY MONITOR ESP8266 ");

  // Menampilkan sensor yang digunakan
  Serial.println(" MQ135 | MQ7 | WiFi ");

  // Garis penutup
  Serial.println("================================");

  // Memanggil fungsi koneksi WiFi
  connectWiFi();

  // Kalibrasi ulang MQ135 agar nilai lebih akurat
  performMQ135Calibration();

  // Delay agar teks LCD terbaca
  delay(2000);

  // Membersihkan LCD
  lcd.clear();
}

/* ================= LOOP ================= */

// Fungsi loop berjalan terus menerus
void loop() {

  // Mengambil waktu saat ini
  unsigned long now = millis();

  // Mengecek koneksi WiFi
  if (WiFi.status() != WL_CONNECTED) {

    // Menandai WiFi tidak terkoneksi
    wifiConnected = false;

    // Reconnect setiap 30 detik
    if (now - tUpload >= 30000) {

      // Memanggil reconnect WiFi
      connectWiFi();

      // Update timer
      tUpload = now;
    }

  } else {

    // Menandai WiFi terkoneksi
    wifiConnected = true;
  }

  // Membaca sensor setiap 2 detik
  if (now - tSensor >= 2000) {

    // Update timer sensor
    tSensor = now;

    // Membaca sensor
    readSensors();

    // Mengecek warning
    checkWarning();
  }

  // Update LCD setiap 1 detik
  if (now - tLCD >= 1000) {

    // Update timer LCD
    tLCD = now;

    // Update tampilan LCD
    updateLCD();
  }

  // Upload data setiap 10 detik jika WiFi terkoneksi
  if (wifiConnected && (now - tUpload >= 10000)) {

    // Update timer upload
    tUpload = now;

    // Upload data ke server
    uploadData();
  }

  // Menjalankan kontrol buzzer
  handleBuzzer();
}

/* ================= WIFI CONNECTION ================= */

// Fungsi koneksi WiFi
void connectWiFi() {

  // Menampilkan teks koneksi
  Serial.print("Connecting to WiFi: ");

  // Menampilkan nama WiFi
  Serial.println(ssid);

  // Memulai koneksi WiFi
  WiFi.begin(ssid, password);

  // Variabel jumlah percobaan
  int attempts = 0;

  // Menunggu koneksi maksimal 20 percobaan
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {

    // Delay 500ms
    delay(500);

    // Menampilkan titik loading
    Serial.print(".");

    // Menambah jumlah percobaan
    attempts++;
  }

  // Jika berhasil terkoneksi
  if (WiFi.status() == WL_CONNECTED) {

    // Status WiFi true
    wifiConnected = true;

    // Menampilkan berhasil konek
    Serial.println("\nWiFi Connected!");

    // Menampilkan IP Address
    Serial.print("IP Address: ");

    // Menampilkan IP
    Serial.println(WiFi.localIP());

  } else {

    // Status WiFi false
    wifiConnected = false;

    // Menampilkan gagal konek
    Serial.println("\nWiFi Connection Failed!");
  }
}

/* ================= SENSOR READ ================= */

// Fungsi membaca sensor
void readSensors() {

  // Membaca ADC yang sudah distabilkan
  int adc = readStableMQ135ADC();

  // Menghitung ppm dari ADC
  float instantPPM = calculateMQ135PPM(adc);

  // Jika pembacaan valid dan masuk akal (>= 100 ppm), lakukan smoothing EMA
  if (instantPPM >= 100.0) {
    mq135_ppm = (MQ135_EMA_ALPHA * instantPPM) + ((1.0 - MQ135_EMA_ALPHA) * mq135_ppm);
  }
  // Jika invalid (-1), pertahankan mq135_ppm sebelumnya (tidak update)

  // Membaca status MQ7 secara stabil (majority sampling)
  int highCount = 0;
  for (int i = 0; i < MQ7_SAMPLES; i++) {
    if (digitalRead(MQ7_DOUT) == HIGH) highCount++;
    delay(2);
  }
  mq7_high_ratio = (float)highCount / (float)MQ7_SAMPLES;

  // MQ7 modul umumnya aktif-low: LOW berarti gas terdeteksi
  mq7_detected = (mq7_high_ratio < 0.5);

  // Estimasi CO dibuat bertahap agar tidak loncat tajam
  float coTarget;
  if (mq7_detected) {
    coTarget = 8.0 + ((1.0 - mq7_high_ratio) * 18.0);
  } else {
    coTarget = 0.8 + ((1.0 - mq7_high_ratio) * 3.0);
  }
  mq7_estimated_co_ppm = (MQ7_EMA_ALPHA * coTarget) + ((1.0 - MQ7_EMA_ALPHA) * mq7_estimated_co_ppm);

  /* ===== SERIAL OUTPUT ===== */

  // Menampilkan nilai MQ135
  Serial.print("MQ135: ");

  // Menampilkan ppm
  Serial.print(mq135_ppm, 2);

  // Menampilkan status MQ7
  Serial.print(" ppm | MQ7: ");

  // Menampilkan hasil deteksi
  Serial.print(mq7_detected ? "DETECTED" : "CLEAN");
  Serial.print(" | CO est: ");
  Serial.println(mq7_estimated_co_ppm, 2);
}

/* ================= MQ135 CALC ================= */

// Fungsi menghitung ppm MQ135
float calculateMQ135PPM(int adc) {

  // Jika ADC terlalu rendah, anggap data invalid
  if (adc < MQ135_MIN_ADC_VALID) return -1;

  // Menghitung resistansi sensor
  float sensorR = calculateMQ135Resistance(adc);

  // Jika resistansi invalid
  if (sensorR <= 0) return -1;

  // Menghitung rasio resistansi
  float ratio = sensorR / mq135_r0;

  // Jika rasio invalid atau <= 0
  if (ratio <= 0) return -1;

  // Jika rasio terlalu tinggi, sensor tidak terhubung atau belum stabil
  // ratio > 1.5 berarti CO2 < 40 ppm (mustahil di lingkungan berpenghuni)
  if (ratio > 1.5) return -1;

  // Menghitung ppm berdasarkan rumus CO2: ppm = 116.6 * (Rs/R0)^(-2.769)
  float ppm = MQ135_A * pow(ratio, MQ135_B);

  // Jika hasil bukan angka valid
  if (isnan(ppm) || isinf(ppm)) return -1;

  // Membatasi nilai ppm: minimum 100 ppm agar tidak pernah menampilkan 0
  return constrain(ppm, 100.0, MQ135_MAX_PPM);
}

// Fungsi menghitung resistansi MQ135 dari ADC
float calculateMQ135Resistance(int adc) {

  // Mengubah ADC menjadi tegangan
  float voltage = (adc / ADC_MAX) * VCC;

  // Cegah pembagian nol
  if (voltage <= 0.01) return -1;

  // Menghitung resistansi sensor
  float sensorR = ((VCC * RL_MQ135) / voltage) - RL_MQ135;

  return sensorR;
}

// Fungsi membaca ADC stabil dengan trimmed mean
int readStableMQ135ADC() {

  const int totalSamples = 25;
  const int trimCount = 5;
  int samples[totalSamples];

  // Ambil beberapa sampel ADC
  for (int i = 0; i < totalSamples; i++) {
    samples[i] = analogRead(MQ135_AOUT);
    delay(4);
  }

  // Urutkan sampel (ascending)
  for (int i = 0; i < totalSamples - 1; i++) {
    for (int j = i + 1; j < totalSamples; j++) {
      if (samples[j] < samples[i]) {
        int temp = samples[i];
        samples[i] = samples[j];
        samples[j] = temp;
      }
    }
  }

  // Hitung rata-rata setelah membuang nilai ekstrim
  long sum = 0;
  int validCount = 0;
  for (int i = trimCount; i < totalSamples - trimCount; i++) {
    sum += samples[i];
    validCount++;
  }

  if (validCount <= 0) return 0;

  return (int)(sum / validCount);
}

// Fungsi kalibrasi ulang R0 saat startup
void performMQ135Calibration() {

  // Tampilkan status kalibrasi
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("MQ135 Calibrate");
  lcd.setCursor(0, 1);
  lcd.print("Keep clean air");

  Serial.println("MQ135 calibration started...");
  Serial.println("Pastikan sensor di udara relatif bersih.");

  // Stabilkan sensor sebelum sampling
  delay(3000);

  float rsTotal = 0;
  int validSamples = 0;

  // Sampling untuk estimasi R0
  for (int i = 0; i < MQ135_CALIBRATION_SAMPLES; i++) {
    int adc = readStableMQ135ADC();
    float rs = calculateMQ135Resistance(adc);

    if (rs > 0) {
      rsTotal += rs;
      validSamples++;
    }

    delay(25);
  }

  // Jika sampel cukup, hitung R0 baru
  if (validSamples >= (MQ135_CALIBRATION_SAMPLES / 2)) {
    float rsAvg = rsTotal / validSamples;
    mq135_r0 = rsAvg / MQ135_CLEAN_AIR_RATIO;

    // Validasi R0 agar tetap masuk akal
    if (mq135_r0 < 1.0 || mq135_r0 > 50.0) {
      mq135_r0 = MQ135_DEFAULT_R0;
      Serial.println("Calibration out-of-range, fallback to default R0.");
    } else {
      Serial.print("Calibration success. New R0: ");
      Serial.println(mq135_r0, 3);
    }
  } else {
    // Fallback jika data kalibrasi jelek
    mq135_r0 = MQ135_DEFAULT_R0;
    Serial.println("Calibration failed, fallback to default R0.");
  }

  // Inisialisasi ppm awal agar tidak loncat dari 0
  int adcInitial = readStableMQ135ADC();
  float ppmInitial = calculateMQ135PPM(adcInitial);
  // Hanya gunakan hasil kalibrasi jika masuk akal (>= 200 ppm)
  mq135_ppm = (ppmInitial > 200.0) ? ppmInitial : 400.0;
}

/* ================= WARNING CHECK ================= */

// Fungsi pengecekan warning
void checkWarning() {

  // Warning aktif jika ppm melebihi batas atau MQ7 terdeteksi
  warningState = (mq135_ppm >= MQ135_WARNING) || mq7_detected;
}

/* ================= LCD DISPLAY ================= */

// Fungsi update tampilan LCD
void updateLCD() {

  // Membersihkan LCD
  lcd.clear();

  // Posisi cursor baris pertama
  lcd.setCursor(0,0);

  // Menampilkan teks MQ135
  lcd.print("MQ135:");

  // Menampilkan nilai ppm
  lcd.print((int)mq135_ppm);

  // Menampilkan satuan ppm
  lcd.print("ppm");

  // Posisi cursor baris kedua
  lcd.setCursor(0,1);

  // Menampilkan teks MQ7
  lcd.print("MQ7:");

  // Menampilkan status MQ7
  lcd.print(mq7_detected ? "DETECT " : "CLEAN  ");

  // Posisi status WiFi
  lcd.setCursor(12,1);

  // Jika WiFi terkoneksi
  if (wifiConnected) {

    // Tampilkan WiFi
    lcd.print("WiFi");

  } else {

    // Tampilkan ----
    lcd.print("----");
  }

  // Jika warning aktif
  if (warningState) {

    // Posisi warning
    lcd.setCursor(12,0);

    // Tampilkan WARN
    lcd.print("WARN");

  } else {

    // Posisi status normal
    lcd.setCursor(12,0);

    // Tampilkan GOOD
    lcd.print("GOOD");
  }
}

/* ================= BUZZER ================= */

// Fungsi kontrol buzzer
void handleBuzzer() {

  // Jika tidak warning
  if (!warningState) {

    // Matikan buzzer
    digitalWrite(BUZZER_PIN, LOW);

    // Keluar fungsi
    return;
  }

  // Mengambil waktu sekarang
  unsigned long now = millis();

  // Blink buzzer setiap 400ms
  if (now - tBuzzer >= 400) {

    // Membalik status buzzer
    digitalWrite(BUZZER_PIN, !digitalRead(BUZZER_PIN));

    // Update timer buzzer
    tBuzzer = now;
  }
}

/* ================= UPLOAD DATA ================= */

// Fungsi upload data ke server
void uploadData() {

  // Jika WiFi tidak terkoneksi
  if (!wifiConnected) return;

  // Membuat client HTTPS
  WiFiClientSecure client;

  // Membuat object HTTP
  HTTPClient http;

  // Menonaktifkan validasi SSL
  client.setInsecure();

  // Menampilkan proses upload
  Serial.print("Uploading data to production server... ");

  // Membuat object JSON
  StaticJsonDocument<200> doc;

  // Menambahkan nilai CO2
  doc["co2_ppm"] = mq135_ppm;

  // Menambahkan estimasi CO
  doc["co_ppm"] = mq7_estimated_co_ppm;

  // Menambahkan status MQ7
  doc["mq7_detected"] = mq7_detected;

  // Menambahkan lokasi
  doc["location"] = location;

  // Timestamp dikosongkan agar server memakai WIB otomatis

  // Variabel payload JSON
  String jsonPayload;

  // Convert JSON menjadi string
  serializeJson(doc, jsonPayload);

  // Memulai koneksi HTTP
  if (http.begin(client, serverUrl)) {

    // Menambahkan header JSON
    http.addHeader("Content-Type", "application/json");

    // Mengirim POST request
    int httpResponseCode = http.POST(jsonPayload);

    // Jika request berhasil
    if (httpResponseCode > 0) {

      // Menampilkan sukses
      Serial.print("Success! Response code: ");

      // Menampilkan kode response
      Serial.println(httpResponseCode);

      // Mengambil response server
      String response = http.getString();

      // Menampilkan response
      Serial.println("Response: " + response);

    } else {

      // Menampilkan error
      Serial.print("Error! HTTP Code: ");

      // Menampilkan kode error
      Serial.println(httpResponseCode);

      // Menampilkan pesan error
      Serial.println("Error message: " + http.errorToString(httpResponseCode));
    }

    // Menutup koneksi HTTP
    http.end();

  } else {

    // Jika koneksi gagal
    Serial.println("Connection failed!");
  }
}
