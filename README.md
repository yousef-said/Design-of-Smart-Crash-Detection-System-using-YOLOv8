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
