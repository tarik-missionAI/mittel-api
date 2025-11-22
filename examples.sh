#!/bin/bash

# Mitel MiContact Center API - Usage Examples
# Demonstrates all Mitel-compliant endpoints

API_URL="${API_URL:-http://localhost:5000}"
API_PATH="/api/v1/reporting"

echo "======================================"
echo "Mitel MiContact Center API Examples"
echo "======================================"
echo "API URL: $API_URL"
echo "API Path: $API_PATH"
echo ""

# Test 1: Health Check
echo "1️⃣  Health Check"
echo "---"
curl -s "$API_URL/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: API Root
echo "2️⃣  API Information"
echo "---"
curl -s "$API_URL/" | python3 -m json.tool
echo ""
echo ""

# Test 3: Get Call Records (default)
echo "3️⃣  Get Call Records (default limit=50)"
echo "---"
curl -s "$API_URL$API_PATH/calls" | python3 -m json.tool | head -60
echo "..."
echo ""

# Test 4: Get Call Records with limit
echo "4️⃣  Get Call Records (limit=5)"
echo "---"
curl -s "$API_URL$API_PATH/calls?limit=5" | python3 -m json.tool | head -50
echo "..."
echo ""

# Test 5: Filter by extension
echo "5️⃣  Filter Calls by Extension (694311)"
echo "---"
curl -s "$API_URL$API_PATH/calls?extension=694311&limit=3" | python3 -m json.tool | head -40
echo "..."
echo ""

# Test 6: Filter by direction
echo "6️⃣  Filter Calls by Direction (Inbound only)"
echo "---"
curl -s "$API_URL$API_PATH/calls?direction=I&limit=5" | python3 -m json.tool | head -40
echo "..."
echo ""

# Test 7: Get Kafka stream format
echo "7️⃣  Get Call Stream in Kafka Format"
echo "---"
curl -s "$API_URL$API_PATH/calls/stream?limit=2" | python3 -m json.tool | head -50
echo "..."
echo ""

# Test 8: Export as CSV
echo "8️⃣  Export Calls as CSV (saved to mitel_calls_export.csv)"
echo "---"
curl -s "$API_URL$API_PATH/calls/export?limit=5" -o mitel_calls_export.csv
echo "✅ Exported to mitel_calls_export.csv"
head -3 mitel_calls_export.csv
echo "..."
echo ""

# Test 9: Get agents
echo "9️⃣  Get Agents/Extensions"
echo "---"
curl -s "$API_URL$API_PATH/agents" | python3 -m json.tool
echo ""
echo ""

# Test 10: Get statistics
echo "🔟  Get Call Statistics & KPIs"
echo "---"
curl -s "$API_URL$API_PATH/statistics" | python3 -m json.tool
echo ""
echo ""

# Test 11: Date range filtering
echo "1️⃣1️⃣  Date Range Filtering"
echo "---"
echo "Get calls from Nov 20-22, 2025..."
curl -s "$API_URL$API_PATH/calls?startDate=2025-11-20&endDate=2025-11-22&limit=5" | python3 -m json.tool | head -40
echo "..."
echo ""

# Test 12: Datetime filtering
echo "1️⃣2️⃣  Datetime Filtering (with time)"
echo "---"
echo "Get calls with specific time range..."
curl -s "$API_URL$API_PATH/calls?startDate=2025-11-20T00:00:00&endDate=2025-11-22T23:59:59&limit=3" | python3 -m json.tool | head -35
echo "..."
echo ""

echo "======================================"
echo "Examples Complete!"
echo "======================================"
echo ""
echo "🎯 Mitel-Compliant Endpoints:"
echo "  - $API_PATH/calls"
echo "  - $API_PATH/calls/stream"
echo "  - $API_PATH/calls/export"
echo "  - $API_PATH/agents"
echo "  - $API_PATH/statistics"
echo ""
echo "For EC2 deployment, set API_URL:"
echo "  export API_URL=http://your-ec2-ip:5000"
echo "  ./examples_mitel.sh"
echo ""

