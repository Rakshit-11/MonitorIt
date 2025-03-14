﻿
# **Lab Monitoring System**  

## **Overview**  
The **Lab Monitoring System** is a real-time monitoring tool designed for computer labs. It enables administrators to track user activity across multiple lab computers, ensuring proper resource utilization and preventing unauthorized usage.  

## **Features**  
✅ **Real-time Monitoring** – View system activity in real time  
✅ **Activity Logging** – Stores logs of user activities for later review  
✅ **Admin Dashboard** – Secure web interface for monitoring  
✅ **Lightweight & Efficient** – Runs in the background with minimal system impact  

## **Tech Stack**  
- **Backend:** Python (Flask)  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** SQLite  
- **System Monitoring:** Python scripts running on lab computers  

---

## **Installation & Setup**  

### **1. Clone the Repository**  
```sh
git clone https://github.com/yourusername/lab-monitoring-system.git
cd lab-monitoring-system
```

### **2. Create a Virtual Environment (Recommended)**  
```sh
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### **3. Install Dependencies**  
```sh
pip install -r requirements.txt
```

### **4. Initialize the Database**  
```sh
python init_db.py
```

### **5. Run the Application**  
```sh
python app.py
```
The application will start on **http://127.0.0.1:5000/**  

---

## **Usage**  

### **Admin Panel**  
- Navigate to **http://127.0.0.1:5000/admin** to access the dashboard  
- Monitor active user sessions and review past logs  

### **Client System Monitoring**  
- A Python script runs on lab computers to log user activities  
- Logs are sent to the Flask backend and stored in SQLite  

---

## **Future Enhancements**  
🚀 **Remote Control** – Allow admins to restrict/block certain activities  
📊 **Detailed Analytics** – Generate reports on system usage  
🌐 **Multi-Lab Support** – Expand monitoring across multiple labs  

---

## **Screenshots**  
(Include relevant screenshots of the admin panel and monitoring system here.)  

---

## **Contributors**  
👤 **Rakshit Shetty** – Developer  

---

## **License**  
This project is open-source under the [MIT License](LICENSE).  

