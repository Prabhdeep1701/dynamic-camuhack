import asyncio
import json
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import httpx
import traceback


async def get_sid(email: str, password: str):
    """Login to Bennett ERP and retrieve session ID"""
    login_url = "https://student.bennetterp.camu.in/login/validate"
    payload = {
        "dtype": "M",
        "Email": email,
        "pwd": password
    }
    
    print(f"[AUTH] Attempting login for {email}...")
    
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.post(login_url, json=payload)
            data = response.json()["output"]["data"]
            session_id = response.cookies.get("connect.sid")

            if "logindetails" in data:
                print(f"[AUTH] Login successful! Got session ID: {session_id[:10]}...")
                # Return both session ID and full response data
                return session_id, data
            else:
                print(f"[AUTH] Login failed for {email}")
                return None, None
    except Exception as e:
        print(f"[AUTH] Error during login: {e}")
        return None, None

async def mark_attendance(session_id: str, attendance_id: str, student_id: str):
    url = "https://student.bennetterp.camu.in/api/Attendance/record-online-attendance"
    headers = {
        "Cookie": f"connect.sid={session_id}",
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://student.bennetterp.camu.in",
        "Referer": "https://student.bennetterp.camu.in/v2/timetable",
    }
    payload = {
        "attendanceId": attendance_id,
        "isMeetingStarted": True,
        "StuID": student_id,
        "offQrCdEnbld": True
    }

    try:
        print(f"\n[SENDING] Marking attendance request for ID: {attendance_id}")
        print(f"[REQUEST] URL: {url}")
        print(f"[REQUEST] Payload: {json.dumps(payload, indent=2)}")
        
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            response = await client.post(url, headers=headers, json=payload)
            elapsed = time.time() - start_time
            
            print(f"[RESPONSE] Status Code: {response.status_code} (took {elapsed:.2f}s)")
            print(f"[RESPONSE] Text: {response.text}")
            
            data = response.json()
            print(f"[RESPONSE] JSON: {json.dumps(data, indent=2)}")
            
            if data.get("output", {}).get("data") is not None:
                code = data["output"]["data"]["code"]
                if code in ["SUCCESS", "ATTENDANCE_ALREADY_RECORDED"]:
                    return True
            return False
    except Exception as e:
        print(f"[ERROR] While marking for student {student_id}: {e}")
        return False

async def fetch_timetable(session_id, student_data, date):
    """Fetch timetable data for a specific date"""
    url = "https://student.bennetterp.camu.in/api/Timetable/get"
    
    if student_data is None:
        print("[ERROR] Student data is None, cannot fetch timetable")
        return None
    
    try:
        # Extract required data from login response
        login_details = student_data.get("logindetails", {})
        student_info = login_details.get("Student", [{}])[0]
        progression_data = student_data.get("progressionData", [{}])[0]

        # Build the dynamic payload
        payload = {
            "PrName": progression_data.get("PrName", ""),
            "SemID": progression_data.get("SemID", ""),
            "SemName": progression_data.get("SemName", ""),
            "AcYrNm": progression_data.get("AcYrNm", ""),
            "AcyrToDt": progression_data.get("AcyrToDt", ""),
            "AcyrFrDt": progression_data.get("AcyrFrDt", ""),
            "DeptCode": progression_data.get("DeptCode", ""),
            "DepName": progression_data.get("DepName", ""),
            "CrCode": progression_data.get("CrCode", ""),
            "CrName": progression_data.get("CrName", ""),
            "InName": progression_data.get("InName", ""),
            "CmProgID": progression_data.get("CmProgID", ""),
            "_id": progression_data.get("_id", ""),
            "stustatus": progression_data.get("stustatus", ""),
            "progstdt": progression_data.get("progstdt", ""),
            "StuID": student_info.get("StuID", ""),
            "semRstd": progression_data.get("semRstd", ""),
            "AcYr": progression_data.get("AcYr", ""),
            "DeptID": progression_data.get("DeptID", ""),
            "CrID": progression_data.get("CrID", ""),
            "PrID": progression_data.get("PrID", ""),
            "InId": progression_data.get("InId", ""),
            "OID": progression_data.get("OID", ""),
            "__v": progression_data.get("__v", 0),
            "StFl": progression_data.get("StFl", "A"),
            "MoAt": progression_data.get("MoAt", ""),
            "CrAt": progression_data.get("CrAt", ""),
            "isFE": progression_data.get("isFE", True),
            "BP": progression_data.get("BP", "N"),
            "lang_code": progression_data.get("lang_code", ""),
            "studStsNm": "Active",
            "studSts": "A",
            "FNa": student_info.get("FNa", ""),
            "LNa": student_info.get("LNa", ""),
            "AplnNum": student_info.get("AplnNum", ""),
            "CnEmail": login_details.get("Email", ""),
            "enableV2": True,
            "start": date,
            "end": date,
            "schdlTyp": "slctdSchdl",
            "isShowCancelledPeriod": True,
            "isFromTt": True
        }

        headers = {
            "Cookie": f"connect.sid={session_id}",
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://student.bennetterp.camu.in",
            "Referer": "https://student.bennetterp.camu.in/v2/timetable",
        }

        print(f"[INFO] Fetching timetable for date: {date}")
        print(f"[DEBUG] Timetable payload: {json.dumps(payload, indent=2)}")

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"[INFO] Timetable API response status: {response.status_code}")
                return data
            else:
                print(f"[ERROR] Timetable API returned status code: {response.status_code}")
                print(f"[ERROR] Response: {response.text}")
                return None
    except Exception as e:
        import traceback
        print(f"[ERROR] Error fetching timetable: {e}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return None

async def check_and_mark_attendance(sid, email, password, student_id):

    print("Starting attendance checker...")
    print(f"Time now: {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')}")
    print("Waiting for an active attendance session...")
    
    marked_attendance_ids = set() 
    request_count = 0
    last_sid_refresh = datetime.now()
    student_data = None

    if sid is None:
        print("[AUTH] No session ID provided. Obtaining one...")
        sid, student_data = await get_sid(email, password)
        if sid is None:
            print("[ERROR] Failed to get a session ID. Check your credentials.")
            return
    
    while True:
        try:

            if datetime.now() - last_sid_refresh > timedelta(minutes=30):
                print("[AUTH] Refreshing session ID...")
                new_sid, new_student_data = await get_sid(email, password)
                if new_sid:
                    sid = new_sid
                    student_data = new_student_data
                    last_sid_refresh = datetime.now()
                    print("[AUTH] Session refreshed successfully!")
                else:
                    print("[AUTH] Failed to refresh session, continuing with existing session")
            
            request_count += 1
            current_date = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d")
            
            print(f"\n[REQUEST #{request_count}] Checking for attendance at {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%H:%M:%S')}")
            
            start_time = time.time()
            timetable_data = await fetch_timetable(sid, student_data, current_date)
            elapsed = time.time() - start_time
            
            if elapsed > 1.0:
                print(f"[WARNING] Request took {elapsed:.2f}s which is longer than our 1s check interval")
            
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
                            time_slot = f"{period.get('FrTime', 'Unknown')} - {period.get('end', 'Unknown').split('T')[1].split('+')[0].split(':')[0]}:{period.get('end', 'Unknown').split('T')[1].split('+')[0].split(':')[1]}"
                            
                            print(f"\n[FOUND] ✨ Active attendance for {subject_name} ✨")
                            print(f"[INFO] Faculty: {faculty_name}")
                            print(f"[INFO] AttendanceID: {attendance_id}")
                            print(f"[INFO] Time: {time_slot}")
                            
                            success = await mark_attendance(sid, attendance_id, student_id)
                            
                            if success:
                                print(f"[SUCCESS] Attendance marked successfully for {subject_name} with {faculty_name}!")
                                marked_attendance_ids.add(attendance_id)
                            else:
                                print(f"[FAILURE] Failed to mark attendance for {subject_name}")
                
                for day in days:
                    for period in day.get("Periods", []):
                        if ("attendanceId" in period and 
                            period.get("isAttendanceSaved", False) and 
                            period["attendanceId"] not in marked_attendance_ids):
                            
                            attendance_id = period["attendanceId"]
                            subject_name = period.get("SubNa", "Unknown Subject")
                            faculty_name = period.get("StaffNm", "Unknown Faculty")
                            
                            print(f"\n[INFO] Attendance for {subject_name} with {faculty_name} was already submitted!")
                            marked_attendance_ids.add(attendance_id)

            request_time = time.time() - start_time
            wait_time = max(0, 1.0 - request_time) 
            
            if wait_time > 0:
                await asyncio.sleep(wait_time)
            
        except KeyboardInterrupt:
            print("\n[INFO] Stopping attendance checker...")
            break
        except Exception as e:
            print(f"[ERROR] Error during attendance check: {e}")
            await asyncio.sleep(1)

async def main():
    email = input("Enter email: ")
    password = input("Enter password: ")         
    
    await check_and_mark_attendance(None, email, password, None)

if __name__ == "__main__":
    print("🚀 Starting Bennett ERP Attendance Checker...")
    asyncio.run(main())