import pandas as pd
import argparse
from itertools import combinations
import json

import tkinter as tk
from tkinter import ttk
# If tkcalendar is not installed, you need to install it via pip
# pip install tkcalendar
from tkcalendar import Calendar

def load_timetable_into_dataframe(path):
    # Load the JSON file
    with open(path, 'r') as file:
        data = json.load(file)
    
    # Prepare data for DataFrame creation
    rows = []
    for subject, info in data.items():
        cp = info.get("CP", 0)  # Default CP to 0 if not present
        for activity_type, sessions in info.items():
            if activity_type == "CP":  # Skip the CP field for session handling
                continue
            for session in sessions:
                rows.append({
                    'subject': subject,
                    'activity_type': activity_type,
                    'start_time': pd.to_datetime(session[0]),
                    'end_time': pd.to_datetime(session[1]),
                    'CP': cp
                })
    
    # Create DataFrame
    df = pd.DataFrame(rows)
    return df

# def filter_by_cp(df, min_cp=None, max_cp=None):
#     if min_cp is not None:
#         df = df[df['CP'] >= min_cp]
#     if max_cp is not None:
#         df = df[df['CP'] <= max_cp]
#     return df

def filter_by_preferred_days(df, preferred_days):
    # Filter sessions by preferred days
    return df[df['start_time'].dt.day_name().isin(preferred_days)]

def find_non_overlapping_combinations(df, max_subjects):
    subjects = df['subject'].unique()
    non_overlapping_combinations = []
    for r in range(1, min(max_subjects, len(subjects)) + 1):
        for combo in combinations(subjects, r):
            combo_df = df[df['subject'].isin(combo)]
            # Check for overlaps within the combination
            overlaps = any(
                combo_df.iloc[i]['end_time'] > combo_df.iloc[j]['start_time']
                for i in range(len(combo_df))
                for j in range(i + 1, len(combo_df))
                if combo_df.iloc[i]['subject'] != combo_df.iloc[j]['subject']
            )
            if not overlaps:
                non_overlapping_combinations.append(combo)
    return non_overlapping_combinations

def is_overlap(session1, session2):
    return session1['end_time'] > session2['start_time'] and session1['start_time'] < session2['end_time']

def find_non_overlapping_combinations(df, min_subjects=0, max_subjects=None):
    subjects = df['subject'].unique()
    valid_combinations = []

    if max_subjects is None:
        max_subjects = len(subjects)

    min_count = max(min_subjects, 1)  # At least 1 subject
    max_count = min(max_subjects, len(subjects))

    for r in range(min_count, max_count + 1):
        for combo in combinations(subjects, r):
            combo_df = df[df['subject'].isin(combo)].sort_values(by='start_time')
            
            # Check for overlaps within the combination
            overlaps = any(
                is_overlap(combo_df.iloc[i], combo_df.iloc[j])
                for i in range(len(combo_df) - 1)
                for j in range(i + 1, len(combo_df))
            )
            
            if not overlaps:
                valid_combinations.append(combo)
    
    return valid_combinations


def load_subjects_from_df(df):
    # Assuming 'subject' is a column in your DataFrame
    return df['subject'].unique().tolist()

def on_select(event):
    # Example function to handle selection
    selected = [listbox.get(i) for i in listbox.curselection()]
    print("Selected subjects:", selected)

def main(timetable_path, fixed_amount_of_subjects, preferred_days):
    df = load_timetable_into_dataframe(timetable_path)
    filtered_df = filter_by_preferred_days(df, preferred_days)
    # filtered_df = filter_by_cp(filtered_df, min_cp, max_cp)
    combinations = list(find_fixed_amount_of_subject_combinations(filtered_df, fixed_amount_of_subjects))
    
    print(f"Found {len(combinations)} combinations with exactly {fixed_amount_of_subjects} subjects.")
    for combo in combinations[:5]:  # Example: Print first 5 combinations
        print(combo)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate non-overlapping university schedules.")
    parser.add_argument("--timetable_path", type=str, required=True, help="Path to the timetable JSON file.")
    parser.add_argument("--max_subjects", type=int, default=5, help="Maximum number of subjects to consider.")
    parser.add_argument("--preferred_days", nargs="+", default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], help="Preferred days for university.")
    # parser.add_argument("--min_cp", type=int, help="Minimum amount of credit points.")
    # parser.add_argument("--max_cp", type=int, help="Maximum amount of credit points.")

    args = parser.parse_args()
    
    main(args.timetable_path, args.max_subjects, args.preferred_days)
