import numpy as np
import os
import matplotlib.pyplot as plt

ubxfolder = "path_to_foldet_with_ubx_files"

count_rxm_rlm = 0
count_nav_pvt = 0
count_nav_sat = 0
count_rxm_measx = 0
count_mon_rf = 0
count_mon_span = 0

for ubxfile in os.listdir(ubxfolder):
    if not ubxfile.lower().endswith(".ubx"):
        continue
    ubx_path = os.path.join(ubxfolder, ubxfile)
    with open(ubx_path, "rb") as f:
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

    for idx in range(len(sync_indices) - 1):
        start = sync_indices[idx]
        end = sync_indices[idx + 1]
        input_line = data[start:end]
        # UBX header: 2 bytes, class: 1 byte, id: 1 byte, length: 2 bytes, then payload
        if len(input_line) < 6:
            continue
        msg_class = input_line[2]
        msg_id = input_line[3]
        if msg_class == 0x02 and msg_id == 0x59:  # RXM-RLM
            count_rxm_rlm += 1
        elif msg_class == 0x01 and msg_id == 0x07:  # NAV-PVT
            count_nav_pvt += 1
        elif msg_class == 0x01 and msg_id == 0x35:  # NAV-SAT
            count_nav_sat += 1
        elif msg_class == 0x02 and msg_id == 0x14:  # RXM-MEASX
            count_rxm_measx += 1
        elif msg_class == 0x0A and msg_id == 0x38:  # MON-RF
            count_mon_rf += 1
        elif msg_class == 0x0A and msg_id == 0x31:  # MON-SPAN
            count_mon_span += 1

    print(f"{ubxfile}:")
    print(f"  UBX-RXM-RLM: {count_rxm_rlm}")
    print(f"  UBX-NAV-PVT: {count_nav_pvt}")
    print(f"  UBX-NAV-SAT: {count_nav_sat}")
    print(f"  UBX-RXM-MEASX: {count_rxm_measx}")
    print(f"  UBX-MON-RF: {count_mon_rf}")
    print(f"  UBX-MON-SPAN: {count_mon_span}")
