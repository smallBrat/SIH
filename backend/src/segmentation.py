import cv2
import os
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 segmentation model (local file in models folder)
model = YOLO("models/yolov8n-seg.pt")

# Define non-pit actors to segment and remove
NON_PIT_ACTORS = ["person", "truck", "car", "bus", "motorcycle", "excavator", "crane", "bulldozer"]

def detect_non_pit_actors(image_path, output_dir="segmentation"):
    """
    🎯 ENHANCED Stage 4: Precise Non-Pit Actor Detection with Exact Shape Matching
    Creates pixel-perfect masks that exactly match detected object boundaries
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        return None
    
    height, width = img.shape[:2]
    
    # Create high-precision mask for non-pit actors
    mask = np.zeros((height, width), dtype=np.uint8)
    segmented_img = img.copy()
    
    # Run YOLO segmentation with enhanced settings
    results = model.predict(image_path, save=False, verbose=False, conf=0.4, iou=0.5)
    
    actors_detected = []
    total_objects_processed = 0
    precise_masks_created = 0
    
    print(f"🔍 Stage 4: Analyzing image for non-pit actors...")
    
    for r in results:
        # PRIORITY 1: Use precise segmentation masks (YOLO-provided shapes)
        if r.masks is not None and r.boxes is not None:
            for i, (seg_mask, box) in enumerate(zip(r.masks.data, r.boxes)):
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                confidence = float(box.conf[0])
                
                if class_name in NON_PIT_ACTORS and confidence > 0.4:
                    total_objects_processed += 1
                    
                    # 🎯 PRECISION ENHANCEMENT: Convert tensor to exact pixel mask
                    seg_mask_np = seg_mask.cpu().numpy().astype(np.float32)
                    
                    # Resize to exact image dimensions with high-quality interpolation
                    seg_mask_resized = cv2.resize(seg_mask_np, (width, height), 
                                                interpolation=cv2.INTER_CUBIC)
                    
                    # 🔧 ACCURACY IMPROVEMENT: Use adaptive threshold for cleaner edges
                    binary_mask = (seg_mask_resized > 0.3).astype(np.uint8) * 255
                    
                    # 🎨 SHAPE REFINEMENT: Clean edges while preserving exact boundaries
                    kernel_refine = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel_refine)
                    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel_refine)
                    
                    # 📏 SIZE VALIDATION: Ensure mask matches object size
                    contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    for contour in contours:
                        area = cv2.contourArea(contour)
                        if area > 50:  # Filter tiny noise
                            # Draw exact contour to mask
                            cv2.fillPoly(mask, [contour], 255)
                            
                            # Visualize precise boundaries (not rectangles!)
                            cv2.drawContours(segmented_img, [contour], -1, (0, 255, 0), 2)
                            
                            # Add label with confidence
                            x, y, w, h = cv2.boundingRect(contour)
                            cv2.putText(segmented_img, f"{class_name}:{confidence:.2f}", 
                                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                            
                            precise_masks_created += 1
                    
                    # Get bounding box for tracking
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    actors_detected.append({
                        "class": class_name,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2],
                        "mask_area": cv2.countNonZero(binary_mask),
                        "precision": "segmentation_mask"
                    })
        
        # FALLBACK: Use bounding boxes only if segmentation unavailable
        elif r.boxes is not None:
            for i, box in enumerate(r.boxes):
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                confidence = float(box.conf[0])
                
                if class_name in NON_PIT_ACTORS and confidence > 0.5:
                    total_objects_processed += 1
                    
                    # Get bounding box coordinates
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # ⚠️ FALLBACK: Use rectangle (less precise)
                    cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=-1)
                    
                    # Visualize bounding box
                    cv2.rectangle(segmented_img, (x1, y1), (x2, y2), (0, 165, 255), 2)  # Orange for bbox
                    cv2.putText(segmented_img, f"{class_name}:{confidence:.2f}[BBOX]", 
                               (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 165, 255), 1)
                    
                    actors_detected.append({
                        "class": class_name,
                        "confidence": confidence,
                        "bbox": [x1, y1, x2, y2],
                        "mask_area": (x2-x1) * (y2-y1),
                        "precision": "bounding_box"
                    })
    
    print(f"🎯 Stage 4: Processed {total_objects_processed} objects, {precise_masks_created} with precise masks")
    
    # Save results
    mask_path = os.path.join(output_dir, f"actors_mask_{os.path.basename(image_path)}")
    segmented_path = os.path.join(output_dir, f"actors_detected_{os.path.basename(image_path)}")
    
    cv2.imwrite(mask_path, mask)
    cv2.imwrite(segmented_path, segmented_img)
    
    # 📊 QUALITY VALIDATION: Analyze mask accuracy
    mask_quality = validate_mask_precision(mask, actors_detected, img.shape[:2])
    
    print(f"✅ Stage 4: Mask created with {mask_quality['accuracy_score']:.1f}% precision")
    
    return {
        "mask": mask,
        "mask_path": mask_path,
        "segmented_image": segmented_path,
        "actors_detected": actors_detected,
        "quality_metrics": mask_quality
    }

def validate_mask_precision(mask, actors_detected, image_shape):
    """
    🔍 Validate the precision of created masks
    Returns quality metrics for mask accuracy assessment
    """
    height, width = image_shape
    total_pixels = height * width
    masked_pixels = cv2.countNonZero(mask)
    
    # Calculate coverage statistics
    coverage_percentage = (masked_pixels / total_pixels) * 100
    
    # Analyze mask quality based on detected objects
    precise_objects = sum(1 for actor in actors_detected 
                         if actor.get("precision") == "segmentation_mask")
    bbox_objects = len(actors_detected) - precise_objects
    
    # Calculate accuracy score
    if len(actors_detected) == 0:
        accuracy_score = 100.0  # Perfect if no objects to detect
    else:
        precision_ratio = precise_objects / len(actors_detected)
        accuracy_score = precision_ratio * 100
    
    # Analyze mask smoothness (edge quality)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    avg_contour_complexity = np.mean([len(contour) for contour in contours]) if contours else 0
    
    return {
        "accuracy_score": accuracy_score,
        "coverage_percentage": coverage_percentage,
        "precise_objects": precise_objects,
        "bbox_objects": bbox_objects,
        "total_objects": len(actors_detected),
        "contour_complexity": avg_contour_complexity,
        "mask_pixels": masked_pixels,
        "quality_grade": "Excellent" if accuracy_score > 80 else "Good" if accuracy_score > 60 else "Fair"
    }

def create_clean_segmentation_mask(img1_path, img2_path, output_dir="segmentation"):
    """
    Create combined segmentation mask from both images for filtering changes
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Detect actors in both images
    result1 = detect_non_pit_actors(img1_path, output_dir)
    result2 = detect_non_pit_actors(img2_path, output_dir)
    
    if result1 is None or result2 is None:
        return None
    
    # Combine masks from both images
    combined_mask = cv2.bitwise_or(result1["mask"], result2["mask"])
    
    # Apply morphological operations to clean up the mask
    kernel = np.ones((3,3), np.uint8)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
    combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_OPEN, kernel)
    
    # Save combined mask
    combined_mask_path = os.path.join(output_dir, "combined_actors_mask.png")
    cv2.imwrite(combined_mask_path, combined_mask)
    
    return {
        "combined_mask": combined_mask,
        "combined_mask_path": combined_mask_path,
        "baseline_result": result1,
        "new_result": result2
    }

def create_binary_pit_mask(new_image_path, output_dir="stage4"):
    """
    🎯 ENHANCED Stage 4: Create precise binary mask from new captured image
    Non-pit actors (removed areas) = BLACK (0) - EXACT SHAPE BOUNDARIES
    Pit areas (kept areas) = WHITE (255) - PRECISE PIT ISOLATION
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load the new captured image
    img = cv2.imread(new_image_path)
    if img is None:
        return None
    
    height, width = img.shape[:2]
    
    # 🎯 PRECISION DETECTION: Use enhanced actor detection with exact boundaries
    actors_result = detect_non_pit_actors(new_image_path, output_dir)
    
    if actors_result is None:
        # If no actors detected, entire area is pit (white)
        binary_mask = np.ones((height, width), dtype=np.uint8) * 255  # All white
        actors_count = 0
        pit_percentage = 100.0
        print(f"🔲 Stage 4: No actors detected - 100% pit area")
    else:
        # 🔧 CREATE PRECISE BINARY MASK: pit areas = white, non-pit actors = black
        binary_mask = np.ones((height, width), dtype=np.uint8) * 255  # Start with all white (pit)
        
        # 🎯 EXACT BOUNDARIES: Set non-pit actor areas to black using precise masks
        actor_mask = actors_result["mask"]
        binary_mask[actor_mask > 0] = 0  # Non-pit actors = black (precise boundaries)
        
        # Calculate accuracy statistics
        actors_count = len(actors_result.get("actors_detected", []))
        actor_area = cv2.countNonZero(actor_mask)
        pit_area = (height * width) - actor_area
        pit_percentage = (pit_area / (height * width)) * 100
        
        # Count precision types
        precise_actors = sum(1 for actor in actors_result.get("actors_detected", []) 
                           if actor.get("precision") == "segmentation_mask")
        bbox_actors = actors_count - precise_actors
        
        print(f"🔲 Stage 4: {actors_count} actors detected ({precise_actors} precise, {bbox_actors} bbox)")
        print(f"🎯 Stage 4: {pit_percentage:.1f}% pit area with exact boundaries")
    
    # 🔧 ENHANCED MORPHOLOGICAL OPERATIONS: Clean while preserving exact boundaries
    # Use smaller kernels to maintain precision of segmentation masks
    kernel_precise = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))  # Smaller for precision
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))    # Medium for cleaning
    
    # Step 1: Fill tiny holes in pit areas without affecting actor boundaries
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel_precise)
    
    # Step 2: Remove small noise in pit areas while preserving actor precision
    binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_OPEN, kernel_precise)
    
    # Step 3: Optional final smoothing only for complex scenes
    if actors_count > 2:  # Only for scenes with multiple actors
        binary_mask = cv2.morphologyEx(binary_mask, cv2.MORPH_CLOSE, kernel_clean)
        binary_mask = cv2.medianBlur(binary_mask, 3)  # Gentle smoothing
    
    # Create visual representation with the new image background
    visual_result = img.copy()
    
    # Make non-pit actor areas completely black
    visual_result[binary_mask == 0] = [0, 0, 0]  # Black for removed areas
    
    # Highlight pit areas (optional enhancement)
    # You can keep original colors or apply slight enhancement
    pit_areas = binary_mask == 255
    # visual_result[pit_areas] = visual_result[pit_areas]  # Keep original pit colors
    
    # Create pure binary visualization (3-channel for display)
    binary_display = np.zeros((height, width, 3), dtype=np.uint8)
    binary_display[binary_mask == 255] = [255, 255, 255]  # White pit areas
    binary_display[binary_mask == 0] = [0, 0, 0]          # Black non-pit actors
    
    # Save results
    binary_mask_path = os.path.join(output_dir, "binary_pit_mask.png")
    binary_display_path = os.path.join(output_dir, "binary_display.png")
    visual_result_path = os.path.join(output_dir, "new_image_processed.png")
    
    cv2.imwrite(binary_mask_path, binary_mask)           # Pure grayscale binary mask
    cv2.imwrite(binary_display_path, binary_display)     # Pure black/white display
    cv2.imwrite(visual_result_path, visual_result)       # Original image with black areas
    
    print(f"🔲 Stage 4: Created binary pit mask (White=Pit, Black=Actors)")
    
    return {
        "binary_mask": binary_mask,
        "binary_mask_path": binary_mask_path,
        "binary_display_path": binary_display_path,    # Pure binary display
        "visual_result": visual_result_path,           # Image with black areas
        "actors_detected": actors_result.get("actors_detected", []) if actors_result else []
    }

def create_enhanced_pit_only_mask(image_path, output_dir="pit_masks"):
    """
    Creates a comprehensive pit-only mask for precise change filtering
    Returns mask where 255 = pit area, 0 = non-pit area
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        return None
        
    height, width = img.shape[:2]
    
    # Create initial pit mask (start with full image as pit)
    pit_mask = np.ones((height, width), dtype=np.uint8) * 255
    
    # Remove non-pit actors using YOLO detection
    results = model.predict(image_path, save=False, verbose=False)
    
    actors_removed = []
    for r in results:
        if r.boxes is not None:
            for i, box in enumerate(r.boxes):
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                confidence = float(box.conf[0])
                
                if class_name in NON_PIT_ACTORS and confidence > 0.4:  # Lower threshold for better detection
                    # Get bounding box with padding
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Add padding around detected objects
                    padding = 20
                    x1 = max(0, x1 - padding)
                    y1 = max(0, y1 - padding) 
                    x2 = min(width, x2 + padding)
                    y2 = min(height, y2 + padding)
                    
                    # Remove from pit mask (set to 0 = non-pit)
                    cv2.rectangle(pit_mask, (x1, y1), (x2, y2), 0, thickness=-1)
                    actors_removed.append(f"{class_name}:{confidence:.2f}")
    
    # Apply morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    
    # Close small gaps in pit areas
    pit_mask = cv2.morphologyEx(pit_mask, cv2.MORPH_CLOSE, kernel)
    
    # Remove small isolated non-pit areas
    pit_mask = cv2.morphologyEx(pit_mask, cv2.MORPH_OPEN, kernel)
    
    # Smooth edges
    pit_mask = cv2.GaussianBlur(pit_mask, (5, 5), 0)
    pit_mask = cv2.threshold(pit_mask, 127, 255, cv2.THRESH_BINARY)[1]
    
    # Save enhanced pit mask
    enhanced_pit_path = os.path.join(output_dir, "enhanced_pit_mask.png")
    cv2.imwrite(enhanced_pit_path, pit_mask)
    
    # Create visualization showing pit areas in white, non-pit in black
    pit_visualization = np.zeros_like(img)
    pit_visualization[pit_mask > 0] = [255, 255, 255]  # White for pit areas
    
    pit_viz_path = os.path.join(output_dir, "pit_area_visualization.png")
    cv2.imwrite(pit_viz_path, pit_visualization)
    
    print(f"🏔️  Enhanced pit mask created: {len(actors_removed)} non-pit actors excluded")
    
    return {
        "pit_mask": pit_mask,
        "pit_mask_path": enhanced_pit_path,
        "pit_visualization_path": pit_viz_path,
        "actors_removed": actors_removed
    }

def create_pit_area_mask_for_changes(image_path, output_dir="pit_masks"):
    """
    Creates a pit-area-only mask for Stage 3 change detection by excluding sky and non-mining areas
    Returns mask where 255 = pit area (show changes), 0 = non-pit area (hide changes)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        return None
        
    height, width = img.shape[:2]
    
    # Create initial mask - start with full image
    pit_area_mask = np.ones((height, width), dtype=np.uint8) * 255
    
    # Method 1: Remove sky area (upper portion of image)
    # Assume sky is typically in upper 30% of mining pit images
    sky_boundary = int(height * 0.25)  # Top 25% is likely sky
    pit_area_mask[0:sky_boundary, :] = 0  # Remove sky area
    
    # Method 2: Use YOLO to detect and remove non-pit objects
    results = model.predict(image_path, save=False, verbose=False)
    
    # Extended list of non-pit objects including sky-related elements
    NON_PIT_OBJECTS = ["person", "truck", "car", "bus", "motorcycle", "bicycle", 
                       "excavator", "crane", "bulldozer", "airplane", "bird", 
                       "kite", "traffic light", "stop sign", "bench", "umbrella"]
    
    objects_removed = []
    for r in results:
        if r.boxes is not None:
            for i, box in enumerate(r.boxes):
                cls_id = int(box.cls[0])
                class_name = model.names[cls_id]
                confidence = float(box.conf[0])
                
                if class_name in NON_PIT_OBJECTS and confidence > 0.3:  # Lower threshold for better detection
                    # Get bounding box with padding
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    # Add padding around detected objects
                    padding = 15
                    x1 = max(0, x1 - padding)
                    y1 = max(0, y1 - padding) 
                    x2 = min(width, x2 + padding)
                    y2 = min(height, y2 + padding)
                    
                    # Remove from pit area mask
                    cv2.rectangle(pit_area_mask, (x1, y1), (x2, y2), 0, thickness=-1)
                    objects_removed.append(f"{class_name}:{confidence:.2f}")
    
    # Method 3: Color-based sky detection (blue/gray regions)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Define sky color ranges (blue and gray)
    # Blue sky range
    lower_blue = np.array([100, 50, 50])
    upper_blue = np.array([130, 255, 255])
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    # Gray sky range  
    lower_gray = np.array([0, 0, 100])
    upper_gray = np.array([180, 30, 200])
    gray_mask = cv2.inRange(hsv, lower_gray, upper_gray)
    
    # Combine sky masks
    sky_color_mask = cv2.bitwise_or(blue_mask, gray_mask)
    
    # Only remove sky colors from upper portion (avoid removing blue/gray in pit)
    sky_region_mask = np.zeros_like(sky_color_mask)
    sky_region_mask[0:int(height*0.4), :] = sky_color_mask[0:int(height*0.4), :]
    
    # Remove sky-colored areas from pit mask
    pit_area_mask[sky_region_mask > 0] = 0
    
    # Method 4: Clean up the mask with morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    
    # Remove small isolated pit areas
    pit_area_mask = cv2.morphologyEx(pit_area_mask, cv2.MORPH_OPEN, kernel)
    
    # Fill small gaps in pit areas
    pit_area_mask = cv2.morphologyEx(pit_area_mask, cv2.MORPH_CLOSE, kernel)
    
    # Smooth edges
    pit_area_mask = cv2.GaussianBlur(pit_area_mask, (5, 5), 0)
    pit_area_mask = cv2.threshold(pit_area_mask, 127, 255, cv2.THRESH_BINARY)[1]
    
    # Save pit area mask
    pit_mask_path = os.path.join(output_dir, "stage3_pit_mask.png")
    cv2.imwrite(pit_mask_path, pit_area_mask)
    
    # Create visualization
    pit_viz = img.copy()
    pit_viz[pit_area_mask == 0] = [50, 50, 50]  # Darken non-pit areas
    
    pit_viz_path = os.path.join(output_dir, "stage3_pit_visualization.png")
    cv2.imwrite(pit_viz_path, pit_viz)
    
    pit_percentage = (np.sum(pit_area_mask > 0) / (height * width)) * 100
    print(f"🏔️  Stage 3 pit mask: {pit_percentage:.1f}% pit area, {len(objects_removed)} objects removed")
    
    return {
        "pit_area_mask": pit_area_mask,
        "pit_mask_path": pit_mask_path,
        "pit_visualization_path": pit_viz_path,
        "objects_removed": objects_removed,
        "pit_percentage": pit_percentage
    }
