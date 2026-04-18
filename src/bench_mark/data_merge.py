#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CS5296 Data Merge Script - Member B
Usage: python3 data_merge.py
"""

import pandas as pd
import glob
import os
from pathlib import Path

# Define paths
script_path = Path(__file__).resolve()
script_folder = script_path.parent
project_root = script_folder.parent.parent
results_dir = project_root / 'results'

def merge_all_results():
    """Find all result CSV files and merge them into a single master file."""
    csv_files = glob.glob(str(results_dir / 'instances' /'*.csv'))

    if not csv_files:
        print("[ERROR] No CSV files found in:", results_dir)
        return

    print(f"[INFO] Found {len(csv_files)} CSV file(s)")

    all_data = []
    for f in csv_files:
        try:
            df = pd.read_csv(f)

            # Extract instance type from filename
            # Example: results_c5.large.csv -> c5.large
            basename = os.path.basename(f)
            instance_name = basename.replace('.csv', '')

            # Filter out ERROR values
            original_count = len(df)
            df = df[df['Value'] != 'ERROR']
            df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
            df = df.dropna(subset=['Value'])

            if len(df) == 0:
                print(f"[WARN] {basename} - No valid data after filtering")
                continue

            df['Instance'] = instance_name
            all_data.append(df)
            print(f"[LOADED] {basename} -> {len(df)}/{original_count} records")

        except Exception as e:
            print(f"[ERROR] Failed to load {f}: {e}")

    if not all_data:
        print("[ERROR] No valid data to merge")
        return

    # Merge and save
    master_df = pd.concat(all_data, ignore_index=True)
    master_df = master_df.sort_values(['Instance', 'Metric'])

    output_path = results_dir/ 'final' / 'final_results.csv'
    master_df.to_csv(output_path, index=False)

    print(f"\n[SUCCESS] master_results.csv created!")
    print(f"[INFO] Output path: {output_path}")
    print(f"[INFO] Total records: {len(master_df)}")
    print("\n[SUMMARY] Records per instance:")
    print(master_df.groupby('Instance')['Metric'].count().to_string())


if __name__ == "__main__":
    merge_all_results()