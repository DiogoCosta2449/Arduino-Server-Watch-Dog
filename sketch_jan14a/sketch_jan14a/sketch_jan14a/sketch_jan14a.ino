#include <Arduino_HS300x.h>
#include <PDM.h>

short sampleBuffer[512];
volatile int samplesRead = 0;

// Control parameters
const int noiseLevelThreshold = 200;
const int stableTimeThreshold = 2;
const int temperatureThreshold = 40;
int currentNoiseLevel = 1;
int lastNoiseLevel = 1;
unsigned long lastAlertTime = 0;
unsigned long lastStableTime = 0;

// Moving average
int noiseLevelHistory[5];
int historyIndex = 0;

// MQ-2 sensor reading pin
const int mq2Pin = A0;

const int buzzerPin = 3;

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize the HS300x sensor
  if (!HS300x.begin()) {
    Serial.println("Failed to initialize the temperature and humidity sensor!");
    while (1);  // Enter loop if initialization fails
  }

  // Initialize the PDM microphone
  PDM.onReceive(onPDMdata);
  if (!PDM.begin(1, 16000)) {
    Serial.println("Failed to initialize the PDM microphone!");
    while (1);
  }

  pinMode(buzzerPin, OUTPUT);
  pinMode(mq2Pin, INPUT);  // Set MQ-2 pin as input

  Serial.println("Arduino ready!");
}

void loop() {
  // Read temperature and humidity from HS300x sensor
  float temperature = HS300x.readTemperature();  // Correction here: 'HS300x' as object
  float humidity = HS300x.readHumidity();        // Correction here as well

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  // Read analog value from MQ-2
  int mq2Value = analogRead(mq2Pin);  // Read value from MQ-2 sensor
  Serial.print("MQ-2 Value: ");
  Serial.println(mq2Value);

  // Calculate noise level
  int noiseLevel = calculateNoiseLevel();
  noiseLevelHistory[historyIndex] = noiseLevel;
  historyIndex = (historyIndex + 1) % 5;

  int averageNoiseLevel = 0;
  for (int i = 0; i < 5; i++) {
    averageNoiseLevel += noiseLevelHistory[i];
  }
  averageNoiseLevel /= 5;

  // Check if noise level exceeds the threshold
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

  // Check if temperature exceeds the threshold
  if (temperature >= temperatureThreshold) {
    if (millis() - lastAlertTime >= 300000) {
      lastAlertTime = millis();
      activateBuzzer();
    }
  }

  Serial.print("Noise Level (Average): ");
  Serial.println(averageNoiseLevel);

  delay(1000);
}

int calculateNoiseLevel() {
  int sum = 0;
  int maxSample = 0;
  int minSample = 1024;

  // Check if there are samples available to calculate noise level
  if (samplesRead > 0) {
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
  } else {
    // If no samples, return 0
    return 0;
  }
}

void onPDMdata() {
  int bytesAvailable = PDM.available();
  PDM.read(sampleBuffer, bytesAvailable);
  samplesRead = bytesAvailable / 2;
}

void activateBuzzer() {
  tone(buzzerPin, 1000);
  delay(500);  // Adjust the buzzer tone duration
  noTone(buzzerPin);
}
