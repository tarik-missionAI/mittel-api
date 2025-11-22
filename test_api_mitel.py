#!/usr/bin/env python3
"""
Test script for Mitel MiContact Center API Mock Server
Tests all Mitel-compliant endpoints
"""

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:5000"
API_PATH = "/api/v1/reporting"

def test_health():
    """Test health endpoint"""
    print("\n🔍 Testing /health...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
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


def test_root():
    """Test root endpoint"""
    print("\n🔍 Testing /...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint passed")
            data = response.json()
            print(f"Name: {data.get('name')}")
            print(f"Version: {data.get('version')}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_calls():
    """Test calls endpoint"""
    print(f"\n🔍 Testing {API_PATH}/calls...")
    try:
        response = requests.get(f"{BASE_URL}{API_PATH}/calls?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Calls endpoint passed")
            print(f"Records returned: {len(data.get('data', []))}")
            if data.get('data'):
                record = data['data'][0]
                print(f"Sample CallId: {record.get('CallId')}")
                print(f"Extension: {record.get('Extno')}")
                print(f"Journey Outcome: {record.get('JourneyOutcome')}")
                print(f"Experience Rating: {record.get('CallExperienceRating')}")
            return True
        else:
            print(f"❌ Calls endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_calls_filter_extension():
    """Test calls endpoint with extension filter"""
    print(f"\n🔍 Testing {API_PATH}/calls with extension filter...")
    try:
        response = requests.get(
            f"{BASE_URL}{API_PATH}/calls?extension=694311&limit=5", 
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Extension filter passed")
            print(f"Records returned: {len(data.get('data', []))}")
            return True
        else:
            print(f"❌ Extension filter failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_calls_stream():
    """Test calls stream endpoint (Kafka format)"""
    print(f"\n🔍 Testing {API_PATH}/calls/stream...")
    try:
        response = requests.get(f"{BASE_URL}{API_PATH}/calls/stream?limit=3", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Calls stream endpoint passed")
            print(f"Messages returned: {data.get('count')}")
            if data.get('messages'):
                msg = data['messages'][0]
                print(f"Sample message timestamp: {msg.get('timestamp')}")
                print(f"Partition: {msg.get('partition')}")
                print(f"Offset: {msg.get('offset')}")
            return True
        else:
            print(f"❌ Calls stream endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_calls_export():
    """Test calls export endpoint"""
    print(f"\n🔍 Testing {API_PATH}/calls/export...")
    try:
        response = requests.get(f"{BASE_URL}{API_PATH}/calls/export?limit=2", timeout=5)
        if response.status_code == 200:
            print(f"✅ Calls export endpoint passed")
            lines = response.text.split('\n')
            print(f"CSV lines returned: {len(lines)}")
            print(f"Header: {lines[0][:60]}...")
            return True
        else:
            print(f"❌ Calls export endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_agents():
    """Test agents endpoint"""
    print(f"\n🔍 Testing {API_PATH}/agents...")
    try:
        response = requests.get(f"{BASE_URL}{API_PATH}/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agents endpoint passed")
            print(f"Agents returned: {data.get('count')}")
            if data.get('data'):
                agent = data['data'][0]
                print(f"Sample agent: {agent.get('extension')} - {agent.get('status')}")
            return True
        else:
            print(f"❌ Agents endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_statistics():
    """Test statistics endpoint"""
    print(f"\n🔍 Testing {API_PATH}/statistics...")
    try:
        response = requests.get(f"{BASE_URL}{API_PATH}/statistics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Statistics endpoint passed")
            stats = data.get('data', {})
            cv = stats.get('callVolume', {})
            print(f"Total calls: {cv.get('totalCalls')}")
            print(f"Inbound: {cv.get('inboundCalls')}, Outbound: {cv.get('outboundCalls')}")
            jm = stats.get('journeyMetrics', {})
            print(f"Average Experience Rating: {jm.get('averageExperienceRating')}")
            return True
        else:
            print(f"❌ Statistics endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_legacy_compatibility():
    """Test legacy endpoints still work"""
    print("\n🔍 Testing legacy endpoint compatibility...")
    try:
        # Test old /api/v1/cdr endpoint
        response = requests.get(f"{BASE_URL}/api/v1/cdr?limit=5", timeout=5)
        if response.status_code == 200:
            print("✅ Legacy /api/v1/cdr endpoint still works")
            return True
        else:
            print(f"❌ Legacy endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("Mitel MiContact Center API Mock Server - Test Suite")
    print("=" * 70)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"API Path: {API_PATH}")
    print(f"\nMake sure the server is running before running these tests")
    
    tests = [
        test_root,
        test_health,
        test_calls,
        test_calls_filter_extension,
        test_calls_stream,
        test_calls_export,
        test_agents,
        test_statistics,
        test_legacy_compatibility
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        print("\n✅ API is Mitel MiContact Center compliant!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

