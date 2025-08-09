#!/bin/bash

# Backend Deployment Script
# This script helps deploy the backend to various platforms

set -e

echo "🚀 Backend Deployment Script"
echo "=============================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Function to deploy to Railway
deploy_railway() {
    echo "📦 Deploying to Railway..."
    
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI not found. Installing..."
        npm install -g @railway/cli
    fi
    
    cd backend
    railway login
    railway init
    railway up
    echo "✅ Railway deployment initiated!"
}

# Function to deploy to Render
deploy_render() {
    echo "🌐 Deploying to Render..."
    echo "📝 Manual steps required:"
    echo "1. Go to https://render.com"
    echo "2. Create a new Web Service"
    echo "3. Connect your GitHub repository"
    echo "4. Set build command: pip install -r requirements.txt"
    echo "5. Set start command: uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo "6. Set environment variables:"
    echo "   - PYTHONPATH: /app"
    echo "   - TRANSFORMERS_CACHE: /app/.cache"
    echo "   - CORS_ORIGINS: https://your-frontend-domain.netlify.app"
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "🦸 Deploying to Heroku..."
    
    if ! command -v heroku &> /dev/null; then
        echo "❌ Heroku CLI not found. Please install from: https://devcenter.heroku.com/articles/heroku-cli"
        exit 1
    fi
    
    # Create Procfile if it doesn't exist
    if [ ! -f "Procfile" ]; then
        echo "📝 Creating Procfile..."
        echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile
    fi
    
    # Create runtime.txt if it doesn't exist
    if [ ! -f "runtime.txt" ]; then
        echo "📝 Creating runtime.txt..."
        echo "python-3.11.7" > runtime.txt
    fi
    
    echo "🚀 Deploying to Heroku..."
    heroku create
    git add Procfile runtime.txt
    git commit -m "Add Heroku deployment files"
    git push heroku main
    
    echo "✅ Heroku deployment completed!"
}

# Function to test locally
test_local() {
    echo "🧪 Testing backend locally..."
    
    if [ ! -d "venv" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv venv
    fi
    
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
    
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    
    echo "🚀 Starting backend server..."
    cd backend
    python main.py
}

# Main menu
echo ""
echo "Choose deployment option:"
echo "1) Deploy to Railway (Recommended)"
echo "2) Deploy to Render"
echo "3) Deploy to Heroku"
echo "4) Test locally"
echo "5) Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        deploy_railway
        ;;
    2)
        deploy_render
        ;;
    3)
        deploy_heroku
        ;;
    4)
        test_local
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
