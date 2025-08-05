from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import asyncio
import threading
import time
from datetime import datetime
import json
from main import get_sid, fetch_timetable, mark_attendance, check_and_mark_attendance
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global variables to track running sessions
active_sessions = {}
session_status = {}

class AttendanceSession:
    def __init__(self, email, password, student_id):
        self.email = email
        self.password = password
        self.student_id = student_id
        self.is_running = False
        self.thread = None
        self.last_activity = None
        self.attendance_log = []
        self.error_log = []

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run_attendance_checker)
            self.thread.daemon = True
            self.thread.start()

    def stop(self):
        self.is_running = False

    def _run_attendance_checker(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(self._attendance_checker())
        except Exception as e:
            self.error_log.append(f"Error: {str(e)}")
        finally:
            loop.close()

    async def _attendance_checker(self):
        sid = None
        student_data = None
        marked_attendance_ids = set()
        request_count = 0

        while self.is_running:
            try:
                # Get session ID if needed
                if sid is None:
                    sid, student_data = await get_sid(self.email, self.password)
                    if sid is None:
                        self.error_log.append("Failed to login. Check credentials.")
                        await asyncio.sleep(30)
                        continue

                request_count += 1
                current_date = datetime.now().strftime("%Y-%m-%d")
                
                # Fetch timetable
                timetable_data = await fetch_timetable(sid, student_data, current_date)
                
                if timetable_data and timetable_data.get("output", {}).get("data"):
                    days = timetable_data.get("output", {}).get("data", [])
                    
                    for day in days:
                        for period in day.get("Periods", []):
                            if ("attendanceId" in period and 
                                not period.get("isAttendanceSaved", False) and 
                                period["attendanceId"] not in marked_attendance_ids):
                                
                                attendance_id = period["attendanceId"]
                                subject_name = period.get("SubNa", "Unknown Subject")
                                faculty_name = period.get("StaffNm", "Unknown Faculty")
                                
                                # Mark attendance
                                success = await mark_attendance(sid, attendance_id, self.student_id)
                                
                                if success:
                                    log_entry = {
                                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                                        'subject': subject_name,
                                        'faculty': faculty_name,
                                        'status': 'SUCCESS'
                                    }
                                    self.attendance_log.append(log_entry)
                                    marked_attendance_ids.add(attendance_id)
                                else:
                                    log_entry = {
                                        'timestamp': datetime.now().strftime('%H:%M:%S'),
                                        'subject': subject_name,
                                        'faculty': faculty_name,
                                        'status': 'FAILED'
                                    }
                                    self.attendance_log.append(log_entry)

                self.last_activity = datetime.now().strftime('%H:%M:%S')
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                self.error_log.append(f"Error: {str(e)}")
                await asyncio.sleep(30)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_session', methods=['POST'])
def start_session():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    student_id = data.get('student_id', '')
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required'})
    
    # Create new session
    session_id = f"session_{int(time.time())}"
    attendance_session = AttendanceSession(email, password, student_id)
    active_sessions[session_id] = attendance_session
    
    # Start the attendance checker
    attendance_session.start()
    
    return jsonify({
        'success': True, 
        'session_id': session_id,
        'message': 'Attendance session started successfully'
    })

@app.route('/stop_session', methods=['POST'])
def stop_session():
    data = request.get_json()
    session_id = data.get('session_id')
    
    if session_id in active_sessions:
        active_sessions[session_id].stop()
        del active_sessions[session_id]
        return jsonify({'success': True, 'message': 'Session stopped successfully'})
    
    return jsonify({'success': False, 'message': 'Session not found'})

@app.route('/get_status')
def get_status():
    session_id = request.args.get('session_id')
    
    if session_id in active_sessions:
        session = active_sessions[session_id]
        return jsonify({
            'is_running': session.is_running,
            'last_activity': session.last_activity,
            'attendance_log': session.attendance_log[-10:],  # Last 10 entries
            'error_log': session.error_log[-5:]  # Last 5 errors
        })
    
    return jsonify({'error': 'Session not found'})

@app.route('/get_active_sessions')
def get_active_sessions():
    sessions = {}
    for session_id, session in active_sessions.items():
        sessions[session_id] = {
            'is_running': session.is_running,
            'last_activity': session.last_activity,
            'email': session.email
        }
    return jsonify(sessions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 