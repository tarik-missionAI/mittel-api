# DNS Setup Guide for Let's Encrypt SSL

This guide helps you configure DNS for your domain to work with Let's Encrypt SSL certificates.

---

## ❌ Current Issue

**Error:** `DNS problem: NXDOMAIN looking up A for mitel-api.mission-ai.fr`

**Meaning:** The domain `mitel-api.mission-ai.fr` doesn't have a DNS record pointing to your EC2 instance.

**Solution:** Add an A record in your DNS settings.

---

## 🔧 How to Fix

### Step 1: Get Your EC2 Public IP

```bash
# Find your EC2 public IP
curl -s http://checkip.amazonaws.com

# Or from AWS Console:
# EC2 Dashboard → Instances → Select your instance → Public IPv4 address
```

**Example:** `54.123.45.67`

---

### Step 2: Configure DNS

Go to your DNS provider (the company where you registered `mission-ai.fr`). Common providers:
- **OVH** (ovh.com)
- **Gandi** (gandi.net)
- **Cloudflare** (cloudflare.com)
- **AWS Route 53** (if using AWS DNS)

#### **Add an A Record:**

| Field | Value                          |
|-------|--------------------------------|
| Type  | `A`                           |
| Name  | `mitel-api`                   |
| Value | `YOUR_EC2_PUBLIC_IP`          |
| TTL   | `300` (5 minutes)             |

**Example configuration:**

```
Type: A
Name: mitel-api
Value: 54.123.45.67
TTL: 300
```

This creates: `mitel-api.mission-ai.fr` → `54.123.45.67`

---

### Step 3: Wait for DNS Propagation

DNS changes take time to propagate:
- **Minimum:** 5 minutes (with TTL=300)
- **Typical:** 10-30 minutes
- **Maximum:** Up to 48 hours (rare)

---

### Step 4: Verify DNS Configuration

#### **Option A: Use the troubleshooting script**

```bash
cd ~/mitel-api
./troubleshoot-dns.sh
```

#### **Option B: Manual verification**

```bash
# Check DNS resolution
dig mitel-api.mission-ai.fr A

# Should show:
# mitel-api.mission-ai.fr. 300 IN A YOUR_EC2_IP

# Or use nslookup
nslookup mitel-api.mission-ai.fr

# Should show:
# Name:    mitel-api.mission-ai.fr
# Address: YOUR_EC2_IP
```

#### **Option C: Online DNS checkers**

- https://dnschecker.org/#A/mitel-api.mission-ai.fr
- https://www.whatsmydns.net/#A/mitel-api.mission-ai.fr

These show DNS propagation status worldwide.

---

### Step 5: Retry Let's Encrypt

Once DNS is configured and propagated:

```bash
cd ~/mitel-api
./setup-ssl.sh
# Choose option 2 (Let's Encrypt)
```

---

## 🚀 Alternative: Use Self-Signed Certificate Now

While waiting for DNS to propagate, you can use a self-signed certificate:

```bash
cd ~/mitel-api
./setup-ssl.sh
# Choose option 1 (Self-Signed Certificate)

# Start services
docker-compose up -d

# Test HTTPS (note: -k flag skips cert verification)
curl -k https://YOUR_EC2_IP/api/health
```

**When DNS is ready**, switch to Let's Encrypt:

```bash
# Stop services
docker-compose down

# Remove self-signed certs
rm -rf ssl/*

# Set up Let's Encrypt
./setup-ssl.sh
# Choose option 2

# Restart services
docker-compose up -d
```

---

## 📋 Specific DNS Provider Instructions

### **OVH**

1. Log in to OVH Manager
2. Go to **Web Cloud** → **Domain names**
3. Select `mission-ai.fr`
4. Click **DNS Zone** tab
5. Click **Add an entry**
6. Choose **A** record
7. Fill in:
   - Subdomain: `mitel-api`
   - Target: `YOUR_EC2_IP`
   - TTL: `300`
8. Click **Confirm**

### **Gandi**

1. Log in to Gandi
2. Go to **Domain names**
3. Select `mission-ai.fr`
4. Click **DNS Records**
5. Click **Add**
6. Fill in:
   - Type: `A`
   - Name: `mitel-api`
   - IPv4 Address: `YOUR_EC2_IP`
   - TTL: `300`
7. Click **Create**

### **Cloudflare**

1. Log in to Cloudflare
2. Select `mission-ai.fr`
3. Click **DNS** tab
4. Click **Add record**
5. Fill in:
   - Type: `A`
   - Name: `mitel-api`
   - IPv4 address: `YOUR_EC2_IP`
   - TTL: `Auto` or `5 min`
   - Proxy status: **DNS only** (gray cloud, not orange)
6. Click **Save**

**Important:** For Let's Encrypt, disable Cloudflare proxy (gray cloud icon).

### **AWS Route 53**

```bash
# Create hosted zone (if not exists)
aws route53 create-hosted-zone \
  --name mission-ai.fr \
  --caller-reference $(date +%s)

# Get hosted zone ID
ZONE_ID=$(aws route53 list-hosted-zones-by-name \
  --dns-name mission-ai.fr \
  --query 'HostedZones[0].Id' \
  --output text)

# Create A record
cat > change-batch.json << EOF
{
  "Changes": [{
    "Action": "CREATE",
    "ResourceRecordSet": {
      "Name": "mitel-api.mission-ai.fr",
      "Type": "A",
      "TTL": 300,
      "ResourceRecords": [{"Value": "YOUR_EC2_IP"}]
    }
  }]
}
EOF

aws route53 change-resource-record-sets \
  --hosted-zone-id $ZONE_ID \
  --change-batch file://change-batch.json
```

---

## 🧪 Testing Checklist

Before retrying Let's Encrypt:

- [ ] DNS A record exists for `mitel-api.mission-ai.fr`
- [ ] A record points to your EC2 public IP
- [ ] DNS resolves correctly: `dig mitel-api.mission-ai.fr`
- [ ] EC2 Security Group allows port 80 (HTTP)
- [ ] EC2 Security Group allows port 443 (HTTPS)
- [ ] HTTP accessible: `curl http://YOUR_EC2_IP`

---

## 🔍 Common Issues

### Issue: "Still getting NXDOMAIN after 30 minutes"

**Possible causes:**
1. DNS record not saved properly
2. Wrong domain/subdomain name
3. DNS provider slow to update

**Solution:**
- Double-check DNS settings in your provider
- Try `dig @8.8.8.8 mitel-api.mission-ai.fr` (Google DNS)
- Contact your DNS provider support

### Issue: "DNS resolves but Let's Encrypt still fails"

**Possible causes:**
1. Port 80 blocked in EC2 Security Group
2. Firewall blocking HTTP
3. Nginx not running

**Solution:**
```bash
# Check port 80 is accessible
curl -v http://mitel-api.mission-ai.fr/.well-known/acme-challenge/test

# Check EC2 Security Group
aws ec2 describe-security-groups --group-ids YOUR_SG_ID

# Check nginx is running
docker-compose ps nginx
```

### Issue: "DNS points to wrong IP"

**Solution:**
```bash
# Find your current EC2 IP
curl http://checkip.amazonaws.com

# Update DNS A record to point to this IP
# Wait 5-10 minutes for propagation
```

---

## 📊 Quick Reference: DNS Record Format

```dns
; A Record for subdomain
mitel-api.mission-ai.fr.  300  IN  A  YOUR_EC2_IP

; Example with real IP
mitel-api.mission-ai.fr.  300  IN  A  54.123.45.67
```

**Breakdown:**
- `mitel-api.mission-ai.fr.` - Full domain name (FQDN)
- `300` - TTL in seconds (5 minutes)
- `IN` - Internet class
- `A` - Record type (IPv4 address)
- `YOUR_EC2_IP` - Your EC2 public IP address

---

## 🆘 Still Having Issues?

Run the troubleshooting script:

```bash
cd ~/mitel-api
./troubleshoot-dns.sh
```

It will:
- Check if DNS is configured
- Verify IP address matches
- Test DNS propagation across multiple servers
- Test HTTP connectivity
- Provide specific recommendations

---

## ✅ Success Checklist

Once DNS is configured:

1. ✅ DNS resolves: `dig mitel-api.mission-ai.fr` shows your EC2 IP
2. ✅ HTTP works: `curl http://mitel-api.mission-ai.fr` connects
3. ✅ Run: `./setup-ssl.sh` and choose Let's Encrypt
4. ✅ Test HTTPS: `curl https://mitel-api.mission-ai.fr/api/health`
5. ✅ No browser warnings when accessing the domain

---

**Your domain will work with Let's Encrypt once DNS is properly configured!** 🚀

