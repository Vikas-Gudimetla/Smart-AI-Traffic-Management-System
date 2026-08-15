from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import cv2
import base64
import threading
import time
from ultralytics import YOLO
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "development-key")
socketio = SocketIO(app, cors_allowed_origins="*")

model = None
camera_active = False

traffic_data = {
    "total_count": 0,
    "vehicle_types": {
        "car": 0,
        "motorcycle": 0,
        "bus": 0,
        "truck": 0,
        "auto": 0,
        "rickshaw": 0
    },
    "signal_status": "GREEN",
    "congestion_level": "LOW",
    "timestamp": datetime.now().isoformat()
}


class TrafficMonitor:
    def __init__(self, video_source="test_video.mp4"):
        self.video_source = video_source

        global model

        if model is None:
            try:
                model = YOLO("yolo11l.pt")
                print("YOLO model loaded successfully")
            except Exception as e:
                print(f"Error loading YOLO model: {e}")
                model = None

        self.model = model

        self.target_classes = [
            "car",
            "motorcycle",
            "bus",
            "truck",
            "auto",
            "rickshaw"
        ]

        if self.model:
            self.target_ids = [
                i for i, name in self.model.names.items()
                if name in self.target_classes
            ]
        else:
            self.target_ids = []

        self.line_y_red = 175
        self.confidence_threshold = 0.5

    def process_frame(self, frame):
        empty_counts = {
            "car": 0,
            "motorcycle": 0,
            "bus": 0,
            "truck": 0,
            "auto": 0,
            "rickshaw": 0
        }

        if self.model is None:
            return frame, 0, empty_counts

        try:
            results = self.model.track(
                frame,
                persist=True,
                classes=self.target_ids,
                conf=self.confidence_threshold
            )

            cv2.line(
                frame,
                (0, self.line_y_red),
                (frame.shape[1], self.line_y_red),
                (0, 0, 255),
                3
            )

            total_count = 0
            vehicle_counts = empty_counts.copy()

            if results[0].boxes.id is not None:
                boxes = results[0].boxes.xyxy.cpu()
                track_ids = results[0].boxes.id.int().cpu().tolist()
                class_indices = results[0].boxes.cls.int().cpu().tolist()

                total_count = max(track_ids) if track_ids else 0

                for box, track_id, class_idx in zip(
                    boxes, track_ids, class_indices
                ):
                    x1, y1, x2, y2 = map(int, box)

                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    class_name = self.model.names[class_idx]

                    if class_name in vehicle_counts:
                        vehicle_counts[class_name] += 1

                    cv2.rectangle(
                        frame,
                        (x1, y1),
                        (x2, y2),
                        (0, 255, 0),
                        2
                    )

                    cv2.circle(
                        frame,
                        (cx, cy),
                        4,
                        (0, 0, 255),
                        -1
                    )

                    cv2.putText(
                        frame,
                        f"ID:{track_id} {class_name}",
                        (x1, max(y1 - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 0),
                        1,
                        cv2.LINE_AA
                    )

            cv2.putText(
                frame,
                f"Total Count: {total_count}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            return frame, total_count, vehicle_counts

        except Exception as e:
            print(f"Error processing frame: {e}")
            return frame, 0, empty_counts


def video_stream():
    global camera_active, traffic_data

    monitor = TrafficMonitor()

    cap = cv2.VideoCapture(monitor.video_source)

    if not cap.isOpened():
        print(f"Could not open video: {monitor.video_source}")

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Could not open webcam")
            camera_active = False
            return

    print("Video stream started")

    while camera_active and cap.isOpened():

        ret, frame = cap.read()

        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        processed_frame, total_count, vehicle_counts = \
            monitor.process_frame(frame)

        traffic_data.update({
            "total_count": total_count,
            "vehicle_types": vehicle_counts,
            "congestion_level":
                "HIGH" if total_count > 30
                else "MEDIUM" if total_count > 15
                else "LOW",
            "timestamp": datetime.now().isoformat()
        })

        try:
            _, buffer = cv2.imencode(
                ".jpg",
                processed_frame,
                [cv2.IMWRITE_JPEG_QUALITY, 70]
            )

            frame_data = base64.b64encode(buffer).decode("utf-8")

            socketio.emit(
                "video_frame",
                {"image": frame_data}
            )

            socketio.emit(
                "traffic_update",
                traffic_data
            )

        except Exception as e:
            print(f"Error encoding frame: {e}")

        time.sleep(0.1)

    cap.release()
    print("Video stream stopped")


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/traffic-data")
def get_traffic_data():
    return jsonify(traffic_data)


@app.route("/api/start-monitoring", methods=["POST"])
def start_monitoring():
    global camera_active

    if not camera_active:
        camera_active = True

        threading.Thread(
            target=video_stream,
            daemon=True
        ).start()

        return jsonify({
            "status": "started",
            "message": "Traffic monitoring started"
        })

    return jsonify({
        "status": "already running",
        "message": "Traffic monitoring already active"
    })


@app.route("/api/stop-monitoring", methods=["POST"])
def stop_monitoring():
    global camera_active

    camera_active = False

    return jsonify({
        "status": "stopped",
        "message": "Traffic monitoring stopped"
    })


@socketio.on("connect")
def handle_connect():
    print("Client connected")

    emit(
        "connection_response",
        {"data": "Connected to traffic monitoring system"}
    )


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


if __name__ == "__main__":
    print("Starting Smart Traffic Management System...")
    print("Dashboard: http://localhost:5000")

    socketio.run(
        app,
        debug=False,
        host="0.0.0.0",
        port=5000
    )
