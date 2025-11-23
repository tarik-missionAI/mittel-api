#!/bin/bash

# Quick deployment script using Docker
# This is the easiest way to deploy on EC2

set -e

echo "======================================"
echo "Mitel API Mock - Docker Deployment"
echo "======================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Build and run the container
echo "Building Docker image..."
docker-compose build

echo "Starting container..."
docker-compose up -d

echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo "The Mitel API Mock server is running in a Docker container"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop: docker-compose stop"
echo "  - Restart: docker-compose restart"
echo "  - Remove: docker-compose down"
echo ""
echo "Test the API:"
echo "  curl http://localhost:5000/api/health"
echo "  curl http://localhost:5000/api/v1/cdr?limit=5"
echo ""
echo "======================================"

