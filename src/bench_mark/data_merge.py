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
    """Find all result CSV files and merge them into a pivot table format."""
    csv_files = glob.glob(str(results_dir / 'instances' / '*.csv'))

    if not csv_files:
        print("[ERROR] No CSV files found in:", results_dir / 'instances')
        return

    print(f"[INFO] Found {len(csv_files)} CSV file(s)")

    all_data = []
    unit_map = {}  # Store unit for each metric

    for f in csv_files:
        try:
            df = pd.read_csv(f)

            # Extract instance type from filename
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

            # Store unit information
            for _, row in df.iterrows():
                if row['Metric'] not in unit_map:
                    unit_map[row['Metric']] = row['Unit']

            df['Instance'] = instance_name
            all_data.append(df)
            print(f"[LOADED] {basename} -> {len(df)}/{original_count} records")

        except Exception as e:
            print(f"[ERROR] Failed to load {f}: {e}")

    if not all_data:
        print("[ERROR] No valid data to merge")
        return

    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)

    # Create pivot table
    pivot_df = combined_df.pivot_table(
        index='Metric',
        columns='Instance',
        values='Value',
        aggfunc='first'
    )

    pivot_df = pivot_df.reset_index()

    # Add unit column
    pivot_df['Unit'] = pivot_df['Metric'].map(unit_map)

    # Reorder columns: Metric, Unit, then instance columns
    instance_cols = sorted([col for col in pivot_df.columns if col not in ['Metric', 'Unit']])
    pivot_df = pivot_df[['Metric', 'Unit'] + instance_cols]

    # Round numeric values
    for col in instance_cols:
        pivot_df[col] = pivot_df[col].round(2)

    # Save pivot table
    output_path = results_dir / 'final' / 'final_results.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pivot_df.to_csv(output_path, index=False)

    print(f"\n[SUCCESS] Pivot table created!")
    print(f"[INFO] Output path: {output_path}")
    print(f"[INFO] Shape: {pivot_df.shape[0]} metrics x {len(instance_cols)} instances")
    print("\n[PREVIEW] Pivot table with units:")
    print(pivot_df.to_string(index=False))


if __name__ == "__main__":
    merge_all_results()