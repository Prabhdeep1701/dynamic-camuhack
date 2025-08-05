# Bennett ERP Attendance Automation - Web Interface

A Flask-based web interface for the Bennett ERP attendance automation system. This provides a user-friendly way to manage attendance automation sessions through a modern web interface.

## Features

- **Web-based Interface**: Modern, responsive web interface built with Bootstrap 5
- **Real-time Monitoring**: Live status updates and attendance logs
- **Session Management**: Start/stop attendance automation sessions
- **Multi-session Support**: Run multiple sessions simultaneously
- **Error Logging**: Comprehensive error tracking and display
- **Beautiful UI**: Modern gradient design with smooth animations

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python app.py
   ```

3. **Access the Web Interface**:
   Open your browser and go to `http://localhost:5000`

## Usage

### Starting a Session

1. Enter your Bennett ERP credentials:
   - **Email**: Your Bennett ERP email address
   - **Password**: Your Bennett ERP password
   - **Student ID** (Optional): Your student ID if needed

2. Click "Start Session" to begin the attendance automation

### Monitoring Sessions

- **Session Status**: Real-time status indicator showing if the session is running
- **Last Activity**: Timestamp of the last activity performed
- **Attendance Log**: Live feed of attendance marking attempts and results
- **Error Log**: Any errors encountered during the session

### Stopping Sessions

- Click "Stop Session" to halt the attendance automation
- The session will be completely terminated and removed from active sessions

## File Structure

```
├── app.py              # Flask application (main web interface)
├── main.py             # Original attendance automation backend
├── templates/
│   └── index.html      # Web interface template
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## API Endpoints

- `GET /` - Main web interface
- `POST /start_session` - Start a new attendance session
- `POST /stop_session` - Stop an active session
- `GET /get_status` - Get status of a specific session
- `GET /get_active_sessions` - Get all active sessions

## Security Notes

- Credentials are stored in memory only during active sessions
- No persistent storage of login credentials
- Sessions are automatically cleaned up when stopped
- Use HTTPS in production environments

## Troubleshooting

### Common Issues

1. **Login Failed**: Verify your Bennett ERP credentials
2. **Session Not Starting**: Check if the Bennett ERP service is accessible
3. **No Attendance Found**: Ensure you have scheduled classes for the current date

### Error Messages

- **"Failed to login"**: Invalid credentials or network issues
- **"Session not found"**: Session was stopped or expired
- **"Error during attendance check"**: Network or API issues

## Development

The application consists of:

- **Backend (`main.py`)**: Original attendance automation logic
- **Flask Wrapper (`app.py`)**: Web interface that wraps the backend
- **Frontend (`templates/index.html`)**: Modern web interface

The Flask wrapper creates a `AttendanceSession` class that manages the async attendance checking in separate threads, providing a clean interface between the web frontend and the original backend code.

## License

This project is for educational purposes. Please ensure compliance with your institution's policies regarding automated attendance systems. 