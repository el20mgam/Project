import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# connect to the SQLite database
conn = sqlite3.connect('co2_measurements_IOM.db')

# create a cursor object to execute SQL queries
cur = conn.cursor()

# select all data from the table
cur.execute("SELECT * FROM measurements")

# fetch all data as a list of tuples
data = cur.fetchall()

# convert the list of tuples to a pandas DataFrame
df = pd.DataFrame(data, columns=['Date Time', 'CO2 (ppm)', 'Temperature (C)', 'Relative Humidity (%)'])

# convert the 'Date Time' column to a datetime object
df['Date Time'] = pd.to_datetime(df['Date Time'])

root = tk.Tk()

figure1 = plt.Figure(figsize=(6, 5), dpi=100)
ax1 = figure1.add_subplot(111)
line1 = FigureCanvasTkAgg(figure1, root)
line1.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
df_co2 = df[['Date Time', 'CO2 (ppm)']].set_index('Date Time')
df_co2.plot(kind='line', legend=True, ax=ax1, color='b', fontsize=10)
ax1.set_title('Date Time Vs. CO2 (ppm)')

figure2 = plt.Figure(figsize=(5, 4), dpi=100)
ax2 = figure2.add_subplot(111)
line2 = FigureCanvasTkAgg(figure2, root)
line2.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
df_temp = df[['Date Time', 'Temperature (C)']].set_index('Date Time')
df_temp.plot(kind='line', legend=True, ax=ax2, color='r', fontsize=10)
ax2.set_title('Date Time Vs. Temperature (C)')

figure3 = plt.Figure(figsize=(5, 4), dpi=100)
ax3 = figure3.add_subplot(111)
line3 = FigureCanvasTkAgg(figure3, root)
line3.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH)
df_humidity = df[['Date Time', 'Relative Humidity (%)']].set_index('Date Time')
df_humidity.plot(kind='line', legend=True, ax=ax3, color='g', fontsize=10)
ax3.set_title('Date Time Vs. Relative Humidity (%)')

root.mainloop()