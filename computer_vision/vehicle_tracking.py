import cv2
from ultralytics import YOLO

model = YOLO("yolo11l.pt")

class_list = model.names

video_source = "test_video.mp4"

line_y_red = 175

target_classes = [
    "car",
    "motorcycle",
    "bus",
    "truck",
    "auto",
    "rickshaw"
]

target_ids = [
    i for i, name in class_list.items()
    if name in target_classes
]

confidence_threshold = 0.5

cap = cv2.VideoCapture(video_source)

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        break

    results = model.track(
        frame,
        persist=True,
        classes=target_ids,
        conf=confidence_threshold
    )

    cv2.line(
        frame,
        (0, line_y_red),
        (frame.shape[1], line_y_red),
        (0, 0, 255),
        3
    )

    total_count = 0

    if results[0].boxes.id is not None:

        boxes = results[0].boxes.xyxy.cpu()
        track_ids = results[0].boxes.id.int().cpu().tolist()
        class_indices = results[0].boxes.cls.int().cpu().tolist()

        total_count = max(track_ids) if track_ids else 0

        for box, track_id, class_idx in zip(
            boxes,
            track_ids,
            class_indices
        ):

            x1, y1, x2, y2 = map(int, box)

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            class_name = class_list[class_idx]

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

    cv2.imshow(
        "YOLO Object Tracking & Counting",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
