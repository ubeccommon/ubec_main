#!/bin/bash
# fix_health_checks.sh
# Automated fix for health check method name errors
# Date: October 17, 2025

set -e  # Exit on error

echo "======================================================================="
echo "Health Check Method Fix Script"
echo "======================================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}✗ Error: main.py not found. Are you in the project root?${NC}"
    echo ""
    echo "Please run this script from: ~/UBEC/projects/UBEC"
    exit 1
fi

echo -e "${YELLOW}Step 1: Backing up files...${NC}"

# Create backups
BACKUP_DIR="backups_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "core/holonic/ubec_holonic_evaluator.py" ]; then
    cp core/holonic/ubec_holonic_evaluator.py "$BACKUP_DIR/"
    echo "  ✓ Backed up ubec_holonic_evaluator.py"
else
    echo -e "${RED}  ✗ Warning: ubec_holonic_evaluator.py not found${NC}"
fi

if [ -f "services/distribution/ubec_distribution_evaluator.py" ]; then
    cp services/distribution/ubec_distribution_evaluator.py "$BACKUP_DIR/"
    echo "  ✓ Backed up ubec_distribution_evaluator.py"
else
    echo -e "${RED}  ✗ Warning: ubec_distribution_evaluator.py not found${NC}"
fi

echo ""
echo -e "${YELLOW}Step 2: Applying fixes...${NC}"

# Fix holonic evaluator
if [ -f "core/holonic/ubec_holonic_evaluator.py" ]; then
    # Check if the wrong method name exists
    if grep -q "database_only_health" core/holonic/ubec_holonic_evaluator.py; then
        sed -i 's/database_only_health/database_dependent_health/g' \
            core/holonic/ubec_holonic_evaluator.py
        echo "  ✓ Fixed holonic_evaluator (database_only_health → database_dependent_health)"
    else
        echo "  • holonic_evaluator already correct or method not found"
    fi
else
    echo -e "${RED}  ✗ Could not fix holonic_evaluator (file not found)${NC}"
fi

# Fix distribution evaluator
if [ -f "services/distribution/ubec_distribution_evaluator.py" ]; then
    # Check if the wrong method name exists
    if grep -q "service_dependent_health" services/distribution/ubec_distribution_evaluator.py; then
        sed -i 's/service_dependent_health/database_dependent_health/g' \
            services/distribution/ubec_distribution_evaluator.py
        echo "  ✓ Fixed distribution_evaluator (service_dependent_health → database_dependent_health)"
    else
        echo "  • distribution_evaluator already correct or method not found"
    fi
else
    echo -e "${RED}  ✗ Could not fix distribution_evaluator (file not found)${NC}"
fi

echo ""
echo -e "${YELLOW}Step 3: Verifying changes...${NC}"

HOLONIC_OK=false
DIST_OK=false

# Verify holonic evaluator
if [ -f "core/holonic/ubec_holonic_evaluator.py" ]; then
    if grep -q "database_dependent_health" core/holonic/ubec_holonic_evaluator.py && \
       ! grep -q "database_only_health" core/holonic/ubec_holonic_evaluator.py; then
        echo -e "  ${GREEN}✓ holonic_evaluator: Correctly using database_dependent_health${NC}"
        HOLONIC_OK=true
    else
        echo -e "  ${RED}✗ holonic_evaluator: Verification failed${NC}"
    fi
fi

# Verify distribution evaluator
if [ -f "services/distribution/ubec_distribution_evaluator.py" ]; then
    if grep -q "database_dependent_health" services/distribution/ubec_distribution_evaluator.py && \
       ! grep -q "service_dependent_health" services/distribution/ubec_distribution_evaluator.py; then
        echo -e "  ${GREEN}✓ distribution_evaluator: Correctly using database_dependent_health${NC}"
        DIST_OK=true
    else
        echo -e "  ${RED}✗ distribution_evaluator: Verification failed${NC}"
    fi
fi

echo ""
echo -e "${YELLOW}Step 4: Cleaning Python cache...${NC}"

# Clear Python cache to ensure changes take effect
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "  ✓ Python cache cleared"

echo ""
echo "======================================================================="
echo "Summary"
echo "======================================================================="
echo ""
echo "Backups saved to: $BACKUP_DIR/"
echo ""

if [ "$HOLONIC_OK" = true ] && [ "$DIST_OK" = true ]; then
    echo -e "${GREEN}✅ All fixes applied successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: python main.py --mode health"
    echo "  2. Verify that errors about 'database_only_health' and"
    echo "     'service_dependent_health' are gone"
    echo "  3. Check that healthy services count increased from 11 to 13"
    echo ""
elif [ "$HOLONIC_OK" = true ] || [ "$DIST_OK" = true ]; then
    echo -e "${YELLOW}⚠️  Partial success - some fixes applied${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Check the warnings above"
    echo "  2. Run: python main.py --mode health"
    echo "  3. Review any remaining errors"
    echo ""
else
    echo -e "${RED}❌ Fixes could not be applied${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check that you're in the project root directory"
    echo "  2. Verify the files exist:"
    echo "     ls -l core/holonic/ubec_holonic_evaluator.py"
    echo "     ls -l services/distribution/ubec_distribution_evaluator.py"
    echo "  3. Check file permissions"
    echo ""
fi

echo "======================================================================="
