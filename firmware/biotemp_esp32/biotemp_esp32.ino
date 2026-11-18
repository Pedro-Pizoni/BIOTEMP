#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include "config.h"

DHT dht(PINO_DHT11, DHT11);

void conectarWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("\nConectado! IP: ");
  Serial.println(WiFi.localIP());
}

void enviarMedicao() {
  float temperatura = dht.readTemperature();
  float umidade = dht.readHumidity();

  if (isnan(temperatura) || isnan(umidade)) {
    Serial.println("Erro ao ler o DHT22");
    return;
  }

  JsonDocument doc;
  doc["equipamento_id"] = EQUIPAMENTO_ID;
  doc["temperatura"] = temperatura;
  doc["umidade"] = umidade;

  String json;
  serializeJson(doc, json);
  Serial.println("Enviando: " + json);

  if (WiFi.status() != WL_CONNECTED) {
    conectarWiFi();
  }

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  int codigo = http.POST(json);
  String resposta = http.getString();
  http.end();

  Serial.printf("Resposta (%d): %s\n", codigo, resposta.c_str());

  if (codigo == 201) {
    JsonDocument retorno;
    deserializeJson(retorno, resposta);
    bool foraDoLimite = retorno["fora_do_limite"];
    digitalWrite(PINO_BUZZER, foraDoLimite ? HIGH : LOW);
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(PINO_BUZZER, OUTPUT);
  dht.begin();
  conectarWiFi();
}

void loop() {
  enviarMedicao();
  delay(INTERVALO_ENVIO);
}
