# Deployment Guide for Bhagwad Gita RAG Chatbot

This guide covers deploying the backend to Render and frontend to Netlify.

## 🌐 Backend Deployment (Render)

### Prerequisites
- Render account
- GitHub repository connected to Render

### Steps

1. **Connect Repository to Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Web Service**
   - **Name**: `bhagwad-gita-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements-stable.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

3. **Environment Variables**
   ```
   PYTHON_VERSION=3.11.0
   CORS_ORIGINS=https://spiritual-rag-chatbot.netlify.app,http://localhost:3000,http://localhost:8000
   TRANSFORMERS_CACHE=/opt/render/project/src/.cache
   PYTHONPATH=/opt/render/project/src
   LOG_LEVEL=INFO
   MODEL_NAME=t5-base
   MAX_LENGTH=512
   SUMMARY_MAX_LENGTH=150
   DEFAULT_TOP_N=5
   MAX_TOP_N=20
   MAX_QUERY_LENGTH=500
   WORKERS=1
   MAX_WORKERS=4
   HEALTH_CHECK_INTERVAL=30s
   HEALTH_CHECK_TIMEOUT=30s
   HEALTH_CHECK_RETRIES=3
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for build and deployment to complete
   - Note the service URL (e.g., `https://bhagwan-gita-summarization-and-verse.onrender.com`)

## 🎨 Frontend Deployment (Netlify)

### Prerequisites
- Netlify account
- GitHub repository connected to Netlify

### Steps

1. **Connect Repository to Netlify**
   - Go to [Netlify Dashboard](https://app.netlify.com/)
   - Click "New site from Git"
   - Connect your GitHub repository

2. **Build Settings**
   - **Build command**: `cd frontend && npm install && npm run build:prod`
   - **Publish directory**: `frontend/build`
   - **Node version**: `18`

3. **Environment Variables**
   ```
   REACT_APP_API_URL=https://bhagwan-gita-summarization-and-verse.onrender.com
   REACT_APP_TITLE=Bhagavad Gita RAG Chatbot
   ```

4. **Deploy**
   - Click "Deploy site"
   - Wait for build and deployment to complete
   - Your site will be available at the provided Netlify URL

## 🔧 Local Testing

### Backend
```bash
# Install dependencies
pip install -r requirements-stable.txt

# Set environment variables
export CORS_ORIGINS="http://localhost:3000,http://localhost:8000,https://spiritual-rag-chatbot.netlify.app"

# Run backend
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend
```bash
# Install dependencies
cd frontend
npm install

# Set environment variables
export REACT_APP_API_URL="http://localhost:8000"

# Run frontend
npm start
```

## 🚀 Production Build

Use the provided build script:
```bash
./build_production.sh
```

This script will:
1. Build the frontend for production
2. Build the backend Docker image
3. Set up all necessary environment variables

## 🔍 Verification

### Backend Health Check
```bash
curl https://bhagwan-gita-summarization-and-verse.onrender.com/health
```

### Frontend API Connection
1. Open the Netlify site
2. Try searching for a spiritual question
3. Check browser console for any API errors

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Verify `CORS_ORIGINS` includes your Netlify domain
   - Check backend logs for CORS configuration

2. **Model Loading Issues**
   - Ensure `TRANSFORMERS_CACHE` is set correctly
   - Check if the dataset directory is accessible

3. **Build Failures**
   - Verify Node.js version (18.x)
   - Check Python version (3.11.x)
   - Ensure all dependencies are compatible

4. **API Connection Issues**
   - Verify the backend URL is correct
   - Check if the backend service is running
   - Verify environment variables are set

### Logs
- **Render**: Check the "Logs" tab in your service dashboard
- **Netlify**: Check the "Deploys" tab for build logs

## 📞 Support

If you encounter issues:
1. Check the logs for error messages
2. Verify all environment variables are set correctly
3. Ensure the dataset files are present in the repository
4. Test the API endpoints individually

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [Netlify Documentation](https://docs.netlify.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
