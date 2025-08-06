# Deployment Guide for Bennett ERP Attendance Automation

## Issues Fixed

### 1. Favicon 404 Error
- ✅ Added `/favicon.ico` route handler
- ✅ Created `static/` folder with favicon.ico file
- ✅ Added proper favicon references in HTML template
- ✅ Added fallback handling if favicon file is missing

### 2. Multi-Device Access Issues
- ✅ Configured Flask to run on `0.0.0.0` (all interfaces)
- ✅ Added environment variable support for HOST and PORT
- ✅ Enabled threaded mode for better concurrent handling
- ✅ Added proper error handlers for 404/500 errors

## Running the Application

### Local Development
```bash
python app.py
```

### Production Deployment
```bash
# Set environment variables
export HOST=0.0.0.0
export PORT=5000
export DEBUG=False
export SECRET_KEY=your-secret-key-here

# Run the application
python app.py
```

### For External Device Access

1. **Find your machine's IP address:**
   ```bash
   # On macOS/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # On Windows
   ipconfig
   ```

2. **Make sure your firewall allows connections on port 5000**

3. **Access from other devices:**
   ```
   http://YOUR_IP_ADDRESS:5000
   ```

### Common Issues and Solutions

#### "Connection Refused" from Other Devices
- Check if your firewall is blocking port 5000
- Ensure the app is running on `0.0.0.0:5000` (not `127.0.0.1:5000`)
- Verify your network allows inter-device communication

#### Favicon Still Shows 404
- Clear your browser cache
- Try a hard refresh (Ctrl+F5 or Cmd+Shift+R)
- Check if the `static/favicon.ico` file exists

#### Session Issues
- Check if cookies are enabled in your browser
- For HTTPS deployments, set `HTTPS=true` environment variable

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Host interface to bind to |
| `PORT` | `5000` | Port number to run on |
| `DEBUG` | `False` | Enable debug mode |
| `SECRET_KEY` | `random` | Flask secret key for sessions |
| `HTTPS` | `False` | Enable HTTPS cookie settings |

## Network Configuration

### Router/Network Settings
If you're still having issues accessing from other devices:

1. Check if your devices are on the same network
2. Disable AP isolation if using WiFi
3. Check for corporate firewall restrictions
4. Try using the machine's hostname instead of IP

### Cloud Deployment
For cloud deployment (Railway, Heroku, etc.):
- The `PORT` environment variable will be automatically set
- Use `0.0.0.0` as the host (already configured)
- Set appropriate environment variables for production