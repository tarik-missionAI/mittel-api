# 🔐 Authentication Guide - Mitel API Mock

## Overview

The mock API supports **optional Bearer Token authentication** matching Mitel's official authentication flow, with **three user management modes** for different use cases.

---

## 👥 User Management Modes

### **Mode 1: Simple (Default) - Hardcoded Users**
- Best for: Quick testing, demos
- Users defined in code
- No external files needed

**Default Users:**
```
admin@mitel.com / admin123  (role: admin)
user@mitel.com / user123    (role: user)
```

### **Mode 2: JSON File - External Configuration**
- Best for: Development, multiple environments
- Users in `users.json` file
- Easy to modify without code changes

### **Mode 3: Environment Variables - Cloud/Docker**
- Best for: Production, containers, secret management
- Users from environment variables
- Integrates with secret managers

---

## 🎛️ How to Configure

### **Step 1: Choose User Management Mode**

#### **Option A: Simple Mode (Default)**
```bash
# Just run - uses hardcoded users
python3 app.py
```

#### **Option B: JSON File Mode**
```bash
# Uses users.json file
USER_MGMT_MODE=json python3 app.py
```

#### **Option C: Environment Variables Mode**
```bash
# Uses environment variables
USER_MGMT_MODE=env \
MITEL_USER_1=admin@company.com:secret123:1:admin:Admin User \
MITEL_USER_2=user@company.com:pass456:1:user:Regular User \
python3 app.py
```

### **Step 2: Enable Authentication**

```bash
# Enable auth with your chosen user mode
REQUIRE_AUTH=true USER_MGMT_MODE=json python3 app.py
```

---

## 📝 Managing Users

### **Simple Mode - Hardcoded Users**

Edit `app.py` to add/modify users:

```python
SIMPLE_USERS = {
    "admin@mitel.com": {
        "password": "admin123",
        "account_id": "1",
        "role": "admin",
        "name": "Admin User"
    },
    "your_user@company.com": {
        "password": "your_password",
        "account_id": "1",
        "role": "user",
        "name": "Your Name"
    }
}
```

### **JSON File Mode - External Configuration**

Create/edit `users.json`:

```json
{
  "users": [
    {
      "username": "admin@company.com",
      "password": "secure_password_123",
      "account_id": "1",
      "role": "admin",
      "name": "Admin User"
    },
    {
      "username": "user1@company.com",
      "password": "user_pass_456",
      "account_id": "1",
      "role": "user",
      "name": "User One"
    },
    {
      "username": "supervisor@company.com",
      "password": "super_pass_789",
      "account_id": "2",
      "role": "supervisor",
      "name": "Supervisor User"
    }
  ]
}
```

**Run with JSON mode:**
```bash
REQUIRE_AUTH=true USER_MGMT_MODE=json python3 app.py
```

**Custom JSON file location:**
```bash
REQUIRE_AUTH=true USER_MGMT_MODE=json USERS_FILE=/path/to/custom_users.json python3 app.py
```

### **Environment Variables Mode - Cloud/Docker**

Set environment variables:

```bash
# Format: MITEL_USER_N=username:password:account_id:role:name
export MITEL_USER_1=admin@company.com:admin_secret:1:admin:Admin User
export MITEL_USER_2=user@company.com:user_secret:1:user:Regular User
export MITEL_USER_3=api@company.com:api_key_xyz:1:api:API Service Account

# Run with env mode
REQUIRE_AUTH=true USER_MGMT_MODE=env python3 app.py
```

**Docker example:**
```dockerfile
ENV REQUIRE_AUTH=true
ENV USER_MGMT_MODE=env
ENV MITEL_USER_1=admin@company.com:secret123:1:admin:Admin
ENV MITEL_USER_2=user@company.com:pass456:1:user:User
```

---

## 🎛️ Authentication On/Off

### **Disabled (Default) - Easy Development**
```bash
# No authentication required
python3 app.py
curl http://localhost:5000/api/v1/reporting/calls?limit=10
```

### **Enabled - Production-Like**
```bash
# Requires bearer token
REQUIRE_AUTH=true python3 app.py
curl http://localhost:5000/api/v1/reporting/calls?limit=10
# Returns 401 Unauthorized
```

---

## 🔑 Getting a Bearer Token

### **1. Request Token**

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password",
    "account_id": "12345"
  }'
```

**Response:**
```json
{
  "success": true,
  "access_token": "mitel_mock_token_12345",
  "refresh_token": "refresh_token_67890",
  "token_type": "Bearer",
  "expires_in": 3600,
  "account_id": "12345"
}
```

### **2. Use Token in Requests**

```bash
curl http://localhost:5000/api/v1/reporting/calls?limit=10 \
  -H "Authorization: Bearer mitel_mock_token_12345"
```

---

## 📋 Authentication Flow

### **Without Authentication (Default)**

```bash
# 1. Start server (auth disabled by default)
python3 app.py

# 2. Make requests directly
curl http://localhost:5000/api/v1/reporting/calls?limit=5
```

### **With Authentication**

```bash
# 1. Start server with auth enabled
REQUIRE_AUTH=true python3 app.py

# 2. Get token
TOKEN=$(curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}' \
  | jq -r '.access_token')

# 3. Use token in requests
curl http://localhost:5000/api/v1/reporting/calls?limit=5 \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🐍 Python Examples

### **Without Authentication**

```python
import requests

# No auth needed
response = requests.get(
    "http://localhost:5000/api/v1/reporting/calls",
    params={"limit": 10}
)
print(response.json())
```

### **With Authentication**

```python
import requests

# 1. Get token
auth_response = requests.post(
    "http://localhost:5000/auth/login",
    json={
        "username": "user@example.com",
        "password": "password123",
        "account_id": "12345"
    }
)
token = auth_response.json()['access_token']

# 2. Use token in requests
headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(
    "http://localhost:5000/api/v1/reporting/calls",
    params={"limit": 10},
    headers=headers
)

calls = response.json()
print(f"Retrieved {len(calls['data'])} calls")
```

---

## 🔒 Protected Endpoints

When `REQUIRE_AUTH=true`, these endpoints require authentication:

| Endpoint | Requires Token |
|----------|----------------|
| `POST /auth/login` | ❌ No |
| `GET /` | ❌ No |
| `GET /health` | ❌ No |
| `GET /api/v1/reporting/calls` | ✅ Yes |
| `GET /api/v1/reporting/calls/stream` | ✅ Yes |
| `GET /api/v1/reporting/calls/export` | ✅ Yes |
| `GET /api/v1/reporting/agents` | ✅ Yes |
| `GET /api/v1/reporting/statistics` | ✅ Yes |

---

## ⚠️ Error Responses

### **Missing Authorization Header**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing Authorization header. Include 'Authorization: Bearer <token>'"
  }
}
```
**HTTP Status:** 401

### **Invalid Format**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_AUTH_FORMAT",
    "message": "Authorization header must use Bearer token format: 'Bearer <token>'"
  }
}
```
**HTTP Status:** 401

### **Invalid Token**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired bearer token"
  }
}
```
**HTTP Status:** 401

---

## 🎯 Real Mitel API Authentication

### **Production Mitel API Uses:**

1. **OAuth 2.0 Authorization Code Flow**
   ```
   https://auth.mitel.io/authorize?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=YOUR_REDIRECT
   ```

2. **Token Endpoint**
   ```
   POST https://auth.mitel.io/token
   ```

3. **Bearer Token in Requests**
   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJyb2xlIjoiMSIsInN1YiI6Im14b25lX2FkbWluIiwiaWF0...
   ```

4. **Additional Headers**
   ```
   X-Mitel-App: app=MyApp/1.0;platform=Linux/Ubuntu;session=abc123;
   ```

---

## 🧪 Testing Authentication

### **Test Without Auth (Default)**
```bash
# Start server
python3 app.py

# Test - should work
curl http://localhost:5000/api/v1/reporting/calls?limit=5
```

### **Test With Auth**
```bash
# Start server with auth
REQUIRE_AUTH=true python3 app.py

# Test without token - should fail
curl http://localhost:5000/api/v1/reporting/calls?limit=5

# Get token
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Test with token - should work
curl http://localhost:5000/api/v1/reporting/calls?limit=5 \
  -H "Authorization: Bearer mitel_mock_token_12345"
```

---

## 🔧 Configuration

### **Environment Variables**

| Variable | Default | Description |
|----------|---------|-------------|
| `REQUIRE_AUTH` | `false` | Set to `true` to enable authentication |

### **Enable Authentication**

```bash
# Option 1: Environment variable
export REQUIRE_AUTH=true
python3 app.py

# Option 2: Inline
REQUIRE_AUTH=true python3 app.py

# Option 3: Docker
docker run -e REQUIRE_AUTH=true ...
```

### **Mock Token**

For testing, the mock accepts any token: `mitel_mock_token_12345`

In production, this would be validated against Mitel's auth service.

---

## 📖 Quick Reference

### **Get Token**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'
```

### **Use Token**
```bash
curl http://localhost:5000/api/v1/reporting/calls \
  -H "Authorization: Bearer mitel_mock_token_12345"
```

### **Python**
```python
headers = {"Authorization": "Bearer mitel_mock_token_12345"}
response = requests.get(url, headers=headers)
```

---

## 💡 Best Practices

1. **Development**: Keep auth disabled (`REQUIRE_AUTH=false`)
2. **Testing**: Enable auth to test integration
3. **Production**: Real Mitel uses OAuth 2.0, not this mock token
4. **Security**: Never commit real tokens to git

---

## ✅ Summary

- ✅ **Optional authentication** - disabled by default
- ✅ **Bearer token format** - matches Mitel API
- ✅ **Login endpoint** - `/auth/login`
- ✅ **Protected endpoints** - all reporting endpoints
- ✅ **Easy toggle** - `REQUIRE_AUTH` environment variable
- ✅ **Production-like** - mimics real Mitel authentication flow

**Enable when you need to test auth flows, disable for easy development!**

