from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def fetch_attendance_data(usn, dob):
    base_url = "https://upylba53h2.execute-api.us-east-1.amazonaws.com/sis" 
    
    student_url = f"{base_url}?usn={usn}&dob={dob}"

    try:
        response = requests.get(student_url)
    except requests.exceptions.RequestException as e: 
        print(f"Error calling API: {e}")
        return None

    if response.status_code != 200:
        print(f"Error from API, status code: {response.status_code}")
        return None
        
    data = response.json()
    
    attendance_data = data.get("attendance", [])
    return attendance_data

def calculate_and_display_data(attendance_data):

    if not attendance_data:
        return None

    calculated_data = []

    for subject_data in attendance_data:
        code = subject_data.get("code", "")
        name = subject_data.get("name", "")
        
        present = int(subject_data.get("present", 0))
        absent = int(subject_data.get("absent", 0)) 
        remaining = int(subject_data.get("remaining", 0))


        if total==remaining:
            percent=100
        else:
            total = present + absent + remaining
        
        percent = present / (total - remaining) * 100

        bunk_75 = int(0.25 * total) - absent  
        bunk_80 = int(0.20 * total) - absent

        if percent < 75:
           row_color = "#ffcccc" 
        elif percent < 80:
           row_color = "#ffffcc" 
        else:
           row_color = ""

        if bunk_75 < 0:
            bunk_75 = "Attendance too low"
        
        if bunk_80 < 0:
            bunk_80 = "Attendance low"

        result = {
            'code': code,
            'name': name, 
            'present': str(present),
            'absent': str(absent),
            'remaining': str(remaining),
            'percent': int(percent),
            'bunk_75': bunk_75,  
            'bunk_80': bunk_80,
            'row_color': row_color
        }

        calculated_data.append(result)

    return calculated_data

@app.route('/')
def index():
    return render_template('index.html', calculated_data=None, error=None)

@app.route('/fetch_attendance', methods=['POST'])
def fetch_attendance():
    data = request.get_json()
    usn = data['usn']
    dob = data['dob']

    attendance_data = fetch_attendance_data(usn, dob)

    if attendance_data:
        calculated_data = calculate_and_display_data(attendance_data) 
        return jsonify(calculated_data) 
    else:
        return jsonify({"error": "Error fetching data"}), 400
    
