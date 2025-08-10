# 🌐 Netlify Deployment Guide

This guide explains how to deploy the **frontend only** on Netlify while deploying the backend separately.

## ⚠️ Important Note

**Netlify is for frontend deployment only.** Your Python backend with scikit-learn and other ML dependencies cannot be deployed on Netlify. You need to deploy the backend separately on a platform that supports Python applications.

## 🚀 Frontend Deployment on Netlify

### 1. Prepare Your Repository

Your repository is already configured with:
- `netlify.toml` - Netlify build configuration
- Frontend code in the `frontend/` directory
- Environment variable configuration in `App.js`

### 2. Deploy to Netlify

1. **Connect your GitHub repository to Netlify:**
   - Go to [netlify.com](https://netlify.com)
   - Click "New site from Git"
   - Choose GitHub and select your repository

2. **Configure build settings:**
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/build`
   - These are already set in `netlify.toml`

3. **Set environment variables:**
   - Go to Site settings → Environment variables
   - Add: `REACT_APP_API_URL` = `https://your-backend-domain.com`

### 3. Backend Deployment Options

You need to deploy your backend separately. Here are recommended options:

#### Option A: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy backend
cd backend
railway login
railway init
railway up
```

#### Option B: Render
- Create a new Web Service on Render
- Connect your GitHub repository
- Set build command: `pip install -r requirements-stable.txt`
- Set start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

#### Option C: Heroku
```bash
# Install Heroku CLI
# Create Procfile with: web: uvicorn main:app --host 0.0.0.0 --port $PORT
heroku create your-app-name
git push heroku main
```

#### Option D: DigitalOcean App Platform
- Create a new app from your GitHub repository
- Select Python as the runtime
- Set build command and start command

## 🔧 Environment Configuration

### Frontend (.env.local)
```env
REACT_APP_API_URL=https://your-backend-domain.com
```

### Backend (.env)
```env
PYTHONPATH=/app
TRANSFORMERS_CACHE=/app/.cache
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=https://your-frontend-domain.netlify.app
```

## 🚨 Common Issues & Solutions

### 1. CORS Errors
Make sure your backend allows requests from your Netlify domain:
```python
# In your backend CORS configuration
CORS_ORIGINS = [
    "https://your-app.netlify.app",
    "http://localhost:3000"  # For local development
]
```

### 2. API Connection Issues
- Verify `REACT_APP_API_URL` is set correctly in Netlify
- Ensure your backend is accessible from the internet
- Check that your backend's CORS settings allow your Netlify domain

### 3. Build Failures
- Ensure Node.js version compatibility (set to 18 in netlify.toml)
- Check that all frontend dependencies are in package.json
- Verify the build command works locally

## 📱 Testing Your Deployment

1. **Test frontend locally:**
   ```bash
   cd frontend
   npm run build
   # Should create a build/ directory
   ```

2. **Test backend locally:**
   ```bash
   cd backend
   python main.py
   # Should start on http://localhost:8000
   ```

3. **Test API connection:**
   - Set `REACT_APP_API_URL=http://localhost:8000` in frontend/.env.local
   - Start both frontend and backend
   - Verify API calls work

## 🔄 Deployment Workflow

1. **Develop locally** with both frontend and backend running
2. **Deploy backend** to your chosen platform
3. **Update frontend** with the backend URL
4. **Deploy frontend** to Netlify
5. **Test the complete system**

## 📚 Additional Resources

- [Netlify Build Configuration](https://docs.netlify.com/configure-builds/overview/)
- [Railway Deployment](https://docs.railway.app/deploy/deployments)
- [Render Deployment](https://render.com/docs/deploy-an-app)
- [Heroku Python Deployment](https://devcenter.heroku.com/categories/python-support)
