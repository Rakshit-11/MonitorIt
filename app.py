from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Function to get logs from the database with filtering
def get_logs(date_filter=None, category_filter=None, search_query=None):
    conn = sqlite3.connect("activity_log.db")  # Ensure this matches your log database name
    c = conn.cursor()

    # Base SQL query
    query = "SELECT * FROM logs WHERE 1=1"
    params = []

    # Apply Date Filter
    if date_filter:
        query += " AND timestamp LIKE ?"
        params.append(date_filter + "%")  # Match the start of the timestamp (YYYY-MM-DD)

    # Apply Category Filter
    if category_filter:
        query += " AND event_type = ?"
        params.append(category_filter)

    # Apply Search Query (matches timestamp, event type, and details)
    if search_query:
        query += " AND (timestamp LIKE ? OR event_type LIKE ? OR details LIKE ?)"
        params.extend(["%" + search_query + "%"] * 3)

    query += " ORDER BY timestamp DESC LIMIT 1000"  # Limit the results

    c.execute(query, params)
    logs = c.fetchall()
    conn.close()
    return logs

@app.route('/')
def index():
    # Get filter values from the request parameters
    date_filter = request.args.get('date', '')
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '')

    # Fetch filtered logs
    logs = get_logs(date_filter, category_filter, search_query)
    
    return render_template('index.html', logs=logs)

if __name__ == '__main__':
    app.run(debug=True)
