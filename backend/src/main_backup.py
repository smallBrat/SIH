from src.preprocessing import preprocess_image, ensure_same_size
from src.segmentation import detect_non_pit_actors, create_clean_segmentation_mask, create_binary_pit_mask, create_enhanced_pit_only_mask, create_pit_area_mask_for_changes
from src.change_detection import (detect_changes_with_dilation, remove_segmented_from_changes, 
                                create_color_coded_superposition, analyze_changes, filter_changes_to_pit_only)
from src.alert_system import log_alert, show_alert
import shutil
import os
import cv2
from PIL import Image

# Ensure output directories exist
os.makedirs("outputs", exist_ok=True)
os.makedirs("outputs/stage1", exist_ok=True)
os.makedirs("outputs/stage2", exist_ok=True)  
os.makedirs("outputs/stage3", exist_ok=True)
os.makedirs("outputs/stage4", exist_ok=True)
os.makedirs("outputs/stage5", exist_ok=True)

def run_pipeline():
    """
    5-Stage Rockfall Detection Pipeline:
    1. Baseline Image (enhanced preprocessing)
    2. New Captured Image (enhanced preprocessing) 
    3. Changes Detected Image (subtraction + dilation)
    4. Non-Pit Actor Removal (segmentation + filtering)
    5. Visualization Phase (color-coded superposition)
    """

    # Raw image paths
    baseline_img_raw = "data/normal/img1_normal.png"
    new_img_raw = "data/rockfall/img1_rockfall.png"

    print("🔄 Starting 5-Stage Pipeline...")

    # STAGE 1 & 2: Enhanced Preprocessing for Both Images
    print("📸 Stage 1 & 2: Processing baseline and new images...")
    
    # Enhanced preprocessing
    baseline_processed = preprocess_image(baseline_img_raw, "outputs/stage1")
    new_processed = preprocess_image(new_img_raw, "outputs/stage2")
    
    # Ensure same dimensions
    baseline_final, new_final = ensure_same_size(baseline_processed, new_processed, "outputs")
    
    # Copy for frontend display
    baseline_display = "outputs/stage1_baseline.png"
    new_display = "outputs/stage2_new.png"
    shutil.copy(baseline_final, baseline_display)
    shutil.copy(new_final, new_display)

    # STAGE 3: Pit-Only Thermal Change Detection (Sky and Non-Mining Areas Excluded)
    print("🏔️  Stage 3: Creating pit-area mask to exclude sky and non-mining regions...")
    
    # Create pit area mask for change detection filtering
    pit_area_result = create_pit_area_mask_for_changes(new_final, "outputs/stage3")
    pit_area_mask = pit_area_result["pit_area_mask"] if pit_area_result else None
    
    print("🔥 Stage 3: Enhanced thermal change detection - PIT AREAS ONLY...")
    changes_result = detect_changes_with_dilation(baseline_final, new_final, "outputs/stage3", pit_area_mask)
    
    changes_display = "outputs/stage3_changes.png"
    if changes_result and changes_result.get("thermal_enhanced"):
        # Use enhanced thermal visualization as primary display
        shutil.copy(changes_result["thermal_enhanced"], changes_display)
    elif changes_result and changes_result["changes_colored"]:
        shutil.copy(changes_result["changes_colored"], changes_display)

    # STAGE 4: Enhanced Pit-Only Area Detection and Change Filtering
    print("🏔️  Stage 4: Creating enhanced pit-only mask and filtering changes...")
    
    # Create enhanced pit-only mask from new image
    enhanced_pit_result = create_enhanced_pit_only_mask(new_final, "outputs/stage4")
    
    # Filter changes to show ONLY pit area changes
    pit_only_filtered_result = None
    if enhanced_pit_result and changes_result:
        pit_only_filtered_result = filter_changes_to_pit_only(
            changes_result["changes_mask"],
            enhanced_pit_result["pit_mask"], 
            "outputs/stage4"
        )
    
    # Also create binary mask for display compatibility
    binary_mask_result = create_binary_pit_mask(new_final, "outputs/stage4")
    
    # Copy enhanced pit visualization for Stage 4 display
    segmentation_display = "outputs/stage4_segmentation.png"
    if enhanced_pit_result and enhanced_pit_result.get("pit_visualization_path"):
        shutil.copy(enhanced_pit_result["pit_visualization_path"], segmentation_display)
    elif binary_mask_result and binary_mask_result.get("binary_display_path"):
        shutil.copy(binary_mask_result["binary_display_path"], segmentation_display)
    elif binary_mask_result and binary_mask_result["visual_result"]:
        # Fallback to visual result if other options not available
        shutil.copy(binary_mask_result["visual_result"], segmentation_display)

    # STAGE 5: Pit-Only Visualization Phase - Color-coded Superposition
    print("🎨 Stage 5: Creating pit-only color-coded visualization...")
    visualization_result = None
    if pit_only_filtered_result:
        visualization_result = create_color_coded_superposition(
            baseline_final, 
            new_final, 
            pit_only_filtered_result["pit_only_mask"], 
            "outputs/stage5"
        )
    
    # Copy final visualizations (both standard and high contrast)
    visualization_display = "outputs/stage5_visualization.png"
    high_contrast_display = "outputs/stage5_high_contrast.png"
    
    if visualization_result:
        if visualization_result.get("visualization"):
            shutil.copy(visualization_result["visualization"], visualization_display)
        if visualization_result.get("high_contrast_visualization"):
            shutil.copy(visualization_result["high_contrast_visualization"], high_contrast_display)
    else:
        # Create fallback visualization if main visualization fails
        fallback_vis = create_fallback_visualization(baseline_final, new_final, "outputs/stage5")
        if fallback_vis:
            shutil.copy(fallback_vis, visualization_display)

    # Enhanced Analysis with Risk Scoring (Pit-Only Focus)
    print("📊 Analyzing pit-only changes with enhanced risk assessment...")
    pit_filtered_mask = pit_only_filtered_result["pit_only_mask"] if pit_only_filtered_result else None
    analysis_result = analyze_changes(baseline_final, new_final, pit_filtered_mask)

    # Enhanced Alert System with Risk Scoring
    print("🚨 Running enhanced alert system with risk scoring...")
    
    # Determine alert message based on risk level
    if analysis_result:
        risk_level = analysis_result.get("risk_level", "STABLE")
        risk_score = analysis_result.get("risk_score", 0)
        
        if risk_level == "CRITICAL":
            alert_message = f"🚨 CRITICAL RISK ({risk_score:.1f}/100): Immediate evacuation required!"
        elif risk_level == "HIGH":
            alert_message = f"⚠️ HIGH RISK ({risk_score:.1f}/100): Significant rockfall activity detected!"
        elif risk_level == "MODERATE":
            alert_message = f"⚠️ MODERATE RISK ({risk_score:.1f}/100): Increased monitoring recommended!"
        elif risk_level == "LOW":
            alert_message = f"⚠️ LOW RISK ({risk_score:.1f}/100): Minor changes detected!"
        else:
            alert_message = f"✅ STABLE ({risk_score:.1f}/100): No significant changes detected!"
    else:
        alert_message = "✅ System analysis completed - monitoring active!"

    # Return comprehensive results
    json_result = {
        "alert": analysis_result and analysis_result.get("risk_level") != "STABLE",
        "message": alert_message,
        "timestamp": "2024-01-15 14:30:00",
        "risk_assessment": {
            "risk_score": analysis_result.get("risk_score", 0) if analysis_result else 0,
            "risk_level": analysis_result.get("risk_level", "STABLE") if analysis_result else "STABLE",
            "confidence": analysis_result.get("confidence", 0.0) if analysis_result else 0.0,
            "change_percentage": changes_result.get("change_percentage", 0) if changes_result else 0
        },
        "detection_stats": {
            "total_changes": changes_result.get("change_percentage", 0) if changes_result else 0,
            "high_intensity_changes": changes_result.get("critical_change_pixels", 0) if changes_result else 0,
            "medium_intensity_changes": changes_result.get("major_change_pixels", 0) if changes_result else 0,
            "low_intensity_changes": changes_result.get("moderate_change_pixels", 0) if changes_result else 0,
        },
        "processing_successful": all([
            changes_result is not None,
            enhanced_pit_result is not None,
            pit_only_filtered_result is not None,
            visualization_result is not None
        ])
    }

    show_alert(json_result)
    log_alert(json_result)

    print("✅ 5-Stage Pipeline completed successfully!")
    return json_result

def create_fallback_visualization(baseline_path, new_path, output_dir="fallback"):
    """
    Create a simple fallback visualization if main visualization fails
    """
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        baseline = cv2.imread(baseline_path)
        new_img = cv2.imread(new_path)
        
        if baseline is None or new_img is None:
            return None
        
        # Simple side-by-side comparison
        combined = np.hstack((baseline, new_img))
        
        fallback_path = os.path.join(output_dir, "fallback_visualization.png")
        cv2.imwrite(fallback_path, combined)
        
        return fallback_path
    except Exception as e:
        print(f"Fallback visualization failed: {e}")
        return None