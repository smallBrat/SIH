import cv2
import os
from ultralytics import YOLO

# Load YOLOv8 segmentation model (local file in models folder)
model = YOLO("models/yolov8n-seg.pt")

# Define which classes to REMOVE (non-pit objects)
REMOVE_CLASSES = ["person", "truck", "car", "bus"]  # adjust as needed

def segment_image(image_path, output_dir="masked"):
    os.makedirs(output_dir, exist_ok=True)

    # Run YOLOv8 segmentation
    results = model.predict(image_path, save=False, verbose=False)

    img = cv2.imread(image_path)

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]

            if class_name in REMOVE_CLASSES:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 0), thickness=-1)

    out_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(out_path, img)
    return out_path
