import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os
from datetime import datetime

def create_thermal_colormap(intensity_map):
    """
    Create thermal colormap from intensity values (0-255)
    Thermal progression: B    # Calculate accuracy metrics
    total_diff_pixels = np.sum(diff_denoised > 5)  # Pixels     print(f"🔥 ACCURATE Change Detection: {change_percentage:.2f}% changed | Preserved Original Sizes | Avg Intensity: {avg_thermal_intensity:.1f}")
    
    return {
        "changes_image": changes_path,
        "changes_colored": colored_changes_path,
        "thermal_enhanced": thermal_enhanced_path,
        "changes_mask": combined_changes,
        "thermal_intensity": thermal_intensity,
        "change_percentage": change_percentage,
        "critical_change_pixels": np.count_nonzero(changes_critical_preserved),
        "major_change_pixels": np.count_nonzero(changes_major_preserved), 
        "moderate_change_pixels": np.count_nonzero(changes_moderate_preserved),
        "minor_change_pixels": np.count_nonzero(changes_minor_preserved),
        "avg_thermal_intensity": avg_thermal_intensity,
        "max_thermal_intensity": max_thermal_intensity,
        "size_preservation": "enabled"
    }nce
    detected_pixels = np.sum(combined_changes > 0)  # Pixels detected as changes
    accuracy_ratio = detected_pixels / max(total_diff_pixels, 1) * 100
    
    print(f"🔥 ACCURATE Change Detection: {change_percentage:.2f}% changed | Accuracy: {accuracy_ratio:.1f}% | Avg Intensity: {avg_thermal_intensity:.1f}")
    
    return {
        "changes_image": changes_path,
        "changes_colored": colored_changes_path,
        "thermal_enhanced": thermal_enhanced_path,
        "changes_mask": combined_changes,
        "thermal_intensity": thermal_intensity,
        "change_percentage": change_percentage,
        "critical_change_pixels": np.count_nonzero(changes_critical),
        "major_change_pixels": np.count_nonzero(changes_major), 
        "moderate_change_pixels": np.count_nonzero(changes_moderate),
        "minor_change_pixels": np.count_nonzero(changes_minor),
        "avg_thermal_intensity": avg_thermal_intensity,
        "max_thermal_intensity": max_thermal_intensity,
        "accuracy_metrics": {
            "detection_accuracy": accuracy_ratio,
            "median_difference": diff_median,
            "threshold_critical": thresh_critical,
            "exposure_difference": exposure_diff if 'exposure_diff' in locals() else 0
        }
    }an → Yellow → Orange → Red → White
    """
    height, width = intensity_map.shape
    thermal_rgb = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Normalize intensity to 0-1 range
    normalized = intensity_map / 255.0
    
    # Apply thermal color mapping with proper array operations
    # Cold (0-0.2): Black to Blue
    mask = (normalized >= 0) & (normalized < 0.2)
    if np.any(mask):
        blue_intensity = (normalized[mask] / 0.2 * 255).astype(np.uint8)
        thermal_rgb[mask, 0] = blue_intensity  # B channel
        thermal_rgb[mask, 1] = 0               # G channel
        thermal_rgb[mask, 2] = 0               # R channel
    
    # Cool (0.2-0.4): Blue to Cyan  
    mask = (normalized >= 0.2) & (normalized < 0.4)
    if np.any(mask):
        progress = (normalized[mask] - 0.2) / 0.2
        cyan_green = (progress * 255).astype(np.uint8)
        thermal_rgb[mask, 0] = 255             # B channel (full blue)
        thermal_rgb[mask, 1] = cyan_green      # G channel (increasing)
        thermal_rgb[mask, 2] = 0               # R channel
    
    # Warm (0.4-0.6): Cyan to Yellow
    mask = (normalized >= 0.4) & (normalized < 0.6)
    if np.any(mask):
        progress = (normalized[mask] - 0.4) / 0.2
        yellow_blue = (255 - progress * 255).astype(np.uint8)
        thermal_rgb[mask, 0] = yellow_blue     # B channel (decreasing)
        thermal_rgb[mask, 1] = 255             # G channel (full green)
        thermal_rgb[mask, 2] = 0               # R channel
    
    # Hot (0.6-0.8): Yellow to Orange
    mask = (normalized >= 0.6) & (normalized < 0.8)
    if np.any(mask):
        progress = (normalized[mask] - 0.6) / 0.2
        orange_red = (progress * 255).astype(np.uint8)
        thermal_rgb[mask, 0] = 0               # B channel
        thermal_rgb[mask, 1] = 255             # G channel (full green)
        thermal_rgb[mask, 2] = orange_red      # R channel (increasing)
    
    # Very Hot (0.8-1.0): Orange to Red
    mask = (normalized >= 0.8) & (normalized <= 1.0)
    if np.any(mask):
        progress = (normalized[mask] - 0.8) / 0.2
        red_green = (255 - progress * 255).astype(np.uint8)
        thermal_rgb[mask, 0] = 0               # B channel
        thermal_rgb[mask, 1] = red_green       # G channel (decreasing)
        thermal_rgb[mask, 2] = 255             # R channel (full red)
    
    return thermal_rgb

def apply_thermal_gradient_effect(base_image, intensity_map, colored_changes):
    """
    Apply thermal gradient effect for enhanced visualization
    """
    # Create thermal overlay
    thermal_colors = create_thermal_colormap(intensity_map)
    
    # Create gradient mask for smooth blending
    gradient_mask = intensity_map / 255.0
    gradient_mask = cv2.GaussianBlur(gradient_mask, (7, 7), 0)
    gradient_mask = np.stack([gradient_mask] * 3, axis=2)
    
    # Blend base image with thermal colors using gradient mask
    thermal_blend = base_image.astype(np.float32) * (1 - gradient_mask) + thermal_colors.astype(np.float32) * gradient_mask
    thermal_blend = np.clip(thermal_blend, 0, 255).astype(np.uint8)
    
    # Enhance high-intensity areas with pure thermal colors
    high_intensity_mask = intensity_map > 150
    thermal_blend[high_intensity_mask] = colored_changes[high_intensity_mask]
    
    return thermal_blend

def enhance_change_precision(diff_image, confidence_threshold=0.7):
    """
    Enhance change detection precision using confidence scoring and noise reduction
    """
    # Calculate local variance to identify textured regions (more reliable for change detection)
    kernel = np.ones((7, 7), np.float32) / 49
    local_mean = cv2.filter2D(diff_image.astype(np.float32), -1, kernel)
    local_variance = cv2.filter2D((diff_image.astype(np.float32) - local_mean) ** 2, -1, kernel)
    
    # Normalize variance to create confidence map
    confidence_map = local_variance / (np.max(local_variance) + 1e-6)
    
    # Apply confidence threshold
    high_confidence_mask = confidence_map > confidence_threshold
    
    # Enhance changes in high-confidence regions
    enhanced_diff = diff_image.copy()
    enhanced_diff[high_confidence_mask] = np.minimum(255, enhanced_diff[high_confidence_mask] * 1.5)
    
    return enhanced_diff, confidence_map

def filter_small_changes(binary_mask, min_area):
    """
    Remove small isolated change regions that are likely noise
    """
    # Find connected components
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask, connectivity=8)
    
    # Create filtered mask
    filtered_mask = np.zeros_like(binary_mask)
    
    # Keep only components larger than min_area
    for i in range(1, num_labels):  # Skip background (label 0)
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            filtered_mask[labels == i] = 255
    
    return filtered_mask

def validate_change_consistency(img1, img2, changes_mask):
    """
    Validate that detected changes represent actual structural changes, not lighting/shadow
    """
    # Check if changes are consistent across color channels
    img1_lab = cv2.cvtColor(img1, cv2.COLOR_BGR2LAB)
    img2_lab = cv2.cvtColor(img2, cv2.COLOR_BGR2LAB)
    
    # Calculate differences in each LAB channel
    l_diff = cv2.absdiff(img1_lab[:,:,0], img2_lab[:,:,0])  # Lightness
    a_diff = cv2.absdiff(img1_lab[:,:,1], img2_lab[:,:,1])  # Green-Red
    b_diff = cv2.absdiff(img1_lab[:,:,2], img2_lab[:,:,2])  # Blue-Yellow
    
    # Structural changes should have color differences, not just lightness
    structure_mask = (a_diff > 5) | (b_diff > 5)  # Color component changes
    lighting_only = (l_diff > 10) & (structure_mask == 0)  # Only lightness changes
    
    # Remove lighting-only changes from the mask
    validated_mask = changes_mask.copy()
    validated_mask[lighting_only] = 0
    
    removed_pixels = np.sum((changes_mask > 0) & (validated_mask == 0))
    if removed_pixels > 0:
        print(f"🔍 Removed {removed_pixels} lighting-only pixels (not structural changes)")
    
    return validated_mask

def preserve_change_boundaries(original_diff, detected_changes, expansion_factor=1.2):
    """
    Preserve original change boundaries while keeping accurate detection
    """
    # Create expanded mask based on original difference intensities
    expanded_mask = np.zeros_like(detected_changes)
    
    # For each detected change region, expand it based on original difference values
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    
    # Dilate detected changes slightly to restore original boundaries
    expanded_changes = cv2.dilate(detected_changes, kernel, iterations=1)
    
    # Only keep expanded pixels that have some difference in original image
    # This prevents expanding into areas with no actual change
    original_threshold = 5  # Minimum difference to consider
    valid_expansion = original_diff > original_threshold
    
    # Combine: expanded changes AND areas with actual differences
    preserved_changes = expanded_changes & valid_expansion
    
    return preserved_changes

def detect_changes_with_dilation(img1_path, img2_path, output_dir="changes", pit_area_mask=None):
    """
    Stage 3: Enhanced change detection with thermal colors - PIT AREAS ONLY (sky and non-mining areas excluded)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Read images
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    
    if img1 is None or img2 is None:
        print("Error: One or both images could not be read.")
        return None
    
    # CONSERVATIVE preprocessing to prevent false changes
    # Convert to grayscale first (minimal processing)
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Apply gentle histogram equalization only if needed
    # Check if images have similar exposure
    mean1, mean2 = np.mean(gray1), np.mean(gray2)
    exposure_diff = abs(mean1 - mean2)
    
    if exposure_diff > 20:  # Only normalize if significant exposure difference
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(16,16))  # Gentler CLAHE
        gray1 = clahe.apply(gray1)
        gray2 = clahe.apply(gray2)
        print(f"📸 Applied gentle exposure normalization (diff: {exposure_diff:.1f})")
    else:
        print(f"📸 Skipped normalization - similar exposure (diff: {exposure_diff:.1f})")
    
    # Apply minimal Gaussian blur to reduce sensor noise
    gray1 = cv2.GaussianBlur(gray1, (3, 3), 0.5)
    gray2 = cv2.GaussianBlur(gray2, (3, 3), 0.5)
    
    # ACCURATE SUBTRACTION ALGORITHM - Prevents false positives
    
    # 1. Robust absolute difference with noise reduction
    diff = cv2.absdiff(gray1, gray2)
    
    # 2. Apply median filter to reduce noise before analysis
    diff_denoised = cv2.medianBlur(diff, 5)
    
    # 3. Calculate robust statistics using percentiles (more accurate than mean/std)
    diff_median = np.median(diff_denoised)
    diff_75th = np.percentile(diff_denoised, 75)
    diff_90th = np.percentile(diff_denoised, 90)
    diff_95th = np.percentile(diff_denoised, 95)
    
    # 4. Set BALANCED thresholds - accurate but preserve real change sizes
    # Detect significant changes while maintaining original change dimensions
    thresh_critical = max(20, diff_95th + 5)      # Top 5% + smaller margin = Critical  
    thresh_major = max(16, diff_90th + 3)         # Top 10% + smaller margin = Major
    thresh_moderate = max(12, diff_75th + 5)      # Top 25% + smaller margin = Moderate  
    thresh_minor = max(8, diff_median + 8)        # Above median + smaller margin = Minor
    
    print(f"🔍 ACCURATE Thresholds: Critical={thresh_critical:.1f}, Major={thresh_major:.1f}, Moderate={thresh_moderate:.1f}, Minor={thresh_minor:.1f}")
    print(f"📊 Image Stats: Median={diff_median:.1f}, 75th={diff_75th:.1f}, 90th={diff_90th:.1f}, 95th={diff_95th:.1f}")
    
    # 5. Apply conservative thresholds to ORIGINAL difference (not enhanced)
    _, changes_critical = cv2.threshold(diff_denoised, thresh_critical, 255, cv2.THRESH_BINARY)
    _, changes_major = cv2.threshold(diff_denoised, thresh_major, 255, cv2.THRESH_BINARY)
    _, changes_moderate = cv2.threshold(diff_denoised, thresh_moderate, 255, cv2.THRESH_BINARY)
    _, changes_minor = cv2.threshold(diff_denoised, thresh_minor, 255, cv2.THRESH_BINARY)
    
    # 6. Remove only very small noise pixels while preserving actual change sizes
    min_noise_area = 8   # Only remove tiny noise spots (reduced from 25)
    
    changes_critical = filter_small_changes(changes_critical, min_noise_area)
    changes_major = filter_small_changes(changes_major, min_noise_area) 
    changes_moderate = filter_small_changes(changes_moderate, min_noise_area // 2)
    changes_minor = filter_small_changes(changes_minor, min_noise_area // 3)
    
    # Enhanced morphological operations - preserve change size while cleaning noise
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    kernel_expand = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    # Clean noise but then restore original change sizes
    changes_critical = cv2.morphologyEx(changes_critical, cv2.MORPH_OPEN, kernel_clean)
    changes_critical = cv2.morphologyEx(changes_critical, cv2.MORPH_CLOSE, kernel_expand)  # Restore size
    
    changes_major = cv2.morphologyEx(changes_major, cv2.MORPH_OPEN, kernel_clean)
    changes_major = cv2.morphologyEx(changes_major, cv2.MORPH_CLOSE, kernel_clean)
    
    changes_moderate = cv2.morphologyEx(changes_moderate, cv2.MORPH_OPEN, kernel_clean)
    changes_moderate = cv2.morphologyEx(changes_moderate, cv2.MORPH_CLOSE, kernel_clean)
    
    changes_minor = cv2.morphologyEx(changes_minor, cv2.MORPH_OPEN, kernel_clean)
    
    # Combine all changes for overall mask (needed before thermal calculations)
    combined_changes = cv2.bitwise_or(changes_critical, changes_major)
    combined_changes = cv2.bitwise_or(combined_changes, changes_moderate)
    combined_changes = cv2.bitwise_or(combined_changes, changes_minor)
    
    # 7. ACCURACY VALIDATION - Verify changes are truly significant
    # Calculate actual intensity values for thermal mapping
    thermal_intensity = np.zeros_like(diff_denoised, dtype=np.float32)
    
    # Recalculate change masks after boundary preservation for thermal intensity
    changes_critical_preserved = cv2.bitwise_and(combined_changes, (diff_denoised >= thresh_critical).astype(np.uint8) * 255)
    changes_major_preserved = cv2.bitwise_and(combined_changes, (diff_denoised >= thresh_major).astype(np.uint8) * 255) & ~changes_critical_preserved
    changes_moderate_preserved = cv2.bitwise_and(combined_changes, (diff_denoised >= thresh_moderate).astype(np.uint8) * 255) & ~changes_major_preserved & ~changes_critical_preserved
    changes_minor_preserved = combined_changes & ~changes_moderate_preserved & ~changes_major_preserved & ~changes_critical_preserved
    
    # Assign thermal intensity based on preserved boundaries and original magnitudes
    thermal_intensity[changes_critical_preserved > 0] = 255.0   # Hottest - Critical changes
    thermal_intensity[changes_major_preserved > 0] = 200.0     # Hot - Major changes  
    thermal_intensity[changes_moderate_preserved > 0] = 150.0  # Warm - Moderate changes
    thermal_intensity[changes_minor_preserved > 0] = 100.0     # Cool - Minor changes
    
    # Apply pit area mask to filter out sky and non-mining areas
    if pit_area_mask is not None:
        print("🏔️  Applying pit-area mask to filter changes...")
        changes_critical = cv2.bitwise_and(changes_critical, pit_area_mask)
        changes_major = cv2.bitwise_and(changes_major, pit_area_mask)
        changes_moderate = cv2.bitwise_and(changes_moderate, pit_area_mask)
        changes_minor = cv2.bitwise_and(changes_minor, pit_area_mask)
        
        # Also filter thermal intensity
        thermal_intensity = thermal_intensity * (pit_area_mask / 255.0)
        
        # Update combined_changes after pit area filtering
        combined_changes = cv2.bitwise_or(changes_critical, changes_major)
        combined_changes = cv2.bitwise_or(combined_changes, changes_moderate)
        combined_changes = cv2.bitwise_or(combined_changes, changes_minor)
    
    # 8. STRUCTURAL VALIDATION - Remove lighting-only changes
    combined_changes = validate_change_consistency(img1, img2, combined_changes)
    
    # 9. BOUNDARY PRESERVATION - Restore original change sizes while keeping accuracy
    combined_changes = preserve_change_boundaries(diff_denoised, combined_changes)

    # Convert back to 3-channel for visualization
    changes_image = cv2.cvtColor(combined_changes, cv2.COLOR_GRAY2BGR)    # THERMAL COLOR MAPPING SYSTEM - True Thermal Colors
    changes_colored = img1.copy()
    thermal_overlay = create_thermal_colormap(thermal_intensity)
    
    # Apply thermal colors based on preserved change boundaries
    # Critical changes - Pure RED (Hottest in thermal imaging)
    changes_colored[changes_critical_preserved > 0] = [0, 0, 255]      # BGR: Pure Red
    
    # Major changes - ORANGE-RED (Very Hot)  
    changes_colored[changes_major_preserved > 0] = [0, 69, 255]        # BGR: Orange-Red
    
    # Moderate changes - YELLOW (Hot)
    changes_colored[changes_moderate_preserved > 0] = [0, 255, 255]    # BGR: Pure Yellow
    
    # Minor changes - CYAN (Warm)
    changes_colored[changes_minor_preserved > 0] = [255, 255, 0]       # BGR: Cyan
    
    # Create enhanced thermal visualization with gradient effect
    thermal_enhanced = apply_thermal_gradient_effect(img1, thermal_intensity, changes_colored)
    
    # Calculate enhanced change statistics
    total_pixels = combined_changes.shape[0] * combined_changes.shape[1]
    changed_pixels = np.count_nonzero(combined_changes)
    change_percentage = (changed_pixels / total_pixels) * 100
    
    # Calculate thermal intensity statistics
    avg_thermal_intensity = np.mean(thermal_intensity[thermal_intensity > 0]) if np.any(thermal_intensity > 0) else 0
    max_thermal_intensity = np.max(thermal_intensity)
    
    # Save enhanced results
    changes_path = os.path.join(output_dir, f"changes_{os.path.basename(img2_path)}")
    colored_changes_path = os.path.join(output_dir, f"thermal_changes_{os.path.basename(img2_path)}")
    thermal_enhanced_path = os.path.join(output_dir, f"thermal_enhanced_{os.path.basename(img2_path)}")
    
    cv2.imwrite(changes_path, changes_image)
    cv2.imwrite(colored_changes_path, changes_colored)
    cv2.imwrite(thermal_enhanced_path, thermal_enhanced)
    
    print(f"� Thermal Change Detection: {change_percentage:.2f}% changed | Avg Intensity: {avg_thermal_intensity:.1f} | Max: {max_thermal_intensity:.1f}")
    
    return {
        "changes_image": changes_path,
        "changes_colored": colored_changes_path,
        "thermal_enhanced": thermal_enhanced_path,
        "changes_mask": combined_changes,
        "thermal_intensity": thermal_intensity,
        "change_percentage": change_percentage,
        "critical_change_pixels": np.count_nonzero(changes_critical),
        "major_change_pixels": np.count_nonzero(changes_major), 
        "moderate_change_pixels": np.count_nonzero(changes_moderate),
        "minor_change_pixels": np.count_nonzero(changes_minor),
        "avg_thermal_intensity": avg_thermal_intensity,
        "max_thermal_intensity": max_thermal_intensity
    }

def remove_segmented_from_changes(changes_mask, segmentation_mask, output_dir="filtered_changes"):
    """
    Stage 4: Remove segmented non-pit actors from the change detection result
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Create inverse mask of segmented areas (areas to keep)
    inverse_seg_mask = cv2.bitwise_not(segmentation_mask)
    
    # Apply inverse mask to changes to remove segmented areas
    filtered_changes = cv2.bitwise_and(changes_mask, inverse_seg_mask)
    
    # Convert to 3-channel for visualization
    filtered_changes_color = cv2.cvtColor(filtered_changes, cv2.COLOR_GRAY2BGR)
    
    # Save filtered changes
    filtered_path = os.path.join(output_dir, "filtered_changes.png")
    cv2.imwrite(filtered_path, filtered_changes_color)
    
    return {
        "filtered_changes": filtered_path,
        "filtered_mask": filtered_changes
    }

def filter_changes_to_pit_only(changes_mask, pit_mask, output_dir="pit_changes"):
    """
    Filter changes to show ONLY changes in pit areas, completely excluding non-pit areas
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Apply pit mask to changes - only keep changes where pit_mask is 255 (pit area)
    pit_only_changes = cv2.bitwise_and(changes_mask, pit_mask)
    
    # Apply additional morphological operations to clean up pit-only changes
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    
    # Remove noise in pit changes
    pit_only_changes = cv2.morphologyEx(pit_only_changes, cv2.MORPH_OPEN, kernel)
    
    # Fill small gaps in pit changes
    pit_only_changes = cv2.morphologyEx(pit_only_changes, cv2.MORPH_CLOSE, kernel)
    
    # Convert to 3-channel for visualization
    pit_changes_color = cv2.cvtColor(pit_only_changes, cv2.COLOR_GRAY2BGR)
    
    # Save pit-only changes
    pit_changes_path = os.path.join(output_dir, "pit_only_changes.png")
    cv2.imwrite(pit_changes_path, pit_changes_color)
    
    # Create debug visualization showing pit mask overlay
    debug_viz = cv2.cvtColor(changes_mask, cv2.COLOR_GRAY2BGR)
    debug_viz[pit_mask == 0] = [100, 100, 100]  # Gray out non-pit areas
    debug_viz_path = os.path.join(output_dir, "pit_mask_debug.png")
    cv2.imwrite(debug_viz_path, debug_viz)
    
    print(f"🏔️  Pit-only changes isolated: {np.sum(pit_only_changes > 0)} pixels")
    
    return {
        "pit_only_changes_path": pit_changes_path,
        "pit_only_mask": pit_only_changes,
        "debug_visualization": debug_viz_path
    }

def create_color_coded_superposition(baseline_path, new_path, filtered_changes_mask, output_dir="visualization"):
    """
    Stage 5: Create color-coded superposition with transparency - PIT AREAS ONLY
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Read baseline image
    baseline = cv2.imread(baseline_path)
    new_img = cv2.imread(new_path)
    
    if baseline is None or new_img is None:
        return None
    
    # Create vibrant color-coded overlay for pit-only visualization
    overlay = baseline.copy()
    
    # Pure vibrant colors for final visualization phase  
    # Critical changes - Pure Bright Red (BGR format)
    overlay[filtered_changes_mask > 200] = [0, 0, 255]  # Pure red
    
    # Moderate changes - Pure Bright Yellow (BGR format)  
    overlay[filtered_changes_mask > 100] = [0, 255, 255]  # Pure yellow
    
    # Minor changes - Pure Bright Red (different intensity)
    overlay[filtered_changes_mask > 50] = [0, 0, 200]   # Slightly darker red
    
    # Very minor changes - Pure Bright Yellow (different intensity)
    overlay[filtered_changes_mask > 20] = [0, 200, 255]   # Slightly darker yellow
    
    # Create vibrant superposition with enhanced visibility
    alpha = 0.6  # Baseline image weight (reduced for more overlay visibility)
    beta = 0.4   # Overlay weight (increased for vibrant colors)
    superposition = cv2.addWeighted(baseline, alpha, overlay, beta, 0)
    
    # Enhance vibrant areas with pure colors
    # Make red areas pure bright red
    red_mask = (overlay[:, :, 2] >= 200) & (overlay[:, :, 1] == 0) & (overlay[:, :, 0] == 0)
    superposition[red_mask] = [0, 0, 255]  # Pure bright red
    
    # Make yellow areas pure bright yellow  
    yellow_mask = (overlay[:, :, 1] >= 200) & (overlay[:, :, 2] >= 200) & (overlay[:, :, 0] == 0)
    superposition[yellow_mask] = [0, 255, 255]  # Pure bright yellow
    
    # Add ground level reference line with vibrant color
    height = baseline.shape[0]
    ground_level = int(height * 0.8)  # Assume ground is at 80% height
    cv2.line(superposition, (0, ground_level), (baseline.shape[1], ground_level), (0, 255, 0), 3)  # Bright green line
    
    # Create an additional high-contrast version
    high_contrast = baseline.copy()
    
    # Apply pure vibrant colors with maximum intensity for high contrast
    high_contrast[filtered_changes_mask > 200] = [0, 0, 255]    # Pure bright red
    high_contrast[filtered_changes_mask > 100] = [0, 255, 255]  # Pure bright yellow  
    high_contrast[filtered_changes_mask > 50] = [0, 0, 200]     # Darker red
    high_contrast[filtered_changes_mask > 20] = [0, 200, 255]   # Darker yellow
    
    # Save both versions
    vis_path = os.path.join(output_dir, "final_visualization.png")
    high_contrast_path = os.path.join(output_dir, "high_contrast_visualization.png")
    
    cv2.imwrite(vis_path, superposition)
    cv2.imwrite(high_contrast_path, high_contrast)
    
    return {
        "visualization": vis_path,
        "high_contrast_visualization": high_contrast_path,
        "overlay": overlay,
        "vibrant_overlay": high_contrast
    }

def create_enhanced_composite_overlay(baseline_path, new_path, stage3_data, stage4_data, output_dir="stage5"):
    """
    🎯 ENHANCED Stage 5: Create composite overlay combining Stage 3 thermal + Stage 4 pit masking
    Displays thermal change detection results with precise pit area masking
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Load baseline image
    baseline = cv2.imread(baseline_path)
    new_img = cv2.imread(new_path)
    
    if baseline is None or new_img is None:
        print("❌ Stage 5: Could not load baseline or new image")
        return None
    
    height, width = baseline.shape[:2]
    print(f"🎨 Stage 5: Creating composite overlay ({width}x{height})")
    
    # Initialize composite overlay with baseline
    composite_overlay = baseline.copy()
    overlay_quality = "Basic"
    
    # LAYER 1: Apply Stage 3 thermal changes if available
    thermal_applied = False
    
    # 🔍 DEBUG: Log what Stage 3 data we received
    print(f"🔍 DEBUG Stage 5: Stage 3 data keys: {list(stage3_data.keys())}")
    if stage3_data.get("changes_result"):
        print(f"🔍 DEBUG Stage 5: Changes result keys: {list(stage3_data['changes_result'].keys())}")
        print(f"🔍 DEBUG Stage 5: thermal_enhanced value: {stage3_data['changes_result'].get('thermal_enhanced')}")
    
    # Try multiple approaches to get thermal data
    thermal_img_path = None
    
    # Approach 1: Direct thermal_path from stage3_data
    if stage3_data.get("thermal_path") and stage3_data["thermal_path"] is not None:
        thermal_img_path = stage3_data["thermal_path"]
        print(f"🔍 DEBUG Stage 5: Using thermal_path: {thermal_img_path}")
    
    # Approach 2: From changes_result -> thermal_enhanced
    elif stage3_data.get("changes_result") and stage3_data["changes_result"].get("thermal_enhanced"):
        thermal_img_path = stage3_data["changes_result"]["thermal_enhanced"]
        print(f"🔍 DEBUG Stage 5: Using changes_result thermal: {thermal_img_path}")
    
    # Approach 3: From changes_result -> changes_colored (fallback)
    elif stage3_data.get("changes_colored") and stage3_data["changes_colored"] is not None:
        thermal_img_path = stage3_data["changes_colored"]
        print(f"🔍 DEBUG Stage 5: Using changes_colored: {thermal_img_path}")
    
    # Approach 4: Look in stage3 directory directly
    else:
        import glob
        thermal_files = glob.glob("outputs/stage3/thermal_enhanced*.png")
        if thermal_files:
            thermal_img_path = thermal_files[0]
            print(f"🔍 DEBUG Stage 5: Found thermal file directly: {thermal_files[0]}")
        else:
            # Try changes_colored files
            colored_files = glob.glob("outputs/stage3/changes_colored*.png")
            if colored_files:
                thermal_img_path = colored_files[0]
                print(f"🔍 DEBUG Stage 5: Found changes_colored file: {colored_files[0]}")
            else:
                print("🔍 DEBUG Stage 5: No thermal files found")
    
    # Apply thermal overlay if we found a thermal image
    if thermal_img_path:
        print(f"🔥 Stage 5: Checking thermal image path: {thermal_img_path}")
        print(f"🔥 Stage 5: Path exists: {os.path.exists(thermal_img_path) if thermal_img_path else False}")
        
        if os.path.exists(thermal_img_path):
            try:
                print(f"🔥 Stage 5: Loading thermal image from: {thermal_img_path}")
                thermal_img = cv2.imread(thermal_img_path)
                
                if thermal_img is not None:
                    print(f"🔥 Stage 5: Thermal image loaded successfully: {thermal_img.shape}")
                    
                    # Resize thermal image to match baseline if needed
                    if thermal_img.shape != baseline.shape:
                        thermal_img = cv2.resize(thermal_img, (width, height))
                        print(f"🔥 Stage 5: Resized thermal image to: {thermal_img.shape}")
                    
                    # Apply thermal changes with enhanced blending to preserve colors
                    composite_overlay = cv2.addWeighted(baseline, 0.3, thermal_img, 0.7, 0)
                    thermal_applied = True
                    overlay_quality = "Thermal-Enhanced"
                    print("🔥 Stage 5: Applied Stage 3 thermal changes with enhanced blending (70% thermal)")
                else:
                    print("❌ Stage 5: thermal_img is None after cv2.imread")
            except Exception as e:
                print(f"⚠️  Stage 5: Exception loading thermal overlay: {e}")
        else:
            print(f"❌ Stage 5: Thermal image file does not exist: {thermal_img_path}")
    else:
        print("❌ Stage 5: No thermal image path found")
        
    # If thermal didn't apply, try to create synthetic thermal overlay from Stage 3 outputs
    if not thermal_applied:
        print("🔄 Stage 5: Attempting fallback synthetic thermal overlay...")
        try:
            # Look for any stage3 output files
            import glob
            stage3_files = glob.glob("outputs/stage3/*.png")
            print(f"🔍 Stage 5: Found {len(stage3_files)} Stage 3 files: {[os.path.basename(f) for f in stage3_files]}")
            
            # Try to use any available stage3 visualization
            for file_path in stage3_files:
                if "thermal" in file_path or "changes" in file_path:
                    try:
                        fallback_img = cv2.imread(file_path)
                        if fallback_img is not None:
                            if fallback_img.shape != baseline.shape:
                                fallback_img = cv2.resize(fallback_img, (width, height))
                            composite_overlay = cv2.addWeighted(baseline, 0.5, fallback_img, 0.5, 0)
                            thermal_applied = True
                            overlay_quality = "Thermal-Fallback"
                            print(f"🔥 Stage 5: Applied fallback thermal from: {os.path.basename(file_path)}")
                            break
                    except:
                        continue
        except Exception as e:
            print(f"⚠️  Stage 5: Fallback thermal failed: {e}")
    
    # LAYER 2: Apply Stage 4 pit masking if available
    pit_masked = False
    
    # 🔍 DEBUG: Log what Stage 4 data we received
    print(f"🔍 DEBUG Stage 5: Stage 4 data keys: {list(stage4_data.keys())}")
    
    # Try multiple approaches to get pit mask
    pit_mask = None
    
    # Approach 1: Enhanced pit result
    if stage4_data.get("enhanced_pit_result") and stage4_data["enhanced_pit_result"].get("pit_mask") is not None:
        pit_mask = stage4_data["enhanced_pit_result"]["pit_mask"]
        print("🔍 DEBUG Stage 5: Using enhanced_pit_result pit_mask")
    
    # Approach 2: Binary mask result
    elif stage4_data.get("binary_mask_result") and stage4_data["binary_mask_result"].get("binary_mask") is not None:
        pit_mask = stage4_data["binary_mask_result"]["binary_mask"]
        print("🔍 DEBUG Stage 5: Using binary_mask_result binary_mask")
    
    # Approach 3: Look for mask files directly
    else:
        import glob
        mask_files = glob.glob("outputs/stage4/*mask*.png")
        if mask_files:
            pit_mask = cv2.imread(mask_files[0], cv2.IMREAD_GRAYSCALE)
            print(f"🔍 DEBUG Stage 5: Loaded pit mask from file: {mask_files[0]}")
    
    # Apply pit masking if we have a mask
    if pit_mask is not None:
        try:
            print(f"🔲 Stage 5: Applying pit mask: {pit_mask.shape}")
            
            # Ensure pit mask matches image dimensions
            if pit_mask.shape[:2] != (height, width):
                pit_mask = cv2.resize(pit_mask, (width, height))
                print(f"🔲 Stage 5: Resized pit mask to: {pit_mask.shape}")
            
            # Apply pit masking - black out non-pit areas (where pit_mask is 0)
            non_pit_areas = pit_mask == 0
            composite_overlay[non_pit_areas] = [0, 0, 0]  # Black out non-pit actors
            pit_masked = True
            overlay_quality += "+PitMasked"
            
            # Calculate masked area percentage
            pit_area_percentage = (np.count_nonzero(pit_mask) / (height * width)) * 100
            print(f"🔲 Stage 5: Applied pit masking - {pit_area_percentage:.1f}% pit area preserved")
            
        except Exception as e:
            print(f"⚠️  Stage 5: Could not apply pit masking: {e}")
    else:
        print("❌ Stage 5: No pit mask found")
    
    # LAYER 3: Enhanced visualization features
    # Add enhanced contrast for critical changes
    if thermal_applied:
        # Boost thermal colors for better visibility
        hsv = cv2.cvtColor(composite_overlay, cv2.COLOR_BGR2HSV)
        hsv[:, :, 1] = cv2.multiply(hsv[:, :, 1], 1.3)  # Increase saturation
        hsv[:, :, 2] = cv2.multiply(hsv[:, :, 2], 1.1)  # Slight brightness boost
        composite_overlay = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        overlay_quality += "+Enhanced"
    
    # Create high contrast version for critical monitoring
    high_contrast_overlay = composite_overlay.copy()
    if thermal_applied or pit_masked:
        # Apply stronger contrast enhancement
        lab = cv2.cvtColor(high_contrast_overlay, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8)).apply(l)
        high_contrast_overlay = cv2.merge([l, a, b])
        high_contrast_overlay = cv2.cvtColor(high_contrast_overlay, cv2.COLOR_LAB2BGR)
    
    # Save composite overlays and debug images
    composite_path = os.path.join(output_dir, "enhanced_composite_overlay.png")
    high_contrast_path = os.path.join(output_dir, "high_contrast_composite.png")
    debug_baseline_path = os.path.join(output_dir, "debug_baseline.png")
    debug_thermal_path = os.path.join(output_dir, "debug_thermal_applied.png")
    debug_final_path = os.path.join(output_dir, "debug_final_overlay.png")
    
    # Save debug images for troubleshooting
    cv2.imwrite(debug_baseline_path, baseline)
    if thermal_applied:
        cv2.imwrite(debug_thermal_path, composite_overlay)
    
    cv2.imwrite(composite_path, composite_overlay)
    cv2.imwrite(high_contrast_path, high_contrast_overlay)
    cv2.imwrite(debug_final_path, composite_overlay)
    
    print(f"🖼️  Stage 5: Saved debug images to {output_dir}/debug_*.png")
    
    # Generate summary
    features_applied = []
    if thermal_applied:
        features_applied.append("Stage 3 Thermal Changes")
    if pit_masked:
        features_applied.append("Stage 4 Pit Masking")
    
    summary = f"Applied: {', '.join(features_applied) if features_applied else 'None'}"
    print(f"✅ Stage 5: Composite overlay created - {summary}")
    
    return {
        "composite_overlay": composite_path,
        "high_contrast_overlay": high_contrast_path,
        "overlay_quality": overlay_quality,
        "features_applied": features_applied,
        "thermal_applied": thermal_applied,
        "pit_masked": pit_masked,
        "summary": summary
    }

def calculate_risk_score(ssim_score, orb_score, change_percentage, filtered_changes_mask=None, thermal_intensity=0, severity_ratio=0):
    """
    Calculate comprehensive risk score based on multiple factors including thermal data
    Returns score from 0-100 and risk level
    """
    risk_score = 0
    factors = []
    
    print(f"🎯 Risk Calculation: Change={change_percentage:.2f}%, Thermal={thermal_intensity:.1f}, Severity={severity_ratio:.2f}")
    
    # SSIM-based risk (lower SSIM = higher risk)
    if ssim_score < 0.95:  # Very sensitive threshold
        ssim_risk = (1 - ssim_score) * 60  # Max 60 points from SSIM
        risk_score += ssim_risk
        factors.append(f"SSIM: {ssim_risk:.1f}/60")
    
    # ORB matches risk (fewer matches = higher risk)  
    if orb_score < 200:  # Lowered threshold
        orb_risk = max(0, (200 - orb_score) / 200 * 25)  # Max 25 points from ORB
        risk_score += orb_risk
        factors.append(f"ORB: {orb_risk:.1f}/25")
    
    # Change percentage risk (enhanced)
    if change_percentage > 0.5:  # Very sensitive - 0.5% change is significant
        change_risk = min(25, change_percentage * 4)  # Max 25 points from changes
        risk_score += change_risk
        factors.append(f"Change%: {change_risk:.1f}/25")
    
    # Thermal intensity risk (new)
    if thermal_intensity > 50:  # Thermal intensity above 50 is concerning
        thermal_risk = min(30, (thermal_intensity - 50) / 200 * 30)  # Max 30 points
        risk_score += thermal_risk
        factors.append(f"Thermal: {thermal_risk:.1f}/30")
    
    # Severity ratio risk (critical vs total changes)
    if severity_ratio > 0.1:  # 10% of changes being critical is significant
        severity_risk = min(20, severity_ratio * 20)  # Max 20 points
        risk_score += severity_risk
        factors.append(f"Severity: {severity_risk:.1f}/20")
    
    # Change intensity from filtered mask
    if filtered_changes_mask is not None:
        total_pixels = filtered_changes_mask.shape[0] * filtered_changes_mask.shape[1]
        changed_pixels = np.count_nonzero(filtered_changes_mask)
        intensity_percentage = (changed_pixels / total_pixels) * 100
        
        if intensity_percentage > 0.5:  # Very sensitive - 0.5% changed pixels
            intensity_risk = min(10, intensity_percentage * 2)  # Max 10 points
            risk_score += intensity_risk
            factors.append(f"Intensity: {intensity_risk:.1f}/10")
    
    # Determine risk level and alert status (more sensitive thresholds)
    if risk_score >= 60:
        risk_level = "CRITICAL"
        alert_status = True
    elif risk_score >= 40:
        risk_level = "HIGH" 
        alert_status = True
    elif risk_score >= 25:
        risk_level = "MODERATE"
        alert_status = True
    elif risk_score >= 10:
        risk_level = "LOW"
        alert_status = True
    else:
        risk_level = "STABLE"
        alert_status = False
    
    print(f"🎯 Final Risk Score: {risk_score:.1f}/100 - {risk_level} ({'ALERT' if alert_status else 'STABLE'})")
    
    return {
        "risk_score": min(100, risk_score),  # Cap at 100
        "risk_level": risk_level,
        "alert_status": alert_status,
        "risk_factors": factors,
        "thermal_contribution": thermal_intensity,
        "change_contribution": change_percentage,
        "severity_contribution": severity_ratio
    }

def analyze_changes(img1_path, img2_path, filtered_changes_mask=None, output_dir="results", thermal_data=None):
    """
    Enhanced analysis with thermal data integration for accurate risk scoring
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Use thermal data from pipeline if available
    if thermal_data:
        print(f"🔥 Using thermal pipeline data for accurate risk assessment...")
        change_percentage = thermal_data.get('change_percentage', 0)
        avg_thermal_intensity = thermal_data.get('avg_thermal_intensity', 0)
        max_thermal_intensity = thermal_data.get('max_thermal_intensity', 0)
        critical_pixels = thermal_data.get('critical_change_pixels', 0)
        major_pixels = thermal_data.get('major_change_pixels', 0)
        
        print(f"🔥 Thermal Analysis: {change_percentage:.2f}% changed, Avg: {avg_thermal_intensity:.1f}, Max: {max_thermal_intensity:.1f}")
        
        # Calculate enhanced metrics from thermal data
        total_change_pixels = critical_pixels + major_pixels
        if total_change_pixels > 0:
            severity_ratio = critical_pixels / max(total_change_pixels, 1)
            print(f"🔥 Change Severity: {severity_ratio:.2f} ({critical_pixels} critical of {total_change_pixels} total)")
        else:
            severity_ratio = 0
    else:
        # Fallback to basic image analysis
        img1 = cv2.imread(img1_path, cv2.IMREAD_COLOR)
        img2 = cv2.imread(img2_path, cv2.IMREAD_COLOR)
        
        if img1 is None or img2 is None:
            return None
        
        # Convert to grayscale for analysis
        gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        
        # Calculate change percentage
        diff = cv2.absdiff(gray1, gray2)
        _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
        changed_pixels = np.count_nonzero(thresh)
        total_pixels = thresh.shape[0] * thresh.shape[1]
        change_percentage = (changed_pixels / total_pixels) * 100
        avg_thermal_intensity = np.mean(diff[diff > 20]) if np.any(diff > 20) else 0
        max_thermal_intensity = np.max(diff)
        severity_ratio = 0.5  # Default moderate severity
    
    # Enhanced SSIM and ORB analysis
    img1 = cv2.imread(img1_path, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_path, cv2.IMREAD_COLOR)
    
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # SSIM analysis
    ssim_score, _ = ssim(gray1, gray2, full=True)
    
    # ORB Feature Matching
    orb = cv2.ORB_create(nfeatures=1000)
    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)
    
    matches = []
    if des1 is not None and des2 is not None:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        matches = sorted(matches, key=lambda x: x.distance)
    
    orb_score = len(matches)
    
    # Calculate comprehensive risk score with thermal data
    risk_analysis = calculate_risk_score(
        ssim_score, orb_score, change_percentage, filtered_changes_mask,
        thermal_intensity=avg_thermal_intensity, severity_ratio=severity_ratio
    )
    
    # Log results with risk analysis
    log_file = os.path.join(output_dir, "alerts.txt")
    with open(log_file, "a") as f:
        f.write(f"[{datetime.now()}] Enhanced Risk Analysis\n")
        f.write(f"   SSIM: {ssim_score:.4f}, ORB Matches: {orb_score}\n")
        f.write(f"   Change%: {change_percentage:.2f}%\n")
        f.write(f"   Risk Score: {risk_analysis['risk_score']:.1f}/100\n")
        f.write(f"   Risk Level: {risk_analysis['risk_level']}\n")
        f.write(f"   Alert: {risk_analysis['alert_status']}\n")
        f.write(f"   Factors: {', '.join(risk_analysis['risk_factors'])}\n\n")
    
    return {
        "ssim_score": ssim_score,
        "orb_score": orb_score,
        "change_percentage": change_percentage,
        "risk_score": risk_analysis["risk_score"],
        "risk_level": risk_analysis["risk_level"], 
        "alert": risk_analysis["alert_status"],
        "risk_factors": risk_analysis["risk_factors"]
    }
