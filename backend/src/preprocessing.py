import cv2
import os

def preprocess_image(image_path, output_dir="preprocessed", size=(640, 480)):
    os.makedirs(output_dir, exist_ok=True)

    # Load image (BGR by default in OpenCV)
    img = cv2.imread(image_path)

    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Resize
    img = cv2.resize(img, size)

    # Convert BGR → RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Save processed copy (for reference/demo)
    out_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(out_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    return out_path
