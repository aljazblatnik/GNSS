import numpy as np
import matplotlib.pyplot as plt

ubxfile = "dan_20241225.ubx"

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
print(f"Found {len(sync_indices)} UBX sync characters.")

agcCntGlobal = []
cwSuppressionGlobal = []
jammingStatusGlobal = []
noisePerMsGlobal = []
magIGlobal = []
magQGlobal = []
for idx in range(len(sync_indices) - 1):
    start = sync_indices[idx]
    end = sync_indices[idx + 1]
    input_line = data[start:end]
    # Check if this is a MON-RF message (class 0x0a, id 0x38)
    # UBX header: 2 bytes, class: 1 byte, id: 1 byte, length: 2 bytes, then payload
    if input_line[2] == 0x0a and input_line[3] == 0x38:
        # Payload starts at offset 6
        payload = input_line[6:]
        # jamming status at offset 5
        jammingStatus = payload[5]
        noisePerMs = int.from_bytes(payload[16:17], byteorder='little')
        # agcCnt: 2 bytes at offset 18
        agcCnt = int.from_bytes(payload[18:20], byteorder='little')
        # cwSuppression: 1 byte at offset 20
        cwSuppression = payload[20]
        # magI: 1 byte at offset 22
        magI = payload[22]
        # ofsI: 1 byte at offset 21
        magQ = int.from_bytes(payload[21:22], byteorder='little', signed=True)
        agcCntGlobal.append(agcCnt)
        cwSuppressionGlobal.append(cwSuppression)
        jammingStatusGlobal.append(jammingStatus)
        noisePerMsGlobal.append(noisePerMs)
        magIGlobal.append(magI)
        magQGlobal.append(magQ)

# convert agcCntGlobal AGC monitor value to % where 0 is 0% and 8191 is 100%
agcCntPercent = [round((x / 8191) * 100, 2) for x in agcCntGlobal]
# same for cwSuppressionGlobal but 0 is 0% and 255 is 100% (strong jamming)
cwSuppressionPercent = [round((x / 255) * 100, 2) if x is not None else None for x in cwSuppressionGlobal]
# Downsample the data to 1 minute intervals
agcCntPercent_stats = downsample_stats(agcCntPercent, 60) # 1 minute
cwSuppressionPercent_stats = downsample_stats(cwSuppressionPercent, 60) # 1 minute
jammingStatus_stats = downsample_stats(jammingStatusGlobal, 60) # 1 minute
# Convert noisePerMsGlobal to dBm using the given equation
# noise_level[dBm] = -174 + 1.5 + 40 + noisePerMsGlobal/10
noisePerMs_dBm = [(-174 + 1.5 + 40 + (x / 10)) if x is not None else None for x in noisePerMsGlobal]
noisePerMs_stats = downsample_stats(noisePerMs_dBm, 60) # 1 minute

# Downsample magI and magQ as well
# Scale magIGlobal to % where 0 is 0% and 255 is 100%
magI_percent = [round((x / 255) * 100, 2) if x is not None else None for x in magIGlobal]
magI_stats = downsample_stats(magI_percent, 60) # 1 minute
# Scale magQGlobal to % where 127 is +100%, -127 is -100%, 0 is 0%
magQ_percent = [round((x / 127) * 100, 2) if x is not None else None for x in magQGlobal]
magQ_stats = downsample_stats(magQ_percent, 60) # 1 minute

minutes = np.arange(len(agcCntPercent_stats))


# Plot for cwSuppressionPercent_stats
avg, std, min_val, max_val = extract_stats(cwSuppressionPercent_stats)
x = np.arange(len(avg))  # x starts at 0 and ends at last sample

# Prepare jammingStatus shading
jamming_avg, _, _, _ = extract_stats(jammingStatus_stats)
# Normalize jamming status: 1 -> 0 (transparent), 3 -> 0.5 (50% alpha)
jam_alpha = np.clip((np.array(jamming_avg, dtype=float) - 1) / 2 * 0.5, 0, 0.5)

fig, axs = plt.subplots(2, 2, figsize=(18, 10))
plt.subplots_adjust(hspace=0.3, wspace=1)

# 1. CW Suppression (upper left)
avg, std, min_val, max_val = extract_stats(cwSuppressionPercent_stats)
x = np.arange(len(avg))
for i in range(len(x)):
    if not np.isnan(jam_alpha[i]) and jam_alpha[i] > 0:
        axs[0, 0].axvspan(i-0.5, i+0.5, color='gray', alpha=jam_alpha[i], zorder=0)
axs[0, 0].plot(x, avg, label="Average", color="black", linewidth=1.5)
axs[0, 0].plot(x, min_val, color='blue', linestyle='-', linewidth=0.5, label="(Min)")
axs[0, 0].plot(x, max_val, color='red', linestyle='-', linewidth=0.5, label="(Max)")
axs[0, 0].set_title(r"$\bf{(a)}$" + " CW Suppression (%)", fontsize=18, loc='center')
axs[0, 0].set_xlabel("Minutes Past Midnight", fontsize=16)
axs[0, 0].set_ylabel("CW Suppression [%]", fontsize=16)
axs[0, 0].legend(loc="lower right", framealpha=1, fontsize=16)
axs[0, 0].grid(True)
axs[0, 0].set_xlim(left=0, right=len(x)-1)
axs[0, 0].set_ylim(0, 50)
axs[0, 0].tick_params(axis='both', labelsize=14)

# 2. Noise level (upper right)
avg, std, min_val, max_val = extract_stats(noisePerMs_stats)
x = np.arange(len(avg))
for i in range(len(x)):
    if not np.isnan(jam_alpha[i]) and jam_alpha[i] > 0:
        axs[0, 1].axvspan(i-0.5, i+0.5, color='gray', alpha=jam_alpha[i], zorder=0)
axs[0, 1].plot(x, avg, label="Average", color="black", linewidth=1.5)
axs[0, 1].plot(x, min_val, color='blue', linestyle='-', linewidth=0.5, label="(Min)")
axs[0, 1].plot(x, max_val, color='red', linestyle='-', linewidth=0.5, label="(Max)")
axs[0, 1].set_title(r"$\bf{(b)}$" + " Noise level", fontsize=18, loc='center')
axs[0, 1].set_xlabel("Minutes Past Midnight", fontsize=16)
axs[0, 1].set_ylabel("Power [dBm]", fontsize=16)
axs[0, 1].legend(loc="lower right", framealpha=1, fontsize=16)
axs[0, 1].grid(True)
axs[0, 1].set_xlim(left=0, right=len(x)-1)
axs[0, 1].set_ylim(-126, -118)
axs[0, 1].tick_params(axis='both', labelsize=14)

# 3. magI (lower left)
avg, std, min_val, max_val = extract_stats(magI_stats)
x = np.arange(len(avg))
for i in range(len(x)):
    if not np.isnan(jam_alpha[i]) and jam_alpha[i] > 0:
        axs[1, 0].axvspan(i-0.5, i+0.5, color='gray', alpha=jam_alpha[i], zorder=0)
axs[1, 0].plot(x, avg, label="Average", color="black", linewidth=1.5)
axs[1, 0].plot(x, min_val, color='blue', linestyle='-', linewidth=0.5, label="(Min)")
axs[1, 0].plot(x, max_val, color='red', linestyle='-', linewidth=0.5, label="(Max)")
axs[1, 0].set_title(r"$\bf{(c)}$" + " Magnitude of In-Phase Component", fontsize=18, loc='center')
axs[1, 0].set_xlabel("Minutes Past Midnight", fontsize=16)
axs[1, 0].set_ylabel("I-Magnitude [%]", fontsize=16)
axs[1, 0].legend(loc="lower right", framealpha=1, fontsize=16)
axs[1, 0].grid(True)
axs[1, 0].set_xlim(left=0, right=len(x)-1)
axs[1, 0].set_ylim(0, 100)
axs[1, 0].tick_params(axis='both', labelsize=14)

# 4. magQ (lower right)
avg, std, min_val, max_val = extract_stats(magQ_stats)
x = np.arange(len(avg))
for i in range(len(x)):
    if not np.isnan(jam_alpha[i]) and jam_alpha[i] > 0:
        axs[1, 1].axvspan(i-0.5, i+0.5, color='gray', alpha=jam_alpha[i], zorder=0)
axs[1, 1].plot(x, avg, label="Average", color="black", linewidth=1.5)
axs[1, 1].plot(x, min_val, color='blue', linestyle='-', linewidth=0.5, label="(Min)")
axs[1, 1].plot(x, max_val, color='red', linestyle='-', linewidth=0.5, label="(Max)")
axs[1, 1].set_title(r"$\bf{(d)}$" + " Imbalance of In-Phase Component", fontsize=18, loc='center')
axs[1, 1].set_xlabel("Minutes Past Midnight", fontsize=16)
axs[1, 1].set_ylabel("I-Imbalance [%]", fontsize=16)
axs[1, 1].legend(loc="lower right", framealpha=1, fontsize=16)
axs[1, 1].grid(True)
axs[1, 1].set_xlim(left=0, right=len(x)-1)
axs[1, 1].set_ylim(-20, 50)
axs[1, 1].tick_params(axis='both', labelsize=14)

plt.tight_layout()
plt.show()
