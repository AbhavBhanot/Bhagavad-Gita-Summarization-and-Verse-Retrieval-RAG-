#!/bin/bash

# Quick Start Script for Bhagwad Gita RAG Chatbot
# This script sets up the development environment and runs both services

echo "🚀 Quick Start for Bhagwad Gita RAG Chatbot"
echo "=============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or later."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or later."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-stable.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies!"
    exit 1
fi

echo "✅ Python dependencies installed!"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies!"
    exit 1
fi

echo "✅ Node.js dependencies installed!"
cd ..

# Set environment variables for local development
export CORS_ORIGINS="http://localhost:3000,http://localhost:8000,https://spiritual-rag-chatbot.netlify.app"
export REACT_APP_API_URL="http://localhost:8000"

echo "🌍 Environment variables set for local development"
echo "   CORS_ORIGINS: $CORS_ORIGINS"
echo "   REACT_APP_API_URL: $REACT_APP_API_URL"

echo ""
echo "🎯 Starting services..."
echo "   Backend will run on: http://localhost:8000"
echo "   Frontend will run on: http://localhost:3000"
echo ""
echo "📋 To start services manually:"
echo "   1. Backend: cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
echo "   2. Frontend: cd frontend && npm start"
echo ""
echo "🔗 Quick links:"
echo "   - Backend API: http://localhost:8000"
echo "   - Backend Docs: http://localhost:8000/docs"
echo "   - Frontend: http://localhost:3000"
echo ""
echo "🚀 Ready to start development!"
