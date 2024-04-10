from flask import Flask, render_template, request, jsonify
import pandas as pd
import json

app = Flask(__name__)

def transform_timetable_to_events(timetable_data):
    events = []
    for subject, details in timetable_data.items():
        for event_type, sessions in details.items():
            if event_type == "CP":  # Skip the CP entry
                continue
            for session in sessions:
                start, end = session  # Assuming each session is a list with [start, end] datetime strings
                event = {
                    "title": f"{subject} - {event_type}",
                    "start": start,
                    "end": end,
                }
                events.append(event)
    return events

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("Processing file upload...")
        # Handle the uploaded file
        if 'file' not in request.files:
            print("No file part in the request.")
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            print("No file selected.")
            return 'No selected file', 400
        if file:
            timetable_data = json.load(file)
            print("File uploaded successfully. Data:", timetable_data)
            events = transform_timetable_to_events(timetable_data)
            return jsonify(events)  # Directly return data for FullCalendar
    return render_template('calendar.html')

@app.route('/api/events')
def events():
    # Load and return events for FullCalendar
    events = load_events()
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
