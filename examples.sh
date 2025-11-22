#!/bin/bash

# Example API Usage Script
# This script demonstrates how to use the Mitel API Mock endpoints

API_URL="${API_URL:-http://localhost:5000}"

echo "======================================"
echo "Mitel API Mock - Usage Examples"
echo "======================================"
echo "API URL: $API_URL"
echo ""

# Test 1: Health Check
echo "1️⃣  Health Check"
echo "---"
curl -s "$API_URL/api/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Home endpoint
echo "2️⃣  API Home"
echo "---"
curl -s "$API_URL/" | python3 -m json.tool
echo ""
echo ""

# Test 3: Get CDR records (default limit)
echo "3️⃣  Get CDR Records (default limit=10)"
echo "---"
curl -s "$API_URL/api/v1/cdr" | python3 -m json.tool | head -50
echo "..."
echo ""

# Test 4: Get CDR records with limit
echo "4️⃣  Get CDR Records (limit=5)"
echo "---"
curl -s "$API_URL/api/v1/cdr?limit=5" | python3 -m json.tool | head -40
echo "..."
echo ""

# Test 5: Filter by extension
echo "5️⃣  Filter CDR by Extension"
echo "---"
curl -s "$API_URL/api/v1/cdr?extension=694311&limit=3" | python3 -m json.tool | head -30
echo "..."
echo ""

# Test 6: Filter by direction
echo "6️⃣  Filter CDR by Direction (Inbound)"
echo "---"
curl -s "$API_URL/api/v1/cdr?direction=I&limit=5" | python3 -m json.tool | head -30
echo "..."
echo ""

# Test 7: Get Kafka stream format
echo "7️⃣  Get CDR in Kafka Stream Format"
echo "---"
curl -s "$API_URL/api/v1/cdr/stream?limit=2" | python3 -m json.tool | head -40
echo "..."
echo ""

# Test 8: Get extensions
echo "8️⃣  Get Extensions"
echo "---"
curl -s "$API_URL/api/v1/extensions" | python3 -m json.tool
echo ""
echo ""

# Test 9: Get statistics
echo "9️⃣  Get Call Statistics"
echo "---"
curl -s "$API_URL/api/v1/stats" | python3 -m json.tool
echo ""
echo ""

# Test 10: Export as CSV
echo "🔟  Export CDR as CSV (saved to cdr_export.csv)"
echo "---"
curl -s "$API_URL/api/v1/cdr/export?limit=5" -o cdr_export.csv
echo "✅ Exported to cdr_export.csv"
head -3 cdr_export.csv
echo "..."
echo ""

echo "======================================"
echo "Examples Complete!"
echo "======================================"
echo ""
echo "For EC2 deployment, set API_URL environment variable:"
echo "  export API_URL=http://your-ec2-ip:5000"
echo "  ./examples.sh"
echo ""

