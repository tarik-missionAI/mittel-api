# Mitel API Mock - Quick Reference

## 🚀 Quick Start

```bash
# Start the server
python3 app.py

# Test it
curl http://localhost:5000/api/v1/reporting/calls?limit=10
```

---

## 📋 All Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/v1/reporting/calls` | GET | Get call records |
| `/api/v1/reporting/calls/stream` | GET | Kafka format stream |
| `/api/v1/reporting/calls/export` | GET | Export as CSV |
| `/api/v1/reporting/agents` | GET | Get agents/extensions |
| `/api/v1/reporting/statistics` | GET | Get statistics & KPIs |

---

## 🔧 Common Query Parameters

### Filters
- `startDate` - Start date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- `endDate` - End date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- `extension` - Extension number (e.g., 694311)
- `direction` - Call direction (I/O/B)

### Pagination
- `limit` - Max records (default: 50, max: 500)
- `offset` - Offset for pagination (default: 0)

---

## 💡 Quick Examples

### Get calls for a specific date
```bash
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20&endDate=2025-11-20&limit=100"
```

### Get calls for date range
```bash
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-15&endDate=2025-11-22&limit=200"
```

### Filter by extension
```bash
curl "http://localhost:5000/api/v1/reporting/calls?extension=694311&limit=50"
```

### Filter by direction (Inbound only)
```bash
curl "http://localhost:5000/api/v1/reporting/calls?direction=I&limit=50"
```

### Combined filters
```bash
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20&extension=694311&direction=I&limit=50"
```

### Export to CSV
```bash
curl "http://localhost:5000/api/v1/reporting/calls/export?startDate=2025-11-20&endDate=2025-11-22&limit=1000" > calls.csv
```

### Get Kafka stream
```bash
curl "http://localhost:5000/api/v1/reporting/calls/stream?startDate=2025-11-20&limit=50"
```

### Get statistics
```bash
curl "http://localhost:5000/api/v1/reporting/statistics?startDate=2025-11-20&endDate=2025-11-22"
```

---

## 🐍 Python Quick Start

```python
import requests

base_url = "http://localhost:5000/api/v1/reporting"

# Get calls
response = requests.get(
    f"{base_url}/calls",
    params={
        "startDate": "2025-11-20",
        "endDate": "2025-11-22",
        "limit": 100
    }
)

calls = response.json()['data']
print(f"Found {len(calls)} calls")
```

---

## 📊 Response Format

```json
{
  "success": true,
  "data": [...],
  "filters": {
    "startDate": "2025-11-20",
    "endDate": "2025-11-22",
    "extension": null,
    "direction": null
  },
  "pagination": {
    "limit": 50,
    "offset": 0,
    "total": 50,
    "hasMore": false
  },
  "timestamp": "2025-11-22T10:30:00"
}
```

---

## 🧪 Testing

```bash
# Run full test suite
python3 test_api.py

# Run examples
./examples.sh
```

---

## 📖 Full Documentation

- **Complete API docs**: `API_STRUCTURE.md`
- **Date filtering**: `DATE_FILTERING_GUIDE.md`
- **Getting started**: `START_HERE.md`
- **Mitel compliance**: `MITEL_COMPLIANCE_SUMMARY.md`
- **Deployment**: `DEPLOYMENT_CHECKLIST.md`

---

## ⚡ Key Features

✅ Mitel MiContact Center compliant
✅ Date range filtering (startDate/endDate)
✅ Extension and direction filtering
✅ Kafka message format support
✅ CSV export with date range in filename
✅ Journey analytics fields
✅ VoIP quality metrics
✅ Production-ready

---

**Version:** 1.0  
**API Version:** v1  
**Base Path:** `/api/v1`

