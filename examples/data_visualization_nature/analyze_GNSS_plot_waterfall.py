import numpy as np
import matplotlib.pyplot as plt

ubxfile1 = "dan_20241225.ubx"
ubxfile2 = "dan_20250128.ubx"

def downsample_stats(data, window_size):
    stats = []
    for i in range(0, len(data), window_size):
        window = [x for x in data[i:i+window_size] if x is not None]
        if window:
            avg = float(np.mean(window))
            std = float(np.std(window))
            min_val = float(np.min(window))
            max_val = float(np.max(window))
            stats.append({
                "avg": avg,
                "std": std,
                "min": min_val,
                "max": max_val
            })
        else:
            stats.append({
                "avg": None,
                "std": None,
                "min": None,
                "max": None
            })
    return stats

# Helper to extract stats for plotting
def extract_stats(stats):
    avg = [s["avg"] for s in stats]
    std = [s["std"] for s in stats]
    min_val = [s["min"] for s in stats]
    max_val = [s["max"] for s in stats]
    return np.array(avg), np.array(std), np.array(min_val), np.array(max_val)

def process_ubx_file(ubxfile):
    with open(ubxfile, "rb") as f:
        data = f.read()

    # Find all occurrences of UBX sync chars
    sync_indices = []
    i = 0
    while i < len(data) - 1:
        if data[i:i+2] == b'\xb5\x62':
            sync_indices.append(i)
            # Skip to the end of the current message
            if i + 6 <= len(data):
                length = int.from_bytes(data[i+4:i+6], byteorder='little')
                i += 6 + length + 2  # Move to the byte after the current message
            else:
                break
        else:
            i += 1

    spectrumSamplesGlobal = []
    spectrumSpanGlobal = 0 # in Hz
    spectrumResolutionGlobal = 0 # in Hz
    spectrumCenterFrequencyGlobal = 0 # in Hz
    spectrumPGAGlobal = [] # PGA gain in dB
    for idx in range(len(sync_indices) - 1):
        start = sync_indices[idx]
        end = sync_indices[idx + 1]
        input_line = data[start:end]
        # Check if this is a MON-SPAN message (class 0x0a, id 0x31)
        # UBX header: 2 bytes, class: 1 byte, id: 1 byte, length: 2 bytes, then payload
        if input_line[2] == 0x0a and input_line[3] == 0x31:
            # Payload starts at offset 6
            payload = input_line[6:]
            # spectrum samples array from offset 4 to 260
            spectrumSamples = payload[4:260]
            spectrumSpanGlobal = int.from_bytes(payload[260:264], byteorder='little')
            spectrumResolutionGlobal = int.from_bytes(payload[264:268], byteorder='little')
            spectrumCenterFrequencyGlobal = int.from_bytes(payload[268:272], byteorder='little')
            spectrumPGA = payload[272]  # PGA gain in dB
            spectrumSamplesGlobal.append(spectrumSamples)
            spectrumPGAGlobal.append(spectrumPGA)

    #convert spectrumSamplesGlobal to float fb where each 0 is 0 dB and 256 is 64 dB
    spectrumSamplesGlobal = [[(x / 256) * 64 for x in spectrum] for spectrum in spectrumSamplesGlobal]
    # substract PGA gain value from each sample inside list of spectrumSamplesGlobal
    spectrumSamplesGlobal = [[x - pga for x in spectrum] for spectrum, pga in zip(spectrumSamplesGlobal, spectrumPGAGlobal)]

    # Prepare waterfall data as a 2D numpy array (time x frequency bins)
    waterfall = np.array(spectrumSamplesGlobal)

    # Frequency axis: 256 bins, centered at spectrumCenterFrequencyGlobal, span spectrumSpanGlobal
    num_bins = 256
    freqs = np.linspace(
        spectrumCenterFrequencyGlobal - spectrumSpanGlobal // 2,
        spectrumCenterFrequencyGlobal + spectrumSpanGlobal // 2,
        num_bins
    )

    # Time axis in minutes (assuming 1 sample per second; adjust if different)
    time_minutes = np.arange(waterfall.shape[0]) / 60

    return waterfall, freqs, time_minutes

# Process both files
waterfall1, freqs1, time_minutes1 = process_ubx_file(ubxfile1)
waterfall2, freqs2, time_minutes2 = process_ubx_file(ubxfile2)

# Enhance dynamic range by normalizing and stretching the color scale for each
vmin1 = np.percentile(waterfall1, 2)
vmax1 = np.percentile(waterfall1, 98)
vmin2 = np.percentile(waterfall2, 2)
vmax2 = np.percentile(waterfall2, 98)

fig, axs = plt.subplots(1, 2, figsize=(15, 8), sharey=True)

im1 = axs[0].imshow(
    waterfall1,
    aspect='auto',
    extent=[freqs1[0]/1e6, freqs1[-1]/1e6, time_minutes1[-1], time_minutes1[0]],
    origin='upper',
    cmap='jet',
    vmin=vmin1,
    vmax=vmax1
)
axs[0].set_xlabel('Frequency (MHz)', fontsize=16)
axs[0].set_ylabel('Time (min)', fontsize=16)
axs[0].set_title('Impact of CW interference', fontsize=18)
axs[0].tick_params(axis='both', which='major', labelsize=14)
cbar1 = fig.colorbar(im1, ax=axs[0], label='Power (dB)')
cbar1.ax.tick_params(labelsize=14)
cbar1.set_label('Power (dB)', fontsize=16)

im2 = axs[1].imshow(
    waterfall2,
    aspect='auto',
    extent=[freqs2[0]/1e6, freqs2[-1]/1e6, time_minutes2[-1], time_minutes2[0]],
    origin='upper',
    cmap='jet',
    vmin=vmin2,
    vmax=vmax2
)
axs[1].set_xlabel('Frequency (MHz)', fontsize=16)
axs[1].set_title('Impact of unresolved jamming', fontsize=18)
axs[1].tick_params(axis='both', which='major', labelsize=14)
cbar2 = fig.colorbar(im2, ax=axs[1], label='Power (dB)')
cbar2.ax.tick_params(labelsize=14)
cbar2.set_label('Power (dB)', fontsize=16)

plt.tight_layout()
plt.show()
