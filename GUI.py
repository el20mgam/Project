import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from datetime import datetime, timedelta
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math
import numpy as np


def calculate_infection_probability_and_ventilation_rates(
    datetimes,
    co2_data,
    number_of_people,
    co2_generation_rate,
    room_volume,
    outdoor_co2_concentration_ppm,
    pulmonary_ventilation_rate,
    time,
    number_of_infectors,
    infection_quanta=3.33,
    co2_conversion_factor=1.98,
):
    # Calculate constants
    emission_rate = number_of_people * co2_generation_rate
    outdoor_co2_concentration = outdoor_co2_concentration_ppm * co2_conversion_factor

    # Function to calculate ventilation rate (Q)
    def calculate_ventilation_rate(df, room_volume, emission_rate, outdoor_co2_concentration):
        delta_time = (df.index[-1] - df.index[0]).seconds / 3600
        delta_co2 = df.iloc[-1] - df.iloc[0]
        dC_dt = delta_co2 / delta_time
        Q = (room_volume * dC_dt + emission_rate) / (outdoor_co2_concentration - df.mean())
        return Q

    # Create a DataFrame from the input data
    co2_levels_df = pd.DataFrame({'timestamp': datetimes, 'co2': co2_data})
    co2_levels_df.set_index('timestamp', inplace=True)

    # Convert CO2 levels to concentrations (mg·m−3)
    co2_levels_df['co2'] = co2_levels_df['co2'] * co2_conversion_factor

    # Calculate ventilation rate (Q) for a rolling hour
    # rolling_hour_df = co2_levels_df.rolling('1H', min_periods=2)
    # ventilation_rates = rolling_hour_df.apply(calculate_ventilation_rate, args=(room_volume, emission_rate, outdoor_co2_concentration))

    # Calculate ventilation rate (Q) for a rolling 20 minutes
    rolling_20_minutes_df = co2_levels_df.rolling('20T', min_periods=2)
    ventilation_rates = rolling_20_minutes_df.apply(calculate_ventilation_rate, args=(room_volume, emission_rate, outdoor_co2_concentration))

    # Calculate the probability of infection for the latest ventilation rate (Q)
    latest_ventilation_rate = ventilation_rates.iloc[-1]
    probability_of_infection = 1 - math.exp(-number_of_infectors * infection_quanta * pulmonary_ventilation_rate * time / latest_ventilation_rate)

    return probability_of_infection


def fetch_data(start_datetime, end_datetime):
    # Get the data from the API
    response = requests.get("http://192.168.0.107:5000/data")
    data = response.json()

    # Process the measurements data
    measurements_data = data["measurements"]
    measurements_data = [d for d in measurements_data if start_datetime <= datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S") <= end_datetime]

    datetimes = [datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S") for d in measurements_data]
    co2 = [d['co2'] for d in measurements_data]
    temperature = [d['temperature'] for d in measurements_data]
    humidity = [d['humidity'] for d in measurements_data]

    # Process the lft data
    lft_data = data["lft"]
    lft_outcomes = [d["outcome"] for d in lft_data if start_datetime <= datetime.strptime(d['datetime'], "%Y-%m-%d %H:%M:%S") <= end_datetime]

    return datetimes, co2, temperature, humidity, lft_outcomes



def update_data_with_range():
    start_datetime = datetime.now() - timedelta(hours=start_datetime_scale.get())
    end_datetime = datetime.now() - timedelta(hours=end_datetime_scale.get())

    datetimes, co2, temperature, humidity, lft_outcomes = fetch_data(start_datetime, end_datetime)

    # Calculate the number of infectors in the past rolling hour
    number_of_infectors = np.sum(np.array(lft_outcomes) == "Positive")

    # Get the number_of_people and room_volume from the Scale widgets
    number_of_people = number_of_people_scale.get()
    room_volume = room_volume_scale.get()

    # Calculate infection probability and ventilation rates
    probability_of_infection = calculate_infection_probability_and_ventilation_rates(
        datetimes=datetimes,
        co2_data=co2,
        number_of_people=number_of_people,
        co2_generation_rate=28.6,
        room_volume=room_volume,
        outdoor_co2_concentration_ppm=450,
        pulmonary_ventilation_rate=6,
        time=0.33,
        number_of_infectors=number_of_infectors,
        infection_quanta=3.33,
    )

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
    current_probability_of_infection.config(text=f"Probability of Infection: {round(probability_of_infection * 100, 2)} %")

    # Redraw the canvas
    canvas.draw()

    # Schedule the next update
    root.after(2000, update_data_with_range)


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

start_datetime_label = tk.Label(side_panel, text="Start time (hours ago):", font=("Arial", 14))
start_datetime_label.pack(pady=10)
start_datetime_scale = tk.Scale(side_panel, from_=0, to=48, orient=tk.HORIZONTAL)
start_datetime_scale.set(12)  # Set default value to 12 hours ago
start_datetime_scale.pack(pady=10)

end_datetime_label = tk.Label(side_panel, text="End time (hours ago):", font=("Arial", 14))
end_datetime_label.pack(pady=10)
end_datetime_scale = tk.Scale(side_panel, from_=0, to=48, orient=tk.HORIZONTAL)
end_datetime_scale.set(0)  # Set default value to now (0 hours ago)
end_datetime_scale.pack(pady=10)

# Add two Scale widgets to the side panel for number_of_people and room_volume
number_of_people_label = tk.Label(side_panel, text="Number of people:", font=("Arial", 14))
number_of_people_label.pack(pady=10)
number_of_people_scale = tk.Scale(side_panel, from_=1, to=50, orient=tk.HORIZONTAL)
number_of_people_scale.set(1)  # Set default value to 1
number_of_people_scale.pack(pady=10)

room_volume_label = tk.Label(side_panel, text="Room volume (m³):", font=("Arial", 14))
room_volume_label.pack(pady=10)
room_volume_scale = tk.Scale(side_panel, from_=1, to=500, orient=tk.HORIZONTAL)
room_volume_scale.set(36)  # Set default value to 36
room_volume_scale.pack(pady=10)

# Display current values
current_co2 = tk.Label(side_panel, font=("Arial", 14))
current_co2.pack(pady=10)
current_temp = tk.Label(side_panel, font=("Arial", 14))
current_temp.pack(pady=10)
current_humidity = tk.Label(side_panel, font=("Arial", 14))
current_humidity.pack(pady=10)
current_probability_of_infection = tk.Label(side_panel, font=("Arial", 14))
current_probability_of_infection.pack(pady=10)

# Add a quit button to the window
quit_button = tk.Button(master=root, text="Quit", command=root.quit)
quit_button.pack(side=tk.BOTTOM)

# Fetch initial data and start the update loop
update_data_with_range()

# Run the tkinter main loop
tk.mainloop()
