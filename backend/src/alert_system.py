import os
from datetime import datetime

def log_alert(result, log_file="alerts/alerts.txt"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Remove emojis from alert message for file logging
    alert_message = result.get('alert_message', 'No message')
    # Simple emoji removal - replace common emojis with text
    alert_message_clean = (alert_message
                          .replace('🚨', 'CRITICAL RISK')
                          .replace('⚠️', 'HIGH RISK') 
                          .replace('🔶', 'MODERATE RISK')
                          .replace('🔹', 'LOW RISK')
                          .replace('✅', 'STABLE')
                          .replace('❌', 'ERROR'))

    with open(log_file, "a", encoding='utf-8') as f:
        f.write(f"[{datetime.now()}] Enhanced Alert Log\n")
        f.write(f"   SSIM: {result.get('ssim_score', 0):.3f}\n")
        f.write(f"   ORB: {result.get('orb_score', 0):.0f}\n") 
        f.write(f"   Change%: {result.get('change_percentage', 0):.2f}%\n")
        f.write(f"   Risk Score: {result.get('risk_score', 0):.1f}/100\n")
        f.write(f"   Risk Level: {result.get('risk_level', 'UNKNOWN')}\n")
        f.write(f"   Alert: {'YES' if result.get('alert', False) else 'NO'}\n")
        f.write(f"   Factors: {', '.join(result.get('risk_factors', []))}\n")
        f.write(f"   Message: {alert_message_clean}\n\n")

def show_alert(result):
    """Enhanced alert display with risk levels and detailed messaging"""
    
    # Display the alert message with appropriate formatting
    alert_message = result.get("alert_message", "Unknown status")
    print(alert_message)
    
    # Additional details for operators
    risk_score = result.get("risk_score", 0)
    risk_level = result.get("risk_level", "UNKNOWN")
    change_percentage = result.get("change_percentage", 0)
    
    print(f"📈 Detection Details:")
    print(f"   • Risk Score: {risk_score:.1f}/100")
    print(f"   • Risk Level: {risk_level}")
    print(f"   • Change Area: {change_percentage:.2f}% of image")
    print(f"   • SSIM Score: {result.get('ssim_score', 0):.3f}")
    print(f"   • ORB Matches: {result.get('orb_score', 0):.0f}")
    
    # Show risk factors if available
    risk_factors = result.get("risk_factors", [])
    if risk_factors:
        print(f"   • Risk Factors: {', '.join(risk_factors)}")
    
    # Recommendations based on risk level
    if risk_level == "CRITICAL":
        print("🚨 IMMEDIATE ACTIONS REQUIRED:")
        print("   • Evacuate personnel immediately")
        print("   • Stop all operations")  
        print("   • Contact emergency response team")
    elif risk_level == "HIGH":
        print("⚠️ HIGH PRIORITY ACTIONS:")
        print("   • Restrict access to high-risk areas")
        print("   • Increase monitoring frequency")
        print("   • Prepare evacuation procedures")
    elif risk_level == "MODERATE":
        print("🔶 PRECAUTIONARY MEASURES:")
        print("   • Monitor area closely")
        print("   • Brief personnel on safety protocols")
        print("   • Consider reducing activity")
    elif risk_level == "LOW":
        print("🔹 AWARENESS MEASURES:")
        print("   • Continue normal monitoring")
        print("   • Document changes for trends")
    else:
        print("✅ NORMAL OPERATIONS:")
        print("   • Continue routine monitoring")
        print("   • No immediate action required")
