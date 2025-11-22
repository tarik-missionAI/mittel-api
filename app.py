"""
Mitel MiContact Center Historical Reporting API - Mock Server
Compliant with Mitel API structure and endpoints

Based on: Mitel MiContact Center Business Historical Reporting API
Endpoints match official Mitel API patterns
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import json
import logging
from typing import List, Dict, Optional

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Version
API_VERSION = "v1"
BASE_PATH = f"/api/{API_VERSION}"

# Mock data pools - based on your CSV
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

# Call directions: I=Inbound, O=Outbound, B=Both/Transfer
CALL_DIRECTIONS = ["I", "O", "B"]

# Call outcomes (Mitel specific codes)
CALL_OUTCOMES = ["103", "108", "207", "202", "105", "102"]

# Journey outcomes (Contact Center specific)
JOURNEY_OUTCOMES = ["701", "702", "703", "0"]

DEVICE_IDS = ["19", "-1", "873", "924", "63", "146", "1345"]

# Starting record ID
record_id_counter = 78340000


def generate_phone_number(international=True):
    """Generate mock phone number"""
    if international:
        return f"+33{random.randint(100000000, 999999999)}"
    return f"0{random.randint(100000000, 999999999)}"


def generate_call_id():
    """Generate Mitel-style call ID"""
    prefix = random.choice(['A', 'B', 'C', 'D', 'I', 'K', 'M', 'Q', 'Y', 'X'])
    number = random.randint(2010000, 2020000)
    return f"{prefix}{number}"


def generate_leg_id(extno, call_id, timestamp):
    """Generate Mitel-style leg ID"""
    phone = random.randint(10000000000, 99999999999)
    return f"{phone}_{extno}_{call_id}_{timestamp}"


def generate_call_record():
    """
    Generate a single Call Detail Record matching Mitel MiContact Center format
    """
    global record_id_counter
    record_id_counter += 1
    
    # Call metadata
    extno = random.choice(EXTENSIONS)
    username = random.choice(USERNAMES)
    direction = random.choice(CALL_DIRECTIONS)
    call_id = generate_call_id()
    group_no = random.choice(GROUP_NUMBERS)
    call_timestamp = int(datetime.now().timestamp())
    
    # Call timing
    ring_time = random.randint(0, 30) if direction in ["I", "B"] else 0
    duration = random.randint(0, 600)
    unanswered = "1" if duration == 0 else "0"
    wait_time = random.randint(0, 60)
    hold_duration = random.randint(0, 120) if duration > 0 else 0
    
    # Journey metrics (Contact Center specific)
    journey_outcome = random.choice(JOURNEY_OUTCOMES)
    contact_points = "1" if duration > 0 else "0"
    call_experience = str(random.randint(0, 5)) if duration > 0 else "0"
    
    # Call date
    call_date = datetime.now() - timedelta(seconds=random.randint(0, 3600))
    
    # Build the record
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
        "LegID": generate_leg_id(extno, call_id, call_timestamp),
        "PreviousLegID": "",
        "Call_legs": str(random.randint(1, 5)),
        "Return_date": "",
        "Return_record": "",
        "Return_direction": "",
        
        # VoIP Quality Metrics (may be empty)
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
        
        # Contact Center / Group fields
        "firstGroupRingpoint": "",
        "GroupPosition": str(random.randint(0, 1)),
        
        # Journey Analytics
        "totalDuration": str(duration + ring_time + random.randint(0, 20)),
        "waitTime": str(wait_time),
        "CallBackAgentAssigned": "",
        "CallBackAssignedDateTime": "",
        "ReturnedByAgent": "",
        "HoldDuration": str(hold_duration),
        "JourneyWaitTime": str(wait_time),
        "JourneyOutcome": journey_outcome,
        "ContactPoints": contact_points,
        "CallExperienceRating": call_experience,
        "DeviceId": random.choice(DEVICE_IDS)
    }
    
    return record


def wrap_in_kafka_format(record):
    """
    Wrap CDR record in Kafka message format (as seen in your CSV)
    """
    timestamp = int(datetime.now().timestamp() * 1000)
    
    return {
        "timestamp": timestamp,
        "timestampType": "CREATE_TIME",
        "partition": 0,
        "offset": random.randint(25393000, 25395000),
        "key": {"key": str(record["RecordId"])},
        "value": record,
        "headers": [],
        "exceededFields": ""
    }


# ==================== API ENDPOINTS ====================

@app.route('/')
def root():
    """API root - returns API information"""
    return jsonify({
        "name": "Mitel MiContact Center Historical Reporting API",
        "version": API_VERSION,
        "description": "Mock API for Mitel MiContact Center Call Detail Records",
        "documentation": "https://developer.mitel.io/",
        "endpoints": {
            f"{BASE_PATH}/reporting/calls": "Get historical call records",
            f"{BASE_PATH}/reporting/calls/stream": "Stream call records (Kafka format)",
            f"{BASE_PATH}/reporting/calls/export": "Export calls as CSV",
            f"{BASE_PATH}/reporting/agents": "Get agent/extension information",
            f"{BASE_PATH}/reporting/statistics": "Get call statistics",
            "/health": "Health check endpoint"
        }
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "mitel-micontact-center-api"
    })


@app.route(f'{BASE_PATH}/reporting/calls', methods=['GET'])
def get_call_records():
    """
    Get Call Detail Records - Mitel MiContact Center format
    
    Query Parameters:
        - startDate: Start date (ISO format)
        - endDate: End date (ISO format)
        - extension: Filter by extension number
        - direction: Filter by direction (I/O/B)
        - limit: Max records to return (default: 50, max: 500)
        - offset: Pagination offset (default: 0)
    """
    try:
        # Parse parameters
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))
        extension = request.args.get('extension')
        direction = request.args.get('direction')
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        # Generate records
        records = []
        attempts = 0
        max_attempts = limit * 3  # Avoid infinite loop with filters
        
        while len(records) < limit and attempts < max_attempts:
            record = generate_call_record()
            attempts += 1
            
            # Apply filters
            if extension and record['Extno'] != extension:
                continue
            if direction and record['Direction'] != direction:
                continue
                
            records.append(record)
        
        logger.info(f"Generated {len(records)} call records")
        
        return jsonify({
            "success": True,
            "data": records,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(records),
                "hasMore": False  # Mock response
            },
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@app.route(f'{BASE_PATH}/reporting/calls/stream', methods=['GET'])
def stream_call_records():
    """
    Stream Call Detail Records in Kafka message format
    This matches the structure in your CSV file
    
    Query Parameters:
        - limit: Number of messages (default: 50, max: 500)
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        
        messages = []
        for _ in range(limit):
            record = generate_call_record()
            message = wrap_in_kafka_format(record)
            messages.append(message)
        
        logger.info(f"Generated {len(messages)} Kafka messages")
        
        return jsonify({
            "success": True,
            "messages": messages,
            "count": len(messages),
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@app.route(f'{BASE_PATH}/reporting/calls/export', methods=['GET'])
def export_calls_csv():
    """
    Export Call Detail Records as CSV
    Matches the exact format of your source CSV file
    
    Query Parameters:
        - limit: Number of records (default: 100, max: 1000)
    """
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        
        # CSV header
        csv_lines = ["timestamp,timestampType,partition,offset,key,value,headers,exceededFields"]
        
        for _ in range(limit):
            record = generate_call_record()
            message = wrap_in_kafka_format(record)
            
            # Format as CSV line (matching your source file)
            line = (
                f"{message['timestamp']},"
                f"{message['timestampType']},"
                f"{message['partition']},"
                f"{message['offset']},"
                f'"{json.dumps(message["key"])}",'
                f'"{json.dumps(message["value"])}",'
                f"[],"
            )
            csv_lines.append(line)
        
        csv_content = '\n'.join(csv_lines)
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=mitel_call_records.csv'
            }
        )
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        }), 500


@app.route(f'{BASE_PATH}/reporting/agents', methods=['GET'])
def get_agents():
    """Get list of agents/extensions"""
    agents = []
    for ext in EXTENSIONS:
        agents.append({
            "extension": ext,
            "username": random.choice(USERNAMES),
            "groupNumber": random.choice(GROUP_NUMBERS),
            "deviceId": random.choice(DEVICE_IDS),
            "status": random.choice(["Available", "Busy", "Away", "Offline"])
        })
    
    return jsonify({
        "success": True,
        "data": agents,
        "count": len(agents),
        "timestamp": datetime.now().isoformat()
    })


@app.route(f'{BASE_PATH}/reporting/statistics', methods=['GET'])
def get_statistics():
    """
    Get call statistics and KPIs
    Mitel MiContact Center format
    """
    return jsonify({
        "success": True,
        "data": {
            "callVolume": {
                "totalCalls": random.randint(500, 2000),
                "inboundCalls": random.randint(300, 1000),
                "outboundCalls": random.randint(200, 1000),
                "answeredCalls": random.randint(400, 1800),
                "missedCalls": random.randint(50, 200)
            },
            "callMetrics": {
                "averageDuration": random.randint(120, 300),
                "averageWaitTime": random.randint(15, 60),
                "averageHoldTime": random.randint(10, 45),
                "serviceLevel": round(random.uniform(0.85, 0.98), 2)
            },
            "journeyMetrics": {
                "totalJourneys": random.randint(400, 1800),
                "completedJourneys": random.randint(350, 1700),
                "averageContactPoints": round(random.uniform(1.0, 2.5), 2),
                "averageExperienceRating": round(random.uniform(3.5, 4.8), 1)
            },
            "agentMetrics": {
                "totalAgents": len(EXTENSIONS),
                "activeAgents": random.randint(5, len(EXTENSIONS)),
                "averageHandleTime": random.randint(180, 360)
            }
        },
        "period": {
            "startDate": (datetime.now() - timedelta(days=1)).isoformat(),
            "endDate": datetime.now().isoformat()
        },
        "timestamp": datetime.now().isoformat()
    })


# Legacy compatibility endpoints (for backward compatibility with your original API)
@app.route('/api/v1/cdr', methods=['GET'])
def legacy_cdr():
    """Legacy endpoint - redirects to new structure"""
    return get_call_records()


@app.route('/api/v1/cdr/stream', methods=['GET'])
def legacy_stream():
    """Legacy endpoint - redirects to new structure"""
    return stream_call_records()


@app.route('/api/v1/cdr/export', methods=['GET'])
def legacy_export():
    """Legacy endpoint - redirects to new structure"""
    return export_calls_csv()


if __name__ == '__main__':
    print("=" * 60)
    print("Mitel MiContact Center Historical Reporting API - Mock Server")
    print("=" * 60)
    print(f"API Version: {API_VERSION}")
    print(f"Base Path: {BASE_PATH}")
    print("\nEndpoints:")
    print(f"  - {BASE_PATH}/reporting/calls")
    print(f"  - {BASE_PATH}/reporting/calls/stream")
    print(f"  - {BASE_PATH}/reporting/calls/export")
    print(f"  - {BASE_PATH}/reporting/agents")
    print(f"  - {BASE_PATH}/reporting/statistics")
    print("\nStarting server on http://0.0.0.0:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)

