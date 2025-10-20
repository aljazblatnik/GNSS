import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs # Cartopy's coordinate reference systems
import cartopy.feature as cfeature # For adding coastlines, land, etc.
import time
import numpy as np

# --- Configuration ---
SOURCE_FILE = 'antarctica_rf_analysis_ALL.parquet' # Input Parquet file genereated by full_stats_v5.py
OUTPUT_MAP_FILE = 'jamming_events_map_cartopy_shifted_east.png' # New filename
SAMPLE_FRACTION = 0.05 # Use 5% of the data. Increase for more detail.


# Define the Cartopy projection - PlateCarree centered east of the antimeridian
MAP_PROJECTION = ccrs.PlateCarree(central_longitude=-160)
# -------------------------

# Data CRS is always standard PlateCarree (lon/lat)
DATA_CRS = ccrs.PlateCarree()
# ---------------------

print(f"Loading data from {SOURCE_FILE}...")
start_time = time.time()

columns_to_read = ['lon', 'lat', 'jamming_state']

try:
    df = pd.read_parquet(SOURCE_FILE, columns=columns_to_read)
    print(f"Loaded {len(df)} total records in {time.time() - start_time:.2f}s.")

    # --- Downsampling ---
    print(f"Downsampling to {SAMPLE_FRACTION * 100:.0f}% of the data...")
    if SAMPLE_FRACTION < 1.0:
        sample_df = df.sample(frac=SAMPLE_FRACTION, random_state=42)
    else:
        sample_df = df
    del df # Free memory

    if sample_df.empty:
        print("No data found after sampling. Was the Parquet file empty?")
    else:
        print(f"Plotting {len(sample_df)} data points...")

        # --- Plotting with Cartopy ---
        colors = {0: '#1f77b4', 1: '#2ca02c', 2: '#ff7f0e', 3: '#d62728'}
        labels = {0: 'Unknown', 1: 'OK (State 1)', 2: 'Warning (State 2)', 3: 'Critical (State 3)'}

        fig = plt.figure(figsize=(15, 8))
        ax = fig.add_subplot(1, 1, 1, projection=MAP_PROJECTION)

        print("Adding map features (coastlines, land)...")
        ax.add_feature(cfeature.LAND, facecolor='lightgray')
        ax.add_feature(cfeature.OCEAN, facecolor='white')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
        ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)

        print("Plotting data points...")
        for state, color in colors.items():
            subset = sample_df[sample_df['jamming_state'] == state]
            if not subset.empty:
                ax.scatter(
                    subset['lon'].values,
                    subset['lat'].values,
                    color=color,
                    label=labels[state],
                    s=5,
                    transform=DATA_CRS
                )

        
        # Only add legend entries for states actually present in the sample
        handles, current_labels = ax.get_legend_handles_labels()
        unique_labels = dict(zip(current_labels, handles)) # Ensure unique legend entries
        ax.legend(unique_labels.values(), unique_labels.keys(), markerscale=5, loc='best')

        ax.set_title(f'Jamming Events Map ({SAMPLE_FRACTION * 100:.0f}% Data Sample, Centered near -160 Lon)')
        # ax.set_global() # Uncomment if you want the full world view guaranteed

        plt.tight_layout()
        plt.savefig(OUTPUT_MAP_FILE, dpi=300)
        print(f"Successfully saved '{OUTPUT_MAP_FILE}'")

except FileNotFoundError:
    print(f"ERROR: '{SOURCE_FILE}' not found.")
    print("Please run the main processing script first.")
except ImportError:
    print("\n--- ERROR ---")
    print("Required libraries not found. Please run:")
    print("conda install -c conda-forge cartopy (recommended)")
    print("OR")
    print("pip install cartopy pandas matplotlib pyarrow numpy (may require manual dependency setup)")
except Exception as e:
    print(f"An error occurred: {e}")