# 🚗 Smart Crash Detection & Emergency Assistance System

An AI-powered real-time system for detecting vehicle collisions using **YOLOv8** and a **Kinect Xbox 360 camera**. It identifies accidents, extracts key data (timestamp, license plate, speed, images, videos), and sends reports to a backend server. GPS location is handled via **ESP32** and data is visualized in a mobile app to support emergency response.

---

## 🛠️ Tech Stack

- YOLOv8 (Ultralytics)
- Python & OpenCV
- Kinect Xbox 360
- ESP32 for GPS tracking
- RESTful API (Flask / FastAPI)
- Linux environment
- Mobile App (Flutter or other)

---

## 🚀 Features

- Real-time accident detection using object detection
- Identifies the responsible vehicle and captures license plate
- Logs speed and timestamp at the moment of crash
- Sends emergency data (image, video, location) to a backend server
- ESP32 module streams GPS location continuously
- Integrated mobile app for emergency visualization

----

## 🔍 How It Works

The system follows a real-time crash detection and emergency reporting pipeline, structured as follows:

1. **Live Video Capture**  
   A Kinect Xbox 360 camera captures live video footage of the highway and streams it into the processing system.

2. **Object Detection with YOLOv8**  
   Each video frame is analyzed using YOLOv8 to detect vehicles and monitor their movements. The model identifies car positions, speeds, and potential collisions.

3. **Crash Detection Algorithm**  
   A custom logic monitors the relative speed and trajectory of vehicles. If a sudden stop, impact pattern, or overlapping bounding boxes is detected, a crash event is flagged.

4. **Responsible Vehicle Identification**  
   The system analyzes pre-collision motion data to determine which vehicle initiated the crash.

5. **Data Logging**  
   On crash detection, the system logs key data:
   - Crash timestamp  
   - Detected license plate number (if available)  
   - Speed of vehicles  
   - Image & short video of the accident scene  

6. **GPS Location Integration**  
   An ESP32 module, connected separately, continuously sends live GPS coordinates to the backend server.

7. **Data Transmission**  
   All collected crash data is sent in real-time to a Flask (or FastAPI) backend via REST API in JSON format.

8. **Mobile App Notification**  
   The mobile app receives and displays the crash alert, including:
   - Accident time  
   - Location on map  
   - Media (image/video)  
   - Car at fault  

This ensures immediate visibility and faster emergency response.
