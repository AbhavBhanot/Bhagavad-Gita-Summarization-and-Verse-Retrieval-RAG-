# Render Deployment Fix for Bhagwad Gita RAG Chatbot

## Problem
The original deployment was failing due to scikit-learn compilation issues during the build process. This happens when Python packages try to compile C extensions on Render's build servers.

## Solution
We've created a stable requirements file and updated the Dockerfile to avoid compilation issues.

## Files Changed
1. **`requirements-stable.txt`** - Contains stable, pre-compiled package versions
2. **`Dockerfile.backend`** - Updated to use Python 3.11 and stable requirements
3. **`deploy_backend.sh`** - Updated deployment script

## Render Deployment Steps

### Option 1: Use Docker (Recommended)
1. In your Render dashboard, create a new **Web Service**
2. Connect your GitHub repository
3. Set the following configuration:
   - **Build Command**: `docker build -f Dockerfile.backend -t backend .`
   - **Start Command**: `docker run -p $PORT:8000 backend`
   - **Environment Variables**:
     - `PORT`: 8000
     - `PYTHONPATH`: /app
     - `TRANSFORMERS_CACHE`: /app/.cache

### Option 2: Direct Python Deployment
1. In your Render dashboard, create a new **Web Service**
2. Connect your GitHub repository
3. Set the following configuration:
   - **Build Command**: `pip install -r requirements-stable.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**:
     - `PORT`: 8000
     - `PYTHONPATH`: /app
     - `TRANSFORMERS_CACHE`: /app/.cache

## Key Changes Made

### 1. Stable Package Versions
- **scikit-learn**: 1.3.0 (stable, pre-compiled)
- **pandas**: 1.5.3 (compatible with Python 3.11)
- **numpy**: 1.24.3 (stable version)
- **torch**: 2.0.1 (stable version)

### 2. Python Version
- Updated to Python 3.11 (more stable than 3.10)
- Matches runtime.txt specification

### 3. Build Optimizations
- Added `--only-binary=all` flag to force pre-compiled wheels
- Updated pip, setuptools, and wheel before installing packages
- Added environment variables to prevent compilation issues

## Testing Locally
Before deploying to Render, test locally:

```bash
# Make the deployment script executable
chmod +x deploy_backend.sh

# Run the deployment script
./deploy_backend.sh
```

## Troubleshooting
If you still encounter issues:

1. **Check Render logs** for specific error messages
2. **Verify Python version** matches runtime.txt
3. **Clear Render cache** by redeploying
4. **Use Docker option** if Python deployment fails

## Alternative: Use Railway
Railway often has better Python support and fewer compilation issues:
1. Install Railway CLI: `npm i -g @railway/cli`
2. Run: `railway login && railway init`
3. Deploy: `railway up`

## Success Indicators
- Build completes without Cython compilation errors
- Health check endpoint responds: `/health`
- API endpoints are accessible
- No scikit-learn compilation warnings in logs
