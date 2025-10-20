import matplotlib.pyplot as plt
import numpy as np
import json

def plot_gps_data(path, module_type, jammer_type, power, data_title, file_title):
    # Function to convert degrees to seconds
    def degrees_to_seconds(degrees):
        return degrees * 3600

    # PLOT - all on one chart illustration
    fig, ax = plt.subplots(1, 1, figsize=(5, 5))

    # Set the global font to Palatino Linotype
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Palatino Linotype']

    real_longitude = 14.508538
    real_latitude = 46.048782

    # Load JSON file
    with open(path, 'r') as f:
        data = json.load(f)

        for measurement in data[module_type][jammer_type][power]:
            Lat = []
            Lon = []
            for sample in measurement:
                Lat.append(degrees_to_seconds(float(sample['Lat']) - real_latitude))
                Lon.append(degrees_to_seconds(float(sample['Lon']) - real_longitude))

            ax.plot(Lat, Lon, label=f'PTN location', color='blue', alpha=0.75, linewidth=0.5)
            ax.scatter(0, 0, color='red', alpha=1, s=50, zorder=5)

    # Add label inside chart area in upper right
    ax.text(0.97, 0.97, data_title, horizontalalignment='right', verticalalignment='top', transform=ax.transAxes, fontsize=14, bbox=dict(facecolor='white', alpha=1))

    ax.set_xlabel('Δ Latitude [°]', fontsize=14)
    ax.set_ylabel('Δ Longitude [°]', fontsize=14)
    ax.grid(True, which='both', linestyle='-', linewidth=0.5)

    ax.grid(which='minor', linestyle=':', linewidth='0.5', alpha=0.7)

    # Set equal scaling and limit the axes so that 0 is in the center
    ax.set_aspect('equal')
    max_deviation = 0.15
    ax.set_xlim(-max_deviation, max_deviation)
    ax.set_ylim(-max_deviation, max_deviation)

    # Add double prime symbol (″) to the tick marks numbers and limit float tick marks to two digits
    def format_ticks(x, pos):
        return f'{x:.2f}″'

    ax.xaxis.set_major_formatter(plt.FuncFormatter(format_ticks))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_ticks))

    # Adjust the tick font size
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=12)

    plt.tight_layout()

    # Save the plot as an SVG file
    #plt.savefig(file_title, format='svg')

    plt.show()

# Draw graphs
plot_gps_data("jamming_dataset_august_2024.json", "Ublox10", "cw", "-60", "Ublox10 CW jammer", "coordinates_deviation/Ublox10_cw_-60_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "Ublox10", "cw3", "-70", "Ublox10 3×CW jammer", "coordinates_deviation/Ublox10_cw3_-70_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "Ublox10", "FM", "-50", "Ublox10 FM jammer", "coordinates_deviation/Ublox10_FM_-50_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "Ublox10", "none", "-155", "Ublox10 no jammer", "coordinates_deviation/Ublox10_none_-155_coordinates_deviation_plot.svg")

plot_gps_data("jamming_dataset_august_2024.json", "Ublox6", "cw", "-60", "Ublox6 CW jammer", "coordinates_deviation/Ublox6_cw_-60_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "Ublox6", "cw3", "-70", "Ublox6 3×CW jammer", "coordinates_deviation/Ublox6_cw3_-70_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "Ublox6", "FM", "-50", "Ublox6 FM jammer", "coordinates_deviation/Ublox6_FM_-50_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "Ublox6", "none", "-155", "Ublox6 no jammer", "coordinates_deviation/Ublox6_none_-155_coordinates_deviation_plot.svg")

plot_gps_data("jamming_dataset_august_2024.json", "GP01", "cw", "-60", "GP01 CW jammer", "coordinates_deviation/GP01_cw_-60_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "GP01", "cw", "-45", "GP01 CW jammer", "coordinates_deviation/GP01_cw_-45_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "GP01", "cw3", "-70", "GP01 3×CW jammer", "coordinates_deviation/GP01_cw3_-70_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "GP01", "cw3", "-45", "GP01 3×CW jammer", "coordinates_deviation/GP01_cw3_-45_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "GP01", "FM", "-50", "GP01 FM jammer", "coordinates_deviation/GP01_FM_-50_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "GP01", "FM", "-45", "GP01 FM jammer", "coordinates_deviation/GP01_FM_-45_coordinates_deviation_plot.svg")
plot_gps_data("jamming_dataset_august_2024.json", "GP01", "none", "-155", "GP01 no jammer", "coordinates_deviation/GP01_none_-155_coordinates_deviation_plot.svg")