import tkinter as tk
import serial
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pushbullet import Pushbullet

# Arduino settings
ser = serial.Serial('COM3', 9600)  # Change to the correct port

# Pushbullet settings
API_KEY = "TOKEN"
pb = Pushbullet(API_KEY)

# Initialization of data lists
temperatures = []
humidities = []
noise_levels = []
mq2_levels = []

# Graph configuration
max_data_points = 100  # Maximum number of data points to display in the graph

# Global alert variables
last_alert_time_temp = 0
last_alert_time_noise = 0
last_alert_time_mq2 = 0
last_alert_time_humidity = 0
last_temp_alert = ""
last_noise_alert = ""
last_mq2_alert = ""
last_humidity_alert = ""

# Function to update the graph
def update_graph():
    if len(temperatures) > max_data_points:
        temperatures.pop(0)
        humidities.pop(0)
        noise_levels.pop(0)
        if mq2_levels:  # Checks if mq2_levels list is not empty
            mq2_levels.pop(0)

    axs[0].cla()
    axs[0].plot(temperatures, label='Temperature (°C)', color='blue')
    axs[0].set_title("Temperature")
    axs[0].set_ylabel("°C")
    
    axs[1].cla()
    axs[1].plot(humidities, label='Humidity (%)', color='green')
    axs[1].set_title("Humidity")
    axs[1].set_ylabel("%")
    
    axs[2].cla()
    axs[2].plot(noise_levels, label='Noise Level', color='red')
    axs[2].set_title("Noise Level")
    axs[2].set_ylabel("Value")

    axs[3].cla()
    # Checks if the mq2_levels list is not empty before trying to calculate the maximum value
    if mq2_levels:
        axs[3].plot(mq2_levels, label='Gas Level', color='orange')
        axs[3].set_ylim(0, max(max(mq2_levels), 1))  # Sets the Y-axis limit for MQ-2
    else:
        axs[3].plot([0] * len(noise_levels), label='Gas Level', color='orange')  # If empty, draws a line with value 0
        axs[3].set_ylim(0, 1)  # Minimum visible limit for the MQ-2 Y-axis

    axs[3].set_title("Gas Level ")
    axs[3].set_ylabel("Value")

    fig.tight_layout()  # Automatically adjusts the layout of the graphs
    canvas.draw()

# Function to read data from the Arduino
def read_arduino_data():
    global last_alert_time_temp, last_alert_time_noise, last_alert_time_mq2, last_alert_time_humidity, last_temp_alert, last_noise_alert, last_mq2_alert, last_humidity_alert
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print("Received from Arduino:", data)

        # Process temperature
        if "Temperature" in data:
            try:
                temperature = float(data.split(":")[1].replace("°C", "").strip())
                temperatures.append(temperature)

                if temperature >= 40.0:
                    if time.time() - last_alert_time_temp >= 300:
                        send_push_notification("High Temperature Alert", f"Temperature: {temperature} °C")
                        last_alert_time_temp = time.time()
                        last_temp_alert = f"Temperature: {temperature} °C - {time.ctime()}"
                        update_alert_labels()
            except ValueError:
                pass
        
        # Process humidity
        if "Humidity" in data:
            try:
                humidity = float(data.split(":")[1].replace("%", "").strip())
                humidities.append(humidity)

                # Check if humidity is out of range
                if humidity < 30 or humidity > 70:  # Adjusted humidity limit
                    if time.time() - last_alert_time_humidity >= 300:
                        send_push_notification("Humidity Out of Range Alert", f"Humidity: {humidity}%")
                        last_alert_time_humidity = time.time()
                        last_humidity_alert = f"Humidity: {humidity}% - {time.ctime()}"
                        update_alert_labels()

            except ValueError:
                pass
        
        # Process noise level
        if "Noise Level" in data:
            try:
                noise_level = int(data.split(":")[1].strip())
                noise_levels.append(noise_level)

                if noise_level >= 200:
                    if time.time() - last_alert_time_noise >= 300:
                        send_push_notification("High Noise Alert", f"Noise Level: {noise_level}")
                        last_alert_time_noise = time.time()
                        last_noise_alert = f"Noise Level: {noise_level} - {time.ctime()}"
                        update_alert_labels()
            except ValueError:
                pass

        # Process gas level (MQ-2)
        if "MQ-2 Value" in data:
            try:
                mq2_level = int(data.split(":")[1].strip())
                if mq2_level == 0:
                    mq2_level = 0.1  # Adjust to ensure the minimum visible value in the graph
                mq2_levels.append(mq2_level)

                if mq2_level >= 200:
                    if time.time() - last_alert_time_mq2 >= 300:
                        send_push_notification("Gas Level Alert", f"Gas Level: {mq2_level}")
                        last_alert_time_mq2 = time.time()
                        last_mq2_alert = f"Gas Level: {mq2_level} - {time.ctime()}"
                        update_alert_labels()
            except ValueError:
                pass

        update_graph()

    root.after(100, read_arduino_data)  # Updates data reading every 100ms

# Function to send a notification via Pushbullet
def send_push_notification(title, message):
    push = pb.push_note(title, message)
    print("Notification sent:", title, message)

# Function to update the alert labels in the interface
def update_alert_labels():
    temp_alert_label.config(text=f"[0°C-40°C] Last temperature alert: {last_temp_alert if last_temp_alert else 'None'}")
    noise_alert_label.config(text=f"[0 - 200] Last noise alert: {last_noise_alert if last_noise_alert else 'None'}")
    mq2_alert_label.config(text=f"[0 - 400] Last gas alert: {last_mq2_alert if last_mq2_alert else 'None'}")
    humidity_alert_label.config(text=f"[ <= 30% | >= 70% ] Last humidity alert: {last_humidity_alert if last_humidity_alert else 'None'}")

# Graphical interface setup with Tkinter
root = tk.Tk()
root.title("Arduino Server Watch Dog")
root.geometry("800x900")

# Alert Frame layout
alert_frame = tk.Frame(root)
alert_frame.pack(fill='x', pady=10)

# Alert labels
temp_alert_label = tk.Label(alert_frame, text="[0°C-40°C] Last temperature alert: None", width=50, anchor="center", relief="solid", height=2)
temp_alert_label.pack(fill='x', padx=10, pady=5)

noise_alert_label = tk.Label(alert_frame, text="[0 - 200] Last noise alert: None", width=50, anchor="center", relief="solid", height=2)
noise_alert_label.pack(fill='x', padx=10, pady=5)

mq2_alert_label = tk.Label(alert_frame, text="[0 - 400] Last gas alert: None", width=50, anchor="center", relief="solid", height=2)
mq2_alert_label.pack(fill='x', padx=10, pady=5)

humidity_alert_label = tk.Label(alert_frame, text="[30% - 70%] Last humidity alert: None", width=50, anchor="center", relief="solid", height=2)
humidity_alert_label.pack(fill='x', padx=10, pady=5)

# Graph configuration
fig, axs = plt.subplots(4, 1, figsize=(8, 12))

# Titles and labels
axs[0].set_title("Temperature")
axs[0].set_ylabel("°C")
axs[1].set_title("Humidity")
axs[1].set_ylabel("%")
axs[2].set_title("Noise Level")
axs[2].set_ylabel("Value")
axs[3].set_title("Gas Level (MQ-2)")
axs[3].set_ylabel("Value")

# Start real-time graphs
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill='both', expand=True)

# Start reading data from Arduino
root.after(100, read_arduino_data)

# Start the GUI loop
root.mainloop()
