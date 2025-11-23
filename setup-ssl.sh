#!/bin/bash

# SSL Setup Script for Mitel API Mock Server
# This script helps you set up HTTPS with either self-signed or Let's Encrypt certificates

set -e

echo "=========================================="
echo "Mitel API - HTTPS/SSL Setup"
echo "=========================================="
echo ""

# Create directories
mkdir -p ssl certbot/www certbot/conf

echo "Choose SSL certificate type:"
echo "1) Self-signed certificate (for testing/development)"
echo "2) Let's Encrypt certificate (for production with domain)"
echo ""
read -p "Enter choice (1 or 2): " SSL_CHOICE

if [ "$SSL_CHOICE" = "1" ]; then
    echo ""
    echo "=========================================="
    echo "Creating Self-Signed Certificate"
    echo "=========================================="
    echo ""
    
    read -p "Enter domain/hostname (or press Enter for 'localhost'): " DOMAIN
    DOMAIN=${DOMAIN:-localhost}
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl/key.pem \
        -out ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
    
    echo ""
    echo "✅ Self-signed certificate created!"
    echo "   Certificate: ssl/cert.pem"
    echo "   Private Key: ssl/key.pem"
    echo "   Valid for: 365 days"
    echo ""
    echo "⚠️  WARNING: Self-signed certificates will show security warnings in browsers."
    echo "   Only use for testing/development!"
    echo ""

elif [ "$SSL_CHOICE" = "2" ]; then
    echo ""
    echo "=========================================="
    echo "Let's Encrypt Certificate Setup"
    echo "=========================================="
    echo ""
    
    read -p "Enter your domain name (e.g., api.example.com): " DOMAIN
    read -p "Enter your email for Let's Encrypt: " EMAIL
    
    if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
        echo "Error: Domain and email are required for Let's Encrypt"
        exit 1
    fi
    
    echo ""
    echo "Setting up Let's Encrypt for: $DOMAIN"
    echo ""
    
    # Update nginx.conf with domain
    sed -i.bak "s/server_name _;/server_name $DOMAIN;/g" nginx.conf
    
    # Temporarily create a basic nginx config for ACME challenge
    cat > nginx-temp.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF
    
    # Start nginx temporarily for ACME challenge
    docker run -d --name nginx-temp \
        -p 80:80 \
        -v $(pwd)/nginx-temp.conf:/etc/nginx/conf.d/default.conf \
        -v $(pwd)/certbot/www:/var/www/certbot \
        nginx:alpine
    
    echo "Obtaining SSL certificate from Let's Encrypt..."
    
    # Get certificate
    docker run --rm \
        -v $(pwd)/certbot/www:/var/www/certbot \
        -v $(pwd)/certbot/conf:/etc/letsencrypt \
        certbot/certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN
    
    # Stop temporary nginx
    docker stop nginx-temp
    docker rm nginx-temp
    rm nginx-temp.conf
    
    # Create symlinks to Let's Encrypt certificates
    ln -sf $(pwd)/certbot/conf/live/$DOMAIN/fullchain.pem ssl/cert.pem
    ln -sf $(pwd)/certbot/conf/live/$DOMAIN/privkey.pem ssl/key.pem
    
    echo ""
    echo "✅ Let's Encrypt certificate obtained!"
    echo "   Domain: $DOMAIN"
    echo "   Certificate will auto-renew every 12 hours"
    echo ""

else
    echo "Invalid choice. Exiting."
    exit 1
fi

echo "=========================================="
echo "SSL Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Start the services with Docker Compose:"
echo "   docker-compose up -d"
echo ""
echo "2. Test HTTPS connection:"
echo "   curl -k https://localhost/api/health"
echo ""
echo "3. Access the API via HTTPS:"
if [ "$SSL_CHOICE" = "2" ]; then
    echo "   https://$DOMAIN/api/v1/reporting/calls"
else
    echo "   https://YOUR_EC2_IP/api/v1/reporting/calls"
fi
echo ""
echo "=========================================="

