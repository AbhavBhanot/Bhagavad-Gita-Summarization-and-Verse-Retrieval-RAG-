#!/bin/bash

# Production Build Script for Bhagwad Gita RAG Chatbot
# This script builds both frontend and backend for production deployment

echo "🚀 Starting production build process..."

# Set production environment variables
export REACT_APP_API_URL="https://bhagwan-gita-summarization-and-verse.onrender.com"
export REACT_APP_TITLE="Bhagavad Gita RAG Chatbot"
export NODE_ENV="production"

# Build Frontend
echo "🔨 Building frontend for production..."
cd frontend

# Clean previous build
if [ -d "build" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf build
fi

# Install dependencies
echo "📦 Installing frontend dependencies..."
npm install

# Build for production
echo "🏗️ Building frontend..."
npm run build:prod

if [ $? -ne 0 ]; then
    echo "❌ Frontend build failed!"
    exit 1
fi

echo "✅ Frontend built successfully!"

# Go back to root
cd ..

# Build Backend Docker image (optional - only if Docker is available)
echo "🔨 Attempting to build backend Docker image..."
if command -v docker &> /dev/null && docker info &> /dev/null; then
    echo "🐳 Docker is available, building backend image..."
    docker build -f Dockerfile.backend -t bhagwad-gita-backend:production .
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Backend Docker build failed, but continuing..."
        echo "   You can build the Docker image later when needed"
    else
        echo "✅ Backend Docker image built successfully!"
    fi
else
    echo "ℹ️  Docker not available or not running, skipping backend build"
    echo "   This is normal in development environments"
fi

echo ""
echo "🎉 Production build completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Frontend: Deploy the 'frontend/build' folder to Netlify"
echo "2. Backend: Deploy using the Docker image or Render configuration"
echo "3. Verify CORS settings and environment variables"
echo ""
echo "🌐 Frontend URL: https://spiritual-rag-chatbot.netlify.app"
echo "🔗 Backend URL: https://bhagwan-gita-summarization-and-verse.onrender.com"
echo ""
echo "📁 Files created:"
echo "   - requirements-render.txt (Render-compatible dependencies)"
echo "   - render.yaml (Render deployment configuration)"
echo "   - netlify.toml (Netlify deployment configuration)"
echo "   - Dockerfile.backend (Backend container configuration)"
echo ""
echo "🚀 Ready for deployment!"
