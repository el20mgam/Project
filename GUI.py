import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def fetch_data():
    # Get the data from the API
    response = requests.get("http://192.168.1.143:5000/measurements")
    data = response.json()

    # Process the data
    now = datetime.now()
    cutoff_time = now - timedelta(hours=12)

    data = [d for d in data if datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S") >= cutoff_time]

    datetimes = [datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S") for d in data]
    co2 = [d['co2'] for d in data]
    temperature = [d['temperature'] for d in data]
    humidity = [d['humidity'] for d in data]

    return datetimes, co2, temperature, humidity


def update_data():
    datetimes, co2, temperature, humidity = fetch_data()

    # Update plots
    for ax in axs:
        ax.clear()

    axs[0].plot(datetimes, co2, label='CO2', color='r')
    axs[1].plot(datetimes, temperature, label='Temperature', color='g')
    axs[2].plot(datetimes, humidity, label='Relative Humidity', color='b')

    # Update side panel values
    current_co2.config(text=f"Current CO2: {round(co2[-1], 1)} ppm")
    current_temp.config(text=f"Current Temperature: {round(temperature[-1], 1)} °C")
    current_humidity.config(text=f"Current Humidity: {round(humidity[-1], 1)} %")

    # Redraw the canvas
    canvas.draw()

    # Schedule the next update
    root.after(2000, update_data)


# Set up the plot
fig, axs = plt.subplots(3, 1, figsize=(10, 15), sharex=True)
plt.subplots_adjust(hspace=0.3)

# Configure the date formatter
date_fmt = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')

# Set axis labels and grid
for ax in axs:
    ax.grid()
    ax.xaxis.set_major_formatter(date_fmt)
    plt.setp(ax.get_xticklabels(), rotation=30, ha='right')

axs[0].set_title('CO2 vs DateTime')
axs[0].set_ylabel('CO2 (ppm)')
axs[1].set_title('Temperature vs DateTime')
axs[1].set_ylabel('Temperature (°C)')
axs[2].set_title('Relative Humidity vs DateTime')
axs[2].set_ylabel('Relative Humidity (%)')

# Create tkinter window
root = tk.Tk()
root.title("Sensor Data")

# Create the matplotlib canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

# Create side panel
side_panel = tk.Frame(root)
side_panel.pack(side=tk.RIGHT, fill=tk.BOTH)

# Display current values
current_co2 = tk.Label(side_panel, font=("Arial", 14))
current_co2.pack(pady=10)
current_temp = tk.Label(side_panel, font=("Arial", 14))
current_temp.pack(pady=10)
current_humidity = tk.Label(side_panel, font=("Arial", 14))
current_humidity.pack(pady=10)

# Add a quit button to the tkinter window
quit_button = tk.Button(master=root, text="Quit", command=root.quit)
quit_button.pack(side=tk.BOTTOM)

# Fetch initial data and start the update loop
update_data()

# Run the tkinter main loop
tk.mainloop()
