import os
from datetime import datetime

def log_alert(result, log_file="alerts/alerts.txt"):
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Get data from the new structure
    risk_assessment = result.get('risk_assessment', {})
    detection_stats = result.get('detection_stats', {})
    
    # Remove emojis from alert message for file logging
    alert_message = result.get('message', 'No message')
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
        f.write(f"   Risk Score: {risk_assessment.get('risk_score', 0):.1f}/100\n")
        f.write(f"   Risk Level: {risk_assessment.get('risk_level', 'UNKNOWN')}\n")
        f.write(f"   Change%: {risk_assessment.get('change_percentage', 0):.2f}%\n")
        f.write(f"   High Intensity: {detection_stats.get('high_intensity_changes', 0)} pixels\n")
        f.write(f"   Alert: {'YES' if result.get('alert', False) else 'NO'}\n")
        f.write(f"   Processing: {'SUCCESS' if result.get('processing_successful', False) else 'ISSUES'}\n")
        f.write(f"   Message: {alert_message_clean}\n\n")

def show_alert(result):
    """Enhanced alert display with risk levels and detailed messaging"""
    
    # Display the alert message with appropriate formatting
    alert_message = result.get("message", "Unknown status")
    print(alert_message)
    
    # Get risk assessment data from the new structure
    risk_assessment = result.get("risk_assessment", {})
    detection_stats = result.get("detection_stats", {})
    
    # Additional details for operators
    risk_score = risk_assessment.get("risk_score", 0)
    risk_level = risk_assessment.get("risk_level", "UNKNOWN")
    change_percentage = risk_assessment.get("change_percentage", 0)
    
    print(f"📈 Detection Details:")
    print(f"   • Risk Score: {risk_score:.1f}/100")
    print(f"   • Risk Level: {risk_level}")
    print(f"   • Change Area: {change_percentage:.2f}% of image")
    print(f"   • High Intensity Changes: {detection_stats.get('high_intensity_changes', 0)} pixels")
    print(f"   • Total Changes: {detection_stats.get('total_changes', 0):.2f}%")
    
    # Show processing status
    processing_successful = result.get("processing_successful", False)
    print(f"   • Processing Status: {'✅ Success' if processing_successful else '❌ Issues detected'}")
    
    # Show confidence if available
    confidence = risk_assessment.get("confidence", 0)
    if confidence > 0:
        print(f"   • Confidence Level: {confidence:.1f}%")
    
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
