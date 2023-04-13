import time
import sqlite3
import math
from scd30_i2c import SCD30

# Connect to the database
conn = sqlite3.connect('co2_measurements_IOM.db')
c = conn.cursor()

# Create the table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS measurements
             (datetime text, co2 real, temperature real, humidity real)''')

scd30 = SCD30()
scd30.set_measurement_interval(2)
scd30.start_periodic_measurement()
scd30.set_temperature_offset(2)

time.sleep(2)

while True:
    if scd30.get_data_ready():
        m = scd30.read_measurement()
        if m is not None:
            co2 = m[0] if not math.isnan(m[0]) else 0
            temp = m[1] if not math.isnan(m[1]) else 0
            rh = m[2] if not math.isnan(m[2]) else 0

            # Get the current date and time to the second
            date_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

            print(f"CO2: {co2:.2f}ppm, temp: {temp:.2f}'C, rh: {rh:.2f}%")

            # Insert the data into the database
            c.execute("INSERT INTO measurements VALUES (?, ?, ?, ?)", (date_time, co2, temp, rh))
            conn.commit()

        time.sleep(2)

    else:
        time.sleep(0.2)


# Close the database connection
c.close()
conn.close()
