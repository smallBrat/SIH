# Render Deployment Quick Fix

## Issue
- Render ignoring `runtime.txt` 
- Python 3.8.1 EOL version being used
- OpenCV compilation failing

## Solution
1. **Lightweight Requirements**: Switched to pre-built wheels and CPU-only PyTorch
2. **Python 3.9.18**: More stable on Render than 3.10
3. **No Compilation**: All packages are pre-built wheels

## New Build Command for Render:
```bash
cd backend && pip install --upgrade pip && pip install -r requirements.txt
```

## Environment Variables in Render Dashboard:
- Set `PYTHON_VERSION` to `3.9.18`
- This overrides the auto-detection

## Key Changes:
- ✅ CPU-only PyTorch (faster install, no CUDA dependencies)
- ✅ Older, stable package versions
- ✅ Pre-built wheels only
- ✅ Python 3.9.18 for better Render compatibility

## Deploy Steps:
1. Push these changes
2. In Render dashboard → Environment Variables → Add `PYTHON_VERSION=3.9.18`
3. Redeploy

This should resolve the build issues completely!