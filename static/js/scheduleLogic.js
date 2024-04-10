var globalEventData = []; // Global variable to store the event data

function saveSelectedSubjects() {
    let selectedSubjects = Array.from(document.querySelectorAll('#subjectSelector input[type="checkbox"]:checked')).map(input => input.value);
    localStorage.setItem('selectedSubjects', JSON.stringify(selectedSubjects));
}

function populateSubjects(data) {
    let uniqueSubjects = new Set(data.map(event => event.title));
    let savedSelectedSubjects = JSON.parse(localStorage.getItem('selectedSubjects') || '[]');
    $('#subjectSelector').empty(); // Clear existing subjects
    uniqueSubjects.forEach(subject => {
        let isChecked = savedSelectedSubjects.includes(subject);
        $('#subjectSelector').append(
            `<label><input type="checkbox" name="subject" value="${subject}" ${isChecked ? 'checked' : ''} onchange="updateCalendarWithSelectedSubjects(); saveSelectedSubjects();">${subject}</label><br>`
        );
    });
}

function initCalendar(events, defaultDate) {
    console.log("Initializing calendar with defaultDate:", defaultDate);
    console.log("Events:", events);
    $('#calendar').fullCalendar({
        defaultView: 'agendaWeek',
        defaultDate: defaultDate,
        events: events,
        minTime: "08:00:00",
        maxTime: "20:00:00",
        height: 'parent',
        header: { // You can adjust the header as needed
            left: 'title',
            center: '',
            right: 'agendaDay agendaWeek month'
        },
        allDaySlot: false,
    });
}

function updateCalendarWithSelectedSubjects() {
    let selectedSubjects = Array.from(document.querySelectorAll('#subjectSelector input[type="checkbox"]:checked')).map(input => input.value);
    let filteredEvents = globalEventData.filter(event => selectedSubjects.includes(event.title));
    $('#calendar').fullCalendar('destroy'); // Clear the old calendar
    var defaultDate = filteredEvents.length ? filteredEvents[0].start : moment().format(); // Use the start date of the first filtered event as default
    initCalendar(filteredEvents, defaultDate); // Re-initialize the calendar with filtered data
}

$(document).ready(function() {
    if (localStorage.getItem('timetableData')) {
        globalEventData = JSON.parse(localStorage.getItem('timetableData'));
        // Populate subject selector and initialize calendar
        populateSubjects(globalEventData);
        updateCalendarWithSelectedSubjects();
    }    
    $('#uploadForm').submit(function(e) {
        e.preventDefault();
        var formData = new FormData(this);
        $.ajax({
            url: '/',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(data) {
                console.log("Upload successful. Data received:", data);
                globalEventData = data; // Store the uploaded data globally
                localStorage.setItem('timetableData', JSON.stringify(data));

                let uniqueSubjects = new Set(data.map(event => event.title));
                $('#subjectSelector').empty(); // Clear existing subjects
                uniqueSubjects.forEach(subject => {
                    $('#subjectSelector').append(`<label><input type="checkbox" name="subject" value="${subject}" onchange="updateCalendarWithSelectedSubjects()">${subject}</label><br>`);
                });

                updateCalendarWithSelectedSubjects(); // Initial calendar update with all events
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error("Upload failed:", textStatus, errorThrown);
            }
        });
    });
    // Trigger updates and save to local storage when subjects are selected or deselected
    $('#subjectSelector').on('change', 'input[type="checkbox"]', function() {
        updateCalendarWithSelectedSubjects();
        saveSelectedSubjects();
    });
    function populateSubjects(data) {
        let uniqueSubjects = new Set(data.map(event => event.title));
        $('#subjectSelector').empty(); // Clear existing subjects
        uniqueSubjects.forEach(subject => {
            $('#subjectSelector').append(`<label><input type="checkbox" name="subject" value="${subject}" onchange="updateCalendarWithSelectedSubjects()">${subject}</label><br>`);
        });
    }
});