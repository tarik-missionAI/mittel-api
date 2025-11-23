#!/bin/bash

# DNS Troubleshooting Script for SSL Setup

echo "=========================================="
echo "DNS Troubleshooting for SSL Certificate"
echo "=========================================="
echo ""

# Get domain from user
read -p "Enter your domain (e.g., mitel-api.mission-ai.fr): " DOMAIN
read -p "Enter your EC2 public IP: " EC2_IP

echo ""
echo "=========================================="
echo "1. Checking DNS Resolution"
echo "=========================================="

# Check A record
echo "Checking A record for $DOMAIN..."
A_RECORD=$(dig +short $DOMAIN A)
if [ -z "$A_RECORD" ]; then
    echo "❌ No A record found for $DOMAIN"
    echo "   DNS is not configured yet."
else
    echo "✅ A record found: $A_RECORD"
    if [ "$A_RECORD" = "$EC2_IP" ]; then
        echo "✅ DNS correctly points to your EC2 IP!"
    else
        echo "⚠️  WARNING: DNS points to $A_RECORD but your EC2 IP is $EC2_IP"
        echo "   Update your DNS record to point to $EC2_IP"
    fi
fi

echo ""
echo "=========================================="
echo "2. Checking DNS Propagation"
echo "=========================================="

echo "Checking from multiple DNS servers..."

# Check Google DNS
echo -n "Google DNS (8.8.8.8): "
GOOGLE_DNS=$(dig @8.8.8.8 +short $DOMAIN A | head -n1)
if [ -z "$GOOGLE_DNS" ]; then
    echo "❌ Not resolved"
else
    echo "✅ $GOOGLE_DNS"
fi

# Check Cloudflare DNS
echo -n "Cloudflare DNS (1.1.1.1): "
CF_DNS=$(dig @1.1.1.1 +short $DOMAIN A | head -n1)
if [ -z "$CF_DNS" ]; then
    echo "❌ Not resolved"
else
    echo "✅ $CF_DNS"
fi

# Check OpenDNS
echo -n "OpenDNS (208.67.222.222): "
OPENDNS=$(dig @208.67.222.222 +short $DOMAIN A | head -n1)
if [ -z "$OPENDNS" ]; then
    echo "❌ Not resolved"
else
    echo "✅ $OPENDNS"
fi

echo ""
echo "=========================================="
echo "3. HTTP Connectivity Test"
echo "=========================================="

echo "Testing HTTP connection to $EC2_IP..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 http://$EC2_IP 2>/dev/null)
if [ "$HTTP_STATUS" = "000" ]; then
    echo "❌ Cannot connect to HTTP on port 80"
    echo "   Check EC2 Security Group allows port 80"
else
    echo "✅ HTTP port 80 is accessible (Status: $HTTP_STATUS)"
fi

echo ""
echo "=========================================="
echo "Summary & Recommendations"
echo "=========================================="
echo ""

if [ -z "$A_RECORD" ]; then
    echo "❌ DNS NOT CONFIGURED"
    echo ""
    echo "You need to:"
    echo "1. Go to your DNS provider (e.g., Gandi, OVH, Cloudflare)"
    echo "2. Create an A record:"
    echo "   Type: A"
    echo "   Name: mitel-api (or @ for root domain)"
    echo "   Value: $EC2_IP"
    echo "   TTL: 300 (5 minutes)"
    echo ""
    echo "3. Wait 5-10 minutes for DNS propagation"
    echo "4. Run this script again to verify"
    echo ""
    echo "In the meantime, use a self-signed certificate:"
    echo "   ./setup-ssl.sh  (choose option 1)"
    echo ""
elif [ "$A_RECORD" != "$EC2_IP" ]; then
    echo "⚠️  DNS MISCONFIGURED"
    echo ""
    echo "DNS points to: $A_RECORD"
    echo "Should point to: $EC2_IP"
    echo ""
    echo "Update your DNS A record to: $EC2_IP"
    echo ""
else
    echo "✅ DNS CORRECTLY CONFIGURED!"
    echo ""
    echo "You can now obtain an SSL certificate:"
    echo "   ./setup-ssl.sh  (choose option 2)"
    echo ""
fi

echo "=========================================="
echo ""
echo "Online DNS propagation checkers:"
echo "  - https://dnschecker.org/#A/$DOMAIN"
echo "  - https://www.whatsmydns.net/#A/$DOMAIN"
echo ""

