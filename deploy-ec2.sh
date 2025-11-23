#!/bin/bash

# EC2 Deployment Script for Mitel API Mock Server
# This script sets up and runs the Mitel API Mock on an Amazon Linux EC2 instance

set -e

echo "======================================"
echo "Mitel API Mock - EC2 Setup Script"
echo "======================================"

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip
echo "Installing Python 3 and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install Docker (optional, for containerized deployment)
echo "Installing Docker..."
sudo apt-get install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Create application directory
echo "Setting up application directory..."
APP_DIR="/opt/mitel-api-mock"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR
cd $APP_DIR

# Clone or copy your application files here
# For manual deployment, you would copy files via scp
echo "Application files should be copied to $APP_DIR"
echo "Use: scp -i your-key.pem -r ./* ec2-user@your-ec2-ip:$APP_DIR"

# Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

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

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow 5000/tcp
sudo ufw allow 22/tcp
sudo ufw --force enable

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo "The Mitel API Mock server should now be running on port 5000"
echo ""
echo "Useful commands:"
echo "  - Check status: sudo systemctl status mitel-api-mock"
echo "  - View logs: sudo journalctl -u mitel-api-mock -f"
echo "  - Restart: sudo systemctl restart mitel-api-mock"
echo "  - Stop: sudo systemctl stop mitel-api-mock"
echo ""
echo "Test the API:"
echo "  curl http://localhost:5000/api/health"
echo "  curl http://localhost:5000/api/v1/cdr?limit=5"
echo ""
echo "Don't forget to configure your EC2 Security Group to allow inbound traffic on port 5000"
echo "======================================"

