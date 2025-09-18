from flask import Flask, jsonify, send_file
from flask_cors import CORS
import os

from src.main import run_pipeline

app = Flask(__name__)
CORS(app)  # allow frontend (React/Vite) to access backend


@app.get("/status")
def status():
    """
    Run the rockfall detection pipeline and return its result.
    """
    try:
        result = run_pipeline()
        return jsonify({"success": True, "result": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.get("/image/<stage>")
def get_image(stage):
    """
    Return images from different stages of the pipeline.
    Stage options: baseline, new, masked, segmented, diff
    """
    path_map = {
        "baseline": "data/normal/img1_normal.png",
        "new": "data/rockfall/img2_rockfall.png",
        "masked": "outputs/masked.png",
        "segmented": "outputs/segmented.png",
        "diff": "outputs/diff.png",
    }

    if stage not in path_map:
        return jsonify({"error": f"Invalid stage '{stage}'"}), 400

    filepath = path_map[stage]

    if not os.path.exists(filepath):
        return jsonify({"error": f"File not found: {filepath}"}), 404

    return send_file(filepath, mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
