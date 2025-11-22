"""
Mitel API Mock Server - Compliant with Official Mitel API Structure
Based on Mitel Call History REST API and CloudLink Analytics API

Official API Documentation:
- Mitel Call History REST API
- Mitel CloudLink Platform APIs
- MiContact Center Business Historical Reporting

This version follows the official Mitel API endpoint structure
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import json
from typing import List, Dict
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data pools (based on your CSV)
USERNAMES = [
    "PTP AG4311,METZ", "PTP AG4311,G1", "COMPTOIR,FIXE2469", 
    "ORBEM,MATTHIAS", "PORT_IVR_9921043_Miv", "CDO AG2653,COUTANCES",
    "CDO AG2469,G1", "PTP AG3592,G1", "ESCAVABAJA,ANTHONY"
]

EXTENSIONS = [
    "694311", "9431101", "711540", "616445", "9921043", 
    "792653", "9246901", "9359201", "712322"
]

GROUP_NUMBERS = ["9431101", "9246901", "9359201", ""]
CALL_DIRECTIONS = ["I", "O", "B"]  # Inbound, Outbound, Both
CALL_OUTCOMES = ["103", "108", "207", "202", "105", "102"]
JOURNEY_OUTCOMES = ["701", "702", "703", "0"]

# Starting record ID
record_id_counter = 78340000


def generate_phone_number(international=True):
    """Generate a mock phone number"""
    if international:
        return f"+33{random.randint(100000000, 999999999)}"
    return f"0{random.randint(100000000, 999999999)}"


def generate_call_id():
    """Generate a mock call ID"""
    prefix = random.choice(['A', 'B', 'C', 'D', 'I', 'K', 'M', 'Q', 'Y'])
    number = random.randint(2010000, 2020000)
    return f"{prefix}{number}"


def generate_leg_id(extno, call_id):
    """Generate a mock leg ID"""
    phone = random.randint(10000000000, 99999999999)
    timestamp = int(datetime.now().timestamp())
    return f"{phone}_{extno}_{call_id}_{timestamp}"


def generate_cdr_record():
    """Generate a single Call Detail Record matching Mitel structure"""
    global record_id_counter
    record_id_counter += 1
    
    extno = random.choice(EXTENSIONS)
    username = random.choice(USERNAMES)
    direction = random.choice(CALL_DIRECTIONS)
    call_id = generate_call_id()
    group_no = random.choice(GROUP_NUMBERS)
    
    # Generate realistic call timing
    ring_time = random.randint(0, 30) if direction in ["I", "B"] else 0
    duration = random.randint(0, 600)
    unanswered = "1" if duration == 0 else "0"
    wait_time = random.randint(0, 60)
    hold_duration = random.randint(0, 120)
    total_duration = duration + ring_time + random.randint(0, 20)
    
    # Current time with some randomness
    call_date = datetime.now() - timedelta(seconds=random.randint(0, 3600))
    
    record = {
        "RecordId": record_id_counter,
        "Extno": extno,
        "Username": username,
        "Call_date": call_date.strftime("%Y-%m-%dT%H:%M:%S"),
        "Number": generate_phone_number(),
        "Port": generate_phone_number() if random.random() > 0.1 else "",
        "Ring_time": ring_time,
        "Account": "",
        "Call_cost": round(random.uniform(0, 5), 2) if duration > 0 else 0,
        "Duration": duration,
        "Direction": direction,
        "Unanswer": unanswered,
        "Transfer": str(random.randint(0, 1)),
        "Vpn": "0",
        "Call_dist": "1",
        "Acc_code": "",
        "Std_code": "0",
        "Destination": "",
        "CallId": call_id,
        "Group_no": group_no,
        "Call_outcome": random.choice(CALL_OUTCOMES),
        "Call_legId": str(random.randint(1, 5)),
        "Call_returnstatus": "0",
        "TenantId": "1",
        "LegID": generate_leg_id(extno, call_id),
        "PreviousLegID": "",
        "Call_legs": str(random.randint(1, 5)),
        "Return_date": "",
        "Return_record": "",
        "Return_direction": "",
        "SourceRoundTripDelay": "",
        "SourceEndSystemDelay": "",
        "TargetEndSystemDelay": "",
        "SourceSymmOneWayDelay": "",
        "TargetSymmOneWayDelay": "",
        "SourceInterarrivalJitter": "",
        "TargetInterarrivalJitter": "",
        "SourceMOSLQ": "",
        "TargetMOSLQ": "",
        "SourceMOSCQ": "",
        "TargetMOSCQ": "",
        "firstGroupRingpoint": "",
        "GroupPosition": str(random.randint(0, 1)),
        "totalDuration": str(total_duration),
        "waitTime": str(wait_time),
        "CallBackAgentAssigned": "",
        "CallBackAssignedDateTime": "",
        "ReturnedByAgent": "",
        "HoldDuration": str(hold_duration),
        "JourneyWaitTime": str(wait_time),
        "JourneyOutcome": random.choice(JOURNEY_OUTCOMES) if duration > 0 else "0",
        "ContactPoints": "1",
        "CallExperienceRating": str(random.randint(0, 5)),
        "DeviceId": str(random.choice([19, -1, 873, 924, 63, 146, 1345]))
    }
    
    return record


# ====================================================================
# MITEL CLOUDLINK / CALL HISTORY API - COMPLIANT ENDPOINTS
# ====================================================================

@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        "service": "Mitel API Mock Server",
        "version": "2.0.0 - Mitel API Compliant",
        "description": "Mock server following official Mitel API structure",
        "api_version": "CloudLink Platform API v1",
        "endpoints": {
            # Mitel-style endpoints
            "/api/v1/accounts/{accountId}/callHistory": "Get call history (Mitel CloudLink style)",
            "/api/v1/accounts/{accountId}/callHistory/query": "Query call history with filters",
            "/api/v1/reporting/callDetailRecords": "Get CDR records (Reporting API style)",
            "/api/v1/reporting/historicalData": "Get historical call data",
            
            # Additional helper endpoints
            "/api/health": "Health check endpoint",
            "/api/v1/extensions": "Get list of extensions",
            "/api/v1/stats": "Get call statistics"
        }
    })


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "mitel-api-mock",
        "version": "2.0.0"
    })


# ====================================================================
# MITEL CLOUDLINK CALL HISTORY API ENDPOINTS
# Following: https://developer.mitel.io CloudLink Platform API
# ====================================================================

@app.route('/api/v1/accounts/<account_id>/callHistory', methods=['GET'])
def get_call_history(account_id):
    """
    Get Call History - Mitel CloudLink API Style
    
    Based on: Mitel CloudLink Platform Call History API
    
    Query Parameters:
        - limit: Number of records (default: 50, max: 500)
        - offset: Pagination offset (default: 0)
        - startDate: Start date (ISO 8601)
        - endDate: End date (ISO 8601)
        - direction: Call direction (inbound/outbound/internal)
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        direction = request.args.get('direction', '').upper()
        
        # Map direction to CDR format
        direction_map = {
            'INBOUND': 'I',
            'OUTBOUND': 'O',
            'INTERNAL': 'B'
        }
        cdr_direction = direction_map.get(direction, None)
        
        # Generate records
        records = []
        for i in range(limit):
            record = generate_cdr_record()
            
            # Apply filters
            if cdr_direction and record['Direction'] != cdr_direction:
                continue
                
            records.append(record)
        
        logger.info(f"GET /callHistory for account {account_id}: {len(records)} records")
        
        # Mitel-style response
        return jsonify({
            "accountId": account_id,
            "callHistory": {
                "items": records,
                "total": len(records) + offset,  # Simulated total
                "offset": offset,
                "limit": limit
            },
            "_links": {
                "self": f"/api/v1/accounts/{account_id}/callHistory?limit={limit}&offset={offset}",
                "next": f"/api/v1/accounts/{account_id}/callHistory?limit={limit}&offset={offset + limit}"
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_call_history: {str(e)}")
        return jsonify({
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@app.route('/api/v1/accounts/<account_id>/callHistory/query', methods=['POST'])
def query_call_history(account_id):
    """
    Query Call History with filters - Mitel CloudLink API Style
    
    Request Body:
    {
        "filter": {
            "startDate": "2025-01-01T00:00:00Z",
            "endDate": "2025-01-31T23:59:59Z",
            "extension": "694311",
            "direction": "inbound",
            "minDuration": 0
        },
        "pagination": {
            "limit": 100,
            "offset": 0
        }
    }
    """
    try:
        data = request.get_json() or {}
        filter_params = data.get('filter', {})
        pagination = data.get('pagination', {})
        
        limit = min(int(pagination.get('limit', 50)), 500)
        offset = int(pagination.get('offset', 0))
        extension = filter_params.get('extension')
        direction = filter_params.get('direction', '').upper()
        min_duration = int(filter_params.get('minDuration', 0))
        
        # Map direction
        direction_map = {'INBOUND': 'I', 'OUTBOUND': 'O', 'INTERNAL': 'B'}
        cdr_direction = direction_map.get(direction, None)
        
        # Generate and filter records
        records = []
        attempts = 0
        max_attempts = limit * 3  # Try to generate enough matching records
        
        while len(records) < limit and attempts < max_attempts:
            record = generate_cdr_record()
            attempts += 1
            
            # Apply filters
            if extension and record['Extno'] != extension:
                continue
            if cdr_direction and record['Direction'] != cdr_direction:
                continue
            if record['Duration'] < min_duration:
                continue
                
            records.append(record)
        
        logger.info(f"POST /callHistory/query for account {account_id}: {len(records)} records")
        
        return jsonify({
            "accountId": account_id,
            "queryResults": {
                "items": records,
                "total": len(records) + offset,
                "offset": offset,
                "limit": limit,
                "hasMore": len(records) == limit
            },
            "filter": filter_params
        })
    
    except Exception as e:
        logger.error(f"Error in query_call_history: {str(e)}")
        return jsonify({
            "error": {
                "code": "QUERY_ERROR",
                "message": str(e)
            }
        }), 500


# ====================================================================
# MITEL REPORTING / ANALYTICS API ENDPOINTS
# Following: Mitel Historical Reporting API structure
# ====================================================================

@app.route('/api/v1/reporting/callDetailRecords', methods=['GET'])
def get_call_detail_records():
    """
    Get Call Detail Records - Mitel Reporting API Style
    
    Query Parameters:
        - startTime: Start timestamp (epoch milliseconds)
        - endTime: End timestamp (epoch milliseconds)
        - limit: Number of records (default: 100, max: 1000)
        - extension: Filter by extension
        - callType: Filter by call type (inbound/outbound/internal)
    """
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        extension = request.args.get('extension')
        call_type = request.args.get('callType', '').upper()
        
        # Generate CDR records
        records = []
        for _ in range(limit):
            record = generate_cdr_record()
            
            if extension and record['Extno'] != extension:
                continue
                
            records.append(record)
        
        logger.info(f"GET /reporting/callDetailRecords: {len(records)} records")
        
        return jsonify({
            "status": "success",
            "data": {
                "callDetailRecords": records,
                "count": len(records),
                "metadata": {
                    "generatedAt": datetime.now().isoformat(),
                    "apiVersion": "v1"
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_call_detail_records: {str(e)}")
        return jsonify({
            "status": "error",
            "error": {
                "code": "CDR_ERROR",
                "message": str(e)
            }
        }), 500


@app.route('/api/v1/reporting/historicalData', methods=['GET'])
def get_historical_data():
    """
    Get Historical Call Data - Returns data in the Kafka/Message Queue format
    This matches your CSV structure with timestamp, partition, offset, key, value
    
    Query Parameters:
        - limit: Number of messages (default: 10, max: 100)
        - partition: Kafka partition (optional)
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        partition = int(request.args.get('partition', 0))
        
        messages = []
        for _ in range(limit):
            record = generate_cdr_record()
            
            # Wrap in Kafka-style message (matching your CSV structure)
            message = {
                "timestamp": int(datetime.now().timestamp() * 1000),
                "timestampType": "CREATE_TIME",
                "partition": partition,
                "offset": random.randint(25393000, 25394000),
                "key": json.dumps({"key": str(record["RecordId"])}),
                "value": json.dumps(record),
                "headers": "[]",
                "exceededFields": ""
            }
            messages.append(message)
        
        logger.info(f"GET /reporting/historicalData: {len(messages)} messages")
        
        return jsonify({
            "status": "success",
            "data": {
                "messages": messages,
                "count": len(messages),
                "partition": partition
            }
        })
    
    except Exception as e:
        logger.error(f"Error in get_historical_data: {str(e)}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/api/v1/reporting/historicalData/export', methods=['GET'])
def export_historical_data_csv():
    """
    Export Historical Data as CSV - Matches your original CSV format exactly
    
    Query Parameters:
        - limit: Number of records (default: 10, max: 100)
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        
        # Generate CSV content matching your original format
        csv_lines = ["timestamp,timestampType,partition,offset,key,value,headers,exceededFields"]
        
        for _ in range(limit):
            record = generate_cdr_record()
            timestamp = int(datetime.now().timestamp() * 1000)
            partition = 0
            offset = random.randint(25393000, 25394000)
            
            key = json.dumps({"key": str(record["RecordId"])})
            value = json.dumps(record)
            
            # Format exactly like your CSV
            line = f'{timestamp},CREATE_TIME,{partition},{offset},"{key}","{value}",[],\n'
            csv_lines.append(line)
        
        logger.info(f"Exporting {len(csv_lines) - 1} records as CSV")
        
        return Response(
            ''.join(csv_lines),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=telephonie_message_data.csv'}
        )
    
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500


# ====================================================================
# ADDITIONAL MANAGEMENT ENDPOINTS
# ====================================================================

@app.route('/api/v1/extensions', methods=['GET'])
def get_extensions():
    """Get list of available extensions"""
    extensions_data = [
        {
            "extension": ext,
            "username": random.choice(USERNAMES),
            "status": random.choice(["active", "inactive", "busy"]),
            "accountId": "default"
        }
        for ext in EXTENSIONS
    ]
    
    return jsonify({
        "extensions": extensions_data,
        "total": len(extensions_data)
    })


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """Get call statistics"""
    return jsonify({
        "statistics": {
            "today": {
                "totalCalls": random.randint(100, 1000),
                "inboundCalls": random.randint(50, 500),
                "outboundCalls": random.randint(50, 500),
                "averageDuration": random.randint(60, 300),
                "averageWaitTime": random.randint(10, 60),
                "answeredPercentage": random.randint(80, 95),
                "missedCalls": random.randint(5, 20)
            },
            "activeExtensions": len(EXTENSIONS),
            "timestamp": datetime.now().isoformat()
        }
    })


if __name__ == '__main__':
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=False)

