#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <ArduinoJson.h>

/* ================= WIFI CONFIG ================= */
const char* ssid = "YOUR_WIFI_SSID";          // ⚠️ GANTI dengan SSID WiFi Anda
const char* password = "YOUR_WIFI_PASSWORD";  // ⚠️ GANTI dengan password WiFi Anda

/* ================= SERVER CONFIG ================= */
const char* serverUrl = "https://dimas.rulsit.com/api/log";
const char* location = "Perkotaan"; // Ganti ke "Pedesaan" jika perlu

/* ================= PIN CONFIG ================= */
#define MQ135_AOUT A0
#define MQ7_DOUT   D6
#define BUZZER_PIN D7
#define WIFI_INDICATOR D0 // OPSIONAL: Indikator WiFi

/* ================= LCD CONFIG ================= */
LiquidCrystal_I2C lcd(0x27, 16, 2);

/* ================= MQ135 CONFIG ================= */
#define RL_MQ135 10.0
#define R0_MQ135 9.83        // ⚠️ GANTI sesuai hasil kalibrasi
#define ADC_MAX 1023.0
#define VCC 5.0

#define MQ135_A 116.6020682
#define MQ135_B -2.769034857

/* ================= THRESHOLD ================= */
#define MQ135_WARNING 1000
#define MQ135_DANGER  2000

/* ================= VARIABLE ================= */
float mq135_ppm = 0;
bool mq7_detected = false;
bool warningState = false;
bool wifiConnected = false;

unsigned long tSensor = 0;
unsigned long tLCD = 0;
unsigned long tBuzzer = 0;
unsigned long tUpload = 0;

/* ================= SETUP ================= */
void setup() {
  Serial.begin(115200);
  delay(500);

  pinMode(MQ7_DOUT, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Wire.begin(D2, D1);   // SDA, SCL (ESP8266 FIX)
  lcd.init();
  lcd.backlight();
  lcd.clear();

  lcd.setCursor(0,0);
  lcd.print("Air Quality");
  lcd.setCursor(0,1);
  lcd.print("Connecting WiFi");

  Serial.println("================================");
  Serial.println(" AIR QUALITY MONITOR ESP8266 ");
  Serial.println(" MQ135 | MQ7 | WiFi ");
  Serial.println("================================");

  // Connect to WiFi
  connectWiFi();

  delay(2000);
  lcd.clear();
}

/* ================= LOOP ================= */
void loop() {
  unsigned long now = millis();

  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    wifiConnected = false;
    if (now - tUpload >= 30000) {  // Try reconnect every 30s
      connectWiFi();
      tUpload = now;
    }
  } else {
    wifiConnected = true;
  }

  // Read sensors every 2 seconds
  if (now - tSensor >= 2000) {
    tSensor = now;
    readSensors();
    checkWarning();
  }

  // Update LCD every 1 second
  if (now - tLCD >= 1000) {
    tLCD = now;
    updateLCD();
  }

  // Upload data every 10 seconds if WiFi connected
  if (wifiConnected && (now - tUpload >= 10000)) {
    tUpload = now;
    uploadData();
  }

  handleBuzzer();
}

/* ================= WIFI CONNECTION ================= */
void connectWiFi() {
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    wifiConnected = false;
    Serial.println("\nWiFi Connection Failed!");
  }
}

/* ================= SENSOR READ ================= */
void readSensors() {
  int adc = 0;
  for (int i = 0; i < 20; i++) {
    adc += analogRead(MQ135_AOUT);
    delay(5);
  }
  adc /= 20;

  mq135_ppm = calculateMQ135PPM(adc);
  mq7_detected = !digitalRead(MQ7_DOUT);

  /* ===== SERIAL OUTPUT ===== */
  Serial.print("MQ135: ");
  Serial.print(mq135_ppm, 2);
  Serial.print(" ppm | MQ7: ");
  Serial.println(mq7_detected ? "DETECTED" : "CLEAN");
}

/* ================= MQ135 CALC ================= */
float calculateMQ135PPM(int adc) {
  if (adc == 0) return 0;

  float voltage = (adc / ADC_MAX) * VCC;
  float sensorR = ((VCC * RL_MQ135) / voltage) - RL_MQ135;
  if (sensorR <= 0) return 0;

  float ratio = sensorR / R0_MQ135;
  float ppm = MQ135_A * pow(ratio, MQ135_B);

  return constrain(ppm, 0, 5000);
}

/* ================= WARNING CHECK ================= */
void checkWarning() {
  warningState = (mq135_ppm >= MQ135_WARNING) || mq7_detected;
}

/* ================= LCD DISPLAY ================= */
void updateLCD() {
  lcd.clear();

  lcd.setCursor(0,0);
  lcd.print("MQ135:");
  lcd.print((int)mq135_ppm);
  lcd.print("ppm");

  lcd.setCursor(0,1);
  lcd.print("MQ7:");
  lcd.print(mq7_detected ? "DETECT " : "CLEAN  ");

  // Show WiFi status
  lcd.setCursor(12,1);
  if (wifiConnected) {
    lcd.print("WiFi");
  } else {
    lcd.print("----");
  }

  if (warningState) {
    lcd.setCursor(12,0);
    lcd.print("WARN");
  } else {
    lcd.setCursor(12,0);
    lcd.print("GOOD");
  }
}

/* ================= BUZZER ================= */
void handleBuzzer() {
  if (!warningState) {
    digitalWrite(BUZZER_PIN, LOW);
    return;
  }

  unsigned long now = millis();
  if (now - tBuzzer >= 400) {
    digitalWrite(BUZZER_PIN, !digitalRead(BUZZER_PIN));
    tBuzzer = now;
  }
}

/* ================= UPLOAD DATA ================= */
void uploadData() {
  if (!wifiConnected) return;

  WiFiClientSecure client;
  HTTPClient http;

  // Set insecure to skip SSL certificate validation (easier for ESP8266)
  client.setInsecure();

  Serial.print("Uploading data to production server... ");

  // Create JSON payload
  StaticJsonDocument<200> doc;
  doc["co2_ppm"] = mq135_ppm;
  doc["co_ppm"] = mq7_detected ? 15.0 : 2.5;  // Estimasi nilai CO
  doc["mq7_detected"] = mq7_detected;
  doc["location"] = location;
  // field 'timestamp' sengaja dikosongkan agar Server menggunakan Waktu Jakarta (WIB) terkini

  String jsonPayload;
  serializeJson(doc, jsonPayload);

  // Send HTTP POST request
  if (http.begin(client, serverUrl)) {
    http.addHeader("Content-Type", "application/json");

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      Serial.print("Success! Response code: ");
      Serial.println(httpResponseCode);
      
      String response = http.getString();
      Serial.println("Response: " + response);
    } else {
      Serial.print("Error! HTTP Code: ");
      Serial.println(httpResponseCode);
      Serial.println("Error message: " + http.errorToString(httpResponseCode));
    }
    http.end();
  } else {
    Serial.println("Connection failed!");
  }
}
