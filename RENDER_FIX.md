# Render Deployment Configuration

## Build Command
```
cd backend && pip install --upgrade pip && pip install -r requirements.txt
```

## Start Command  
```
cd backend && python app.py
```

## Environment Variables
Set in Render Dashboard:
- `PORT`: (auto-provided by Render)
- `PYTHON_VERSION`: 3.10.12

## Python Version
- Runtime specified in `runtime.txt`: python-3.10.12
- This avoids the Python 3.8.1 end-of-life warning

## Key Changes Made:
1. **Updated requirements.txt**: Pinned specific versions for stability
2. **opencv-python-headless**: Replaced opencv-python for server deployment (no GUI dependencies)
3. **runtime.txt**: Specifies Python 3.10.12 to avoid EOL version
4. **Upgraded pip**: Added pip upgrade in build command to avoid version warnings

## Deployment Steps:
1. Push these changes to GitHub
2. In Render, update build command to: `cd backend && pip install --upgrade pip && pip install -r requirements.txt`
3. Deploy with the new configuration