# 🚀 Deployment Guide - AI-Based Rockfall Prediction System

## **Quick Deploy Options (Ranked by Ease)**

### **🥇 Option 1: Railway (RECOMMENDED - Free + Easy)**

**Why Railway?**
- ✅ Supports ML models (YOLO) out of the box
- ✅ Free tier: 500 hours/month
- ✅ Auto-deploys from GitHub
- ✅ Handles both Python backend + static frontend

**Steps:**
1. **Go to**: https://railway.app
2. **Sign up** with GitHub account
3. **New Project** → **Deploy from GitHub repo**
4. **Select**: `smallBrat/SIH` repository
5. **Auto-deployment** starts immediately!

**URL**: Your app will be live at `https://your-app-name.railway.app`

---

### **🥈 Option 2: Render (Good Alternative)**

**Why Render?**
- ✅ Generous free tier
- ✅ Automatic HTTPS
- ✅ Great for Python ML apps

**Steps:**
1. **Go to**: https://render.com
2. **Connect GitHub** account
3. **New Web Service** → Select your repo
4. **Build Command**: `cd backend && pip install -r requirements.txt`
5. **Start Command**: `cd backend && python app.py`

---

### **🥉 Option 3: Heroku (Traditional)**

**Setup:**
1. **Install Heroku CLI**: https://devcenter.heroku.com/articles/heroku-cli
2. **Login**: `heroku login`
3. **Create app**: `heroku create your-app-name`
4. **Deploy**: `git push heroku main`

---

## **🔧 Configuration Files (Already Created)**

### **Files Added to Your Project:**
- ✅ `Procfile` - Tells Heroku/Railway how to run your app
- ✅ `railway.json` - Railway-specific configuration
- ✅ `requirements.txt` - Python dependencies (already exists)

### **Environment Variables Needed:**
```bash
PORT=5000
FLASK_ENV=production
YOLO_VERBOSE=False
TOKENIZERS_PARALLELISM=false
```

---

## **🎯 Deployment Steps for Railway (Detailed)**

### **Step 1: Prepare Repository**
Your repo is already ready! The deployment files are in place.

### **Step 2: Deploy on Railway**
1. **Visit**: https://railway.app
2. **Sign up/Login** with GitHub
3. **Dashboard** → **New Project**
4. **Deploy from GitHub repo**
5. **Select**: `smallBrat/SIH`
6. **Railway detects**: Python + Node.js project
7. **Auto-build starts**

### **Step 3: Configure Environment**
In Railway dashboard:
- **Variables** tab → **Add variables**:
  ```
  PORT=5000
  FLASK_ENV=production
  YOLO_VERBOSE=False
  ```

### **Step 4: Monitor Deployment**
- **Deployments** tab shows build progress
- **Logs** tab shows real-time deployment logs
- **Settings** → **Domains** shows your live URL

---

## **📱 Frontend Deployment Options**

### **Option A: Serve with Flask (Simplest)**
Your Flask app can serve the built React frontend:

```python
# Add to app.py
from flask import send_from_directory

@app.route('/')
def serve_frontend():
    return send_from_directory('../frontend/build', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend/build', path)
```

### **Option B: Separate Frontend Deployment**
Deploy frontend separately on:
- **Netlify**: https://netlify.com (drag & drop `frontend/build` folder)
- **Vercel**: https://vercel.com (connects to GitHub automatically)

---

## **🔍 Testing Your Deployment**

### **Backend API Endpoints:**
- `GET /health` - Check if API is running
- `GET /status` - Run rockfall detection pipeline
- `GET /image/stage1` - Get Stage 1 image
- `GET /image/stage2` - Get Stage 2 image
- ... (all 5 stages)

### **Test Commands:**
```bash
# Check health
curl https://your-app.railway.app/health

# Run detection
curl https://your-app.railway.app/status

# Get stage 1 image
curl https://your-app.railway.app/image/stage1
```

---

## **⚡ Performance Optimization**

### **For Large Model Files:**
If YOLO model is too large (>100MB), consider:
1. **Git LFS** for model files
2. **Download on startup** instead of including in repo
3. **Model optimization** (quantization)

### **Memory Management:**
```python
# Add to requirements.txt
gunicorn==20.1.0

# Create gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 1  # Important: Keep at 1 for ML models
timeout = 300  # 5 minutes for ML processing
max_requests = 100
max_requests_jitter = 10
```

---

## **🚨 Troubleshooting**

### **Common Issues:**
1. **YOLO Model Loading**: Increase memory limit in platform settings
2. **Build Timeout**: Increase build timeout (usually in platform settings)
3. **Port Issues**: Ensure `app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))`

### **Quick Fixes:**
```python
# Add to app.py top
import os
port = int(os.environ.get("PORT", 5000))

# Update app.run
app.run(host="0.0.0.0", port=port, debug=False)
```

---

## **🎉 Go Live Now!**

**Recommended Path:**
1. **Railway** (easiest): https://railway.app → Deploy from GitHub
2. **Wait 5-10 minutes** for build to complete
3. **Access your live URL**: `https://your-app.railway.app`
4. **Test endpoints**: `/health`, `/status`, `/image/stage1`

Your AI-Based Rockfall Prediction System will be **LIVE** and accessible worldwide! 🌍