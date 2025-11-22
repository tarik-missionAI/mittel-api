# Quick Start Guide - Mitel API Mock Server

This guide will help you get the Mitel API Mock Server up and running in under 5 minutes.

## Prerequisites

- Python 3.8+ (local development)
- Docker & Docker Compose (for containerized deployment)
- AWS EC2 instance (for cloud deployment)

## Option 1: Local Development (Fastest)

### Step 1: Install Dependencies

```bash
cd /Users/tarik.boukherissa/Documents/mitel-api
pip3 install -r requirements.txt
```

### Step 2: Run the Server

```bash
python3 app.py
```

The server will start on `http://localhost:5000`

### Step 3: Test the API

Open a new terminal and run:

```bash
# Simple test
curl http://localhost:5000/api/health

# Get CDR records
curl http://localhost:5000/api/v1/cdr?limit=5

# Or run the full test suite
pip3 install -r requirements-dev.txt
python3 test_api.py
```

## Option 2: Docker Deployment (Recommended for Production)

### Step 1: Build and Run

```bash
cd /Users/tarik.boukherissa/Documents/mitel-api
./deploy-docker.sh
```

Or manually:

```bash
docker-compose up -d
```

### Step 2: Verify It's Running

```bash
docker-compose ps
docker-compose logs -f
```

### Step 3: Test

```bash
curl http://localhost:5000/api/health
```

## Option 3: AWS EC2 Deployment

### Step 1: Launch EC2 Instance

1. Go to AWS Console → EC2
2. Launch instance:
   - AMI: Ubuntu Server 20.04 LTS
   - Instance type: t2.small (recommended) or t2.micro
   - Storage: 8 GB
   - Create/use existing key pair

### Step 2: Configure Security Group

Add these inbound rules:
- SSH (22) from your IP
- Custom TCP (5000) from 0.0.0.0/0 (or your IP range)

### Step 3: Copy Files to EC2

From your local machine:

```bash
# Replace with your values
EC2_IP="your-ec2-public-ip"
KEY_FILE="path/to/your-key.pem"

# Copy all files
scp -i $KEY_FILE -r /Users/tarik.boukherissa/Documents/mitel-api/* ubuntu@$EC2_IP:~/mitel-api/
```

### Step 4: Connect and Deploy

```bash
# Connect to EC2
ssh -i $KEY_FILE ubuntu@$EC2_IP

# Deploy with Docker (recommended)
cd ~/mitel-api
./deploy-docker.sh

# OR deploy with systemd
cd ~/mitel-api
./deploy-ec2.sh
```

### Step 5: Test Your EC2 Deployment

From your local machine:

```bash
curl http://your-ec2-ip:5000/api/health
curl http://your-ec2-ip:5000/api/v1/cdr?limit=5
```

## Common Commands

### Local Development

```bash
# Start server
python3 app.py

# Run tests
python3 test_api.py

# Run examples
./examples.sh
```

### Docker

```bash
# Start
docker-compose up -d

# Stop
docker-compose stop

# Restart
docker-compose restart

# View logs
docker-compose logs -f

# Remove
docker-compose down
```

### EC2 (systemd deployment)

```bash
# Check status
sudo systemctl status mitel-api-mock

# View logs
sudo journalctl -u mitel-api-mock -f

# Restart
sudo systemctl restart mitel-api-mock

# Stop
sudo systemctl stop mitel-api-mock
```

## Available Endpoints

Once running, you can access:

- **API Home**: `http://localhost:5000/`
- **Health Check**: `http://localhost:5000/api/health`
- **CDR Records**: `http://localhost:5000/api/v1/cdr?limit=10`
- **CDR Stream**: `http://localhost:5000/api/v1/cdr/stream?limit=10`
- **Extensions**: `http://localhost:5000/api/v1/extensions`
- **Statistics**: `http://localhost:5000/api/v1/stats`
- **Export CSV**: `http://localhost:5000/api/v1/cdr/export?limit=100`

## Troubleshooting

### Port 5000 already in use

```bash
# Find and kill the process
sudo lsof -i :5000
sudo kill -9 <PID>
```

### Can't connect to EC2

1. Check Security Group allows port 5000
2. Verify service is running: `sudo systemctl status mitel-api-mock`
3. Check firewall: `sudo ufw status`

### Docker issues

```bash
# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Next Steps

1. ✅ Test all endpoints using `test_api.py`
2. ✅ Review the API documentation in `README.md`
3. ✅ Customize mock data in `app.py` if needed
4. ✅ Integrate with your application

## Support

For detailed documentation, see `README.md`

For issues:
- Check logs for error messages
- Verify all dependencies are installed
- Ensure ports are not blocked

Happy coding! 🚀

