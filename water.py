import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import glob

import json

# Get list of all JSON files in the directory
json_files = glob.glob('water_level/*.json-*')

dfs = []
bad_files = 0

for file in json_files:
    try:
        # Try fast pandas read first
        df_temp = pd.read_json(file, lines=True)
        dfs.append(df_temp)
    except Exception as e:
        # Fallback: read line-by-line for problematic files
        print(f"Recovering from error in {file}: {type(e).__name__}")
        data = []
        try:
            with open(file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass  # Skip malformed JSON lines
            if data:
                dfs.append(pd.DataFrame(data))
                print(f"  Recovered {len(data)} records from {file}")
            else:
                bad_files += 1
        except Exception as e2:
            print(f"  Could not recover {file}: {e2}")
            bad_files += 1

if bad_files > 0:
    print(f"\nWarning: {bad_files} file(s) could not be read")

# Concatenate all dataframes
df = pd.concat(dfs, ignore_index=True)

# Remove duplicated rows
df = df.drop_duplicates()
# Remove missing values
df = df.dropna(subset=['time', 'level'])

# Parse datetime
df['datetime'] = pd.to_datetime(df['time'], format='mixed')
# Discard data before 2024-10-23 00:00:00
df = df[df['datetime'] >= '2024-10-23 00:00:00'] 
df.set_index('datetime', inplace=True)

print(f"\nLoaded {len(df)} total records spanning {df.index.min()} to {df.index.max()}")

# change dataset
df.drop(columns=['time'], inplace=True)
df.sort_index(inplace=True)

# Resample to hourly data
df_hourly = df.resample('h').mean()
df_hourly['depth'] = df_hourly['level'].apply(lambda x: -1.2 + x/100)
df_hourly.tail()
print(f"\nHourly data has {len(df_hourly)} records spanning {df_hourly.index.min()} to {df_hourly.index.max()}")

# Read in weather data from csv

cols = ['wind_direction', 'wind_speed', 'temperature', 'humidity', 'pressure',
        'rain', 'rd', 'ri', 'hail', 'hd', 'hi']

dfm = pd.read_csv('meteo/weather.csv', header=None, parse_dates=True, index_col=0)
dfm.columns = cols
dfm.index.name = 'date'
# Discard data before 2024-10-23 00:00:00
dfm = dfm.loc['2024-10-23 00:00:00':]
#dfm.tail()

# Subset the data to only include the rain column

dfrain = dfm[['rain']]

# Resample to hourly data
dfrainJS = dfrain.resample('h').sum()
dfrainJS.tail()
print(f"\nHourly rain data has {len(dfrainJS)} records spanning {dfrainJS.index.min()} to {dfrainJS.index.max()}")


# Remove very high level values
df_hourly2 = df_hourly[df_hourly['level'] < 150]

# Plot the water level and rain data together
fig, ax = plt.subplots(figsize=(15, 6)) 
ax.plot(df_hourly2.index, df_hourly2['depth'], label='Water Level')
ax.set_title('Groundwater Level and Rainfall at SMEAR Estonia')
ax.set_ylabel('Water Level (m)')
ax.set_xlabel('Time')
ax.grid()
ax2 = ax.twinx()
ax2.bar(dfrainJS.index, dfrainJS['rain'], width=0.5, color='blue', alpha=0.3, label='Rainfall')
ax2.invert_yaxis()
ax2.set_ylabel('Rainfall (mm)')
ax2.grid(False)
#plt.show()
plt.savefig('water_level_rainfall.png', dpi=600)
print("\nPlot saved as 'water_level_rainfall.png'")
