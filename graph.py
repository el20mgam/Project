import pandas as pd
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--start', type=str, help='start date in YYYY-MM-DD format')
parser.add_argument('--end', type=str, help='end date in YYYY-MM-DD format')
parser.add_argument('--csv_file', type=str, help='name of the CSV file')
parser.add_argument('--chart', type=str, help='name of the measurement')
args = parser.parse_args()

# read in the CSV file
df = pd.read_csv('measurements_bedroom.csv')

# convert the 'Date Time' column to a datetime object
df['Date Time'] = pd.to_datetime(df['Date Time'])

# filter the data based on the specified date range
if args.start and args.end:
   start_date = pd.to_datetime(args.start)
   end_date = pd.to_datetime(args.end)
   mask = (df['Date Time'] >= start_date) & (df['Date Time'] <= end_date)
   df = df.loc[mask]

# create a plot of Date Time against CO2
if args.chart == 'C':
    plt.plot(df['Date Time'], df['CO2 (ppm)'])
elif args.chart == 'T':
    plt.plot(df['Date Time'], df['Temperature (C)'])
elif args.chart == 'H':
    plt.plot(df['Date Time'], df['Relative Humidity (%)'])

# add labels and title to the plot
plt.xlabel('Date Time')
plt.ylabel('CO2 (ppm)')
plt.title('CO2 Levels Over Time')

# display the plot
plt.show()
