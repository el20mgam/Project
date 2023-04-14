import sqlite3
import pandas as pd
import numpy as np
import datetime

# Constants and parameters
CO2_CONVERSION_FACTOR = 1.98  # Conversion factor for CO2 concentration (ppm to mg·m−3)
NUMBER_OF_PEOPLE = 10  # Example: 10 people in the room
CO2_GENERATION_RATE = 100  # Example: 100 L·h−1 per person
EMISSION_RATE = NUMBER_OF_PEOPLE * CO2_GENERATION_RATE
ROOM_VOLUME = 100  # Example: 100 m3
OUTDOOR_CO2_CONCENTRATION_PPM = 400  # Example: 400 ppm
OUTDOOR_CO2_CONCENTRATION = OUTDOOR_CO2_CONCENTRATION_PPM * CO2_CONVERSION_FACTOR
DB_FILE = 'your_database_file_path_here'  # Provide your SQLite database file path
TABLE_NAME = 'your_table_name_here'  # Provide the table name where the CO2 levels are stored
COLUMN_NAME = 'your_column_name_here'  # Provide the column name where the CO2 levels are stored


# Function to calculate ventilation rate (Q)
def calculate_ventilation_rate(df, room_volume, emission_rate, outdoor_co2_concentration):
    delta_time = (df.index[-1] - df.index[0]).seconds / 3600  # Time difference in hours
    delta_co2 = df.iloc[-1] - df.iloc[0]
    dC_dt = delta_co2 / delta_time
    Q = (room_volume * dC_dt + emission_rate) / (outdoor_co2_concentration - df.mean())
    return Q


# Function to read CO2 levels from SQLite database
def read_co2_levels(db_file, table_name, column_name):
    conn = sqlite3.connect(db_file)
    df = pd.read_sql(f'SELECT timestamp, {column_name} FROM {table_name}', conn, parse_dates=['timestamp'], index_col='timestamp')
    conn.close()
    return df


# Main script
def main():
    # Read CO2 levels from SQLite database
    co2_levels_df = read_co2_levels(DB_FILE, TABLE_NAME, COLUMN_NAME)

    # Convert CO2 levels to concentrations (mg·m−3)
    co2_levels_df[COLUMN_NAME] = co2_levels_df[COLUMN_NAME] * CO2_CONVERSION_FACTOR

    # Calculate ventilation rate (Q) for a rolling hour
    rolling_hour_df = co2_levels_df.rolling('1H', min_periods=2)
    ventilation_rates = rolling_hour_df.apply(calculate_ventilation_rate, args=(ROOM_VOLUME, EMISSION_RATE, OUTDOOR_CO2_CONCENTRATION))

    print("Ventilation rates for rolling hour:")
    print(ventilation_rates)


if __name__ == "__main__":
    main()
