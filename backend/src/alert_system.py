import os
from datetime import datetime

def log_alert(result, log_file="alerts/alerts.txt"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "a") as f:
        f.write(f"[{datetime.now()}] SSIM={result['ssim_score']:.3f}, "
                f"ORB={result['orb_score']:.3f}, "
                f"ALERT={'YES' if result['alert'] else 'NO'}\n")

def show_alert(result):
    if result["alert"]:
        print("⚠️ Rockfall Predicted! Immediate Action Required.")
    else:
        print("✅ Stable Pit, No Rockfall Detected.")
