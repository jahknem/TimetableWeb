from itertools import combinations
from datetime import datetime
import json
import argparse
import pandas as pd

# Function to check if two time ranges overlap
def is_overlap(time_range1, time_range2):
    return max(time_range1[0], time_range2[0]) < min(time_range1[1], time_range2[1])

def find_non_overlapping_combinations(class_times, max_subjects, preferred_days):
    non_overlapping_combinations = []
    # Ensure preferred_days are in the correct format (assuming they are provided as full day names)
    preferred_day_names = preferred_days  # Assuming preferred_days are already correct, adjust if necessary
    
    # Filter subjects by preferred days
    subjects_filtered_by_day = [
        subject for subject in class_times.keys() 
        if any(time[0].strftime('%A') in preferred_day_names for time in class_times[subject])
    ]
    
    # Find combinations
    for r in range(1, min(max_subjects, len(subjects_filtered_by_day)) + 1):
        for combo in combinations(subjects_filtered_by_day, r):
            combo_times = [class_times[subject] for subject in combo]
            overlap = False
            for i in range(len(combo_times)):
                for j in range(i + 1, len(combo_times)):
                    for time1 in combo_times[i]:
                        for time2 in combo_times[j]:
                            if is_overlap(time1, time2):
                                overlap = True
                                break
                        if overlap:
                            break
                    if overlap:
                        break
                if overlap:
                    break
            if not overlap:
                non_overlapping_combinations.append(combo)
    return non_overlapping_combinations


def load_timetable(path):
    with open(path, 'r') as file:
        return json.load(file)

def load_timetable_into_dataframe(path):
    # Load the JSON file into a DataFrame
    df = pd.read_json(path, orient='index').explode('sessions').reset_index().rename(columns={'index': 'subject'})
    # Convert start and end times to datetime
    df[['start_time', 'end_time']] = pd.DataFrame(df['sessions'].tolist(), index=df.index)
    return df

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

def main2():
    parser = argparse.ArgumentParser(description='Find non-overlapping university class schedules.')
    parser.add_argument('--timetable_path', type=str, required=True, help='Path to the timetable JSON file')
    parser.add_argument('--max_subjects', type=int, default=5, help='Maximum number of subjects to consider')
    parser.add_argument('--preferred_days', type=str, nargs='+', default=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'], help='Preferred days for university classes')
    
    args = parser.parse_args()

    # Load timetable from the specified JSON file
    timetable_iso8601 = load_timetable(args.timetable_path)

    # Convert session times to datetime objects for comparison
    flat_class_times_fixed = {}
    for subject, sessions in timetable_iso8601.items():
        all_sessions = []
        for key, value in sessions.items():
            if isinstance(value[0], str):  # Single session
                all_sessions.append((datetime.fromisoformat(value[0]), datetime.fromisoformat(value[1])))
            else:  # Multiple sessions
                for session in value:
                    all_sessions.append((datetime.fromisoformat(session[0]), datetime.fromisoformat(session[1])))
        flat_class_times_fixed[subject] = all_sessions

    # Finding non-overlapping combinations considering the preferred days and max subjects
    non_overlapping_combinations_fixed = find_non_overlapping_combinations(flat_class_times_fixed, args.max_subjects, args.preferred_days)

    # Outputting the results
    print(f"Total non-overlapping combinations: {len(non_overlapping_combinations_fixed)}")
    for combo in non_overlapping_combinations_fixed[:5]:
        print(combo)

def main(timetable_path, max_subjects, preferred_days):
    df = load_timetable_into_dataframe(timetable_path)
    filtered_df = filter_by_preferred_days(df, preferred_days)
    combinations = find_non_overlapping_combinations(filtered_df, max_subjects)
    print(f"Found {len(combinations)} non-overlapping combinations.")
    for combo in combinations:
        print(combo)

# if __name__ == '__main__':
#     main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate non-overlapping university schedules.")
    parser.add_argument("--timetable_path", type=str, required=True, help="Path to the timetable JSON file.")
    parser.add_argument("--max_subjects", type=int, default=5, help="Maximum number of subjects to consider.")
    parser.add_argument("--preferred_days", nargs="+", default=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], help="Preferred days for university.")
    args = parser.parse_args()
    
    main(args.timetable_path, args.max_subjects, args.preferred_days)