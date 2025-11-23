# ⏱️ Token Expiration Configuration

## Overview

Bearer tokens can be configured to expire after a custom time period. This provides flexibility for different use cases: short-lived tokens for security, long-lived tokens for automation.

---

## 🔧 Configuration Methods

### **Method 1: Environment Variable (Default for All Tokens)**

Set the default expiration for all tokens:

```bash
# 1 hour (default)
TOKEN_EXPIRATION=3600 python3 app.py

# 2 hours
TOKEN_EXPIRATION=7200 python3 app.py

# 24 hours (for automation/scripts)
TOKEN_EXPIRATION=86400 python3 app.py

# 7 days (maximum allowed)
TOKEN_EXPIRATION=604800 python3 app.py
```

### **Method 2: Per-Login Request (Override Default)**

Specify expiration in the login request:

```bash
# Short-lived token (5 minutes)
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin@mitel.com",
    "password": "admin123",
    "expires_in": 300
  }'

# Long-lived token (24 hours)
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "api@mitel.com",
    "password": "apikey",
    "expires_in": 86400
  }'
```

---

## 📋 Common Expiration Times

| Duration | Seconds | Use Case | Example |
|----------|---------|----------|---------|
| 5 minutes | 300 | High security, testing | `"expires_in": 300` |
| 15 minutes | 900 | Temporary access | `"expires_in": 900` |
| 1 hour | 3600 | **Default - Interactive users** | `"expires_in": 3600` |
| 2 hours | 7200 | Extended sessions | `"expires_in": 7200` |
| 8 hours | 28800 | Work day | `"expires_in": 28800` |
| 24 hours | 86400 | Daily automation | `"expires_in": 86400` |
| 7 days | 604800 | **Maximum - Long-running scripts** | `"expires_in": 604800` |

---

## 🎯 Use Cases

### **Interactive Users (Default: 1 hour)**

```bash
# Login without specifying expiration - uses default
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@company.com",
    "password": "userpass"
  }'
```

**Response:**
```json
{
  "success": true,
  "access_token": "abc123...",
  "expires_in": 3600,  // 1 hour
  "user": {...}
}
```

### **API Service Accounts (24 hours)**

```bash
# Long-lived token for automated scripts
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "api@company.com",
    "password": "api_key_xyz",
    "expires_in": 86400
  }'
```

**Response:**
```json
{
  "success": true,
  "access_token": "xyz789...",
  "expires_in": 86400,  // 24 hours
  "user": {...}
}
```

### **Testing/Development (Short-lived)**

```bash
# 5-minute token for quick tests
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "dev@company.com",
    "password": "devpass",
    "expires_in": 300
  }'
```

---

## 🔒 Expiration Limits

### **Minimum: 60 seconds (1 minute)**
```bash
# Too short - will be rejected
curl -X POST http://localhost:5000/auth/login \
  -d '{"username":"user","password":"pass","expires_in":30}'

# Error response:
{
  "success": false,
  "error": {
    "code": "INVALID_EXPIRATION",
    "message": "Token expiration must be at least 60 seconds"
  }
}
```

### **Maximum: 604800 seconds (7 days)**
```bash
# Too long - will be rejected
curl -X POST http://localhost:5000/auth/login \
  -d '{"username":"user","password":"pass","expires_in":999999}'

# Error response:
{
  "success": false,
  "error": {
    "code": "INVALID_EXPIRATION",
    "message": "Token expiration cannot exceed 7 days (604800 seconds)"
  }
}
```

---

## 🐍 Python Examples

### **Default Expiration**

```python
import requests

# Login with default expiration (1 hour)
response = requests.post(
    "http://localhost:5000/auth/login",
    json={
        "username": "user@company.com",
        "password": "userpass"
    }
)

token_data = response.json()
print(f"Token expires in: {token_data['expires_in']} seconds")
```

### **Custom Expiration**

```python
import requests

# Login with 24-hour token
response = requests.post(
    "http://localhost:5000/auth/login",
    json={
        "username": "api@company.com",
        "password": "apikey",
        "expires_in": 86400  # 24 hours
    }
)

token_data = response.json()
access_token = token_data['access_token']
expires_in = token_data['expires_in']

print(f"Token valid for: {expires_in / 3600} hours")

# Use token for API calls
headers = {"Authorization": f"Bearer {access_token}"}
calls = requests.get(
    "http://localhost:5000/api/v1/reporting/calls",
    headers=headers,
    params={"limit": 100}
)
```

### **Token Expiration Handling**

```python
import requests
from datetime import datetime, timedelta

class MitelAPIClient:
    def __init__(self, base_url, username, password, token_lifetime=3600):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.token_lifetime = token_lifetime
        self.token = None
        self.token_expires_at = None
    
    def login(self):
        """Get a new token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={
                "username": self.username,
                "password": self.password,
                "expires_in": self.token_lifetime
            }
        )
        data = response.json()
        self.token = data['access_token']
        self.token_expires_at = datetime.now() + timedelta(seconds=data['expires_in'])
        print(f"Token acquired, expires at {self.token_expires_at}")
    
    def ensure_valid_token(self):
        """Refresh token if expired"""
        if not self.token or datetime.now() >= self.token_expires_at:
            print("Token expired or missing, getting new token...")
            self.login()
    
    def get_calls(self, start_date, end_date, limit=100):
        """Get calls with automatic token refresh"""
        self.ensure_valid_token()
        
        response = requests.get(
            f"{self.base_url}/api/v1/reporting/calls",
            headers={"Authorization": f"Bearer {self.token}"},
            params={
                "startDate": start_date,
                "endDate": end_date,
                "limit": limit
            }
        )
        return response.json()

# Usage
client = MitelAPIClient(
    "http://localhost:5000",
    "api@company.com",
    "apikey",
    token_lifetime=86400  # 24-hour tokens
)

# Token refreshes automatically
calls = client.get_calls("2025-11-20", "2025-11-22")
```

---

## 🐳 Docker/Kubernetes Configuration

### **Docker Compose**

```yaml
version: '3.8'
services:
  mitel-api:
    build: .
    environment:
      - REQUIRE_AUTH=true
      - USER_MGMT_MODE=env
      - TOKEN_EXPIRATION=7200  # 2 hours default
      - MITEL_USER_1=admin@company.com:secret:1:admin:Admin
```

### **Kubernetes ConfigMap**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mitel-api-config
data:
  REQUIRE_AUTH: "true"
  TOKEN_EXPIRATION: "3600"  # 1 hour
  USER_MGMT_MODE: "env"
```

### **Environment Variable**

```bash
# Development - short tokens
docker run -e TOKEN_EXPIRATION=1800 ...  # 30 minutes

# Production - longer tokens
docker run -e TOKEN_EXPIRATION=7200 ...  # 2 hours
```

---

## ⚙️ Configuration Examples

### **Development Environment**

```bash
# Short-lived tokens for testing
REQUIRE_AUTH=true \
TOKEN_EXPIRATION=900 \
USER_MGMT_MODE=simple \
python3 app.py
```

### **Production Environment**

```bash
# Longer tokens for production
REQUIRE_AUTH=true \
TOKEN_EXPIRATION=7200 \
USER_MGMT_MODE=env \
MITEL_USER_1=admin@company.com:${ADMIN_PASSWORD}:1:admin:Admin \
python3 app.py
```

### **API Automation**

```bash
# Very long tokens for automated scripts
REQUIRE_AUTH=true \
TOKEN_EXPIRATION=86400 \
USER_MGMT_MODE=json \
USERS_FILE=api_users.json \
python3 app.py
```

---

## 🔄 Token Lifecycle

### **1. Token Creation**
```
Login Request → Validate Credentials → Generate Token → Set Expiration
```

### **2. Token Usage**
```
API Request → Extract Token → Validate Token → Check Expiration → Allow/Deny
```

### **3. Token Expiration**
```
Time > Expiration → Token Invalid → Return 401 → Client Must Re-Login
```

---

## 📊 Token Expiration Response

When a token expires:

```bash
curl -H "Authorization: Bearer expired_token_123" \
  http://localhost:5000/api/v1/reporting/calls
```

**Response (401):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired bearer token"
  }
}
```

**Action:** Re-login to get a new token

---

## ✅ Best Practices

### **Security**
- ✅ Use **short-lived tokens** (1-2 hours) for interactive users
- ✅ Use **longer tokens** (24 hours) only for automation/service accounts
- ✅ Never set expiration > 7 days
- ✅ Implement token refresh logic in your app
- ❌ Don't use permanent tokens

### **Use Cases**
| Scenario | Recommended Expiration |
|----------|----------------------|
| Web application users | 1-2 hours (3600-7200) |
| Mobile app users | 4-8 hours (14400-28800) |
| API service accounts | 24 hours (86400) |
| CI/CD pipelines | 1-4 hours (3600-14400) |
| Testing/development | 15-30 minutes (900-1800) |

### **Implementation**
```python
# ✅ Good: Handle expiration gracefully
def make_api_call():
    try:
        response = api_call_with_token()
    except TokenExpiredError:
        refresh_token()
        response = api_call_with_token()
    return response

# ❌ Bad: Ignore expiration, fail on 401
def make_api_call():
    response = api_call_with_token()  # Will fail when token expires
    return response
```

---

## 🧪 Testing Different Expirations

```bash
# Test 5-minute expiration
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@mitel.com","password":"admin123","expires_in":300}'

# Save token
TOKEN="your_token_here"

# Use immediately (should work)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/v1/reporting/calls?limit=5

# Wait 6 minutes and try again (should fail with 401)
sleep 360
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/v1/reporting/calls?limit=5
```

---

## 📝 Summary

### **Set Default Expiration**
```bash
TOKEN_EXPIRATION=7200 python3 app.py  # All tokens last 2 hours
```

### **Override Per-Login**
```json
{
  "username": "user@example.com",
  "password": "password",
  "expires_in": 86400  // This token lasts 24 hours
}
```

### **Limits**
- Minimum: 60 seconds (1 minute)
- Maximum: 604800 seconds (7 days)
- Default: 3600 seconds (1 hour)

**Flexible token expiration for every use case!** ⏱️

