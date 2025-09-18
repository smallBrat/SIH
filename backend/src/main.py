from src.preprocessing import preprocess_image
from src.segmentation import segment_image
from src.change_detection import detect_change
from src.alert_system import log_alert, show_alert
import shutil
import os
from PIL import Image

# Ensure output directory exists
os.makedirs("outputs", exist_ok=True)

def run_pipeline():
    """
    Full pipeline for rockfall prediction:
    1. Preprocess images
    2. Segment relevant pit regions
    3. Detect changes
    4. Trigger alerts
    """

    # Paths (raw images)
    normal_img = "data/normal/img1_normal.png"
    rockfall_img = "data/rockfall/img2_rockfall.png"

    print("🔄 Starting pipeline...")

    # 1. Preprocess
    print("🖼️ Preprocessing images...")
    normal_prep_path = preprocess_image(normal_img)       # returns path
    rockfall_prep_path = preprocess_image(rockfall_img)   # returns path

    # 2. Segmentation
    print("✂️ Segmenting pit areas...")
    masked_normal_path_original = segment_image(normal_prep_path)    # returns path
    masked_rockfall_path_original = segment_image(rockfall_prep_path)  # returns path

    # Copy intermediate images for frontend
    masked_normal_path = "outputs/masked.png"
    masked_rockfall_path = "outputs/segmented.png"
    shutil.copy(masked_normal_path_original, masked_normal_path)
    shutil.copy(masked_rockfall_path_original, masked_rockfall_path)

    # 3. Change Detection
    print("📊 Detecting changes...")
    result = detect_change(masked_normal_path, masked_rockfall_path)  # pass paths

    # Copy or save diff image for frontend
    diff_image_path = "outputs/diff.png"
    if "diff_image" in result and os.path.exists(result["diff_image"]):
        shutil.copy(result["diff_image"], diff_image_path)
    else:
        # create blank placeholder if diff not returned
        size = Image.open(masked_normal_path).size
        Image.new("RGB", size, color=(255, 255, 255)).save(diff_image_path)

    # 4. Alert System
    print("🚨 Running alert system...")
    # Convert scores to primitive types for JSON
    json_result = {
        "ssim_score": float(result.get("ssim_score", 0)),
        "orb_score": float(result.get("orb_score", 0)),
        "alert": bool(result.get("alert", False)),
        "diff_image": diff_image_path
    }

    show_alert(json_result)
    log_alert(json_result)

    print("✅ Pipeline completed.")

    return json_result
