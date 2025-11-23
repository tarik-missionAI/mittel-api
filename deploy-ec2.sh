#!/bin/bash

# EC2 Deployment Script for Mitel API Mock Server
# This script sets up and runs the Mitel API Mock on an Amazon Linux EC2 instance

set -e

APP_DIR="/home/ec2-user/mitel-api"

echo "======================================"
echo "Mitel API Mock - EC2 Setup Script"
echo "======================================"

# Detect OS and set package manager
if command -v dnf &> /dev/null; then
    PKG_MGR="dnf"
    echo "Detected: Amazon Linux 2023 (dnf)"
elif command -v yum &> /dev/null; then
    PKG_MGR="yum"
    echo "Detected: Amazon Linux 2 (yum)"
elif command -v apt-get &> /dev/null; then
    PKG_MGR="apt-get"
    echo "Detected: Ubuntu/Debian (apt-get)"
else
    echo "Error: No supported package manager found"
    exit 1
fi

# Update system
echo "Updating system packages..."
case $PKG_MGR in
    dnf|yum)
        sudo $PKG_MGR update -y
        sudo $PKG_MGR install -y python3 python3-pip
        ;;
    apt-get)
        sudo apt-get update
        sudo apt-get upgrade -y
        sudo apt-get install -y python3 python3-pip python3-venv
        ;;
esac

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    echo "Docker already installed"
fi

sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    echo "Docker Compose already installed"
fi

# Create application directory
echo "Setting up application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

# Clone or copy your application files here
# For manual deployment, you would copy files via scp
echo ""
echo "======================================"
echo "Application files should be copied to $APP_DIR"
echo "Use one of these commands from your local machine:"
echo ""
echo "Option 1 (rsync - recommended):"
echo "  rsync -avz -e 'ssh -i your-key.pem' \\"
echo "    --exclude 'venv/' --exclude '__pycache__/' --exclude '.git/' \\"
echo "    ./ ec2-user@your-ec2-ip:$APP_DIR"
echo ""
echo "Option 2 (tar):"
echo "  tar --exclude='venv' --exclude='__pycache__' --exclude='.git' -czf mitel-api.tar.gz ."
echo "  scp -i your-key.pem mitel-api.tar.gz ec2-user@your-ec2-ip:~/"
echo "  ssh -i your-key.pem ec2-user@your-ec2-ip 'tar -xzf ~/mitel-api.tar.gz -C $APP_DIR'"
echo "======================================"
echo ""

# If requirements.txt exists, set up Python virtual environment
if [ -f "requirements.txt" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Create systemd service file
    echo "Creating systemd service..."
    sudo tee /etc/systemd/system/mitel-api-mock.service > /dev/null <<EOF
[Unit]
Description=Mitel API Mock Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable mitel-api-mock
    sudo systemctl start mitel-api-mock
    
    echo "✅ Systemd service created and started"
fi

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo "The Mitel API Mock server setup is complete"
echo ""
echo "Useful commands:"
echo "  - Check status: sudo systemctl status mitel-api-mock"
echo "  - View logs: sudo journalctl -u mitel-api-mock -f"
echo "  - Restart: sudo systemctl restart mitel-api-mock"
echo "  - Stop: sudo systemctl stop mitel-api-mock"
echo ""
echo "Test the API:"
echo "  curl http://localhost:5000/api/health"
echo "  curl http://localhost:5000/api/v1/reporting/calls?limit=5"
echo ""
echo "IMPORTANT: Configure your EC2 Security Group to allow:"
echo "  - Inbound TCP port 5000 (API access)"
echo "  - Inbound TCP port 22 (SSH access)"
echo "======================================"
echo ""
