import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from timetable_analysis import load_timetable_into_dataframe, filter_by_preferred_days, find_non_overlapping_combinations
from calendar_view.core import data
from calendar_view.core.config import CalendarConfig
from calendar_view.calendar import Calendar
from calendar_view.core.event import Event
from calendar_view.core.style import EventStyles
import pandas as pd

def load_subjects_from_df(df):
    return df['subject'].unique().tolist()

def on_subject_select(event):
    selected = [listbox.get(i) for i in listbox.curselection()]
    print("Selected subjects:", selected)

def show_calendar():
    def on_date_select(event):
        # Get selected date
        selected_date = cal.selection_get()
        print(f"Selected Date: {selected_date}")
        # Filter df for selected subjects and date
        selected_subjects = [listbox.get(i) for i in listbox.curselection()]
        if not selected_subjects:
            print("No subjects selected.")
            return
        entries_for_day = df[df['subject'].isin(selected_subjects) & (df['start_time'].dt.date == selected_date)]
        print(entries_for_day)
        # Implement displaying entries logic

    # Calendar window
    cal_window = tk.Toplevel(root)
    cal_window.title("Calendar")
    cal = Calendar(cal_window, selectmode='day', year=2023, month=4, day=5)
    cal.pack(pady=20)
    cal.bind("<<CalendarSelected>>", on_date_select)

def update_combinations():
    # Update and display non-overlapping combinations based on GUI inputs
    pass  # Implement based on the selected subjects and other criteria

def show_week_calendar():
    # Define the window
    week_cal_window = tk.Toplevel(root)
    week_cal_window.title("Week View Calendar")

    # Days headers
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for i, day in enumerate(days):
        tk.Label(week_cal_window, text=day, width=10, borderwidth=2, relief='ridge').grid(row=0, column=i)

    # Hours for each day
    for hour in range(7, 22):  # Example: from 7:00 to 21:00
        for day in range(7):  # 7 days a week
            tk.Label(week_cal_window, text=f'{hour}:00', width=10, height=2, borderwidth=2, relief='ridge').grid(row=hour-6, column=day)

def setup_gui():
    root = tk.Tk()
    root.title("University Schedule Planner")

    # Subject selection listbox
    listbox = tk.Listbox(root, selectmode='multiple', exportselection=0)
    subjects = load_subjects_from_df(df)
    for subject in subjects:
        listbox.insert(tk.END, subject)
    listbox.bind('<<ListboxSelect>>', on_subject_select)
    listbox.pack(pady=15)

    # Button to show week calendar
    week_calendar_button = ttk.Button(root, text="Show Week Calendar", command=show_week_calendar)
    week_calendar_button.pack(pady=5)

    return root

if __name__ == "__main__":
    df = load_timetable_into_dataframe("./timetable.json")
    root = setup_gui()
    root.mainloop()