#!/bin/bash

# Deploy Backend Script for Bhagwad Gita RAG Chatbot
# This script deploys the backend using the stable requirements

echo "🚀 Starting backend deployment..."

# Check if we're in the right directory
if [ ! -f "requirements-stable.txt" ]; then
    echo "❌ Error: requirements-stable.txt not found. Please run this script from the project root."
    exit 1
fi

# Build the Docker image with stable requirements
echo "🔨 Building Docker image..."
docker build -f Dockerfile.backend -t bhagwad-gita-backend:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed. Check the error messages above."
    exit 1
fi

echo "✅ Docker image built successfully!"

# Run the container
echo "🐳 Starting container..."
docker run -d \
    --name bhagwad-gita-backend \
    -p 8000:8000 \
    --restart unless-stopped \
    bhagwad-gita-backend:latest

if [ $? -ne 0 ]; then
    echo "❌ Failed to start container. Check if a container with the same name already exists."
    echo "💡 You can remove existing containers with: docker rm -f bhagwad-gita-backend"
    exit 1
fi

echo "✅ Backend deployed successfully!"
echo "🌐 Backend is running on http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"

# Show container status
echo "📋 Container status:"
docker ps | grep bhagwad-gita-backend
