# GNSS tools and databases
A global repository for research materials concerning GNSS receiver vulnerability to jamming and spoofing.

## Publicly available datasets
### GNSS Jamming Response Dataset 2025
[---> Dataset download (5.5 GB) <---](https://lso.fe.uni-lj.si/video/arhiv/GNSS/jamming_dataset_august_2024.json)

This dataset is a key component of the research presented in the article **"Evaluating GNSS Receiver Resilience: A Study on Simulation Environment Repeatability"** [link to published article]. It includes measurements capturing the response of three GNSS receivers – `Ai-Thinker GP-01`, `U-blox NEO-6M` (6-Series), and `U-blox MAX-M10` (10-Series) – under three different jamming conditions, each with varying jamming strengths. The article provides an in-depth explanation of the measurement setup, methodology employed, and a detailed analysis of the results contained within this dataset.
#### Data Access Example Code
Here's an example of accessing the `json_data` dictionary in Python:
```python
json_data = json.load('jamming_dataset_august_2024.json')

for measurement in json_data["ublox6"]["cw"]["-70"]:
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
Every jamming type features 6 different power levels, with the exception of the `none` option, which has only one power level: `"-155"`.
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
Each measurement is contained within its specific data structure:
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