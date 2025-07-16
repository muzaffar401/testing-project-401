#!/bin/bash

# Health & Wellness Planner Agent - Local Deployment Script
# This script helps you test the Docker deployment locally before deploying to Choreo

set -e

echo "🏥 Health & Wellness Planner Agent - Local Deployment"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f "python-backend/.env" ]; then
    echo "⚠️  No .env file found in python-backend directory."
    echo "Please create python-backend/.env with your OPENAI_API_KEY:"
    echo "OPENAI_API_KEY=your_api_key_here"
    exit 1
fi

echo "🔧 Building Docker images..."

# Build backend image
echo "Building backend image..."
docker build -t health-planner-backend:latest .

# Build frontend image
echo "Building frontend image..."
cd ui
docker build -t health-planner-frontend:latest .
cd ..

echo "🚀 Starting services with docker-compose..."

# Start services
docker-compose up -d

echo "⏳ Waiting for services to be ready..."

# Wait for backend to be healthy
echo "Waiting for backend service..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy!"
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -eq $timeout ]; then
    echo "❌ Backend failed to start within $timeout seconds"
    docker-compose logs backend
    exit 1
fi

# Wait for frontend to be ready
echo "Waiting for frontend service..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -f http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready!"
        break
    fi
    sleep 2
    counter=$((counter + 2))
done

if [ $counter -eq $timeout ]; then
    echo "❌ Frontend failed to start within $timeout seconds"
    docker-compose logs frontend
    exit 1
fi

echo ""
echo "🎉 Deployment successful!"
echo "========================"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "Health Check: http://localhost:8000/health"
echo ""
echo "To stop the services:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To test the API:"
echo "  curl -X POST http://localhost:8000/chat \\"
echo "    -H \"Content-Type: application/json\" \\"
echo "    -d '{\"message\": \"I want to lose 5kg in 2 months\"}'" 