# Railway Deployment Configuration

# 1. Create railway.json in root directory
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "cd backend && python app.py"
  }
}

# 2. Add Procfile in root directory  
web: cd backend && python app.py

# 3. Set environment variables in Railway dashboard:
PORT=5000
FLASK_ENV=production
YOLO_VERBOSE=False