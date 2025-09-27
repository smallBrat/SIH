from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os
import sys
from datetime import datetime

# Set environment variables to prevent torch/YOLO from causing Flask reloads
os.environ['YOLO_VERBOSE'] = 'False'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Ensure we're in the correct directory
backend_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(backend_dir)

# Add current directory to Python path
sys.path.insert(0, backend_dir)

from src.main import run_pipeline

app = Flask(__name__)
CORS(app)  # allow frontend (React/Vite) to access backend

# Ensure required directories exist at startup
required_dirs = ["outputs", "data", "data/normal", "data/rockfall", "models"]
for dir_path in required_dirs:
    os.makedirs(dir_path, exist_ok=True)

print("🏗️  Required directories verified")


@app.route('/')
def home():
    """Root endpoint with API documentation"""
    return jsonify({
        "message": "🎯 Rockfall Detection API",
        "status": "✅ Live and Ready",
        "version": "1.0.0",
        "endpoints": {
            "/run-pipeline": "POST - Run complete 5-stage rockfall detection",
            "/image/<stage>": "GET - Retrieve processed images (stage1-stage5)",
            "/health": "GET - Health check endpoint"
        },
        "stages": {
            "stage1": "Preprocessed images",
            "stage2": "Temporal analysis", 
            "stage3": "Thermal change detection",
            "stage4": "Pit masking (precise boundaries)",
            "stage5": "Composite overlay visualization"
        },
        "deployment": "Render Cloud Platform",
        "docs": "Visit GitHub: smallBrat/SIH for documentation"
    })


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Rockfall Detection API"
    }), 200


def convert_numpy_types(obj):
    """Convert numpy types to Python native types for JSON serialization"""
    import numpy as np
    
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


@app.get("/status")
def status():
    """
    Run the rockfall detection pipeline and return its result.
    """
    try:
        import traceback
        print("🔥 Flask: Starting enhanced pipeline execution...")
        
        # Set environment variables to prevent YOLO from causing reloads
        os.environ['YOLO_VERBOSE'] = 'False'
        
        result = run_pipeline()
        print("✅ Flask: Pipeline execution completed successfully")
        
        # Convert numpy types to JSON-serializable types
        result_serializable = convert_numpy_types(result)
        
        return jsonify({"success": True, "result": result_serializable})
    except Exception as e:
        print(f"❌ Flask: Error occurred: {e}")
        traceback.print_exc()
        
        # More user-friendly error response
        error_message = str(e)
        if "YOLO" in error_message or "torch" in error_message:
            error_message = "YOLO model loading issue. Please restart the server."
        elif "OpenCV" in error_message:
            error_message = "Image processing error. Check image files."
            
        return jsonify({
            "success": False, 
            "error": error_message,
            "error_type": type(e).__name__,
            "suggestion": "Try restarting the server if the issue persists"
        }), 500


@app.get("/image/<stage>")
def get_image(stage):
    """
    Return images from the 5-stage rockfall detection pipeline.
    Stage options: stage1, stage2, stage3, stage4, stage5
    """
    path_map = {
        "stage1": "outputs/stage1_baseline.png",           # Stage 1: Baseline Image
        "stage2": "outputs/stage2_new.png",               # Stage 2: New Captured Image  
        "stage3": "outputs/stage3_changes.png",           # Stage 3: Changes Detected (Light Colors)
        "stage4": "outputs/stage4_segmentation.png",      # Stage 4: Non-Pit Actor Removal
        "stage5": "outputs/stage5_visualization.png",     # Stage 5: Vibrant Color Visualization
        "stage5_contrast": "outputs/stage5_high_contrast.png",  # Stage 5: High Contrast Version
        
        # Legacy endpoints for backward compatibility
        "baseline": "outputs/stage1_baseline.png",
        "new": "outputs/stage2_new.png", 
        "changes": "outputs/stage3_changes.png",
        "segmentation": "outputs/stage4_segmentation.png",
        "visualization": "outputs/stage5_visualization.png",
        "high_contrast": "outputs/stage5_high_contrast.png",
    }

    if stage not in path_map:
        return jsonify({
            "error": f"Invalid stage '{stage}'", 
            "valid_stages": list(path_map.keys()),
            "description": {
                "stage1": "Baseline Image (enhanced preprocessing)",
                "stage2": "New Captured Image (enhanced preprocessing)", 
                "stage3": "Changes Detected (subtraction + dilation)",
                "stage4": "Non-Pit Actor Removal (segmentation filtering)",
                "stage5": "Visualization (color-coded superposition)"
            }
        }), 400

    filepath = path_map[stage]

    if not os.path.exists(filepath):
        return jsonify({"error": f"File not found: {filepath}. Run /status first to generate images."}), 404

    return send_file(filepath, mimetype="image/png")

@app.get("/pipeline/info")
def pipeline_info():
    """
    Get information about the 5-stage pipeline process
    """
    return jsonify({
        "pipeline_stages": [
            {
                "stage": 1,
                "name": "Baseline Image",
                "description": "Enhanced preprocessing with noise reduction and contrast enhancement",
                "endpoint": "/image/stage1"
            },
            {
                "stage": 2, 
                "name": "New Captured Image",
                "description": "Latest image with same preprocessing and size normalization",
                "endpoint": "/image/stage2"
            },
            {
                "stage": 3,
                "name": "Changes Detected", 
                "description": "Image subtraction with light color coding (light red, orange, yellow)",
                "endpoint": "/image/stage3"
            },
            {
                "stage": 4,
                "name": "Binary Pit Mask",
                "description": "New image processed: WHITE=pit areas, BLACK=removed non-pit actors",
                "endpoint": "/image/stage4"
            },
            {
                "stage": 5,
                "name": "Visualization Phase",
                "description": "Vibrant color-coded superposition (bright red/yellow) for final results",
                "endpoint": "/image/stage5"
            },
            {
                "stage": "5b",
                "name": "High Contrast Visualization",
                "description": "Maximum contrast version with pure vibrant colors",
                "endpoint": "/image/stage5_contrast"
            }
        ],
        "usage": "Call /status to run the pipeline, then access images via /image/<stage>"
    })


if __name__ == "__main__":
    # Get port from environment variable (for deployment platforms)
    port = int(os.environ.get("PORT", 5000))
    
    # Disable debug mode to prevent auto-reload issues with YOLO model loading
    print(f"🚀 Starting Flask server on http://0.0.0.0:{port}")
    print("📊 Rockfall Detection API Ready")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
