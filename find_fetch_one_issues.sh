#!/bin/bash
# find_fetch_one_issues.sh
# Script to find all fetch_one/fetch_all/execute calls that may be missing params

set -e

echo "======================================================================="
echo "Database Method Call Analyzer"
echo "======================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}✗ Error: main.py not found. Are you in the project root?${NC}"
    exit 1
fi

echo -e "${YELLOW}Scanning for potential database method call issues...${NC}"
echo ""

# Create a temporary file for results
RESULTS_FILE=$(mktemp)

# Function to check a file
check_file() {
    local file=$1
    local issues=0
    
    # Check for fetch_one calls
    if grep -n "\.fetch_one(" "$file" | grep -v "\.fetch_one([^,]*," > /dev/null 2>&1; then
        echo -e "${YELLOW}File: $file${NC}"
        echo "  Potential fetch_one issues:"
        grep -n "\.fetch_one(" "$file" | grep -v "\.fetch_one([^,]*," | while read line; do
            echo "    Line: $line"
            ((issues++))
        done
        echo ""
    fi
    
    # Check for fetch_all calls
    if grep -n "\.fetch_all(" "$file" | grep -v "\.fetch_all([^,]*," > /dev/null 2>&1; then
        echo -e "${YELLOW}File: $file${NC}"
        echo "  Potential fetch_all issues:"
        grep -n "\.fetch_all(" "$file" | grep -v "\.fetch_all([^,]*," | while read line; do
            echo "    Line: $line"
            ((issues++))
        done
        echo ""
    fi
    
    # Check for execute calls (less reliable due to print/other execute methods)
    if grep -n "\.execute(" "$file" | grep "self\.db\.execute\|db_manager\.execute\|self\.db_manager\.execute" | grep -v "\.execute([^,]*," > /dev/null 2>&1; then
        echo -e "${YELLOW}File: $file${NC}"
        echo "  Potential execute issues:"
        grep -n "\.execute(" "$file" | grep "self\.db\.execute\|db_manager\.execute\|self\.db_manager\.execute" | grep -v "\.execute([^,]*," | while read line; do
            echo "    Line: $line"
            ((issues++))
        done
        echo ""
    fi
}

# Scan Python files
echo "Scanning services/..."
find services/ -name "*.py" -type f 2>/dev/null | while read file; do
    check_file "$file"
done

echo "Scanning core/..."
find core/ -name "*.py" -type f 2>/dev/null | while read file; do
    check_file "$file"
done

echo ""
echo "======================================================================="
echo "Summary"
echo "======================================================================="
echo ""
echo -e "${GREEN}Scan complete!${NC}"
echo ""
echo "Review the results above. Lines shown may need to be fixed to include"
echo "the params tuple as the second argument."
echo ""
echo "Example fixes:"
echo "  ${RED}BEFORE:${NC} await self.db.fetch_one(query)"
echo "  ${GREEN}AFTER:${NC}  await self.db.fetch_one(query, ())"
echo ""
echo "  ${RED}BEFORE:${NC} await self.db.execute(query, value)"
echo "  ${GREEN}AFTER:${NC}  await self.db.execute(query, (value,))"
echo ""
echo "Next steps:"
echo "  1. Review each flagged line manually"
echo "  2. Add empty tuple () for queries with no parameters"
echo "  3. Wrap single parameters in tuple: (value,)"
echo "  4. Ensure multiple parameters are in tuple: (a, b, c)"
echo "  5. Test with: python main.py --mode health"
echo ""
echo "======================================================================="
