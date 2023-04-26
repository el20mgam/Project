import requests
from datetime import datetime
import matplotlib.pyplot as plt


def fetch_data(start_datetime, end_datetime):
    # Get the data from the API
    response = requests.get("http://0.0.0.0:5001/data")
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


def plot_co2_levels(datetimes, co2):
    minutes_elapsed = [(dt - start_datetime).total_seconds() / 60 for dt in datetimes]

    plt.plot(minutes_elapsed, co2)
    plt.xlabel('Time (minutes)')
    plt.ylabel('CO2 Levels (PPM)')
    plt.title('Light exercise with Natural Ventilation ')
    plt.grid()
    plt.show()


if __name__ == "__main__":
    start_datetime = datetime.strptime("2023-04-22 15:00:00", "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.strptime("2023-04-22 15:30:00", "%Y-%m-%d %H:%M:%S")
    datetimes, co2, temperature, humidity, lft_outcomes = fetch_data(start_datetime, end_datetime)
    plot_co2_levels(datetimes, co2)
