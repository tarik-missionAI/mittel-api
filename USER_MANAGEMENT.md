# 👥 User Management Guide

## Overview

The Mitel API Mock supports **three user management modes** to handle authentication:

1. **Simple Mode** - Hardcoded users (default)
2. **JSON File Mode** - External configuration file
3. **Environment Variables Mode** - For containers/cloud

---

## 🎯 Quick Start

### **Default Users (Simple Mode)**

```bash
# Start with auth enabled
REQUIRE_AUTH=true python3 app.py

# Login with default users
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@mitel.com","password":"admin123"}'
```

**Default users:**
- `admin@mitel.com` / `admin123` (admin role)
- `user@mitel.com` / `user123` (user role)

---

## 🔧 Mode 1: Simple (Hardcoded Users)

### **When to Use:**
- ✅ Quick testing
- ✅ Demos
- ✅ Local development
- ❌ Don't use for production

### **How it Works:**
Users are defined directly in `app.py`:

```python
SIMPLE_USERS = {
    "admin@mitel.com": {
        "password": "admin123",
        "account_id": "1",
        "role": "admin",
        "name": "Admin User"
    },
    "user@mitel.com": {
        "password": "user123",
        "account_id": "1",
        "role": "user",
        "name": "Regular User"
    }
}
```

### **Add New Users:**

1. Edit `app.py`
2. Find `SIMPLE_USERS` dictionary
3. Add new user:

```python
SIMPLE_USERS = {
    # ... existing users ...
    "myuser@company.com": {
        "password": "mypassword",
        "account_id": "1",
        "role": "user",
        "name": "My Name"
    }
}
```

4. Restart server

### **Run:**
```bash
# Default mode (simple)
REQUIRE_AUTH=true python3 app.py

# Or explicitly
REQUIRE_AUTH=true USER_MGMT_MODE=simple python3 app.py
```

---

## 📄 Mode 2: JSON File

### **When to Use:**
- ✅ Multiple environments (dev/staging/prod)
- ✅ Easy user management without code changes
- ✅ Team collaboration
- ✅ Recommended for development

### **Setup:**

1. Create `users.json` file:

```json
{
  "users": [
    {
      "username": "admin@company.com",
      "password": "SecurePass123!",
      "account_id": "1",
      "role": "admin",
      "name": "Admin User"
    },
    {
      "username": "john@company.com",
      "password": "JohnPass456!",
      "account_id": "1",
      "role": "user",
      "name": "John Doe"
    },
    {
      "username": "supervisor@company.com",
      "password": "SuperPass789!",
      "account_id": "2",
      "role": "supervisor",
      "name": "Jane Smith"
    },
    {
      "username": "api_service@company.com",
      "password": "ApiKey_XYZ_123",
      "account_id": "1",
      "role": "api",
      "name": "API Service Account"
    }
  ]
}
```

2. Run with JSON mode:

```bash
REQUIRE_AUTH=true USER_MGMT_MODE=json python3 app.py
```

### **Custom File Location:**

```bash
REQUIRE_AUTH=true \
USER_MGMT_MODE=json \
USERS_FILE=/path/to/my_users.json \
python3 app.py
```

### **Add/Remove Users:**

1. Edit `users.json`
2. Restart server
3. New users active immediately

### **Different Files for Environments:**

```bash
# Development
USERS_FILE=users.dev.json python3 app.py

# Staging
USERS_FILE=users.staging.json python3 app.py

# Production
USERS_FILE=users.prod.json python3 app.py
```

---

## 🌍 Mode 3: Environment Variables

### **When to Use:**
- ✅ Docker/Kubernetes deployments
- ✅ Cloud platforms (AWS, Azure, GCP)
- ✅ Secret management systems
- ✅ **Recommended for production**

### **Setup:**

Set environment variables with format:
```
MITEL_USER_N=username:password:account_id:role:name
```

**Example:**

```bash
export MITEL_USER_1=admin@company.com:SecurePass123:1:admin:Admin User
export MITEL_USER_2=user@company.com:UserPass456:1:user:Regular User
export MITEL_USER_3=api@company.com:ApiKey789:1:api:API Service
```

### **Run:**

```bash
REQUIRE_AUTH=true USER_MGMT_MODE=env python3 app.py
```

### **Docker Example:**

**Dockerfile:**
```dockerfile
ENV REQUIRE_AUTH=true
ENV USER_MGMT_MODE=env
ENV MITEL_USER_1=admin@company.com:secret123:1:admin:Admin
ENV MITEL_USER_2=user@company.com:pass456:1:user:User
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  mitel-api:
    build: .
    environment:
      - REQUIRE_AUTH=true
      - USER_MGMT_MODE=env
      - MITEL_USER_1=admin@company.com:secret123:1:admin:Admin User
      - MITEL_USER_2=user@company.com:pass456:1:user:Regular User
```

### **Kubernetes Secret:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mitel-users
type: Opaque
stringData:
  MITEL_USER_1: "admin@company.com:SecurePass:1:admin:Admin"
  MITEL_USER_2: "user@company.com:UserPass:1:user:User"
```

### **AWS Secrets Manager / Azure Key Vault:**

```bash
# Fetch from secret manager and set as env vars
export MITEL_USER_1=$(aws secretsmanager get-secret-value --secret-id mitel/user1 --query SecretString --output text)
export MITEL_USER_2=$(aws secretsmanager get-secret-value --secret-id mitel/user2 --query SecretString --output text)

# Run
REQUIRE_AUTH=true USER_MGMT_MODE=env python3 app.py
```

---

## 📋 User Fields Reference

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `username` | ✅ Yes | Unique username (email recommended) | `admin@company.com` |
| `password` | ✅ Yes | Password (plaintext in mock) | `SecurePass123` |
| `account_id` | ⚠️ Optional | Account/tenant ID | `1` (default) |
| `role` | ⚠️ Optional | User role | `admin`, `user`, `supervisor`, `api` |
| `name` | ⚠️ Optional | Display name | `Admin User` |

---

## 🧪 Testing Users

### **List All Users**

```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin@mitel.com","password":"admin123"}' \
  | jq -r '.access_token')

# List users
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/auth/users
```

**Response:**
```json
{
  "success": true,
  "users": [
    {
      "username": "admin@mitel.com",
      "account_id": "1",
      "role": "admin",
      "name": "Admin User"
    },
    {
      "username": "user@mitel.com",
      "account_id": "1",
      "role": "user",
      "name": "Regular User"
    }
  ],
  "count": 2,
  "management_mode": "simple"
}
```

---

## 🔐 Security Best Practices

### **Development**
- ✅ Use simple mode for local testing
- ✅ Use weak passwords (admin123, user123)
- ✅ Commit `users.json` to git (if needed)

### **Staging**
- ✅ Use JSON file mode
- ⚠️ Use stronger passwords
- ⚠️ Don't commit `users.json` to git

### **Production**
- ✅ **Use environment variables mode**
- ✅ **Strong, unique passwords**
- ✅ **Store in secret manager** (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
- ✅ **Rotate passwords regularly**
- ✅ **Use service accounts for APIs**
- ❌ **Never commit passwords to git**
- ❌ **Never hardcode in code**

### **Password Guidelines (Production)**
```
❌ Bad:  admin123, password, 123456
✅ Good: Xk9!mP2@qL5$wN8#rT3^
```

### **In Production, Use Real Auth Systems**
This mock is for **development only**. In production:
- Use OAuth 2.0
- Use JWT with proper signing
- Use external auth services (Auth0, Okta, Azure AD)
- Implement password hashing (bcrypt, argon2)
- Add multi-factor authentication (MFA)

---

## 🎯 Quick Comparison

| Feature | Simple | JSON File | Environment Variables |
|---------|--------|-----------|---------------------|
| **Setup** | None | Create JSON file | Set env vars |
| **Modify Users** | Edit code | Edit JSON | Update env vars |
| **Restart Required** | Yes | Yes | Yes |
| **Git Safe** | ⚠️ In code | ❌ Secrets in file | ✅ Not in code |
| **Multi-Env** | ❌ No | ✅ Yes | ✅ Yes |
| **Containers** | ⚠️ Rebuild | ⚠️ Mount volume | ✅ Perfect |
| **Best For** | Dev/Demo | Dev/Staging | Staging/Prod |

---

## 📝 Examples

### **Example 1: Development Team**

```bash
# Create users.dev.json
cat > users.dev.json << EOF
{
  "users": [
    {"username": "alice@dev.com", "password": "alice123", "role": "admin", "name": "Alice"},
    {"username": "bob@dev.com", "password": "bob123", "role": "user", "name": "Bob"},
    {"username": "charlie@dev.com", "password": "charlie123", "role": "user", "name": "Charlie"}
  ]
}
EOF

# Run
REQUIRE_AUTH=true USER_MGMT_MODE=json USERS_FILE=users.dev.json python3 app.py
```

### **Example 2: Docker Production**

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .

# Don't hardcode users - use env vars!
ENV REQUIRE_AUTH=true
ENV USER_MGMT_MODE=env

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

```bash
# Pass users at runtime
docker run -p 5000:5000 \
  -e MITEL_USER_1=admin@company.com:$ADMIN_PASSWORD:1:admin:Admin \
  -e MITEL_USER_2=api@company.com:$API_KEY:1:api:API \
  mitel-api
```

### **Example 3: Multiple Accounts/Tenants**

```json
{
  "users": [
    {
      "username": "admin@tenant1.com",
      "password": "pass1",
      "account_id": "tenant_001",
      "role": "admin",
      "name": "Tenant 1 Admin"
    },
    {
      "username": "admin@tenant2.com",
      "password": "pass2",
      "account_id": "tenant_002",
      "role": "admin",
      "name": "Tenant 2 Admin"
    }
  ]
}
```

---

## ❓ FAQ

**Q: How do I add a new user without restarting?**
A: Currently requires restart. In production, you'd use a database with hot-reload.

**Q: Can I use a database for users?**
A: Not in this mock, but you could modify `get_users()` to query a database.

**Q: Are passwords hashed?**
A: No - this is a mock for development. In production, **always hash passwords** (bcrypt, argon2).

**Q: Can I mix modes?**
A: No - choose one mode at a time via `USER_MGMT_MODE`.

**Q: What if `users.json` is missing?**
A: Falls back to simple mode with default users.

**Q: How do I disable authentication?**
A: Set `REQUIRE_AUTH=false` or just run `python3 app.py` (disabled by default).

---

## ✅ Summary

Choose your mode:

- **Testing locally?** → Use **Simple mode** (default)
- **Development team?** → Use **JSON file mode**
- **Production/Docker?** → Use **Environment variables mode**

**Remember**: This is a mock for development. In production, use proper authentication systems!

---

**See also:**
- `AUTHENTICATION.md` - How to use authentication
- `QUICK_REFERENCE.md` - Quick commands
- `API_STRUCTURE.md` - Complete API reference

