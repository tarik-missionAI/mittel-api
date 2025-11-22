# Date Filtering Guide - Mitel API Mock

## 📅 Date Range Support

The Mitel MiContact Center API supports date range filtering on all reporting endpoints. This allows you to retrieve historical data for specific time periods.

---

## Supported Date Formats

### ISO 8601 Standard

All date parameters support ISO 8601 format:

| Format | Example | Description |
|--------|---------|-------------|
| **Date only** | `2025-11-20` | Automatically uses 00:00:00 for startDate, 23:59:59 for endDate |
| **Date + Time** | `2025-11-20T10:30:00` | Specific date and time |
| **Date + Time + Z** | `2025-11-20T10:30:00Z` | UTC timezone indicator |

---

## Query Parameters

### All Reporting Endpoints Support:

- `startDate` - Start of date range (ISO 8601)
- `endDate` - End of date range (ISO 8601)

### Additional Parameters:

- `limit` - Maximum records to return (default: varies by endpoint)
- `offset` - Pagination offset (default: 0)
- `extension` - Filter by extension number
- `direction` - Filter by call direction (I/O/B)

---

## Examples

### 1. Date Only (Recommended for Daily Reports)

```bash
# Get all calls on November 20, 2025
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20&endDate=2025-11-20&limit=100"

# Get calls for a week
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-15&endDate=2025-11-22&limit=500"
```

### 2. Date + Time (For Precise Time Ranges)

```bash
# Get calls during business hours on Nov 20
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20T09:00:00&endDate=2025-11-20T17:00:00&limit=200"

# Get overnight calls
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20T22:00:00&endDate=2025-11-21T06:00:00&limit=100"
```

### 3. Open-Ended Ranges

```bash
# All calls after November 20 (up to current time)
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20&limit=100"

# All calls before November 22
curl "http://localhost:5000/api/v1/reporting/calls?endDate=2025-11-22&limit=100"
```

### 4. Combined with Other Filters

```bash
# Inbound calls from extension 694311 on Nov 20
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20&endDate=2025-11-20&extension=694311&direction=I&limit=50"

# Outbound calls during business hours
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20T09:00:00&endDate=2025-11-20T17:00:00&direction=O&limit=100"
```

---

## API Endpoints with Date Support

### 1. GET /api/v1/reporting/calls

**Get call detail records within date range**

```bash
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-20&endDate=2025-11-22&limit=100"
```

**Response includes filters applied:**
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
  "pagination": {...}
}
```

### 2. GET /api/v1/reporting/calls/stream

**Stream calls in Kafka format within date range**

```bash
curl "http://localhost:5000/api/v1/reporting/calls/stream?startDate=2025-11-20&endDate=2025-11-22&limit=50"
```

### 3. GET /api/v1/reporting/calls/export

**Export calls to CSV for specific period**

```bash
curl "http://localhost:5000/api/v1/reporting/calls/export?startDate=2025-11-20&endDate=2025-11-22&limit=1000" > calls_nov20-22.csv
```

**Note:** The exported CSV filename will include the date range!

### 4. GET /api/v1/reporting/statistics

**Get statistics for specific period**

```bash
curl "http://localhost:5000/api/v1/reporting/statistics?startDate=2025-11-20&endDate=2025-11-22"
```

**Response includes period:**
```json
{
  "success": true,
  "data": {
    "callVolume": {...},
    "callMetrics": {...},
    "journeyMetrics": {...}
  },
  "period": {
    "startDate": "2025-11-20",
    "endDate": "2025-11-22"
  }
}
```

---

## Python Examples

### Basic Date Range Query

```python
import requests
from datetime import datetime, timedelta

base_url = "http://localhost:5000/api/v1/reporting"

# Get calls for last 7 days
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

response = requests.get(
    f"{base_url}/calls",
    params={
        "startDate": start_date,
        "endDate": end_date,
        "limit": 100
    }
)

data = response.json()
print(f"Found {len(data['data'])} calls from {start_date} to {end_date}")
```

### Specific Time Range

```python
import requests

base_url = "http://localhost:5000/api/v1/reporting"

# Business hours on specific day
response = requests.get(
    f"{base_url}/calls",
    params={
        "startDate": "2025-11-20T09:00:00",
        "endDate": "2025-11-20T17:00:00",
        "direction": "I",  # Inbound only
        "limit": 200
    }
)

for call in response.json()['data']:
    print(f"{call['Call_date']} - {call['Direction']} - {call['Duration']}s")
```

### Export to CSV by Date

```python
import requests

base_url = "http://localhost:5000/api/v1/reporting"

# Export last month's calls
response = requests.get(
    f"{base_url}/calls/export",
    params={
        "startDate": "2025-10-01",
        "endDate": "2025-10-31",
        "limit": 5000
    }
)

# Save to file
with open("october_2025_calls.csv", "w") as f:
    f.write(response.text)
```

---

## Error Handling

### Invalid Date Format

**Request:**
```bash
curl "http://localhost:5000/api/v1/reporting/calls?startDate=20-11-2025"
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_DATE_FORMAT",
    "message": "Invalid startDate format. Use ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS"
  }
}
```

### Invalid Date Range

**Request:**
```bash
curl "http://localhost:5000/api/v1/reporting/calls?startDate=2025-11-22&endDate=2025-11-20"
```

**Response:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_DATE_RANGE",
    "message": "startDate must be before or equal to endDate"
  }
}
```

---

## Best Practices

### 1. Use Date-Only Format for Daily Reports
```bash
# ✅ Good
curl "...?startDate=2025-11-20&endDate=2025-11-20"

# ⚠️ Less efficient (but works)
curl "...?startDate=2025-11-20T00:00:00&endDate=2025-11-20T23:59:59"
```

### 2. Limit Large Date Ranges
```bash
# ✅ Good - reasonable limit
curl "...?startDate=2025-11-01&endDate=2025-11-30&limit=500"

# ⚠️ May return fewer results than expected
curl "...?startDate=2025-01-01&endDate=2025-12-31&limit=100"
```

### 3. Combine Filters for Precision
```bash
# ✅ Good - specific query
curl "...?startDate=2025-11-20&extension=694311&direction=I"
```

### 4. Use Pagination for Large Datasets
```python
# Get all calls for a month with pagination
def get_all_calls(start_date, end_date):
    all_calls = []
    offset = 0
    limit = 500
    
    while True:
        response = requests.get(
            f"{base_url}/calls",
            params={
                "startDate": start_date,
                "endDate": end_date,
                "limit": limit,
                "offset": offset
            }
        )
        data = response.json()
        calls = data['data']
        all_calls.extend(calls)
        
        if not data['pagination']['hasMore']:
            break
        offset += limit
    
    return all_calls
```

---

## Testing Date Filtering

```bash
# Run the test suite (includes date filter tests)
python3 test_api.py

# Or test manually
./examples.sh  # See examples 11 & 12
```

---

## Summary

✅ **All reporting endpoints support date filtering**
✅ **ISO 8601 format: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS**
✅ **Combine with other filters (extension, direction)**
✅ **Automatic validation with helpful error messages**
✅ **Works with Kafka stream and CSV export**

**Ready to filter your historical call data by date!** 📅

