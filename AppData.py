import serial
import time
import matplotlib.pyplot as plt
from pushbullet import Pushbullet
import tkinter as tk
from tkinter import scrolledtext
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuração do Pushbullet
API_KEY = "TOKEN"
pb = Pushbullet(API_KEY)

# Configuração da porta serial (alterar conforme necessário)
ser = serial.Serial("COM3", 9600)  # Ajuste a porta serial conforme seu dispositivo

# Variáveis para armazenar os dados
temperatures = []
humidities = []
noise_levels = []
last_alert_time_temp = 0
last_alert_time_noise = 0

# Número máximo de pontos no gráfico
max_data_points = 100

# Variáveis para armazenar os últimos alertas
last_temp_alert = None
last_noise_alert = None

# Configuração do gráfico
fig, axs = plt.subplots(3, 1, figsize=(8, 10))  # Tamanho ajustado para gráficos maiores e mais separados

# Configuração dos gráficos
axs[0].set_title("Temperatura")
axs[0].set_ylabel("°C")
axs[1].set_title("Humidade")
axs[1].set_ylabel("%")
axs[2].set_title("Nível de Ruído")
axs[2].set_ylabel("Valor")

# Função para adicionar dados ao gráfico
def update_graph():
    # Limita o número de pontos no gráfico
    if len(temperatures) > max_data_points:
        temperatures.pop(0)
        humidities.pop(0)
        noise_levels.pop(0)

    # Atualiza os gráficos
    axs[0].cla()
    axs[0].plot(temperatures, label='Temperatura (°C)', color='blue')
    axs[0].set_title("Temperatura")
    axs[0].set_ylabel("°C")
    
    axs[1].cla()
    axs[1].plot(humidities, label='Humidade (%)', color='green')
    axs[1].set_title("Humidade")
    axs[1].set_ylabel("%")
    
    axs[2].cla()
    axs[2].plot(noise_levels, label='Nível de Ruído', color='red')
    axs[2].set_title("Nível de Ruído")
    axs[2].set_ylabel("Valor")

    fig.tight_layout()  # Ajusta automaticamente o layout dos gráficos
    canvas.draw()

# Função para enviar notificação via Pushbullet
def send_push_notification(title, message):
    push = pb.push_note(title, message)
    print("Notificação enviada:", title, message)

# Função para exibir os últimos alertas na interface
def update_alerts():
    if last_temp_alert:
        temp_alert_label.config(text=f"Último alerta de temperatura: {last_temp_alert}", bg="lightcoral")
    else:
        temp_alert_label.config(text="Nenhum alerta de temperatura recente.", bg="lightgreen")

    if last_noise_alert:
        noise_alert_label.config(text=f"Último alerta de ruído: {last_noise_alert}", bg="lightcoral")
    else:
        noise_alert_label.config(text="Nenhum alerta de ruído recente.", bg="lightgreen")

# Função para exibir os últimos alertas
def display_alerts():
    update_alerts()

# Função para ler dados do Arduino
def read_arduino_data():
    if ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print("Recebido do Arduino:", data)

        # Verifica o nível de temperatura
        if "Temperatura" in data:
            try:
                temperature = float(data.split(":")[1].replace("°C", "").strip())
                temperatures.append(temperature)

                if temperature >= 40.0:
                    # Envia alerta de temperatura se ainda não enviou recentemente
                    if time.time() - last_alert_time_temp >= 300:
                        send_push_notification("Alerta de Temperatura Alta", f"Temperatura: {temperature} °C")
                        last_alert_time_temp = time.time()
                        last_temp_alert = f"Temperatura: {temperature} °C - {time.ctime()}"

            except ValueError:
                pass
        
        # Verifica o nível de humidade
        if "Humidade" in data:
            try:
                humidity = float(data.split(":")[1].replace("%", "").strip())
                humidities.append(humidity)
            except ValueError:
                pass
        
        # Verifica o nível de ruído
        if "Nível de Ruído" in data:
            try:
                noise_level = int(data.split(":")[1].strip())
                noise_levels.append(noise_level)

                if noise_level >= 200:
                    # Envia alerta de ruído se ainda não enviou recentemente
                    if time.time() - last_alert_time_noise >= 300:
                        send_push_notification("Alerta de Ruído Alto", f"Nível de Ruído: {noise_level}")
                        last_alert_time_noise = time.time()
                        last_noise_alert = f"Nível de Ruído: {noise_level} - {time.ctime()}"

            except ValueError:
                pass
        
        # Atualiza os gráficos
        update_graph()

        # Exibe os últimos alertas
        display_alerts()

    root.after(1000, read_arduino_data)  # Chama a função novamente após 1 segundo

# Configuração da interface gráfica com Tkinter
root = tk.Tk()
root.title("Monitor de Temperatura, Humidade e Ruído")
root.geometry("700x600")  # Tamanho ajustado para janela mais ampla e gráfica maior

# Área para exibir os últimos alertas
alert_frame = tk.Frame(root)
alert_frame.pack(fill="x", padx=10, pady=10)

# Label para alertas de temperatura
temp_alert_label = tk.Label(alert_frame, text="Último alerta de temperatura: Nenhum", width=50, anchor="center", relief="solid", height=2)
temp_alert_label.pack(fill="x", padx=10, pady=5)

# Label para alertas de ruído
noise_alert_label = tk.Label(alert_frame, text="Último alerta de ruído: Nenhum", width=50, anchor="center", relief="solid", height=2)
noise_alert_label.pack(fill="x", padx=10, pady=5)

# Configuração dos gráficos
graph_frame = tk.Frame(root)
graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Inicia os gráficos em tempo real
canvas = FigureCanvasTkAgg(fig, master=graph_frame)  # Correção aqui
canvas.get_tk_widget().pack(fill="both", expand=True)

# Começa a leitura dos dados do Arduino
read_arduino_data()  # Inicia a leitura dos dados

# Executa a interface gráfica
root.mainloop()
