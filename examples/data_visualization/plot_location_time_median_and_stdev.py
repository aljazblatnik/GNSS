import matplotlib.pyplot as plt
import numpy as np
import json

def plot_jamming_data(combos, yscale):
    # Load JSON file
    with open("jamming_dataset_august_2024.json", 'r') as f:
        data = json.load(f)

    fig, ax = plt.subplots(1, 1, figsize=(10, 4))
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Palatino Linotype']

    filename = ""

    for combo in combos:
        gnss_module, jammer_type, power = combo
        all_dev = []
        max_length = 0

        filename += str(gnss_module) + str(jammer_type) + str(power) + "_"

        for measurement in data[gnss_module][jammer_type][power]:
            Dev = []
            Time = []
            for sample in measurement:
                Dev.append(float(sample['Dev']) if sample['Lat'] != 0 and sample['Lon'] != 0 else np.nan)
                Time.append(sample['Time'])

            if not all(np.isnan(Dev)):
                # Calculate the mean value of the first 100 samples to determine the correction factor
                correction_factor = np.nanmean(Dev[:100])
                # Apply the correction factor to shift the data to start at 0 deviation
                Dev = [d - correction_factor for d in Dev]
                
                all_dev.append(Dev)
                max_length = max(max_length, len(Dev))

        if not all_dev:
            print(f"No valid data for {gnss_module} {jammer_type} Power {power}")
            continue

        # Pad sequences with np.nan to make them of equal length
        all_dev_padded = [np.pad(dev, (0, max_length - len(dev)), constant_values=np.nan) for dev in all_dev]
        all_dev_padded = np.array(all_dev_padded)

        if all_dev_padded.size > 0:
            mean_dev = np.nanmean(all_dev_padded, axis=0)
            std_dev = np.nanstd(all_dev_padded, axis=0)
        else:
            print(f"No valid data for {gnss_module} {jammer_type} Power {power}")
            continue

        # jammer type label
        jammerTypeLabel = jammer_type.upper()
        jammerPower = str(int(power)) + " dBm"
        if(jammerTypeLabel == "CW3"):
            jammerTypeLabel = "3×CW"

        if(jammerTypeLabel == "NONE"):
            jammerTypeLabel = "no"
            jammerPower = ""
        
        ax.plot(Time, mean_dev[:len(Time)], label=f'{gnss_module} {jammerTypeLabel} {jammerPower} jammer', linestyle='-', alpha=0.75)
        ax.fill_between(Time, mean_dev[:len(Time)] - std_dev[:len(Time)], mean_dev[:len(Time)] + std_dev[:len(Time)], alpha=0.2)

    # Plot the red vertical lines and labels
    if 'Time' in locals():
        ax.axvline(x=100, ymin=0.70, ymax=1, color='red', linestyle='--', alpha=0.75)
        ax.axvline(x=100, ymin=0, ymax=0.30, color='red', linestyle='--', alpha=0.75)
        ax.axvline(x=200, ymin=0.70, ymax=1, color='red', linestyle='--', alpha=0.75)
        ax.axvline(x=200, ymin=0, ymax=0.30, color='red', linestyle='--', alpha=0.75)
        ax.annotate('Jamming start', xy=(100, yscale[1]), xytext=(100, (yscale[0]+yscale[1]) / 2),
                    arrowprops=dict(arrowstyle='-', color='red', alpha=0),
                    verticalalignment='center', horizontalalignment='center', rotation=90, fontsize=12, color='red', alpha=0.75, bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.3'))
        ax.annotate('Jamming stop', xy=(200, yscale[1]), xytext=(200, (yscale[0]+yscale[1]) / 2),
                    arrowprops=dict(arrowstyle='-', color='red', alpha=0),
                    verticalalignment='center', horizontalalignment='center', rotation=90, fontsize=12, color='red', alpha=0.75, bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', boxstyle='round,pad=0.3'))

    ax.set_xlabel('Simulation time [s]', fontsize=14)
    ax.set_ylabel('Location deviation Δ [cm]', fontsize=14)
    ax.set_xlim(0, len(Time) - 1)
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))  # Limit the number of major ticks
    ax.set_ylim(yscale[0], yscale[1])
    ax.yaxis.set_major_locator(plt.MaxNLocator(yscale[2]))  # Limit the number of major ticks
    ax.tick_params(axis='both', which='major', labelsize=12)
    ax.grid(True, which='both', linestyle='-', linewidth=0.5)
    ax.xaxis.set_minor_locator(plt.MultipleLocator(10))
    ax.yaxis.set_minor_locator(plt.MultipleLocator(yscale[3]))
    ax.grid(which='minor', linestyle=':', linewidth='0.5', alpha=0.7)
    
    # Customize legend
    legend = ax.legend(loc='upper left', bbox_to_anchor=(0, 1), borderaxespad=0.6)
    legend.get_frame().set_edgecolor('black')
    legend.get_frame().set_facecolor('white')
    legend.get_frame().set_alpha(1)  # No transparency
    legend.get_frame().set_boxstyle('Square', pad=0)  # Rectangular box without rounded edges
    plt.setp(legend.get_texts(), fontsize=12, fontfamily='serif')  # Set font and font size

    plt.tight_layout()

    # Save the plot as an SVG file
    filename += "stdev_plot.svg"
    #plt.savefig("median_stdev/" + filename, format='svg')

    plt.show()


combos = [
    ('Ublox6', 'cw', '-70'),
    ('Ublox10', 'cw', '-70'),
    ('GP01', 'cw', '-70')
]
# min, max, max major locators, minor multiple locator
ylimits = [-200, 2000, 7, 200]
plot_jamming_data(combos, ylimits)


combos = [
    ('Ublox10', 'cw', '-45'),
    ('Ublox10', 'cw3', '-45'),
    ('Ublox10', 'FM', '-45')
]
# min, max, max major locators, minor multiple locator
ylimits = [-200, 400, 7, 50]
plot_jamming_data(combos, ylimits)


combos = [
    ('Ublox6', 'cw3', '-45'),
    ('Ublox10', 'cw3', '-45'),
    ('GP01', 'cw3', '-45')
]
# min, max, max major locators, minor multiple locator
ylimits = [-200, 400, 7, 50]
plot_jamming_data(combos, ylimits)

combos = [
    ('Ublox6', 'FM', '-50'),
    ('Ublox10', 'FM', '-50'),
    ('GP01', 'FM', '-50')
]
# min, max, max major locators, minor multiple locator
ylimits = [-200, 2000, 7, 200]
plot_jamming_data(combos, ylimits)

combos = [
    ('GP01', 'cw', '-45'),
    ('GP01', 'cw3', '-45'),
    ('GP01', 'none', '-155')
]
# min, max, max major locators, minor multiple locator
ylimits = [-200, 400, 7, 50]
plot_jamming_data(combos, ylimits)


combos = [
    ('Ublox6', 'cw', '-70'),
    ('Ublox6', 'cw3', '-70'),
    ('Ublox6', 'FM', '-70')
]
# min, max, max major locators, minor multiple locator
ylimits = [-200, 2000, 7, 200]
plot_jamming_data(combos, ylimits)

combos = [
    ('Ublox10', 'cw', '-45'),
    ('Ublox10', 'cw', '-50'),
    ('Ublox10', 'cw', '-55'),
    ('Ublox10', 'cw', '-60'),
    ('Ublox10', 'cw', '-65'),
    ('Ublox10', 'cw', '-70')
]
# min, max, max major locators, minor multiple locator
ylimits = [-200, 400, 7, 50]
plot_jamming_data(combos, ylimits)

combos = [
    ('Ublox6', 'cw', '-70'),
    ('Ublox10', 'cw', '-70'),
    ('GP01', 'cw', '-70')
]
# min, max, max major locators, minor multiple locator
ylimits = [-200, 2000, 7, 200]
plot_jamming_data(combos, ylimits)