#!/bin/bash

# Bhagavad Gita RAG Chatbot - Startup Script
# This script sets up and starts the application

set -e  # Exit on any error

echo "🕉️  Bhagavad Gita RAG Chatbot - Starting Application"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi

    print_success "Docker and Docker Compose are available"
}

# Check if required files exist
check_files() {
    required_files=(
        "docker-compose.yml"
        "Dockerfile.backend"
        "Dockerfile.frontend" 
        "requirements.txt"
        "dataset/BWG data"
        "dataset/PYS Data"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -e "$file" ]]; then
            print_error "Required file/directory not found: $file"
            echo "Please ensure you're running this script from the project root directory."
            exit 1
        fi
    done

    print_success "All required files found"
}

# Stop any existing containers
cleanup_existing() {
    print_status "Cleaning up any existing containers..."
    docker-compose down --remove-orphans 2>/dev/null || true
    print_success "Cleanup completed"
}

# Build and start the application
start_application() {
    print_status "Building and starting the application..."
    print_warning "First startup may take 2-3 minutes to download ML models"
    
    # Build images
    print_status "Building Docker images..."
    docker-compose build

    # Start services
    print_status "Starting services..."
    docker-compose up -d

    print_success "Application started successfully!"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for backend
    echo -n "Waiting for backend to be ready"
    max_attempts=60
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
            echo ""
            print_success "Backend is ready!"
            break
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done

    if [ $attempt -eq $max_attempts ]; then
        echo ""
        print_error "Backend failed to start within expected time"
        print_status "Checking backend logs:"
        docker-compose logs backend
        exit 1
    fi

    # Wait for frontend
    echo -n "Waiting for frontend to be ready"
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -sf http://localhost:3000 > /dev/null 2>&1; then
            echo ""
            print_success "Frontend is ready!"
            break
        fi
        echo -n "."
        sleep 2
        ((attempt++))
    done

    if [ $attempt -eq $max_attempts ]; then
        echo ""
        print_warning "Frontend may still be starting. Check http://localhost:3000 in a moment."
    fi
}

# Display application information
show_info() {
    echo ""
    echo "🎉 Application is now running!"
    echo "================================"
    echo ""
    echo "📱 Frontend Application: http://localhost:3000"
    echo "🔌 Backend API:          http://localhost:8000"
    echo "📚 API Documentation:    http://localhost:8000/docs"
    echo "📋 Alternative Docs:     http://localhost:8000/redoc"
    echo ""
    echo "🔍 Useful Commands:"
    echo "   View logs:       docker-compose logs -f"
    echo "   Stop app:        docker-compose down"
    echo "   Restart app:     docker-compose restart"
    echo "   Update app:      docker-compose down && docker-compose up --build -d"
    echo ""
    echo "❓ For troubleshooting, check DEPLOYMENT.md"
    echo ""
}

# Show application logs
show_logs() {
    print_status "Showing application logs (Press Ctrl+C to exit)..."
    docker-compose logs -f
}

# Main execution
main() {
    # Parse command line arguments
    SHOW_LOGS=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --logs|-l)
                SHOW_LOGS=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --logs, -l     Show application logs after startup"
                echo "  --help, -h     Show this help message"
                echo ""
                echo "This script will:"
                echo "  1. Check for Docker and required files"
                echo "  2. Build and start the application using Docker Compose"
                echo "  3. Wait for services to be ready"
                echo "  4. Display access information"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
    done

    # Run startup sequence
    print_status "Starting Bhagavad Gita RAG Chatbot setup..."
    
    check_docker
    check_files
    cleanup_existing
    start_application
    wait_for_services
    show_info
    
    if [ "$SHOW_LOGS" = true ]; then
        show_logs
    fi
}

# Handle script interruption
trap 'echo -e "\n${YELLOW}[INFO]${NC} Startup interrupted. Run ${BLUE}docker-compose down${NC} to stop services."; exit 1' INT

# Run main function with all arguments
main "$@"

