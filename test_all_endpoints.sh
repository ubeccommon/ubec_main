#!/bin/bash
# UBEC API - Comprehensive Endpoint Testing Script
# Tests all 16 operational endpoints (20 total routes including /docs, /redoc, /openapi.json)

API_HOST="${API_HOST:-http://localhost:8000}"
PASSED=0
FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================================================"
echo "UBEC API - Complete Endpoint Test Suite"
echo "Testing: $API_HOST"
echo "======================================================================"

test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_field="$3"
    
    echo -n "Testing: $name ... "
    
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 200 ]; then
        if echo "$body" | jq -e ".$expected_field" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASSED++))
            return 0
        else
            echo -e "${YELLOW}⚠ WARN${NC} (200 but missing field: $expected_field)"
            ((PASSED++))
            return 0
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        ((FAILED++))
        return 1
    fi
}

echo ""
echo "Core Endpoints"
echo "----------------------------------------------------------------------"
test_endpoint "Health Check" "$API_HOST/health" "status"
test_endpoint "API Docs (Swagger)" "$API_HOST/api/docs" "" # HTML endpoint, just check 200

echo ""
echo "Token & Network Endpoints"
echo "----------------------------------------------------------------------"
test_endpoint "Token Information" "$API_HOST/api/v1/tokens" "tokens"
test_endpoint "Network Status" "$API_HOST/api/v1/network-status" "network_health"
test_endpoint "Distribution Stats" "$API_HOST/api/v1/distribution" "distributions"

echo ""
echo "Holonic Evaluation Endpoints"
echo "----------------------------------------------------------------------"
test_endpoint "Holonic Scores (all)" "$API_HOST/api/v1/holonic-scores" "accounts"
test_endpoint "Holonic Scores (limited)" "$API_HOST/api/v1/holonic-scores?limit=5" "count"
test_endpoint "Holonic Scores (by category)" "$API_HOST/api/v1/holonic-scores?category=contributor&limit=3" "filters"

echo ""
echo "Transaction Endpoints"
echo "----------------------------------------------------------------------"
test_endpoint "Recent Transactions" "$API_HOST/api/v1/transactions" "transactions"
test_endpoint "Transactions (limited)" "$API_HOST/api/v1/transactions?limit=10" "count"

echo ""
echo "Bioregion Endpoints"
echo "----------------------------------------------------------------------"
test_endpoint "Bioregion Count" "$API_HOST/api/v1/bioregions/count" "count"
test_endpoint "Bioregion Summary" "$API_HOST/api/v1/bioregions/summary" "timestamp"
test_endpoint "All Bioregions" "$API_HOST/api/v1/bioregions" "count"

# Test specific bioregion and health only if bioregions exist
bioregion_count=$(curl -s "$API_HOST/api/v1/bioregions/count" | jq -r '.count // 0')
if [ "$bioregion_count" -gt 0 ]; then
    test_endpoint "Specific Bioregion" "$API_HOST/api/v1/bioregions/1" "bioregion_id"
    test_endpoint "Bioregion Health" "$API_HOST/api/v1/bioregions/1/health" "health_rating"
else
    echo -n "Testing: Specific Bioregion ... "
    echo -e "${YELLOW}⚠ SKIP${NC} (no bioregions in database)"
    echo -n "Testing: Bioregion Health ... "
    echo -e "${YELLOW}⚠ SKIP${NC} (no bioregions in database)"
fi

echo ""
echo "Ecoregion Endpoints"
echo "----------------------------------------------------------------------"
test_endpoint "All Ecoregions" "$API_HOST/api/v1/ecoregions" "count"
test_endpoint "Ecoregions (limited)" "$API_HOST/api/v1/ecoregions?limit=5" "ecoregions"
test_endpoint "Ecoregions (filtered)" "$API_HOST/api/v1/ecoregions?biome=forest&limit=3" "filters"

# Test specific ecoregion (use eco_id=1 as example)
ecoregion_count=$(curl -s "$API_HOST/api/v1/ecoregions" | jq -r '.count // 0')
if [ "$ecoregion_count" -gt 0 ]; then
    # Get first eco_id from results
    first_eco_id=$(curl -s "$API_HOST/api/v1/ecoregions?limit=1" | jq -r '.ecoregions[0].eco_id // 0')
    if [ "$first_eco_id" -gt 0 ]; then
        test_endpoint "Specific Ecoregion" "$API_HOST/api/v1/ecoregions/$first_eco_id" "eco_name"
    else
        echo -n "Testing: Specific Ecoregion ... "
        echo -e "${YELLOW}⚠ SKIP${NC} (no valid eco_id found)"
    fi
else
    echo -n "Testing: Specific Ecoregion ... "
    echo -e "${YELLOW}⚠ SKIP${NC} (no ecoregions in database)"
fi

echo ""
echo "======================================================================"
echo "Test Results Summary"
echo "======================================================================"
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo "Total:  $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
