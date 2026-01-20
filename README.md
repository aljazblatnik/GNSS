# Voyage to the Frozen Continent: Maritime GNSS & Jamming Dataset

**A global repository for research materials concerning GNSS receiver vulnerability to jamming, spoofing, and harsh maritime environments.**

## 🚢 Dataset Overview: Why Use This Data?
This repository hosts the code and documentation for the dataset associated with the article **"Voyage to the Frozen Continent: A Comprehensive GNSS Dataset from a Ship’s Expedition to Antarctica"** published in *Scientific Data*.

This is not a static station dataset; it captures the dynamic reality of the **Laura Bassi icebreaker** over a **200-day expedition** (Oct 7, 2024 – April 24, 2025). It bridges the gap in maritime data availability by providing continuous recording from the Mediterranean, through the Panama Canal, to the polar conditions of the Ross Sea.

### ⚡ Key Features for AI & Research Analysis
* **Real-World Jamming Labels:** The dataset contains **81 days** with confirmed jamming events, totaling **154,874 recorded interference instances**. This makes it an ideal training ground for Machine Learning (ML) classifiers distinguishing between intentional jamming and unintentional interference.
* **Spectrum "Waterfalls":** Unlike standard logs, this dataset includes `UBX-MON-SPAN` messages (1 Hz), allowing you to visualize the RF spectrum and characterize interference shapes (broadband vs. narrowband) alongside position errors.
* **Raw Observations:** Includes `UBX-RXM-MEASX` (pseudorange, carrier phase, Doppler) for testing resilient PNT algorithms and RTK performance in low-SNR polar environments.
* **Harsh Environments:** Captures signal behavior during high-latitude ionospheric disturbances, severe weather, and dynamic vessel motion (roll/pitch) in the Antarctic Circle.

---

## 📥 Access the Data
**[Download via Zenodo (111.7 GB)](https://zenodo.org/records/15783534)**

* **Format:** Daily binary `.ubx` files (approx. 600 MB each).
* **Coverage:** 200 continuous days (2024-10-07 to 2025-04-24).
* **Constellations:** GPS, Galileo, BeiDou (L1 Frequency).

---

## 🛠️ Code & Usage
We provide Python scripts to help you immediately parse the binary structure without needing external libraries. These scripts were used to generate the figures in the published paper and are optimized for speed by reading directly from the binary stream.

You can find these tools in the `examples/data_visualization_nature` directory:

| Script | Function |
| :--- | :--- |
| **[`analyze_GNSS_count.py`](examples/data_visualization_nature/analyze_GNSS_count.py)** | Performs statistical processing of received sentence counts. |
| **[`analyze_GNSS_full_stats.py`](examples/data_visualization_nature/analyze_GNSS_full_stats.py)** | Extracts detailed statistics of GNSS parameters (C/N0, satellite visibility). |
| **[`plotting_GNSS_path.py`](examples/data_visualization_nature/plotting_GNSS_path.py)** | Reconstructs and visualizes the research vessel's complete navigation trajectory. |
| **[`analyze_GNSS_plot_waterfall.py`](examples/data_visualization_nature/analyze_GNSS_plot_waterfall.py)** | Plots RF spectrum waterfalls (`UBX-MON-SPAN`) to visualize jamming and noise. |
| **[`analyze_GNSS_logger_data.py`](examples/data_visualization_nature/analyze_GNSS_logger_data.py)** | Graphically visualizes specific jamming parameters and receiver state metrics. |

### Quick Start Note
While the data is compatible with **u-blox u-center 1.x.x**, our provided Python scripts offer a more flexible way to batch-process the 200 days of recordings for scientific analysis.

---

## 📚 Citation
If you utilize this dataset or code in your research, please cite the following paper:

**Bertalanič, B., Dimc, F., Bažec, M., & Blatnik, A.**. *Voyage to the Frozen Continent: A Comprehensive GNSS Dataset from a Ship’s Expedition to Antarctica*. Sci Data 13, 49 (2026) DOI: [10.1038/s41597-025-06366-x](https://doi.org/10.1038/s41597-025-06366-x).

```bibtex
@article{Bertalanic2025,
  title = {Voyage to the Frozen Continent: A Comprehensive GNSS Dataset from a Ship’s Expedition to Antarctica},
  author = {Bertalanič, Blaž and Dimc, Franc and Bažec, Matej and Blatnik, Aljaž},
  journal = {Scientific Data},
  year = {2025},
  url = {[https://doi.org/10.1038/s41597-025-06366-x](https://doi.org/10.1038/s41597-025-06366-x)}
}
```

### (MDPI) GNSS Jamming Response Dataset 2025
[---> Dataset download (5.5 GB) <---](https://lso.fe.uni-lj.si/video/arhiv/GNSS/jamming_dataset_august_2024.json)

This dataset is a key component of the research presented in the article **"Evaluating GNSS Receiver Resilience: A Study on Simulation Environment Repeatability"** [https://www.mdpi.com/3289316](https://www.mdpi.com/3289316). It includes measurements capturing the response of three GNSS receivers – Ai-Thinker `GP-01`, U-blox `NEO-6M` (6-Series), and U-blox `MAX-M10` (10-Series) – under three different jamming conditions, each with varying jamming strengths. The article provides an in-depth explanation of the measurement setup, methodology employed, and a detailed analysis of the results contained within this dataset.
#### Dataset access example code
Here's an example of accessing the `json_data` dictionary in Python:
```python
json_data = json.load('jamming_dataset_august_2024.json')

for measurement in json_data['ublox6']['cw']['-70']:
    # Prepare before iterating through available data points (seconds).
    for sample in measurement:
        latitude = float(sample['Lat']) # Must be converted to float
        Longitude = float(sample['Lon'])
        timeStamp = sample['Time']
        sattelitesUsed = sample['usedTotalCnt']
        .
        .
        .
```
#### Data structure
The top-level structure of the `jamming_dataset_august_2024.json` file is represented in JSON as follows:
```JSON
[
 "ublox6": ["cw / cw3 / FM / none"],
 "ublox10": ["cw / cw3 / FM / none"],
 "GP01": ["cw / cw3 / FM / none"]
]
```
Every jamming type features 6 different power levels, with the exception of the `none` option, which has only one power level at `"-155"`.
```JSON
[
 "-70": [0-49],
 "-65": [0-49],
 "-60": [0-49],
 "-55": [0-49],
 "-50": [0-49],
 "-45": [0-49]
]
```
Each measurement is contained within an array structure as follows:
```JSON
[
{
    "Lat": 46.0487815, 
    "Lon": 14.5085375, 
    "LatDev": -5.5555500649226985, 
    "LonDev": -5.3783852879677285, 
    "Time": 1, 
    "Power": -155, 
    "fixMode": 3, 
    "pdop": 0.94, 
    "hdop": 0.51, 
    "vdop": 0.79, 
    "usedTotalCnt": 26,
    "GPS": {
        "usedCnt": 9,
        "used": [
            8,
            10,
            18,
            "..."
        ],
        "visible": [
            {
            "ID": 7,
            "el": 7,
            "az": 311,
            "SNR": 18
            },
            "..."
        ],
        "visibleCnt": 13
        },
    "GALILEO": {
        "usedCnt": 7,
        "used": [
            15,
            13,
            "..."
        ],
        "visible": [
            {
            "ID": 5,
            "el": 15,
            "az": 79,
            "SNR": 38
            },
            "..."
        ],
        "visibleCnt": 7
    },
    "GLONASS": {},
    "BEIDOU": {},
    "QZSS": {}
},
"..."
]
```
#### Data visualization examples

This publicly available dataset offers a wide range of applications, including detailed response analysis, machine learning implementation, and anomaly detection. A straightforward way to illustrate its use is through time series visualizations. You can find three example Python scripts for data visualization in the `examples/data_visualization_mdpi directory`:

[Plotting position deviation from the reference point](examples/data_visualization_mdpi/plot_location_deviation_from_center.py)\
[Plotting position deviation over time](examples/data_visualization_mdpi/plot_location_time_deviation.py)\
[Position deviation over time plot (median & std dev)](examples/data_visualization_mdpi/plot_location_time_median_and_stdev.py)

#### Copyright and Terms of Use

This dataset is publicly available under the **Creative Commons Attribution-NonCommercial (CC BY-NC) 4.0 International license**.

This means you're free to:

* **Share** — copy and redistribute the material in any medium or format.
* **Adapt** — remix, transform, and build upon the material.

Under the following terms:

* **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
* **NonCommercial** — You may not use the material for commercial purposes.

---

When citing this database or any of its code examples, please reference the following publication:

[https://www.mdpi.com/3289316](https://www.mdpi.com/3289316)

### Source Verification
* **Vessel & Timeline:** The dataset covers 200 days from Oct 7, 2024, to April 24, 2025, aboard the Laura Bassi[cite: 2, 26, 31].
* **Jamming Statistics:** The specific mention of "81 days" and "154,874 recorded interference instances" is derived directly from the validation section of the paper[cite: 163, 164].
* **Spectrum Data:** The inclusion of `UBX-MON-SPAN` for spectrum visualization is confirmed in the data record[cite: 33, 96, 119].
* **Code Availability:** The Python scripts listed correspond to the files provided in the code availability section and the Zenodo repository[cite: 90, 186].