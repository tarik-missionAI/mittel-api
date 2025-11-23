"""
Mitel MiContact Center Historical Reporting API - Mock Server
Compliant with Mitel API structure and endpoints

Based on: Mitel MiContact Center Business Historical Reporting API
Endpoints match official Mitel API patterns
Includes Bearer Token authentication (optional)
"""

from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta
from functools import wraps
import random
import json
import logging
import os
from typing import Optional

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Version
API_VERSION = "v1"
BASE_PATH = f"/api/{API_VERSION}"

# Authentication Configuration
# Set REQUIRE_AUTH=true in environment to enable authentication
REQUIRE_AUTH = os.getenv('REQUIRE_AUTH', 'false').lower() == 'true'
# User management mode: 'simple', 'json', 'env'
USER_MGMT_MODE = os.getenv('USER_MGMT_MODE', 'simple')
# Users file path
USERS_FILE = os.getenv('USERS_FILE', 'users.json')

# Simple mode - hardcoded users (for quick testing)
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

# Store active tokens (in production, use Redis or database)
active_tokens = {}

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


def generate_call_record(start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
    """
    Generate a single Call Detail Record matching Mitel MiContact Center format
    
    Args:
        start_date: Start of date range for call_date
        end_date: End of date range for call_date
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
    
    # Call date - within specified range if provided
    if start_date and end_date:
        # Generate random datetime within range
        time_diff = (end_date - start_date).total_seconds()
        random_seconds = random.uniform(0, time_diff)
        call_date = start_date + timedelta(seconds=random_seconds)
    elif start_date:
        # Generate from start_date to now
        time_diff = (datetime.now() - start_date).total_seconds()
        if time_diff > 0:
            random_seconds = random.uniform(0, time_diff)
            call_date = start_date + timedelta(seconds=random_seconds)
        else:
            call_date = start_date
    elif end_date:
        # Generate from 30 days before end_date to end_date
        start = end_date - timedelta(days=30)
        time_diff = (end_date - start).total_seconds()
        random_seconds = random.uniform(0, time_diff)
        call_date = start + timedelta(seconds=random_seconds)
    else:
        # Default: random time in last hour
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


def parse_date_param(date_str: str, param_name: str, end_of_day: bool = False):
    """
    Parse date parameter from request
    
    Supports:
    - ISO 8601: 2025-11-20T10:30:00
    - ISO 8601 with Z: 2025-11-20T10:30:00Z
    - Date only: 2025-11-20
    """
    if not date_str:
        return None
        
    try:
        # Handle ISO 8601 with timezone
        if 'T' in date_str:
            date_str = date_str.replace('Z', '+00:00')
            return datetime.fromisoformat(date_str)
        else:
            # Date only - parse and optionally set to end of day
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59)
            return dt
    except ValueError:
        raise ValueError(f"Invalid {param_name} format. Use ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")


def load_users_from_json():
    """Load users from JSON file"""
    try:
        with open(USERS_FILE, 'r') as f:
            data = json.load(f)
            users = {}
            for user in data.get('users', []):
                users[user['username']] = user
            return users
    except FileNotFoundError:
        logger.warning(f"Users file '{USERS_FILE}' not found. Using simple mode.")
        return SIMPLE_USERS
    except Exception as e:
        logger.error(f"Error loading users file: {e}. Using simple mode.")
        return SIMPLE_USERS


def load_users_from_env():
    """Load users from environment variables"""
    # Format: MITEL_USER_1=username:password:account_id:role:name
    users = {}
    i = 1
    while True:
        user_env = os.getenv(f'MITEL_USER_{i}')
        if not user_env:
            break
        
        parts = user_env.split(':')
        if len(parts) >= 2:
            username = parts[0]
            users[username] = {
                'password': parts[1],
                'account_id': parts[2] if len(parts) > 2 else '1',
                'role': parts[3] if len(parts) > 3 else 'user',
                'name': parts[4] if len(parts) > 4 else username
            }
        i += 1
    
    return users if users else SIMPLE_USERS


def get_users():
    """Get users based on configured mode"""
    if USER_MGMT_MODE == 'json':
        return load_users_from_json()
    elif USER_MGMT_MODE == 'env':
        return load_users_from_env()
    else:  # simple mode
        return SIMPLE_USERS


def generate_token(username, account_id):
    """Generate a bearer token for a user"""
    import hashlib
    import time
    
    # Create a simple token (in production, use JWT)
    token_data = f"{username}:{account_id}:{time.time()}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    
    # Store token with user info and expiration
    active_tokens[token] = {
        'username': username,
        'account_id': account_id,
        'created_at': datetime.now(),
        'expires_at': datetime.now() + timedelta(hours=1)
    }
    
    return token


def validate_token(token):
    """Validate a bearer token"""
    if token not in active_tokens:
        return None
    
    token_info = active_tokens[token]
    
    # Check if token expired
    if datetime.now() > token_info['expires_at']:
        del active_tokens[token]
        return None
    
    return token_info


def require_auth(f):
    """
    Decorator to require Bearer token authentication
    Only enforced if REQUIRE_AUTH=true
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not REQUIRE_AUTH:
            # Auth disabled - allow all requests
            return f(*args, **kwargs)
        
        # Check for Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                "success": False,
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Missing Authorization header. Include 'Authorization: Bearer <token>'"
                }
            }), 401
        
        # Check Bearer token format
        if not auth_header.startswith('Bearer '):
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_AUTH_FORMAT",
                    "message": "Authorization header must use Bearer token format: 'Bearer <token>'"
                }
            }), 401
        
        # Extract token
        token = auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Validate token
        token_info = validate_token(token)
        if not token_info:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_TOKEN",
                    "message": "Invalid or expired bearer token"
                }
            }), 401
        
        # Token valid - add user info to request context
        request.user_info = token_info
        return f(*args, **kwargs)
    
    return decorated_function


# ==================== API ENDPOINTS ====================

@app.route('/')
def root():
    """API root - returns API information"""
    return jsonify({
        "name": "Mitel MiContact Center Historical Reporting API",
        "version": API_VERSION,
        "description": "Mock API for Mitel MiContact Center Call Detail Records",
        "documentation": "https://developer.mitel.io/",
        "authentication": {
            "required": REQUIRE_AUTH,
            "type": "Bearer Token",
            "header": "Authorization: Bearer <token>",
            "user_management": USER_MGMT_MODE,
            "note": "Set REQUIRE_AUTH=true to enable authentication"
        },
        "endpoints": {
            "/auth/login": "Get bearer token (POST)",
            "/auth/logout": "Invalidate token (POST, requires auth)",
            "/auth/users": "List users (GET, requires auth)",
            f"{BASE_PATH}/reporting/calls": "Get historical call records with date filtering",
            f"{BASE_PATH}/reporting/calls/stream": "Stream call records (Kafka format)",
            f"{BASE_PATH}/reporting/calls/export": "Export calls as CSV",
            f"{BASE_PATH}/reporting/agents": "Get agent/extension information",
            f"{BASE_PATH}/reporting/statistics": "Get call statistics",
            "/health": "Health check endpoint"
        }
    })


@app.route('/auth/login', methods=['POST'])
def login():
    """
    Authentication endpoint - returns bearer token
    
    Request Body:
    {
        "username": "user@example.com",
        "password": "password",
        "account_id": "12345"  (optional)
    }
    
    Response:
    {
        "success": true,
        "access_token": "abc123...",
        "refresh_token": "xyz789...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "username": "user@example.com",
            "account_id": "1",
            "role": "user",
            "name": "Regular User"
        }
    }
    """
    data = request.get_json() or {}
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({
            "success": False,
            "error": {
                "code": "MISSING_CREDENTIALS",
                "message": "Username and password are required"
            }
        }), 400
    
    # Get users based on configured mode
    users = get_users()
    
    # Validate credentials
    if username not in users:
        logger.warning(f"Login attempt with unknown username: {username}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid username or password"
            }
        }), 401
    
    user = users[username]
    
    if user['password'] != password:
        logger.warning(f"Login attempt with incorrect password for user: {username}")
        return jsonify({
            "success": False,
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid username or password"
            }
        }), 401
    
    # Generate token
    account_id = user.get('account_id', '1')
    access_token = generate_token(username, account_id)
    
    logger.info(f"User logged in successfully: {username}")
    
    # Return token and user info
    return jsonify({
        "success": True,
        "access_token": access_token,
        "refresh_token": f"refresh_{access_token[:20]}",
        "token_type": "Bearer",
        "expires_in": 3600,
        "user": {
            "username": username,
            "account_id": account_id,
            "role": user.get('role', 'user'),
            "name": user.get('name', username)
        }
    })


@app.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """
    Logout endpoint - invalidates bearer token
    
    Headers:
        Authorization: Bearer <token>
    
    Response:
    {
        "success": true,
        "message": "Logged out successfully"
    }
    """
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        if token in active_tokens:
            username = active_tokens[token]['username']
            del active_tokens[token]
            logger.info(f"User logged out: {username}")
    
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


@app.route('/auth/users', methods=['GET'])
@require_auth
def list_users():
    """
    List all configured users (for admin/testing)
    Requires authentication
    
    Response:
    {
        "success": true,
        "users": [...]
    }
    """
    users = get_users()
    
    # Return users without passwords
    safe_users = []
    for username, user_data in users.items():
        safe_users.append({
            "username": username,
            "account_id": user_data.get('account_id', '1'),
            "role": user_data.get('role', 'user'),
            "name": user_data.get('name', username)
        })
    
    return jsonify({
        "success": True,
        "users": safe_users,
        "count": len(safe_users),
        "management_mode": USER_MGMT_MODE
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
@require_auth
def get_call_records():
    """
    Get Call Detail Records - Mitel MiContact Center format
    
    Query Parameters:
        - startDate: Start date/time (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        - endDate: End date/time (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
        - extension: Filter by extension number
        - direction: Filter by direction (I/O/B)
        - limit: Max records to return (default: 50, max: 500)
        - offset: Pagination offset (default: 0)
    
    Examples:
        /api/v1/reporting/calls?startDate=2025-11-20&endDate=2025-11-22
        /api/v1/reporting/calls?startDate=2025-11-20T00:00:00&endDate=2025-11-22T23:59:59
        /api/v1/reporting/calls?extension=694311&limit=50
        /api/v1/reporting/calls?direction=I&startDate=2025-11-20
    """
    try:
        # Parse parameters
        limit = min(int(request.args.get('limit', 50)), 500)
        offset = int(request.args.get('offset', 0))
        extension = request.args.get('extension')
        direction = request.args.get('direction')
        start_date_str = request.args.get('startDate')
        end_date_str = request.args.get('endDate')
        
        # Parse and validate dates
        try:
            start_date = parse_date_param(start_date_str, 'startDate', end_of_day=False)
            end_date = parse_date_param(end_date_str, 'endDate', end_of_day=True)
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_DATE_FORMAT",
                    "message": str(e)
                }
            }), 400
        
        # Validate date range
        if start_date and end_date and start_date > end_date:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_DATE_RANGE",
                    "message": "startDate must be before or equal to endDate"
                }
            }), 400
        
        # Generate records
        records = []
        attempts = 0
        max_attempts = limit * 3  # Avoid infinite loop with filters
        
        while len(records) < limit and attempts < max_attempts:
            record = generate_call_record(start_date, end_date)
            attempts += 1
            
            # Apply filters
            if extension and record['Extno'] != extension:
                continue
            if direction and record['Direction'] != direction:
                continue
            
            records.append(record)
        
        logger.info(f"Generated {len(records)} call records (date range: {start_date_str} to {end_date_str})")
        
        return jsonify({
            "success": True,
            "data": records,
            "filters": {
                "startDate": start_date_str,
                "endDate": end_date_str,
                "extension": extension,
                "direction": direction
            },
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
@require_auth
def stream_call_records():
    """
    Stream Call Detail Records in Kafka message format
    This matches the structure in your CSV file
    
    Query Parameters:
        - startDate: Start date (ISO 8601)
        - endDate: End date (ISO 8601)
        - limit: Number of messages (default: 50, max: 500)
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 500)
        start_date_str = request.args.get('startDate')
        end_date_str = request.args.get('endDate')
        
        # Parse dates
        try:
            start_date = parse_date_param(start_date_str, 'startDate', end_of_day=False)
            end_date = parse_date_param(end_date_str, 'endDate', end_of_day=True)
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_DATE_FORMAT",
                    "message": str(e)
                }
            }), 400
        
        messages = []
        for _ in range(limit):
            record = generate_call_record(start_date, end_date)
            message = wrap_in_kafka_format(record)
            messages.append(message)
        
        logger.info(f"Generated {len(messages)} Kafka-formatted messages")
        
        return jsonify({
            "success": True,
            "messages": messages,
            "count": len(messages),
            "filters": {
                "startDate": start_date_str,
                "endDate": end_date_str
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


@app.route(f'{BASE_PATH}/reporting/calls/export', methods=['GET'])
@require_auth
def export_calls_csv():
    """
    Export Call Detail Records as CSV
    Matches the exact format of your source CSV file
    
    Query Parameters:
        - startDate: Start date (ISO 8601)
        - endDate: End date (ISO 8601)
        - limit: Number of records (default: 100, max: 1000)
    """
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        start_date_str = request.args.get('startDate')
        end_date_str = request.args.get('endDate')
        
        # Parse dates
        try:
            start_date = parse_date_param(start_date_str, 'startDate', end_of_day=False)
            end_date = parse_date_param(end_date_str, 'endDate', end_of_day=True)
        except ValueError as e:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_DATE_FORMAT",
                    "message": str(e)
                }
            }), 400
        
        # CSV header
        csv_lines = ["timestamp,timestampType,partition,offset,key,value,headers,exceededFields"]
        
        for _ in range(limit):
            record = generate_call_record(start_date, end_date)
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
        
        # Generate filename with date range if provided
        filename = "mitel_call_records"
        if start_date_str:
            filename += f"_{start_date_str}"
        if end_date_str:
            filename += f"_to_{end_date_str}"
        filename += ".csv"
        
        return Response(
            csv_content,
            mimetype='text/csv',
            headers={
                'Content-Disposition': f'attachment; filename={filename}'
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
@require_auth
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
@require_auth
def get_statistics():
    """
    Get call statistics and KPIs
    Mitel MiContact Center format
    
    Query Parameters:
        - startDate: Start date for statistics (ISO 8601)
        - endDate: End date for statistics (ISO 8601)
    """
    start_date_str = request.args.get('startDate')
    end_date_str = request.args.get('endDate')
    
    # Default to last 24 hours if not specified
    if not start_date_str:
        start_date = datetime.now() - timedelta(days=1)
        start_date_str = start_date.isoformat()
    if not end_date_str:
        end_date_str = datetime.now().isoformat()
    
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
            "startDate": start_date_str,
            "endDate": end_date_str
        },
        "timestamp": datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("=" * 70)
    print("Mitel MiContact Center Historical Reporting API - Mock Server")
    print("=" * 70)
    print(f"API Version: {API_VERSION}")
    print(f"Base Path: {BASE_PATH}")
    print("\nEndpoints:")
    print(f"  - {BASE_PATH}/reporting/calls")
    print(f"  - {BASE_PATH}/reporting/calls/stream")
    print(f"  - {BASE_PATH}/reporting/calls/export")
    print(f"  - {BASE_PATH}/reporting/agents")
    print(f"  - {BASE_PATH}/reporting/statistics")
    print("\nFeatures:")
    print("  ✓ Date range filtering (startDate/endDate)")
    print("  ✓ Extension and direction filtering")
    print("  ✓ Kafka message format support")
    print("  ✓ CSV export with exact format match")
    print(f"  ✓ Bearer token authentication: {'ENABLED' if REQUIRE_AUTH else 'DISABLED'}")
    print("\nAuthentication:")
    if REQUIRE_AUTH:
        print(f"  - Auth is ENABLED (set REQUIRE_AUTH=false to disable)")
        print(f"  - User management: {USER_MGMT_MODE} mode")
        print(f"  - Get token: POST /auth/login")
        if USER_MGMT_MODE == 'simple':
            print("  - Default users: admin@mitel.com/admin123, user@mitel.com/user123")
        elif USER_MGMT_MODE == 'json':
            print(f"  - Users loaded from: {USERS_FILE}")
        elif USER_MGMT_MODE == 'env':
            print("  - Users loaded from environment variables (MITEL_USER_*)")
    else:
        print("  - Auth is DISABLED (set REQUIRE_AUTH=true to enable)")
        print("  - All endpoints accessible without authentication")
    print("\nStarting server on http://0.0.0.0:5000")
    print("=" * 70)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
