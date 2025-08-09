# 🚀 Deployment Guide - Bhagavad Gita RAG Chatbot

This guide provides comprehensive instructions for deploying the Bhagavad Gita RAG Chatbot using different methods.

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (for containerized deployment)
- Git

## 🏃‍♂️ Quick Start (Docker - Recommended)

The fastest way to get the application running:

```bash
# Clone the repository
git clone <your-repo-url>
cd "Bhagwad Gita RAG Chatbot"

# Start the application with Docker Compose
docker-compose up --build

# Wait for initialization (first run may take 2-3 minutes)
# The backend will download ML models on first startup
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🛠 Manual Development Setup

### Backend Setup

```bash
# Navigate to project root
cd "Bhagwad Gita RAG Chatbot"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
cd backend
python main.py

# Or use uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# The frontend will be available at http://localhost:3000
```

## 🌐 Production Deployment

### Environment Variables

Create a `.env` file in the project root:

```env
# Backend Configuration
PYTHONPATH=/app
TRANSFORMERS_CACHE=/app/.cache
API_HOST=0.0.0.0
API_PORT=8000

# Frontend Configuration
REACT_APP_API_URL=http://your-backend-domain.com

# Security (for production)
CORS_ORIGINS=https://your-frontend-domain.com
```

### Docker Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f

# Scale services (if needed)
docker-compose up --scale backend=2 -d
```

### Cloud Platform Deployment

#### AWS Deployment

1. **Using AWS ECS:**
```bash
# Push images to ECR
aws ecr create-repository --repository-name gita-rag-backend
aws ecr create-repository --repository-name gita-rag-frontend

# Tag and push
docker tag gita-rag-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/gita-rag-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/gita-rag-backend:latest
```

2. **Using AWS App Runner:**
- Upload the source code to a GitHub repository
- Create App Runner service pointing to the repository
- Configure build settings with the appropriate Dockerfile

#### Google Cloud Platform

```bash
# Deploy to Cloud Run
gcloud run deploy gita-rag-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

gcloud run deploy gita-rag-frontend \
  --source ./frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Heroku Deployment

1. **Backend (Heroku):**
```bash
# Create Heroku app
heroku create your-gita-rag-api

# Set buildpack
heroku buildpacks:set heroku/python

# Deploy
git subtree push --prefix backend heroku main
```

2. **Frontend (Netlify/Vercel):**
```bash
# For Netlify
npm run build
# Upload the build folder to Netlify

# For Vercel
npx vercel --prod
```

## 🔧 Configuration

### Backend Configuration

Edit `backend/main.py` for customization:

```python
# CORS settings for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],  # Update for production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Frontend Configuration

Update `frontend/src/App.js`:

```javascript
// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-api-domain.com';
```

## 📊 Performance Optimization

### Backend Optimizations

1. **Model Caching:**
```python
# The T5 model is loaded once at startup
# Ensure adequate memory allocation (4GB+ recommended)
```

2. **Vector Caching:**
```python
# TF-IDF vectors are computed once during initialization
# Consider saving/loading pre-computed vectors for faster startup
```

3. **API Rate Limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/query")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def process_query(request: Request, query_request: QueryRequest):
    # ... existing code
```

### Frontend Optimizations

1. **Build Optimization:**
```bash
# Use production build
npm run build

# Analyze bundle size
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer build/static/js/*.js
```

2. **CDN Integration:**
```html
<!-- Add to public/index.html -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

## 🔒 Security Considerations

### Backend Security

1. **API Security:**
```python
# Add API key authentication
from fastapi.security import HTTPBearer
security = HTTPBearer()

@app.post("/query")
async def process_query(credentials: HTTPAuthorizationCredentials = Security(security)):
    # Validate API key
    if credentials.credentials != "your-api-key":
        raise HTTPException(status_code=401, detail="Invalid API key")
```

2. **Input Validation:**
```python
# Already implemented in Pydantic models
# Additional sanitization can be added in the service layer
```

### Frontend Security

1. **Environment Variables:**
```javascript
// Never expose sensitive data in frontend
// Use backend proxy for sensitive API calls
```

2. **Content Security Policy:**
```nginx
# Already configured in nginx.conf
add_header Content-Security-Policy "default-src 'self'..." always;
```

## 📈 Monitoring & Logging

### Application Monitoring

```python
# Add to backend/main.py
import logging
from fastapi.middleware.base import BaseHTTPMiddleware
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time:.2f}s")
        return response

app.add_middleware(LoggingMiddleware)
```

### Health Checks

```python
# Enhanced health check
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": rag_service.model is not None,
        "data_loaded": rag_service.data is not None,
        "vectorizer_ready": rag_service.vectorizer is not None
    }
```

## 🐛 Troubleshooting

### Common Issues

1. **Model Loading Errors:**
```bash
# Increase memory allocation
docker run --memory=4g your-image

# Clear transformers cache
rm -rf ~/.cache/huggingface/transformers/
```

2. **CORS Issues:**
```python
# Update CORS origins in main.py
allow_origins=["http://localhost:3000", "https://your-domain.com"]
```

3. **Port Conflicts:**
```bash
# Check port usage
lsof -i :8000
lsof -i :3000

# Use different ports
uvicorn main:app --port 8001
npm start # Will automatically use 3001 if 3000 is busy
```

4. **Docker Build Issues:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker-compose build --no-cache
```

## 📝 Maintenance

### Regular Tasks

1. **Update Dependencies:**
```bash
# Backend
pip list --outdated
pip install -r requirements.txt --upgrade

# Frontend
npm outdated
npm update
```

2. **Monitor Performance:**
```bash
# Check container stats
docker stats

# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

3. **Backup Data:**
```bash
# Backup dataset
tar -czf dataset-backup-$(date +%Y%m%d).tar.gz dataset/
```

## 🆘 Support

For issues and questions:
1. Check the application logs first
2. Review this deployment guide
3. Check the main README.md for additional information
4. Open an issue in the repository with:
   - Error logs
   - Environment details
   - Steps to reproduce

---

**Happy Deploying! 🚀**

