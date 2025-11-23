# 🚀 EC2 Deployment Guide - Complete Walkthrough

## Prerequisites

- ✅ AWS EC2 instance running (Ubuntu 20.04 or later)
- ✅ SSH key (.pem file) to access EC2
- ✅ Security Group allows ports 22 (SSH) and 5000 (API)
- ✅ Username and password for your API user

---

## 📋 Step-by-Step Deployment

### **Step 1: Copy Files to EC2**

From your local machine:

```bash
# Set your variables
EC2_IP="YOUR_EC2_PUBLIC_IP"
KEY_FILE="path/to/your-key.pem"

# Option A: Using rsync (recommended - excludes venv, __pycache__, etc.)
cd /Users/tarik.boukherissa/Documents/mitel-api
rsync -avz -e "ssh -i $KEY_FILE" \
  --exclude 'venv/' \
  --exclude '__pycache__/' \
  --exclude '*.pyc' \
  --exclude '.git/' \
  ./ ec2-user@$EC2_IP:~/mitel-api/

# Option B: Using tar (if rsync not available)
cd /Users/tarik.boukherissa/Documents/mitel-api
tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
  -czf /tmp/mitel-api.tar.gz .
scp -i $KEY_FILE /tmp/mitel-api.tar.gz ec2-user@$EC2_IP:~/
ssh -i $KEY_FILE ec2-user@$EC2_IP \
  "mkdir -p ~/mitel-api && tar -xzf ~/mitel-api.tar.gz -C ~/mitel-api && rm ~/mitel-api.tar.gz"
rm /tmp/mitel-api.tar.gz

# Option C: Using scp (simple but includes everything)
# Note: This will copy venv which is not recommended
scp -i $KEY_FILE -r ./* ec2-user@$EC2_IP:~/mitel-api/
```

### **Step 2: Connect to EC2**

```bash
ssh -i $KEY_FILE ubuntu@$EC2_IP
```

### **Step 3: Deploy with Docker (Recommended)**

Once connected to EC2:

```bash
# Navigate to app directory
cd ~/mitel-api

# Run the Docker deployment script
chmod +x deploy-docker.sh
./deploy-docker.sh

# Wait for deployment to complete
```

**The script will:**
- Install Docker if needed
- Build the container
- Start the API on port 5000

### **Step 4: Verify Deployment**

```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs -f

# Test health endpoint
curl http://localhost:5000/health
```

---

## 👥 User Management Options

### **Option A: JSON File (Recommended for EC2)**

#### **1. Create users.json with your credentials:**

```bash
cd ~/mitel-api

# Create users.json
cat > users.json << 'EOF'
{
  "users": [
    {
      "username": "YOUR_USERNAME",
      "password": "YOUR_PASSWORD",
      "account_id": "1",
      "role": "admin",
      "name": "Your Name"
    }
  ]
}
EOF

# Secure the file
chmod 600 users.json
```

#### **2. Restart with JSON mode and auth enabled:**

```bash
# Stop current container
docker-compose down

# Update docker-compose.yml to enable auth
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

# Start with new configuration
docker-compose up -d

# Check logs
docker-compose logs -f
```

### **Option B: Environment Variables (Most Secure)**

```bash
# Stop current container
docker-compose down

# Create docker-compose.yml with your user in env vars
cat > docker-compose.yml << EOF
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
      - USER_MGMT_MODE=env
      - TOKEN_EXPIRATION=7200
      - MITEL_USER_1=YOUR_USERNAME:YOUR_PASSWORD:1:admin:Your Name
    restart: unless-stopped
EOF

# Start
docker-compose up -d
```

---

## 🔑 Generate Bearer Token

### **From EC2 Instance (Local Test)**

```bash
# Get token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "expires_in": 7200
  }' | jq

# Save token to variable
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "expires_in": 7200
  }' | jq -r '.access_token')

echo "Your token: $TOKEN"

# Test with token
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:5000/api/v1/reporting/calls?limit=5" | jq
```

### **From Your Local Machine (External Access)**

```bash
# Set your EC2 IP
EC2_IP="YOUR_EC2_PUBLIC_IP"

# Get token
curl -X POST http://$EC2_IP:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "expires_in": 7200
  }' | jq

# Save token
TOKEN=$(curl -s -X POST http://$EC2_IP:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD"
  }' | jq -r '.access_token')

echo "Token: $TOKEN"

# Test API
curl -H "Authorization: Bearer $TOKEN" \
  "http://$EC2_IP:5000/api/v1/reporting/calls?limit=5" | jq
```

---

## 📝 Complete Command Sequence

Here's the complete sequence to copy and paste (replace YOUR_* values):

```bash
#!/bin/bash

# === CONFIGURATION ===
EC2_IP="YOUR_EC2_PUBLIC_IP"
KEY_FILE="path/to/your-key.pem"
API_USERNAME="YOUR_USERNAME"
API_PASSWORD="YOUR_PASSWORD"

# === 1. COPY FILES TO EC2 ===
echo "Copying files to EC2..."
cd /Users/tarik.boukherissa/Documents/mitel-api
scp -i $KEY_FILE -r ./* ubuntu@$EC2_IP:~/mitel-api/

# === 2. DEPLOY ON EC2 ===
echo "Deploying on EC2..."
ssh -i $KEY_FILE ubuntu@$EC2_IP << 'ENDSSH'
cd ~/mitel-api

# Install Docker if needed
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# Install Docker Compose if needed
if ! command -v docker-compose &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y docker-compose
fi

# Create users.json
cat > users.json << 'EOF'
{
  "users": [
    {
      "username": "API_USERNAME_PLACEHOLDER",
      "password": "API_PASSWORD_PLACEHOLDER",
      "account_id": "1",
      "role": "admin",
      "name": "API User"
    }
  ]
}
EOF

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
EOF

# Build and start
docker-compose build
docker-compose up -d

echo "Deployment complete!"
docker-compose ps
ENDSSH

# === 3. REPLACE PLACEHOLDERS WITH ACTUAL VALUES ===
echo "Updating credentials on EC2..."
ssh -i $KEY_FILE ubuntu@$EC2_IP << ENDSSH2
cd ~/mitel-api
sed -i "s/API_USERNAME_PLACEHOLDER/$API_USERNAME/g" users.json
sed -i "s/API_PASSWORD_PLACEHOLDER/$API_PASSWORD/g" users.json
docker-compose restart
ENDSSH2

# === 4. GET TOKEN ===
echo "Waiting for API to start..."
sleep 10

echo "Getting bearer token..."
TOKEN=$(curl -s -X POST http://$EC2_IP:5000/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$API_USERNAME\",
    \"password\": \"$API_PASSWORD\",
    \"expires_in\": 7200
  }" | jq -r '.access_token')

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo "API URL: http://$EC2_IP:5000"
echo "Username: $API_USERNAME"
echo "Bearer Token: $TOKEN"
echo ""
echo "Test command:"
echo "curl -H \"Authorization: Bearer $TOKEN\" \\"
echo "  \"http://$EC2_IP:5000/api/v1/reporting/calls?limit=5\""
echo "=========================================="
```

---

## ⚡ Quick Manual Deployment

If you prefer to do it manually step by step:

### **On EC2:**

```bash
# 1. Connect
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# 2. Navigate to app
cd ~/mitel-api

# 3. Create your user
cat > users.json << 'EOF'
{
  "users": [
    {
      "username": "myuser@company.com",
      "password": "MySecurePassword123!",
      "account_id": "1",
      "role": "admin",
      "name": "My Name"
    }
  ]
}
EOF

# 4. Enable auth in docker-compose.yml
# Edit the file and add:
#   - REQUIRE_AUTH=true
#   - USER_MGMT_MODE=json
#   - USERS_FILE=/app/users.json
# And mount the file:
#   volumes:
#     - ./users.json:/app/users.json:ro

# 5. Deploy
docker-compose up -d

# 6. Get token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser@company.com",
    "password": "MySecurePassword123!",
    "expires_in": 7200
  }' | jq
```

---

## 🔒 Security Checklist

After deployment:

```bash
# On EC2:
cd ~/mitel-api

# 1. Secure users.json
chmod 600 users.json

# 2. Check Security Group
# Ensure port 5000 is only open to your IPs (not 0.0.0.0/0)

# 3. Verify auth is enabled
curl http://localhost:5000/ | jq '.authentication'

# Should show: "required": true

# 4. Test unauthorized access fails
curl http://localhost:5000/api/v1/reporting/calls
# Should return 401 Unauthorized
```

---

## 🧪 Verification Commands

```bash
# Health check
curl http://YOUR_EC2_IP:5000/health

# API info
curl http://YOUR_EC2_IP:5000/

# Login (get token)
curl -X POST http://YOUR_EC2_IP:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}'

# Test authenticated endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://YOUR_EC2_IP:5000/api/v1/reporting/calls?limit=5"

# List users (requires token)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://YOUR_EC2_IP:5000/auth/users
```

---

## 🔧 Troubleshooting

### **Can't connect to API**

```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs -f

# Check if port is open
curl http://localhost:5000/health

# Check Security Group in AWS console
# - Port 5000 must be open from your IP
```

### **Login fails**

```bash
# Check users.json
cat ~/mitel-api/users.json

# Check container environment
docker-compose exec mitel-api-mock env | grep AUTH

# Check logs for errors
docker-compose logs | grep -i error
```

### **401 Unauthorized**

```bash
# Verify token is valid
TOKEN="your_token_here"
curl -H "Authorization: Bearer $TOKEN" \
  http://YOUR_EC2_IP:5000/auth/users

# Get a fresh token
TOKEN=$(curl -s -X POST http://YOUR_EC2_IP:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}' \
  | jq -r '.access_token')
```

---

## 📊 Monitoring

```bash
# View logs
docker-compose logs -f

# Check status
docker-compose ps

# Restart if needed
docker-compose restart

# Stop
docker-compose stop

# Start
docker-compose start
```

---

## ✅ Summary

**To deploy and get a token, run these commands:**

```bash
# 1. Copy files
scp -i KEY.pem -r ./* ubuntu@EC2_IP:~/mitel-api/

# 2. SSH to EC2
ssh -i KEY.pem ubuntu@EC2_IP

# 3. Create user file
cd ~/mitel-api
cat > users.json << EOF
{
  "users": [
    {"username": "YOUR_USER", "password": "YOUR_PASS", "account_id": "1", "role": "admin", "name": "Your Name"}
  ]
}
EOF

# 4. Deploy
./deploy-docker.sh

# 5. Enable auth (edit docker-compose.yml or use env vars)
# Add: REQUIRE_AUTH=true, USER_MGMT_MODE=json
docker-compose restart

# 6. Get token
curl -X POST http://localhost:5000/auth/login \
  -d '{"username":"YOUR_USER","password":"YOUR_PASS"}' | jq
```

**Your API is live!** 🎉

