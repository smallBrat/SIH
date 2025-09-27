import cv2
import numpy as np
import os

def preprocess_image(image_path, output_dir="preprocessed", size=(640, 480)):
    """
    Enhanced preprocessing: resize, noise reduction, contrast enhancement
    """
    os.makedirs(output_dir, exist_ok=True)

    # Load image (BGR by default in OpenCV)
    img = cv2.imread(image_path)

    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Resize to standard dimensions
    img = cv2.resize(img, size)

    # Noise reduction using bilateral filter
    img = cv2.bilateralFilter(img, 9, 75, 75)

    # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    lab[:,:,0] = clahe.apply(lab[:,:,0])
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # Gaussian blur for smoothing
    img = cv2.GaussianBlur(img, (3, 3), 0)

    # Save processed copy
    out_path = os.path.join(output_dir, os.path.basename(image_path))
    cv2.imwrite(out_path, img)

    return out_path

def ensure_same_size(img1_path, img2_path, output_dir="preprocessed"):
    """
    Ensure both images have exactly the same dimensions
    """
    os.makedirs(output_dir, exist_ok=True)
    
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    
    if img1 is None or img2 is None:
        raise FileNotFoundError("One or both images not found")
    
    # Get the minimum dimensions to avoid any cropping issues
    height = min(img1.shape[0], img2.shape[0])
    width = min(img1.shape[1], img2.shape[1])
    
    # Resize both images to the same size
    img1_resized = cv2.resize(img1, (width, height))
    img2_resized = cv2.resize(img2, (width, height))
    
    # Save resized images
    img1_out = os.path.join(output_dir, f"baseline_{os.path.basename(img1_path)}")
    img2_out = os.path.join(output_dir, f"new_{os.path.basename(img2_path)}")
    
    cv2.imwrite(img1_out, img1_resized)
    cv2.imwrite(img2_out, img2_resized)
    
    return img1_out, img2_out
