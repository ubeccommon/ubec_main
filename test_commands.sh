#!/bin/bash
# UBEC API Service Test Suite - Quick Reference Commands
# =======================================================
# 
# This script provides quick access to common test commands.
# Make executable with: chmod +x test_commands.sh

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}UBEC API Service Test Suite - Quick Commands${NC}\n"

# Function to print command and execute
run_test() {
    echo -e "${GREEN}$1${NC}"
    echo -e "${YELLOW}Command: $2${NC}"
    echo ""
    eval $2
    echo ""
}

# Main menu
echo "Available test commands:"
echo "========================"
echo ""
echo "1. Install dependencies"
echo "2. Run ALL tests"
echo "3. Test TOKENS endpoint (v2.2.0 enhancements)"
echo "4. Test HOLONIC SCORES endpoint (v2.2.0 enhancements)"
echo "5. Test HEALTH endpoints"
echo "6. Test NETWORK STATUS"
echo "7. Test BIOREGIONS"
echo "8. Test TRANSACTIONS"
echo "9. Test DISTRIBUTION"
echo "10. Test RATE LIMITING"
echo ""

read -p "Select option (1-10) or 'all' to run all: " choice

case $choice in
    1)
        run_test "Installing dependencies..." \
                 "pip install aiohttp colorama --break-system-packages"
        ;;
    2|all)
        run_test "Running ALL API tests..." \
                 "python test_api_service.py"
        ;;
    3)
        run_test "Testing TOKENS endpoint (NEW: name, total_supply)..." \
                 "python test_api_service.py --category tokens"
        ;;
    4)
        run_test "Testing HOLONIC SCORES (NEW: reciprocity_health, mutualism_capacity)..." \
                 "python test_api_service.py --category holonic"
        ;;
    5)
        run_test "Testing HEALTH endpoints..." \
                 "python test_api_service.py --category health"
        ;;
    6)
        run_test "Testing NETWORK STATUS..." \
                 "python test_api_service.py --category network"
        ;;
    7)
        run_test "Testing BIOREGIONS..." \
                 "python test_api_service.py --category bioregions"
        ;;
    8)
        run_test "Testing TRANSACTIONS..." \
                 "python test_api_service.py --category transactions"
        ;;
    9)
        run_test "Testing DISTRIBUTION..." \
                 "python test_api_service.py --category distribution"
        ;;
    10)
        run_test "Testing RATE LIMITING..." \
                 "python test_api_service.py --category ratelimit"
        ;;
    *)
        echo -e "${YELLOW}Invalid option. Usage examples:${NC}"
        echo ""
        echo "  ./test_commands.sh       # Interactive menu"
        echo "  python test_api_service.py                    # All tests"
        echo "  python test_api_service.py --category tokens  # Tokens only"
        echo "  python test_api_service.py --category holonic # Holonic only"
        echo ""
        ;;
esac
