import os
import glob
import struct
import pandas as pd
import time 
from multiprocessing import Pool
import pyarrow as pa
import pyarrow.parquet as pq
import gc
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# --- UBX Checksum Calculator---

def calculate_checksum(payload_with_header):
    """
    Calculates the 8-bit Fletcher-16 checksum for a UBX message.
    """
    ck_a = 0
    ck_b = 0
    for byte in payload_with_header:
        ck_a = (ck_a + byte) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return ck_a, ck_b

# --- The Core Binary Processing Function ---

def process_single_file_binary(filepath):
    """
    Reads a single UBX file, finds both MON-RF (jamming) and
    NAV-PVT (position) messages, and links them.
    """
    data = []
    
    # This holds the most recent valid position
    last_known_pos = {'lon': None, 'lat': None}
    
    with open(filepath, 'rb') as f:
        buffer = bytearray()
        
        while True:
            chunk = f.read(8192)
            if not chunk:
                break  
            
            buffer.extend(chunk)
            
            while len(buffer) > 8: 
                idx = buffer.find(b'\xb5\x62')
                
                if idx == -1:
                    buffer = buffer[-1:]
                    break
                
                if idx > 0:
                    buffer = buffer[idx:]
                
                if len(buffer) < 6:
                    break
                    
                msg_cls, msg_id, payload_len = struct.unpack('<BBH', buffer[2:6])
                
                total_msg_len = 8 + payload_len
                if len(buffer) < total_msg_len:
                    break
                
                message_frame = buffer[:total_msg_len]
                buffer = buffer[total_msg_len:] 

                header_and_payload = message_frame[2:6+payload_len]
                ck_a_rcv, ck_b_rcv = struct.unpack('<BB', message_frame[6+payload_len:])
                ck_a_calc, ck_b_calc = calculate_checksum(header_and_payload)

                if ck_a_calc != ck_a_rcv or ck_b_calc != ck_b_rcv:
                    continue
                
                payload = message_frame[6:6+payload_len]

                # --- Check for NAV-PVT (Position) Message ---
                if msg_cls == 0x01 and msg_id == 0x07:
                    # 'fixType' is at offset 20
                    if payload_len >= 21: # Check payload is long enough for fixType
                        # '<B' = unsigned char at offset 20
                        fixType = struct.unpack_from('<B', payload, 20)[0]
                        
                        # fixType == 3 is a 3D-fix. Also check payload length for lon/lat
                        if fixType == 3 and payload_len >= 32:
                            # '<i' = signed 4-byte int
                            # lon is at offset 24, lat is at offset 28
                            lon = struct.unpack_from('<i', payload, 24)[0]
                            lat = struct.unpack_from('<i', payload, 28)[0]
                            
                            # Scale values (1e-7)
                            last_known_pos['lon'] = lon * 1e-7
                            last_known_pos['lat'] = lat * 1e-7

                # --- Check for MON-RF (Jamming) Message ---
                elif msg_cls == 0x0A and msg_id == 0x38:
                    if len(payload) < 1:
                        continue
                    version = struct.unpack_from('<B', payload, 0)[0]
                    
                    if version != 0: # Only parse v0 of the protocol
                        continue

                    if len(payload) < 4:
                        continue
                        
                    nBlocks = struct.unpack_from('<B', payload, 1)[0]
                    offset = 4
                    block_size = 24
                    
                    for i in range(nBlocks):
                        block_start = offset + (i * block_size)
                        
                        if block_start + 19 > len(payload): 
                            break
                        
                        flags_byte = struct.unpack_from('<B', payload, block_start + 1)[0]
                        jam_state = flags_byte & 0x03
                        
                        agc_cnt = struct.unpack_from('<H', payload, block_start + 18)[0]

                        # Stamp the jamming data with the last known position
                        data.append({
                            'jamming_state': jam_state, 
                            'agc_count': agc_cnt,
                            'rf_block': i,
                            'lon': last_known_pos['lon'], # NEW
                            'lat': last_known_pos['lat']  # NEW
                        })

    # --- Metadata/Summary Logic (All Stats) ---
    df = pd.DataFrame(data)
    
    # Drop any rows that were recorded before the first valid GPS fix
    df.dropna(subset=['lon', 'lat'], inplace=True)
    
    if not df.empty:
        # Get counts for each jamming state
        state_counts = df['jamming_state'].value_counts()
        jam_state_0 = int(state_counts.get(0, 0)) # 0 = Unknown
        jam_state_1 = int(state_counts.get(1, 0)) # 1 = OK
        jam_state_2 = int(state_counts.get(2, 0)) # 2 = Warning
        jam_state_3 = int(state_counts.get(3, 0)) # 3 = Critical
        
        jamming_detected = (jam_state_2 > 0) or (jam_state_3 > 0)
        jamming_event_count = jam_state_2 + jam_state_3
        
        # Get quantiles/stats
        stats = df['agc_count'].describe()
        agc_mean = float(stats.get('mean', np.nan))
        agc_std = float(stats.get('std', np.nan))
        agc_min = float(stats.get('min', np.nan))
        agc_q1 = float(stats.get('25%', np.nan))
        agc_median = float(stats.get('50%', np.nan))
        agc_q3 = float(stats.get('75%', np.nan))
        agc_max = float(stats.get('max', np.nan))
        
    else:
        # Default values if file had no MON-RF data
        jamming_detected = False
        jamming_event_count = 0
        jam_state_0, jam_state_1, jam_state_2, jam_state_3 = 0, 0, 0, 0
        agc_mean, agc_std, agc_min, agc_q1, agc_median, agc_q3, agc_max = (np.nan,) * 7
        
    summary = {
        'filename': os.path.basename(filepath),
        'jamming_detected': bool(jamming_detected),
        'jamming_event_count': int(jamming_event_count),
        'jam_state_0_unknown': jam_state_0,
        'jam_state_1_ok': jam_state_1,
        'jam_state_2_warn': jam_state_2,
        'jam_state_3_crit': jam_state_3,
        'agc_mean': agc_mean,
        'agc_std': agc_std,
        'agc_min': agc_min,
        'agc_q1': agc_q1,
        'agc_median': agc_median,
        'agc_q3': agc_q3,
        'agc_max': agc_max
    }
    
    return (df, summary) 

# --- Main Script (20 Workers, With All Plots) ---

if __name__ == '__main__':
    
    # --- Set your folder path with data here ---
    ubx_folder = 'data/antarctica2025/processed'
    # ---------------------------------------------
    
    all_files = glob.glob(os.path.join(ubx_folder, '*.ubx'))
    all_files.sort()
    
    if not all_files:
        print(f"--- ERROR ---")
        print(f"No '.ubx' files found in the folder: {ubx_folder}")
        print("Please check the 'ubx_folder' variable in the script.")
    else:
        # --- Configuration ---
        PROCESS_COUNT = 20
        FINAL_DATA_FILE = 'antarctica_rf_analysis_ALL.parquet'
        FINAL_META_FILE = 'jamming_metadata_by_day.csv'
        # ---------------------

        print(f"--- Starting Analysis (with Position) ---")
        print(f"Found {len(all_files)} UBX files.")
        print(f"Using {PROCESS_COUNT} parallel workers.")
        
        start_time = time.perf_counter()

        all_summaries = []
        parquet_writer = None 
        
        # Define the Parquet schema to handle the new columns
        schema = pa.schema([
            pa.field('jamming_state', pa.int64()),
            pa.field('agc_count', pa.int64()),
            pa.field('rf_block', pa.int64()),
            pa.field('lon', pa.float64()),
            pa.field('lat', pa.float64())
        ])
        
        with Pool(processes=PROCESS_COUNT) as pool:
            for (df, summary) in pool.imap_unordered(process_single_file_binary, all_files):
                
                all_summaries.append(summary)
                
                if not df.empty:
                    # Ensure DataFrame columns match schema order/types
                    df = df.astype({'jamming_state': 'int64', 'agc_count': 'int64', 'rf_block': 'int64', 'lon': 'float64', 'lat': 'float64'})
                    table = pa.Table.from_pandas(df[schema.names], schema=schema)
                    # Write to Parquet file for faster post-processing
                    if parquet_writer is None:
                        parquet_writer = pq.ParquetWriter(FINAL_DATA_FILE, table.schema)
                    parquet_writer.write_table(table)
                    
                    del df
                    del table
                
                print(f"Processed: {summary['filename']} (Jamming: {summary['jamming_detected']}, "
                      f"Events: {summary['jamming_event_count']})")

        if parquet_writer:
            parquet_writer.close()
            
        print("Forcing garbage collection...")
        gc.collect()

        end_time = time.perf_counter()
        print(f"\n--- Processing Finished ---")
        print(f"Total time taken: {end_time - start_time:.4f} seconds")
        print(f"Full data (with position) saved to: {FINAL_DATA_FILE}")

        # --- METADATA ANALYSIS & PLOTTING ---
        print("\n\n--- Jamming Metadata (Per-Day/File Analysis) ---")
        
        meta_df = pd.DataFrame(all_summaries)
        meta_df.sort_values(by='filename', inplace=True)
        days_with_jamming = meta_df['jamming_detected'].sum()
        total_days = len(meta_df)
        print(f"Jamming Summary: {days_with_jamming} out of {total_days} days had jamming events.")
        print(f"\nSaving metadata report (with detailed stats) to: {FINAL_META_FILE}...")
        meta_df.to_csv(FINAL_META_FILE, index=False)
        
        # --- GLOBAL ANALYSIS & PLOT (from Parquet file) ---
        print("\n\n--- Global Statistics & Plot (from Parquet file) ---")
        
        try:
            full_pq_file = pq.ParquetFile(FINAL_DATA_FILE)
            print(f"Total {full_pq_file.metadata.num_rows} MON-RF messages found.")

            df_stats = full_pq_file.read(columns=['agc_count', 'jamming_state']).to_pandas()

            # 5. Global AGC vs. Jamming Box Plot
            print(f"Plotting global AGC vs. Jamming box plot...")
            try:
                df_stats['is_jammed'] = df_stats['jamming_state'] > 1
                fig, ax = plt.subplots(figsize=(10, 8))
                
                df_stats.boxplot(
                    column='agc_count',
                    by='is_jammed',
                    ax=ax,
                    patch_artist=True,
                    showmeans=True
                )
                
                ax.set_title('Global AGC Count by Jamming Status', fontsize=16)
                ax.set_ylabel('AGC Count', fontsize=12)
                ax.set_xlabel('Jamming Status', fontsize=12)
                ax.set_xticklabels(['Not Jammed (State 0/1)', 'Jammed (State 2/3)'])
                plt.suptitle('') 
                plt.tight_layout()
                plt.savefig('agc_global_jamming_boxplot.png')
                print("Saved agc_global_jamming_boxplot.png")
                plt.close()

            except Exception as e:
                print(f"An error occurred during global plotting: {e}")

            # --- Print Global Text Statistics ---
            print("\n--- Global AGC (Automatic Gain Control) Statistics ---")
            print(df_stats['agc_count'].describe())
            
            print("\n--- Global Jamming State (Overall Statistics) ---")
            print(df_stats['jamming_state'].describe())

            print("\n--- Global Jamming State Counts (0=Unk, 1=OK, 2=Warn, 3=Crit) ---")
            state_counts = df_stats['jamming_state'].value_counts().sort_index()
            print(state_counts)
            
            del df_stats
            del state_counts
            gc.collect()

        except FileNotFoundError:
            print(f"\nNOTE: No data was written to {FINAL_DATA_FILE}.")
            print("Global analysis will be skipped.")
        except Exception as e:
            print(f"Could not read Parquet file for stats. Error: {e}")

    print("\n--- All Done ---")