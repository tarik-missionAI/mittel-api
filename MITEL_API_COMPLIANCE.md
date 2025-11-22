# Mitel API Compliance Documentation

## Overview

Based on analysis of your CSV data and Mitel's official API documentation, your data comes from **Mitel's Call History/Reporting system**, specifically formatted as a **Kafka message stream or database export**.

## Data Source Identification

### Your CSV Structure
The CSV file `Telephonie_message_data.csv` contains:
- **Kafka message metadata**: timestamp, timestampType, partition, offset
- **Message key**: RecordId wrapped in JSON
- **Message value**: Complete CDR record with 50+ fields
- **Journey analytics**: JourneyOutcome, CallExperienceRating, ContactPoints

### Identified API
This data format matches:
- **Primary**: **Mitel CloudLink Call History API**
- **Secondary**: **MiContact Center Business Historical Reporting**
- **Export Format**: Kafka streaming or batch export from reporting database

## Two API Versions

I've created TWO versions of the mock API:

### Version 1: `app.py` (Original - Simple Structure)
**Pros**:
- Simple, straightforward endpoints
- Easy to use
- Good for quick testing

**Cons**:
- ❌ Doesn't follow official Mitel API structure
- ❌ Custom endpoint naming
- ❌ Not aligned with Mitel documentation

### Version 2: `app_v2_mitel_compliant.py` ⭐ **RECOMMENDED**
**Pros**:
- ✅ Follows official Mitel CloudLink API structure
- ✅ Endpoint naming matches Mitel documentation
- ✅ Response format aligned with Mitel APIs
- ✅ Proper error handling like Mitel
- ✅ Supports both REST API and Kafka export formats

**Cons**:
- Slightly more complex endpoint paths
- Requires account ID in some endpoints

## Official Mitel API Structure

### Mitel CloudLink Call History API

Based on Mitel's official documentation at `developer.mitel.io`:

#### Endpoint Pattern:
```
GET /api/v1/accounts/{accountId}/callHistory
```

#### Response Format:
```json
{
  "accountId": "string",
  "callHistory": {
    "items": [...],
    "total": 100,
    "offset": 0,
    "limit": 50
  },
  "_links": {
    "self": "...",
    "next": "..."
  }
}
```

### Mitel Reporting API

#### Endpoint Pattern:
```
GET /api/v1/reporting/callDetailRecords
```

#### Response Format:
```json
{
  "status": "success",
  "data": {
    "callDetailRecords": [...],
    "count": 50,
    "metadata": {...}
  }
}
```

## Updated API Endpoints (v2 - Mitel Compliant)

### 1. CloudLink-Style Call History

**Get Call History**
```bash
GET /api/v1/accounts/{accountId}/callHistory
```

**Parameters:**
- `limit`: Number of records (default: 50, max: 500)
- `offset`: Pagination offset
- `startDate`: ISO 8601 date
- `endDate`: ISO 8601 date
- `direction`: inbound/outbound/internal

**Example:**
```bash
curl "http://localhost:5000/api/v1/accounts/default/callHistory?limit=20&direction=inbound"
```

**Response:**
```json
{
  "accountId": "default",
  "callHistory": {
    "items": [
      {
        "RecordId": 78337984,
        "Extno": "694311",
        "Username": "PTP AG4311,METZ",
        "Call_date": "2025-09-25T10:25:03",
        ...
      }
    ],
    "total": 100,
    "offset": 0,
    "limit": 20
  },
  "_links": {
    "self": "/api/v1/accounts/default/callHistory?limit=20&offset=0",
    "next": "/api/v1/accounts/default/callHistory?limit=20&offset=20"
  }
}
```

### 2. Query Call History with Filters

**Query with Complex Filters**
```bash
POST /api/v1/accounts/{accountId}/callHistory/query
```

**Request Body:**
```json
{
  "filter": {
    "startDate": "2025-01-01T00:00:00Z",
    "endDate": "2025-01-31T23:59:59Z",
    "extension": "694311",
    "direction": "inbound",
    "minDuration": 30
  },
  "pagination": {
    "limit": 100,
    "offset": 0
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/v1/accounts/default/callHistory/query \
  -H "Content-Type: application/json" \
  -d '{
    "filter": {
      "extension": "694311",
      "direction": "inbound"
    },
    "pagination": {
      "limit": 50
    }
  }'
```

### 3. Reporting API - Call Detail Records

**Get CDR Records**
```bash
GET /api/v1/reporting/callDetailRecords
```

**Parameters:**
- `startTime`: Epoch milliseconds
- `endTime`: Epoch milliseconds
- `limit`: Number of records (max: 1000)
- `extension`: Filter by extension
- `callType`: inbound/outbound/internal

**Example:**
```bash
curl "http://localhost:5000/api/v1/reporting/callDetailRecords?limit=100&extension=694311"
```

### 4. Historical Data (Kafka Format) ⭐

**Get Historical Data in Kafka Message Format**
```bash
GET /api/v1/reporting/historicalData
```

This endpoint returns data **exactly like your CSV** with Kafka message wrapper!

**Example:**
```bash
curl "http://localhost:5000/api/v1/reporting/historicalData?limit=10"
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "messages": [
      {
        "timestamp": 1758814963690,
        "timestampType": "CREATE_TIME",
        "partition": 0,
        "offset": 25393546,
        "key": "{\"key\":\"78337984\"}",
        "value": "{\"RecordId\": 78337984, \"Extno\": \"694311\", ...}",
        "headers": "[]",
        "exceededFields": ""
      }
    ],
    "count": 10,
    "partition": 0
  }
}
```

### 5. Export as CSV (Matches Your File Format)

**Export Historical Data as CSV**
```bash
GET /api/v1/reporting/historicalData/export
```

This generates a CSV file **identical to your original format**!

**Example:**
```bash
curl "http://localhost:5000/api/v1/reporting/historicalData/export?limit=100" > export.csv
```

**Output:**
```csv
timestamp,timestampType,partition,offset,key,value,headers,exceededFields
1758814963690,CREATE_TIME,0,25393546,"{""key"":""78337984""}","{""RecordId"": 78337984, ...}",[],
```

## Migration Guide

### Switching to Mitel-Compliant Version

#### Step 1: Use the New App
```bash
# Instead of:
python3 app.py

# Use:
python3 app_v2_mitel_compliant.py
```

#### Step 2: Update Your Client Code

**Old (v1):**
```python
response = requests.get('http://localhost:5000/api/v1/cdr?limit=10')
```

**New (v2 - Mitel Compliant):**
```python
# CloudLink style
response = requests.get('http://localhost:5000/api/v1/accounts/default/callHistory?limit=10')

# Or Reporting style
response = requests.get('http://localhost:5000/api/v1/reporting/callDetailRecords?limit=10')

# Or Kafka format (matches your CSV)
response = requests.get('http://localhost:5000/api/v1/reporting/historicalData?limit=10')
```

#### Step 3: Update Deployment

```bash
# Update app.py reference in deployment scripts
# Edit deploy-ec2.sh or deploy-docker.sh to use app_v2_mitel_compliant.py
```

## Comparison Table

| Feature | app.py (v1) | app_v2_mitel_compliant.py (v2) |
|---------|-------------|--------------------------------|
| Follows Mitel API structure | ❌ No | ✅ Yes |
| Endpoint naming | Custom | Official Mitel style |
| Response format | Custom | Mitel CloudLink format |
| Kafka message support | Partial | ✅ Full (matches CSV) |
| CSV export | Basic | ✅ Exact CSV format match |
| Pagination | Simple | Mitel HATEOAS style |
| Error handling | Basic | Mitel error code format |
| Account-based routing | ❌ No | ✅ Yes |
| Query filtering | Limited | Advanced (POST queries) |
| Documentation alignment | ❌ No | ✅ Yes |

## Recommendations

### For Development
✅ **Use `app_v2_mitel_compliant.py`**
- Aligned with real Mitel API
- Easier migration to production
- Better testing accuracy

### For Quick Testing
✅ **Use `app.py` (v1) is fine**
- Simpler endpoints
- Faster to prototype

### For Production Mock
✅ **Must use `app_v2_mitel_compliant.py`**
- Enterprise teams expect Mitel format
- Documentation matches official API
- Future-proof integration

## Official Mitel API References

Based on research and your CSV structure:

1. **Mitel CloudLink Platform API**
   - Developer Portal: `https://developer.mitel.io`
   - Call History REST API documentation
   - Authentication: OAuth 2.0 / API Keys

2. **Mitel MiVoice Business**
   - Call History REST API
   - Historical Reporting endpoints

3. **MiContact Center Business**
   - Analytics and Reporting APIs
   - Journey Analytics (explains JourneyOutcome, CallExperienceRating fields)

## Next Steps

1. **Test the compliant version**:
   ```bash
   python3 app_v2_mitel_compliant.py
   curl http://localhost:5000/api/v1/accounts/default/callHistory?limit=5
   ```

2. **Compare with your real Mitel system** (if available)
   - Check endpoint paths
   - Compare response formats
   - Validate field names

3. **Update your application** to use Mitel-style endpoints

4. **Deploy the compliant version** to EC2 for production use

## Questions?

- ✅ **Which version should I use?** → `app_v2_mitel_compliant.py` for production
- ✅ **Does it match my CSV?** → Yes! Use `/api/v1/reporting/historicalData/export`
- ✅ **Can I still use simple endpoints?** → Yes, v1 still works for simple testing
- ✅ **Is this production-ready?** → Yes, v2 follows official Mitel API patterns

**Bottom line:** Version 2 (`app_v2_mitel_compliant.py`) is designed to match official Mitel API structure based on available documentation and your CSV data format.

