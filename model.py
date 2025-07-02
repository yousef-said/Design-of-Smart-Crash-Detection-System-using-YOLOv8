from ultralytics import YOLO
import cv2
import freenect
import requests
import time
import serial
import re
import os
import threading
from datetime import datetime
from collections import deque
from typing import Tuple
import logging

# Log settings
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Load the trained model
model = YOLO('/home/walid/Desktop/Weights4/best.pt')

# Static information
responsible = "g4yp25-2"
speed1 = 0.3
speed2 = 0.5
FPS = 10
FRAME_BUFFER = deque(maxlen=FPS * 3)  # 3 seconds before the accident
last_detection_time = 0
CRASH_COOLDOWN = 5  # Seconds between each crash report

# Function to read GPS from ESP32
def get_location_from_esp32(port='/dev/ttyUSB0', baudrate=115200):
    try:
        with serial.Serial(port, baudrate, timeout=2) as ser:
            lat = None
            lon = None
            while True:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line.startswith("Latitude:"):
                    lat = float(line.split(":")[1].strip())
                elif line.startswith("Longitude:"):
                    lon = float(line.split(":")[1].strip())
                if lat is not None and lon is not None:
                    return lat, lon, f"https://www.google.com/maps?q={lat},{lon}"
    except Exception as e:
        logger.error(f"Failed to read GPS from ESP32: {e}")
    
    # Default coordinates
    default_lat = 29.958681
    default_lon = 31.052607
    return default_lat, default_lon, f"https://www.google.com/maps?q={default_lat},{default_lon}"

# Function to get frame from Kinect
def get_kinect_frame():
    frame, _ = freenect.sync_get_video()
    if frame is not None:
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    return None

# Save video from buffer + post-accident
def save_buffered_video(buffer, post_duration_sec=2, filename="crash_video.mp4"):
    if not buffer:
        print("⚠️ Buffer is empty. Skipping video generation.")
        return None

    width = buffer[0].shape[1]
    height = buffer[0].shape[0]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(filename, fourcc, FPS, (width, height))

    for f in buffer:
        out.write(f)

    start_time = time.time()
    while time.time() - start_time < post_duration_sec:
        post_frame = get_kinect_frame()
        if post_frame is not None:
            out.write(post_frame)
        time.sleep(1 / FPS)

    out.release()
    return filename

# Send crash data in a separate thread
def send_crash_data_async(frame, car1, car2):
    def send_data():
        try:
            now = datetime.now()
            timestamp = now.strftime('%Y%m%d_%H%M%S')
            lat, lon, location = get_location_from_esp32()

            image_path = f"crash_{timestamp}.jpg"
            video_path = f"crash_{timestamp}.mp4"
            cv2.imwrite(image_path, frame)

            print("🎥 Generating buffered crash video...")
            video_path = save_buffered_video(FRAME_BUFFER, post_duration_sec=2, filename=video_path)
            if video_path is None:
                return

            avg_speed = (speed1 + speed2) / 2
            data = {
                'car_id': car1,
                'car_id2': car2,
                'link': location,
                'person_name': responsible,
                'speed': str(round(avg_speed, 2)),
                'timestamp': timestamp,
                'depth_info': "N/A",
                'confidence1': "1.0",
                'confidence2': "1.0"
            }

            print("📤 Sending data with video:", data)

            with open(image_path, 'rb') as img_file, open(video_path, 'rb') as vid_file:
                files = {
                    'image': ('crash_image.jpg', img_file, 'image/jpeg'),
                    'video': ('crash_video.mp4', vid_file, 'video/mp4')
                }
                response = requests.post(
                    "https://7stars.pythonanywhere.com/api/upload/",
                    data=data,
                    files=files,
                    timeout=30
                )
                print("✅ API response:", response.status_code, response.text)

        except Exception as e:
            print("❌ Error sending crash data:", e)

    threading.Thread(target=send_data, daemon=True).start()

# Main loop
while True:
    frame = get_kinect_frame()
    if frame is None:
        continue

    FRAME_BUFFER.append(frame.copy())

    results = model(frame)
    annotated = results[0].plot()
    labels = results[0].names
    boxes = results[0].boxes

    detected_classes = []
    for box in boxes:
        cls_id = int(box.cls[0])
        class_name = labels[cls_id]
        detected_classes.append(class_name)

    print("📦 Detected:", detected_classes)

    car_ids = [cls for cls in detected_classes if cls.lower().startswith("g4yp")]
    accident_detected = any(cls.lower() == "accident" for cls in detected_classes)

    current_time = time.time()
    if accident_detected and len(car_ids) >= 2 and current_time - last_detection_time > CRASH_COOLDOWN:
        print("🚨 Accident detected between:", car_ids[:2])
        last_detection_time = current_time
        send_crash_data_async(frame, car_ids[0], car_ids[1])
        time.sleep(3)

    cv2.imshow("YOLOv8s Kinect Detection", annotated)
    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()