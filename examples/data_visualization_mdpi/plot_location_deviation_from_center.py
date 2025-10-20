import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd
import math
import json

#1 PLOT - all on one chart ilustration
fig, ax = plt.subplots(1,1,figsize=(10, 4))

# Set the global font to Palatino Linotype
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Palatino Linotype']

# DATA EXTRAPOLATION
extrapolateData = False

# Load JSON file
with open("jamming_dataset_august_2024.json", 'r') as f:
    data = json.load(f)

    for measurement in data['Ublox6']['none']['-155']:
        LatDev = []
        LonDev = []
        Dev = []
        Power =  []
        Time = []
        for sample in measurement:
            LatDev.append(float(sample['LatDev']) if sample['Lat'] != 0 else np.nan)
            LonDev.append(float(sample['LonDev']) if sample['Lon'] != 0 else np.nan)
            Power.append(float(sample['Power']) if sample['Power'] != -155 else np.nan)
            Dev.append(float(sample['Dev']) if sample['Lat'] != 0 and sample['Lon'] != 0 else np.nan)
            Time.append(sample['Time'])

        # Calculate the mean value of the first 100 seconds
        first_100_seconds = np.array(Time) <= 100
        mean_LatDev = np.nanmean(np.array(LatDev)[first_100_seconds])
        mean_LonDev = np.nanmean(np.array(LonDev)[first_100_seconds])
        mean_Dev = np.nanmean(np.array(Dev)[first_100_seconds])

        # Recalculate LatDev, LonDev, and Dev values to be +- from the mean value
        LatDev = [value - mean_LatDev if not np.isnan(value) else np.nan for value in LatDev]
        LonDev = [value - mean_LonDev if not np.isnan(value) else np.nan for value in LonDev]
        Dev = [value - mean_Dev if not np.isnan(value) else np.nan for value in Dev]

        ax.plot(Time, Dev, label=f'Dev', linestyle='-', alpha=0.75)

        # Iterate over the data to find and plot the missing parts with a dotted line
        if(extrapolateData):
            for i in range(1, len(Time)):
                if np.isnan(Dev[i-1]) and not np.isnan(Dev[i]):
                    # Find the last non-NaN value before the current NaN sequence
                    j = i - 1
                    while j >= 0 and np.isnan(Dev[j]):
                        j -= 1
                    if j >= 0:
                        plt.plot([Time[j], Time[i]], [Dev[j], Dev[i]], linestyle='dotted', color='gray', alpha=0.5, linewidth=0.8)
                elif not np.isnan(Dev[i-1]) and np.isnan(Dev[i]):
                    # Find the next non-NaN value after the current NaN sequence
                    k = i + 1
                    while k < len(Dev) and np.isnan(Dev[k]):
                        k += 1
                    if k < len(Dev):
                        plt.plot([Time[i-1], Time[k]], [Dev[i-1], Dev[k]], linestyle='dotted', color='gray', alpha=0.5, linewidth=0.8)


# Add label inside chart area in upper right
ax.text(0.98, 0.95, 'Ublox6 no jammer', horizontalalignment='right', verticalalignment='top', transform=ax.transAxes, fontsize=14, bbox=dict(facecolor='white', alpha=1))

ax.set_xlabel('Simulation time [s]', fontsize=14)
ax.set_ylabel('Loaction deviation Δ [cm]', fontsize=14)
ax.set_xlim(0, len(Time) - 1)
ax.set_ylim(-200,400)
ax.tick_params(axis='both', which='major', labelsize=12)
ax.grid(True, which='both', linestyle='-', linewidth=0.5)

# Add minor grid lines every 10 seconds on x-axis
ax.xaxis.set_minor_locator(plt.MultipleLocator(10))
ax.yaxis.set_minor_locator(plt.MultipleLocator(50))
ax.grid(which='minor', linestyle=':', linewidth='0.5', alpha=0.7)

ax.fill_between(Time, ax.get_ylim()[0], ax.get_ylim()[1], where=(np.array(Time) >= 100) & (np.array(Time) <= 200), color='red', alpha=0.15)

plt.tight_layout()

# Save the plot as an SVG file
#plt.savefig('Ublox6_none_-155_all.svg', format='svg')
plt.show()

