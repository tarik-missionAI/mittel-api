# HTTPS/SSL Setup Guide

This guide explains how to enable HTTPS for the Mitel API Mock Server.

---

## 🔐 Overview

The Mitel API now supports HTTPS through Nginx reverse proxy with two options:

1. **Self-Signed Certificates** - For development/testing
2. **Let's Encrypt Certificates** - For production with a domain name

---

## 📋 Prerequisites

- Docker and Docker Compose installed
- Port 80 and 443 open in EC2 Security Group
- (For Let's Encrypt) A domain name pointing to your EC2 instance

---

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

Run the SSL setup script:

```bash
cd /Users/tarik.boukherissa/Documents/mitel-api
./setup-ssl.sh
```

Follow the prompts to choose:
- **Choice 1**: Self-signed certificate (testing)
- **Choice 2**: Let's Encrypt certificate (production)

### Option 2: Manual Setup

#### A. Self-Signed Certificate (Development/Testing)

```bash
# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate (valid for 1 year)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem \
  -out ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=YourOrg/CN=localhost"

# Start services
docker-compose up -d
```

**Test it:**
```bash
curl -k https://localhost/api/health
```

⚠️ **Note**: Self-signed certificates will show security warnings in browsers.

---

#### B. Let's Encrypt Certificate (Production)

**Requirements:**
- A domain name (e.g., `api.example.com`)
- Domain DNS pointing to your EC2 public IP
- Port 80 and 443 accessible

**Steps:**

1. **Update nginx.conf with your domain:**

```bash
# Replace server_name _ with your domain
sed -i 's/server_name _;/server_name api.example.com;/g' nginx.conf
```

2. **Create directories:**

```bash
mkdir -p ssl certbot/www certbot/conf
```

3. **Start Docker Compose:**

```bash
docker-compose up -d
```

4. **Obtain SSL certificate:**

```bash
docker-compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d api.example.com
```

5. **Create symlinks:**

```bash
ln -sf $(pwd)/certbot/conf/live/api.example.com/fullchain.pem ssl/cert.pem
ln -sf $(pwd)/certbot/conf/live/api.example.com/privkey.pem ssl/key.pem
```

6. **Restart nginx:**

```bash
docker-compose restart nginx
```

**Test it:**
```bash
curl https://api.example.com/api/health
```

---

## 🔄 Automatic Certificate Renewal

Let's Encrypt certificates are valid for 90 days. The `certbot` container automatically renews them:

- Checks for renewal every 12 hours
- Renews certificates 30 days before expiration
- No manual intervention needed

**Manual renewal:**
```bash
docker-compose run --rm certbot renew
docker-compose restart nginx
```

---

## 📡 EC2 Security Group Configuration

Ensure your EC2 Security Group allows:

| Type  | Protocol | Port | Source    | Description          |
|-------|----------|------|-----------|----------------------|
| HTTP  | TCP      | 80   | 0.0.0.0/0 | Let's Encrypt ACME   |
| HTTPS | TCP      | 443  | 0.0.0.0/0 | API HTTPS access     |
| SSH   | TCP      | 22   | Your IP   | SSH access           |

---

## 🧪 Testing HTTPS

### 1. Health Check

```bash
# Self-signed (use -k to skip certificate verification)
curl -k https://YOUR_EC2_IP/api/health

# Let's Encrypt (with domain)
curl https://api.example.com/api/health
```

### 2. API Endpoints

```bash
# Get calls with authentication
curl -k https://YOUR_EC2_IP/api/v1/reporting/calls?limit=5 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Login

```bash
# Login to get token
curl -k https://YOUR_EC2_IP/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@company.com",
    "password": "SecurePass123"
  }'
```

---

## 🔧 Troubleshooting

### Issue: "SSL certificate problem: self signed certificate"

**Solution:** Use `-k` flag with curl or configure your client to trust the certificate.

```bash
curl -k https://localhost/api/health
```

### Issue: "Connection refused on port 443"

**Solution:** Check Docker containers are running and port 443 is open:

```bash
docker-compose ps
sudo netstat -tlnp | grep 443
```

### Issue: Let's Encrypt challenge fails (NXDOMAIN error)

**Error:** `DNS problem: NXDOMAIN looking up A for your-domain.com`

**Cause:** DNS not configured or not propagated yet.

**Solution:** 

1. Configure DNS A record (see `DNS_SETUP_GUIDE.md`)
2. Verify DNS: `dig your-domain.com` or `nslookup your-domain.com`
3. Use troubleshooting script: `./troubleshoot-dns.sh`
4. Wait 5-30 minutes for DNS propagation
5. Check online: https://dnschecker.org

**Temporary workaround:** Use self-signed certificate:
```bash
./setup-ssl.sh  # Choose option 1
```

### Issue: Let's Encrypt challenge fails (HTTP not accessible)

**Solution:** Verify:
- Domain DNS points to your EC2 IP
- Port 80 is accessible from the internet
- No firewall blocking port 80

```bash
# Test port 80 is accessible
curl http://YOUR_DOMAIN/.well-known/acme-challenge/test
```

### Issue: "nginx: [emerg] cannot load certificate"

**Solution:** Ensure SSL certificates exist:

```bash
ls -la ssl/
# Should show cert.pem and key.pem
```

---

## 🔄 Updated Deployment with HTTPS

### Deploy to EC2 with HTTPS

```bash
# 1. Set environment variables
export EC2_IP="YOUR_EC2_IP"
export KEY_FILE="~/.ssh/your-key.pem"
export API_USERNAME="admin@company.com"
export API_PASSWORD="SecurePass123"
export SSL_DOMAIN="api.example.com"  # Optional for Let's Encrypt

# 2. Deploy the API
./deploy_with_user.sh

# 3. SSH to EC2 and set up SSL
ssh -i $KEY_FILE ec2-user@$EC2_IP
cd ~/mitel-api
./setup-ssl.sh

# 4. Test HTTPS
curl -k https://$EC2_IP/api/health
```

---

## 📊 Architecture with HTTPS

```
Internet
    |
    | HTTPS (443)
    ↓
[Nginx Reverse Proxy]
    |
    | HTTP (5000)
    ↓
[Flask Application]
```

**Benefits:**
- ✅ SSL/TLS termination at Nginx
- ✅ Automatic HTTP to HTTPS redirect
- ✅ Security headers (HSTS, X-Frame-Options, etc.)
- ✅ Better performance (Nginx handles static content)
- ✅ Automatic certificate renewal

---

## 🔐 Security Best Practices

1. **Use Let's Encrypt for production** - Free, trusted certificates
2. **Keep certificates secure** - Never commit `ssl/` directory to git
3. **Enable HSTS** - Forces HTTPS (already configured in nginx.conf)
4. **Use strong ciphers** - TLS 1.2+ only (already configured)
5. **Regular updates** - Keep Nginx and SSL libraries updated
6. **Monitor expiration** - Let's Encrypt certs expire in 90 days

---

## 📁 Files Added

- `nginx.conf` - Nginx reverse proxy configuration
- `docker-compose.yml` - Updated with Nginx and Certbot services
- `setup-ssl.sh` - Automated SSL setup script
- `HTTPS_SETUP_GUIDE.md` - This guide

---

## 🆘 Need Help?

- Check nginx logs: `docker-compose logs nginx`
- Check app logs: `docker-compose logs mitel-api-mock`
- Verify SSL: `openssl s_client -connect YOUR_DOMAIN:443`
- Test certificate: `curl -vI https://YOUR_DOMAIN/api/health`

---

**You're all set! Your Mitel API Mock Server is now secured with HTTPS! 🔒**

