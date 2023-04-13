import pandas as pd
import matplotlib.pyplot as plt

# read in the CSV file
df = pd.read_csv('total.csv')

df['Date Time'] = pd.to_datetime(df['Date Time'])

# create a plot of Date Time against CO2
plt.plot(df['Date Time'], df['CO2 (ppm)'])

# add labels and title to the plot
plt.xlabel('Date Time')
plt.ylabel('CO2 (ppm)')
plt.title('CO2 Levels Over Time')

# display the plot
plt.show()
