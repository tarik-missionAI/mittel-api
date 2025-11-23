#!/bin/bash

# Mitel API EC2 Deployment Script with User Creation
# This script deploys the API to EC2 and creates a user with bearer token

set -e

echo "=========================================="
echo "Mitel API EC2 Deployment"
echo "=========================================="

# Check if required variables are set
if [ -z "$EC2_IP" ] || [ -z "$KEY_FILE" ] || [ -z "$API_USERNAME" ] || [ -z "$API_PASSWORD" ]; then
    echo "Please set the following environment variables:"
    echo "  export EC2_IP=\"your-ec2-public-ip\""
    echo "  export KEY_FILE=\"path/to/your-key.pem\""
    echo "  export API_USERNAME=\"your-username\""
    echo "  export API_PASSWORD=\"your-password\""
    echo ""
    echo "Example:"
    echo "  export EC2_IP=\"54.123.45.67\""
    echo "  export KEY_FILE=\"~/.ssh/my-key.pem\""
    echo "  export API_USERNAME=\"admin@company.com\""
    echo "  export API_PASSWORD=\"SecurePass123!\""
    echo "  ./deploy_with_user.sh"
    exit 1
fi

echo "Configuration:"
echo "  EC2 IP: $EC2_IP"
echo "  SSH Key: $KEY_FILE"
echo "  Username: $API_USERNAME"
echo "  Password: ********"
echo ""

# Step 1: Copy files to EC2
echo "Step 1/5: Copying files to EC2..."
scp -i "$KEY_FILE" -r ./* ubuntu@$EC2_IP:~/mitel-api/
echo "✅ Files copied"
echo ""

# Step 2: Deploy Docker
echo "Step 2/5: Deploying with Docker..."
ssh -i "$KEY_FILE" ubuntu@$EC2_IP << 'ENDSSH'
cd ~/mitel-api

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if needed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose
fi

echo "✅ Docker installed"
ENDSSH
echo ""

# Step 3: Create users.json
echo "Step 3/5: Creating user configuration..."
ssh -i "$KEY_FILE" ubuntu@$EC2_IP << ENDSSH3
cd ~/mitel-api

# Create users.json
cat > users.json << 'EOF'
{
  "users": [
    {
      "username": "$API_USERNAME",
      "password": "$API_PASSWORD",
      "account_id": "1",
      "role": "admin",
      "name": "API User"
    }
  ]
}
EOF

# Secure the file
chmod 600 users.json

echo "✅ User created"
ENDSSH3
echo ""

# Step 4: Configure and start
echo "Step 4/5: Configuring and starting API..."
ssh -i "$KEY_FILE" ubuntu@$EC2_IP << 'ENDSSH4'
cd ~/mitel-api

# Update docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  mitel-api-mock:
    build: .
    container_name: mitel-api-mock
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - PORT=5000
      - REQUIRE_AUTH=true
      - USER_MGMT_MODE=json
      - USERS_FILE=/app/users.json
      - TOKEN_EXPIRATION=7200
    volumes:
      - ./users.json:/app/users.json:ro
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
EOF

# Build and start
echo "Building Docker image..."
docker-compose build --no-cache

echo "Starting API..."
docker-compose up -d

echo "✅ API started"
ENDSSH4
echo ""

# Wait for API to be ready
echo "Waiting for API to be ready..."
sleep 15

# Step 5: Get bearer token
echo "Step 5/5: Generating bearer token..."
RESPONSE=$(curl -s -X POST http://$EC2_IP:5000/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$API_USERNAME\",
    \"password\": \"$API_PASSWORD\",
    \"expires_in\": 7200
  }")

TOKEN=$(echo $RESPONSE | jq -r '.access_token')
EXPIRES_IN=$(echo $RESPONSE | jq -r '.expires_in')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Failed to get token. Response:"
    echo $RESPONSE | jq
    exit 1
fi

echo "✅ Token generated"
echo ""

# Verify token works
echo "Verifying token..."
TEST_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://$EC2_IP:5000/api/v1/reporting/calls?limit=1")

if echo $TEST_RESPONSE | jq -e '.success' > /dev/null 2>&1; then
    echo "✅ Token verified - API is working!"
else
    echo "⚠️  Warning: Token test failed"
    echo $TEST_RESPONSE | jq
fi

echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "API Details:"
echo "  URL: http://$EC2_IP:5000"
echo "  Username: $API_USERNAME"
echo "  Token Expiration: $EXPIRES_IN seconds ($(($EXPIRES_IN / 3600)) hours)"
echo ""
echo "Bearer Token:"
echo "  $TOKEN"
echo ""
echo "Test Commands:"
echo ""
echo "  # Health check"
echo "  curl http://$EC2_IP:5000/health"
echo ""
echo "  # Get calls (with authentication)"
echo "  curl -H \"Authorization: Bearer $TOKEN\" \\"
echo "    \"http://$EC2_IP:5000/api/v1/reporting/calls?limit=5\""
echo ""
echo "  # Get calls with date range"
echo "  curl -H \"Authorization: Bearer $TOKEN\" \\"
echo "    \"http://$EC2_IP:5000/api/v1/reporting/calls?startDate=2025-11-20&endDate=2025-11-22&limit=10\""
echo ""
echo "  # Export as CSV"
echo "  curl -H \"Authorization: Bearer $TOKEN\" \\"
echo "    \"http://$EC2_IP:5000/api/v1/reporting/calls/export?limit=100\" > calls.csv"
echo ""
echo "Save your token for future use!"
echo "=========================================="

