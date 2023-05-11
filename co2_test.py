import requests
from datetime import datetime
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd


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


def calculate_Q(datetimes, co2_data, room_volume, number_of_people, co2_generation_rate, outdoor_co2_concentration_ppm, co2_conversion_factor=1.98):
    # Calculate constants
    emission_rate = number_of_people * co2_generation_rate
    outdoor_co2_concentration = outdoor_co2_concentration_ppm * co2_conversion_factor

    # Create a DataFrame from the input data
    co2_levels_df = pd.DataFrame({'timestamp': datetimes, 'co2': co2_data})
    co2_levels_df.set_index('timestamp', inplace=True)

    # Convert CO2 levels to concentrations (mg·m−3)
    co2_levels_df['co2'] = co2_levels_df['co2'] * co2_conversion_factor

    # Calculate ventilation rate (Q) for a rolling 20 minutes
    rolling_20_minutes_df = co2_levels_df.rolling('30T', min_periods=2)

    def calculate_ventilation_rate(df, room_volume, emission_rate, outdoor_co2_concentration):
        delta_time = (df.index[-1] - df.index[0]).seconds / 3600
        delta_co2 = df.iloc[-1] - df.iloc[0]
        dC_dt = delta_co2 / delta_time
        Q = (room_volume * dC_dt + emission_rate) / (outdoor_co2_concentration - df.mean())
        return Q

    def calculate_second_derivative(df, room_volume, emission_rate, outdoor_co2_concentration):
        # Calculate Q
        Q = calculate_ventilation_rate(df, room_volume, emission_rate, outdoor_co2_concentration)

        # Calculate the derivative of Q
        delta_time_Q = Q.index.to_series().diff().dt.seconds / 3600
        delta_Q = Q.diff()

        dQ_dt = delta_Q / delta_time_Q

        # Drop NaN values
        dQ_dt = dQ_dt.dropna()

        return dQ_dt

    ventilation_rates = rolling_20_minutes_df.apply(calculate_ventilation_rate,
                                                    args=(room_volume, emission_rate, outdoor_co2_concentration))

    return ventilation_rates.values.flatten()


def plot_Q_levels(datetimes, Q):
    minutes_elapsed = [(dt - start_datetime).total_seconds() / 60 for dt in datetimes]

    plt.plot(minutes_elapsed, abs(Q))
    plt.xlabel('Time (minutes)')
    plt.ylabel('Ventilation Rates (m³/h)')
    plt.ylim([0, 370])
    plt.xlim([0, 31])
    plt.title('Ventilation Rates (Q) during Light Exercise with Natural Ventilation')
    plt.grid()
    plt.show()


if __name__ == "__main__":
    start_datetime = datetime.strptime("2023-04-22 15:00:00", "%Y-%m-%d %H:%M:%S")
end_datetime = datetime.strptime("2023-04-22 15:40:00", "%Y-%m-%d %H:%M:%S")
datetimes, co2, temperature, humidity, lft_outcomes = fetch_data(start_datetime, end_datetime)

# Example parameters for calculate_Q function
room_volume = 20.97  # m^3
number_of_people = 25
co2_generation_rate = 28.6  # m^3/h
outdoor_co2_concentration_ppm = 350

Q = calculate_Q(datetimes, co2, room_volume, number_of_people, co2_generation_rate, outdoor_co2_concentration_ppm)
plot_Q_levels(datetimes, Q)
