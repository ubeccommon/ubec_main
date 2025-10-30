#!/bin/bash
# ============================================================================
# UBEC Protocol - Comprehensive Health Check Fixes
# ============================================================================
# Applies all critical fixes identified in health check analysis:
# 1. Fix health check method names in main.py
# 2. Create missing database index
# 
# Attribution:
#     This project uses the services of Claude and Anthropic PBC to inform our
#     decisions and recommendations. This project was made possible with the
#     assistance of Claude and Anthropic PBC.
# ============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "UBEC Protocol - Comprehensive Health Check Fixes"
echo "========================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}✗ Error: main.py not found${NC}"
    echo "  Please run this script from the UBEC protocol root directory"
    exit 1
fi

echo -e "${GREEN}✓ Found main.py${NC}"
echo ""

# ============================================================================
# FIX 1: Health Check System
# ============================================================================

echo "========================================================================"
echo "FIX #1: Health Check System (CRITICAL)"
echo "========================================================================"
echo ""
echo "Issue: main.py checks for 'get_health()' but services implement 'health_check()'"
echo "Impact: NO health checks are actually running"
echo "Fix: Update method names in main.py"
echo ""

read -p "Apply Fix #1? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Applying Fix #1..."
    python3 fix_health_check_system.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Fix #1 applied successfully${NC}"
    else
        echo -e "${RED}✗ Fix #1 failed${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⊘ Skipped Fix #1${NC}"
fi

echo ""

# ============================================================================
# FIX 2: Database Index
# ============================================================================

echo "========================================================================"
echo "FIX #2: Database Performance (HIGH PRIORITY)"
echo "========================================================================"
echo ""
echo "Issue: Missing database index causes 1019ms query time (should be <20ms)"
echo "Impact: System startup 50x slower than specification"
echo "Fix: Create idx_system_settings_key_active index"
echo ""

read -p "Apply Fix #2? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Applying Fix #2..."
    
    # Check if database credentials are available
    if [ -z "$PGUSER" ]; then
        echo "Database user not set in environment"
        read -p "Enter database user (default: ubec_app): " db_user
        db_user=${db_user:-ubec_app}
    else
        db_user=$PGUSER
    fi
    
    if [ -z "$PGDATABASE" ]; then
        echo "Database name not set in environment"
        read -p "Enter database name (default: ubec): " db_name
        db_name=${db_name:-ubec}
    else
        db_name=$PGDATABASE
    fi
    
    echo ""
    echo "Executing SQL fix..."
    psql -U "$db_user" -d "$db_name" -f fix_database_index.sql
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Fix #2 applied successfully${NC}"
    else
        echo -e "${RED}✗ Fix #2 failed${NC}"
        echo "  You may need to manually execute: psql -U $db_user -d $db_name -f fix_database_index.sql"
    fi
else
    echo -e "${YELLOW}⊘ Skipped Fix #2${NC}"
fi

echo ""

# ============================================================================
# VERIFICATION
# ============================================================================

echo "========================================================================"
echo "VERIFICATION"
echo "========================================================================"
echo ""

read -p "Run health check to verify fixes? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running health check..."
    echo ""
    python3 main.py --mode health --log-level INFO
    
    echo ""
    echo "========================================================================"
    echo "VERIFICATION CHECKLIST"
    echo "========================================================================"
    echo ""
    echo "✓ Check that services show detailed health info, NOT:"
    echo "  \"Health check not implemented\""
    echo ""
    echo "✓ Check for NO warnings about \"Query time exceeds 20ms\""
    echo ""
    echo "✓ Check that rate_limiter initialization is < 50ms"
    echo ""
    echo "✓ Check that total system initialization is < 800ms"
    echo ""
else
    echo -e "${YELLOW}⊘ Skipped verification${NC}"
    echo ""
    echo "To verify manually, run:"
    echo "  python main.py --mode health --log-level INFO"
fi

echo ""
echo "========================================================================"
echo "SUMMARY"
echo "========================================================================"
echo ""
echo "Fixes Applied:"
echo "  - Fix #1: Health check method names"
echo "  - Fix #2: Database index creation"
echo ""
echo "Expected Results:"
echo "  - All services show detailed health information"
echo "  - Rate limiter initialization < 50ms (was 1019ms)"
echo "  - Total startup time < 800ms (was 1677ms)"
echo "  - No 'Health check not implemented' messages"
echo "  - No 'Query time exceeds threshold' warnings"
echo ""
echo "If issues persist, review:"
echo "  - HEALTH_CHECK_CRITICAL_FIXES.md (detailed analysis)"
echo "  - logs/ubec_main.log (system logs)"
echo "  - Backup files created during fix process"
echo ""
echo "========================================================================"
