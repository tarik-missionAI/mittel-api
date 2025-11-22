"""
Mitel API Mock Server
Simulates a Mitel telephony system API that provides Call Detail Records (CDR)
Based on Mitel MiVoice Business/CloudLink platform structure
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random
import string
from typing import List, Dict
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock data pools
USERNAMES = [
    "PTP AG4311,METZ", "PTP AG4311,G1", "COMPTOIR,FIXE2469", 
    "ORBEM,MATTHIAS", "PORT_IVR_9921043_Miv", "CDO AG2653,COUTANCES",
    "CDO AG2469,G1", "PTP AG3592,G1", "ESCAVABAJA,ANTHONY",
    "DUPONT,JEAN", "MARTIN,SOPHIE", "BERNARD,PAUL",
    "THOMAS,MARIE", "ROBERT,LUC", "PETIT,ANNE"
]

EXTENSIONS = [
    "694311", "9431101", "711540", "616445", "9921043", 
    "792653", "9246901", "9359201", "712322", "610234",
    "615789", "620456", "625890", "630123", "635567"
]

GROUP_NUMBERS = [
    "9431101", "9246901", "9359201", "9123401", "9456701", ""
]

CALL_DIRECTIONS = ["I", "O", "B"]  # Inbound, Outbound, Both
CALL_OUTCOMES = ["103", "108", "207", "202", "105", "102"]
DEVICE_IDS = ["19", "-1", "873", "924", "63", "146", "1345"]

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
    """Generate a single Call Detail Record"""
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
        "totalDuration": str(duration + ring_time + random.randint(0, 20)),
        "waitTime": str(random.randint(0, 60)),
        "CallBackAgentAssigned": "",
        "CallBackAssignedDateTime": "",
        "ReturnedByAgent": "",
        "HoldDuration": str(random.randint(0, 120)),
        "JourneyWaitTime": str(random.randint(0, 60)),
        "JourneyOutcome": "701" if duration > 0 else "0",
        "ContactPoints": "1",
        "CallExperienceRating": str(random.randint(0, 5)),
        "DeviceId": random.choice(DEVICE_IDS)
    }
    
    return record


def generate_kafka_message(cdr_record):
    """Wrap CDR in Kafka-like message structure"""
    timestamp = int(datetime.now().timestamp() * 1000)
    
    return {
        "timestamp": timestamp,
        "timestampType": "CREATE_TIME",
        "partition": 0,
        "offset": random.randint(25393000, 25394000),
        "key": {"key": str(cdr_record["RecordId"])},
        "value": cdr_record,
        "headers": [],
        "exceededFields": ""
    }


@app.route('/')
def home():
    """API home endpoint"""
    return jsonify({
        "service": "Mitel API Mock Server",
        "version": "1.0.0",
        "description": "Mock Mitel telephony system API for development",
        "endpoints": {
            "/api/health": "Health check endpoint",
            "/api/v1/cdr": "Get Call Detail Records (CDR)",
            "/api/v1/cdr/stream": "Stream CDR records in Kafka format",
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
        "service": "mitel-api-mock"
    })


@app.route('/api/v1/cdr', methods=['GET'])
def get_cdr_records():
    """
    Get Call Detail Records
    Query Parameters:
        - limit: Number of records to return (default: 10, max: 100)
        - from_date: Start date in ISO format
        - to_date: End date in ISO format
        - extension: Filter by extension number
        - direction: Filter by call direction (I/O/B)
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        extension = request.args.get('extension')
        direction = request.args.get('direction')
        
        records = []
        for _ in range(limit):
            record = generate_cdr_record()
            
            # Apply filters
            if extension and record['Extno'] != extension:
                continue
            if direction and record['Direction'] != direction:
                continue
                
            records.append(record)
        
        logger.info(f"Generated {len(records)} CDR records")
        
        return jsonify({
            "success": True,
            "count": len(records),
            "records": records,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating CDR records: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/v1/cdr/stream', methods=['GET'])
def get_cdr_stream():
    """
    Get CDR records in Kafka message format (similar to CSV structure)
    Query Parameters:
        - limit: Number of records to return (default: 10, max: 100)
    """
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        
        messages = []
        for _ in range(limit):
            record = generate_cdr_record()
            message = generate_kafka_message(record)
            messages.append(message)
        
        logger.info(f"Generated {len(messages)} Kafka-formatted messages")
        
        return jsonify({
            "success": True,
            "count": len(messages),
            "messages": messages,
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Error generating Kafka messages: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/v1/extensions', methods=['GET'])
def get_extensions():
    """Get list of available extensions"""
    extensions_data = [
        {
            "extension": ext,
            "username": random.choice(USERNAMES),
            "status": random.choice(["active", "inactive", "busy"]),
            "device_id": random.choice(DEVICE_IDS)
        }
        for ext in EXTENSIONS
    ]
    
    return jsonify({
        "success": True,
        "count": len(extensions_data),
        "extensions": extensions_data
    })


@app.route('/api/v1/stats', methods=['GET'])
def get_stats():
    """Get call statistics"""
    return jsonify({
        "success": True,
        "stats": {
            "total_calls_today": random.randint(100, 1000),
            "inbound_calls": random.randint(50, 500),
            "outbound_calls": random.randint(50, 500),
            "average_duration": random.randint(60, 300),
            "average_wait_time": random.randint(10, 60),
            "answered_calls": random.randint(80, 95),
            "missed_calls": random.randint(5, 20),
            "active_extensions": len(EXTENSIONS)
        },
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/v1/cdr/export', methods=['GET'])
def export_cdr():
    """Export CDR records in CSV format (like the original file)"""
    try:
        limit = min(int(request.args.get('limit', 10)), 100)
        
        # Generate CSV content
        csv_lines = ["timestamp,timestampType,partition,offset,key,value,headers,exceededFields"]
        
        for _ in range(limit):
            record = generate_cdr_record()
            message = generate_kafka_message(record)
            
            import json
            line = f"{message['timestamp']},{message['timestampType']},{message['partition']},{message['offset']},"
            line += f'"{json.dumps(message["key"])}","{json.dumps(message["value"])}",[],\n'
            csv_lines.append(line)
        
        from flask import Response
        return Response(
            '\n'.join(csv_lines),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=cdr_export.csv'}
        )
    
    except Exception as e:
        logger.error(f"Error exporting CDR: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    # Run the application
    # For production, use gunicorn or similar WSGI server
    app.run(host='0.0.0.0', port=5000, debug=False)

