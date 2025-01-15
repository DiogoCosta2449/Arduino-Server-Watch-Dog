#include <Arduino_HS300x.h>
#include <PDM.h>

short sampleBuffer[512];
volatile int samplesRead = 0;

// Parâmetros de controle
const int noiseLevelThreshold = 200;
const int stableTimeThreshold = 2;
const int temperatureThreshold = 40;
int currentNoiseLevel = 1;
int lastNoiseLevel = 1;
unsigned long lastAlertTime = 0;
unsigned long lastStableTime = 0;

// Média móvel
int noiseLevelHistory[5];
int historyIndex = 0;

const int buzzerPin = 3;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!HS300x.begin()) {
    Serial.println("Falha ao inicializar o sensor de temperatura e umidade!");
    while (1);
  }

  PDM.onReceive(onPDMdata);
  if (!PDM.begin(1, 16000)) {
    Serial.println("Falha ao inicializar o microfone PDM!");
    while (1);
  }

  pinMode(buzzerPin, OUTPUT);

  Serial.println("Arduino pronto!");
}

void loop() {
  float temperature = HS300x.readTemperature();
  float humidity = HS300x.readHumidity();

  Serial.print("Temperatura: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Humidade: ");
  Serial.print(humidity);
  Serial.println(" %");

  int noiseLevel = calculateNoiseLevel();
  noiseLevelHistory[historyIndex] = noiseLevel;
  historyIndex = (historyIndex + 1) % 5;

  int averageNoiseLevel = 0;
  for (int i = 0; i < 5; i++) {
    averageNoiseLevel += noiseLevelHistory[i];
  }
  averageNoiseLevel /= 5;

  if (averageNoiseLevel >= noiseLevelThreshold) {
    if (millis() - lastStableTime >= stableTimeThreshold * 1000) {
      currentNoiseLevel = map(averageNoiseLevel, 0, 1024, 1, 10);
      if (currentNoiseLevel != lastNoiseLevel) {
        lastAlertTime = millis();
        lastNoiseLevel = currentNoiseLevel;
        activateBuzzer();
      }
    }
  } else {
    currentNoiseLevel = 1;
    lastStableTime = millis();
  }

  if (temperature >= temperatureThreshold) {
    if (millis() - lastAlertTime >= 300000) {
      lastAlertTime = millis();
      activateBuzzer();
    }
  }

  Serial.print("Nível de Ruído (Média): ");
  Serial.println(averageNoiseLevel);

  delay(1000);
}

int calculateNoiseLevel() {
  int sum = 0;
  int maxSample = 0;
  int minSample = 1024;

  for (int i = 0; i < samplesRead; i++) {
    sum += abs(sampleBuffer[i]);
    if (sampleBuffer[i] > maxSample) {
      maxSample = sampleBuffer[i];
    }
    if (sampleBuffer[i] < minSample) {
      minSample = sampleBuffer[i];
    }
  }

  int noiseLevel = maxSample - minSample;

  return noiseLevel;
}

void onPDMdata() {
  int bytesAvailable = PDM.available();
  PDM.read(sampleBuffer, bytesAvailable);
  samplesRead = bytesAvailable / 2;
}

void activateBuzzer() {
  tone(buzzerPin, 1000);
  delay(0000);
  noTone(buzzerPin);
}
