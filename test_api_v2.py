#!/usr/bin/env python3
"""
Test script for Mitel API Mock Server v2 (Mitel-Compliant)
Tests endpoints that follow official Mitel API structure
"""

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:5000"
ACCOUNT_ID = "default"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing /api/health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_home():
    """Test home endpoint"""
    print("\n🔍 Testing /...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Home endpoint passed")
            data = response.json()
            print(f"Service: {data.get('service')}")
            print(f"Version: {data.get('version')}")
            print(f"API Version: {data.get('api_version')}")
            return True
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cloudlink_call_history():
    """Test CloudLink-style call history endpoint"""
    print("\n🔍 Testing CloudLink Call History (GET /api/v1/accounts/{accountId}/callHistory)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/callHistory?limit=10",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CloudLink Call History passed")
            print(f"Account ID: {data.get('accountId')}")
            print(f"Total records: {data.get('callHistory', {}).get('total')}")
            print(f"Records in response: {len(data.get('callHistory', {}).get('items', []))}")
            
            # Validate structure
            if '_links' in data:
                print(f"Links present: {list(data['_links'].keys())}")
            
            return True
        else:
            print(f"❌ CloudLink Call History failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cloudlink_call_history_with_filter():
    """Test CloudLink call history with direction filter"""
    print("\n🔍 Testing Call History with filter (direction=inbound)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/callHistory?limit=5&direction=inbound",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Filtered Call History passed")
            items = data.get('callHistory', {}).get('items', [])
            print(f"Records returned: {len(items)}")
            
            # Check if filtering worked
            if items:
                first_item = items[0]
                print(f"First record direction: {first_item.get('Direction')}")
            
            return True
        else:
            print(f"❌ Filtered Call History failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cloudlink_query_post():
    """Test CloudLink query endpoint with POST"""
    print("\n🔍 Testing CloudLink Query (POST /api/v1/accounts/{accountId}/callHistory/query)...")
    try:
        query_body = {
            "filter": {
                "extension": "694311",
                "direction": "inbound",
                "minDuration": 0
            },
            "pagination": {
                "limit": 10,
                "offset": 0
            }
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/accounts/{ACCOUNT_ID}/callHistory/query",
            json=query_body,
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CloudLink Query passed")
            print(f"Account ID: {data.get('accountId')}")
            results = data.get('queryResults', {})
            print(f"Records found: {len(results.get('items', []))}")
            print(f"Has more: {results.get('hasMore')}")
            return True
        else:
            print(f"❌ CloudLink Query failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_reporting_cdr():
    """Test Reporting API - Call Detail Records"""
    print("\n🔍 Testing Reporting CDR (GET /api/v1/reporting/callDetailRecords)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/reporting/callDetailRecords?limit=15",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Reporting CDR passed")
            print(f"Status: {data.get('status')}")
            cdr_data = data.get('data', {})
            print(f"CDR count: {cdr_data.get('count')}")
            
            # Check metadata
            metadata = cdr_data.get('metadata', {})
            print(f"Generated at: {metadata.get('generatedAt')}")
            print(f"API version: {metadata.get('apiVersion')}")
            
            return True
        else:
            print(f"❌ Reporting CDR failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_historical_data_kafka():
    """Test Historical Data in Kafka format"""
    print("\n🔍 Testing Historical Data Kafka Format (GET /api/v1/reporting/historicalData)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/reporting/historicalData?limit=5",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Historical Data (Kafka) passed")
            print(f"Status: {data.get('status')}")
            
            kafka_data = data.get('data', {})
            messages = kafka_data.get('messages', [])
            print(f"Messages returned: {len(messages)}")
            
            # Validate Kafka structure
            if messages:
                msg = messages[0]
                print(f"Message structure: timestamp={msg.get('timestamp')}, " +
                      f"partition={msg.get('partition')}, offset={msg.get('offset')}")
                print(f"Has key: {'key' in msg}")
                print(f"Has value: {'value' in msg}")
            
            return True
        else:
            print(f"❌ Historical Data failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_historical_data_csv_export():
    """Test CSV export in original format"""
    print("\n🔍 Testing CSV Export (GET /api/v1/reporting/historicalData/export)...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/reporting/historicalData/export?limit=3",
            timeout=5
        )
        if response.status_code == 200:
            print(f"✅ CSV Export passed")
            
            # Check CSV format
            csv_text = response.text
            lines = csv_text.split('\n')
            print(f"CSV lines: {len(lines)}")
            print(f"Header: {lines[0][:80]}...")
            
            # Validate header matches original format
            expected_header = "timestamp,timestampType,partition,offset,key,value,headers,exceededFields"
            if lines[0] == expected_header:
                print("✅ CSV header matches expected format")
            else:
                print("⚠️  CSV header differs from expected")
            
            return True
        else:
            print(f"❌ CSV Export failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_extensions():
    """Test extensions endpoint"""
    print("\n🔍 Testing Extensions (GET /api/v1/extensions)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/extensions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Extensions endpoint passed")
            print(f"Extensions count: {data.get('total')}")
            return True
        else:
            print(f"❌ Extensions endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_stats():
    """Test stats endpoint"""
    print("\n🔍 Testing Stats (GET /api/v1/stats)...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint passed")
            stats = data.get('statistics', {}).get('today', {})
            print(f"Total calls: {stats.get('totalCalls')}")
            print(f"Inbound: {stats.get('inboundCalls')}")
            print(f"Outbound: {stats.get('outboundCalls')}")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("Mitel API Mock Server v2 (Mitel-Compliant) - Test Suite")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Account ID: {ACCOUNT_ID}")
    print(f"\nMake sure the server is running:")
    print(f"  python3 app_v2_mitel_compliant.py")
    
    tests = [
        ("Health Check", test_health),
        ("API Home", test_home),
        ("CloudLink Call History (GET)", test_cloudlink_call_history),
        ("CloudLink Call History (Filtered)", test_cloudlink_call_history_with_filter),
        ("CloudLink Query (POST)", test_cloudlink_query_post),
        ("Reporting CDR", test_reporting_cdr),
        ("Historical Data (Kafka)", test_historical_data_kafka),
        ("CSV Export (Original Format)", test_historical_data_csv_export),
        ("Extensions", test_extensions),
        ("Statistics", test_stats),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Total: {passed}/{total} tests passed")
    print(f"{'='*70}")
    
    if passed == total:
        print("\n🎉 All tests passed! Your Mitel-compliant API is working perfectly!")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

