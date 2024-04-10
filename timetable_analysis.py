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
