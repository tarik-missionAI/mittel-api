#!/usr/bin/env python3
"""
Test script for Mitel API Mock Server
Run this to verify the API is working correctly
"""

import requests
import json
import sys

# API base URL
BASE_URL = "http://localhost:5000"

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
            return True
        else:
            print(f"❌ Home endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cdr():
    """Test CDR endpoint"""
    print("\n🔍 Testing /api/v1/cdr...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/cdr?limit=5", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CDR endpoint passed")
            print(f"Records returned: {data.get('count')}")
            if data.get('records'):
                record = data['records'][0]
                print(f"Sample record ID: {record.get('RecordId')}")
                print(f"Extension: {record.get('Extno')}")
                print(f"Direction: {record.get('Direction')}")
            return True
        else:
            print(f"❌ CDR endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cdr_stream():
    """Test CDR stream endpoint"""
    print("\n🔍 Testing /api/v1/cdr/stream...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/cdr/stream?limit=3", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ CDR stream endpoint passed")
            print(f"Messages returned: {data.get('count')}")
            if data.get('messages'):
                msg = data['messages'][0]
                print(f"Sample message timestamp: {msg.get('timestamp')}")
                print(f"Partition: {msg.get('partition')}")
            return True
        else:
            print(f"❌ CDR stream endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_extensions():
    """Test extensions endpoint"""
    print("\n🔍 Testing /api/v1/extensions...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/extensions", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Extensions endpoint passed")
            print(f"Extensions returned: {data.get('count')}")
            return True
        else:
            print(f"❌ Extensions endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_stats():
    """Test stats endpoint"""
    print("\n🔍 Testing /api/v1/stats...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint passed")
            stats = data.get('stats', {})
            print(f"Total calls today: {stats.get('total_calls_today')}")
            print(f"Inbound calls: {stats.get('inbound_calls')}")
            print(f"Outbound calls: {stats.get('outbound_calls')}")
            return True
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_cdr_export():
    """Test CDR export endpoint"""
    print("\n🔍 Testing /api/v1/cdr/export...")
    try:
        response = requests.get(f"{BASE_URL}/api/v1/cdr/export?limit=2", timeout=5)
        if response.status_code == 200:
            print(f"✅ CDR export endpoint passed")
            lines = response.text.split('\n')
            print(f"CSV lines returned: {len(lines)}")
            print(f"Header: {lines[0][:50]}...")
            return True
        else:
            print(f"❌ CDR export endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Mitel API Mock Server - Test Suite")
    print("=" * 60)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Make sure the server is running before running these tests")
    
    tests = [
        test_home,
        test_health,
        test_cdr,
        test_cdr_stream,
        test_extensions,
        test_stats,
        test_cdr_export
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()

