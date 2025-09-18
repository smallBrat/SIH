import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os
from datetime import datetime

def detect_change(img1_path, img2_path, output_dir="results", ssim_thresh=0.85, orb_thresh=50):
    os.makedirs(output_dir, exist_ok=True)

    # Read images
    img1 = cv2.imread(img1_path, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_path, cv2.IMREAD_COLOR)

    if img1 is None or img2 is None:
        print("Error: One or both images could not be read.")
        return None

    # Resize to same size
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Convert to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # --- SSIM ---
    score, diff = ssim(gray1, gray2, full=True)
    diff = (diff * 255).astype("uint8")

    # --- ORB Feature Matching ---
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2) if des1 is not None and des2 is not None else []
    matches = sorted(matches, key=lambda x: x.distance)
    orb_score = len(matches)

    # --- Decision ---
    alert = (score < ssim_thresh) or (orb_score < orb_thresh)

    # --- Save results ---
    diff_path = os.path.join(output_dir, f"diff_{os.path.basename(img2_path)}.png")
    cv2.imwrite(diff_path, diff)

    # --- Log results ---
    log_file = os.path.join(output_dir, "alerts.txt")
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now()}] {os.path.basename(img1_path)} vs {os.path.basename(img2_path)}\n")
        f.write(f"   SSIM: {score:.4f}, ORB Matches: {orb_score}, ALERT: {alert}\n\n")

    return {
        "ssim_score": score,
        "orb_score": orb_score,
        "alert": alert,
        "diff_image": diff_path
    }
