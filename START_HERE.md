# 🚀 Getting Started - Your Mitel API Mock Server

Hi! Your Mitel API Mock Server is ready to use. Here's how to get started in 3 simple steps.

---

## 🎯 What You Got

A complete mock API that simulates your Mitel telephony system. It generates data exactly like your CSV file shows.

**Location**: `/Users/tarik.boukherissa/Documents/mitel-api`

---

## ⚡ Quick Test (30 seconds)

### Step 1: Install Dependencies
```bash
cd /Users/tarik.boukherissa/Documents/mitel-api
pip3 install -r requirements.txt
```

### Step 2: Start the Server
```bash
python3 app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Step 3: Test It (in a new terminal)
```bash
# Test health
curl http://localhost:5000/api/health

# Get some call records
curl http://localhost:5000/api/v1/cdr?limit=5 | python3 -m json.tool
```

✅ **If you see JSON data, it's working!**

---

## 🧪 Run the Full Test Suite

```bash
pip3 install -r requirements-dev.txt
python3 test_api.py
```

This tests all 7 endpoints automatically.

---

## 📖 See All Examples

```bash
./examples.sh
```

This shows you how to use every endpoint.

---

## 🐳 Deploy with Docker (Recommended for EC2)

### Build and Run
```bash
./deploy-docker.sh
```

### Check Status
```bash
docker-compose ps
docker-compose logs -f
```

### Stop
```bash
docker-compose stop
```

---

## ☁️ Deploy to AWS EC2

### Prerequisites
1. Launch an Amazon Linux 2023 EC2 instance (t2.small recommended)
2. Security Group: Allow ports 22 (SSH) and 5000 (API)
3. Download your .pem key file

### Deploy Steps

#### 1. Copy Files to EC2
```bash
# Replace with your values
export EC2_IP="your-ec2-public-ip"
export KEY_FILE="/path/to/your-key.pem"

# Copy all files
scp -i $KEY_FILE -r /Users/tarik.boukherissa/Documents/mitel-api/* ec2-user@$EC2_IP:~/mitel-api/
```

#### 2. Connect and Deploy
```bash
# SSH to EC2
ssh -i $KEY_FILE ec2-user@$EC2_IP

# Deploy
cd ~/mitel-api
./deploy-docker.sh
```

#### 3. Test
```bash
# From your local machine
curl http://YOUR_EC2_IP:5000/api/health
curl http://YOUR_EC2_IP:5000/api/v1/cdr?limit=5
```

---

## 📱 Use in Your Application

### Python Example
```python
import requests

# Point to your API (local or EC2)
api_url = "http://localhost:5000"  # or "http://your-ec2-ip:5000"

# Get CDR records
response = requests.get(f"{api_url}/api/v1/cdr?limit=100")
data = response.json()

for record in data['records']:
    print(f"Call ID: {record['CallId']}")
    print(f"Extension: {record['Extno']}")
    print(f"Duration: {record['Duration']} seconds")
    print(f"Direction: {record['Direction']}")
    print("---")
```

### JavaScript Example
```javascript
const apiUrl = "http://localhost:5000"; // or your EC2 IP

fetch(`${apiUrl}/api/v1/cdr?limit=50`)
  .then(response => response.json())
  .then(data => {
    data.records.forEach(record => {
      console.log(`Call ${record.CallId}: ${record.Duration}s`);
    });
  });
```

### cURL Examples
```bash
# Get 10 records
curl "http://localhost:5000/api/v1/cdr?limit=10"

# Filter by extension
curl "http://localhost:5000/api/v1/cdr?extension=694311"

# Filter by direction (I=Inbound, O=Outbound, B=Both)
curl "http://localhost:5000/api/v1/cdr?direction=I&limit=20"

# Export as CSV
curl "http://localhost:5000/api/v1/cdr/export?limit=100" > calls.csv

# Get call statistics
curl "http://localhost:5000/api/v1/stats"

# Get extensions list
curl "http://localhost:5000/api/v1/extensions"
```

---

## 🎯 Available Endpoints

| Endpoint | What It Does |
|----------|--------------|
| `GET /` | Shows API info and all endpoints |
| `GET /api/health` | Checks if API is running |
| `GET /api/v1/cdr` | Gets call detail records |
| `GET /api/v1/cdr/stream` | Gets records in Kafka format (like your CSV) |
| `GET /api/v1/cdr/export` | Downloads records as CSV file |
| `GET /api/v1/extensions` | Lists all phone extensions |
| `GET /api/v1/stats` | Shows call statistics |

---

## 🔧 Customizing the Mock Data

Want different usernames or extensions? Edit `app.py`:

```python
# Around line 20-40, find these arrays:

USERNAMES = [
    "PTP AG4311,METZ", 
    "COMPTOIR,FIXE2469",
    # Add your own names here
]

EXTENSIONS = [
    "694311", 
    "711540",
    # Add your own extensions here
]
```

Save and restart the server.

---

## 📚 Need More Help?

| Question | Read This |
|----------|-----------|
| "How do I start?" | You're reading it! 😊 |
| "What's the quick way?" | `QUICKSTART.md` |
| "What are all the files?" | `STRUCTURE.md` |
| "How do I deploy properly?" | `DEPLOYMENT_CHECKLIST.md` |
| "What's the big picture?" | `OVERVIEW.md` or `PROJECT_SUMMARY.md` |
| "Full documentation?" | `README.md` |

---

## 🎓 Your Workflow

### For Development
1. Run locally: `python3 app.py`
2. Test your app against: `http://localhost:5000`
3. See example code above ☝️

### For Testing
1. Run test suite: `python3 test_api.py`
2. Check examples: `./examples.sh`

### For Production
1. Deploy to EC2 (see steps above)
2. Point your app to: `http://your-ec2-ip:5000`
3. Monitor: `docker-compose logs -f`

---

## 🐛 Troubleshooting

### "Port 5000 already in use"
```bash
sudo lsof -i :5000
sudo kill -9 <PID>
```

### "Module not found"
```bash
pip3 install -r requirements.txt
```

### "Can't connect to EC2"
- Check Security Group allows port 5000
- Verify service is running: `docker-compose ps`

### "Permission denied on .sh files"
```bash
chmod +x deploy-ec2.sh deploy-docker.sh examples.sh test_api.py
```

---

## ✨ Pro Tips

1. **Use Postman**: Import `Mitel_API_Mock.postman_collection.json` for easy testing
2. **Check logs**: Add `&& docker-compose logs -f` to see what's happening
3. **Test first**: Always run `test_api.py` before deploying
4. **Secure it**: For production, add authentication (instructions in `README.md`)

---

## 🎉 You're All Set!

Your Mitel API mock is ready. Start with a local test:

```bash
# Terminal 1
python3 app.py

# Terminal 2
curl http://localhost:5000/api/v1/cdr?limit=5
```

When you're ready, deploy to EC2 and use it in your application!

**Questions?** Check the documentation files listed above.

**Happy coding!** 🚀

