# Arduino-Server-Watch-Dog

## Project Overview
The **Arduino-Server-Watch-Dog** is a monitoring system designed to track environmental conditions such as temperature, humidity, noise levels, and gas concentrations. It provides real-time data visualization and sends alerts when specified thresholds are exceeded.

This project is being developed as part of the **Applied Physics in Computing** course in the **Computer Engineering** program at **IPBeja - Escola Superior de Tecnologia e Gestão (ESTIG)**.

## Hardware Requirements
To set up and execute this project, the following hardware components are required:

- **Arduino Nano 33 BLE Sense Rev2**
- **MQ-2 Gas Sensor**
- **Passive Buzzer**
- **USB Cable**
- **Breadboard and Jumper Wires**

## Software Requirements
Ensure you have the following software installed:

- **Arduino IDE** (with necessary libraries such as `Arduino_HS300x`, `PDM`, and `Pushbullet` integration)
- **Java Runtime Environment** (for the real-time data visualization application)
- **Pushbullet** app on your PC and mobile device

## Installation and Setup
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/yourusername/Arduino-Server-Watch-Dog.git
   ```

2. Open the project in the **Arduino IDE**.

3. Upload the sketch to your **Arduino Nano 33 BLE Sense Rev2** using the USB cable.

4. Install the **Pushbullet** app on your PC and mobile device, and link them using the API token.

5. Run the **Java** application provided in the repository to visualize the sensor data in real-time.

## How to Run
1. Connect all the hardware components as per the circuit diagram provided in the repository.

2. Power up the Arduino via USB.

3. Launch the **Java** application to start visualizing data.

4. You will receive notifications on your PC and mobile through Pushbullet when the thresholds for temperature, humidity, noise, or gas levels are exceeded.

## Project Contributors
- [Diogo Costa] - Developer and Maintainer

## Acknowledgements
This project is part of the **Applied Physics in Computing** course at **IPBeja - University of Technology and Management**.

## License
This project is licensed under the [MIT License](LICENSE).
