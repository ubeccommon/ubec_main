#!/bin/bash
# Fix UBECtt Protocol Cursor Issue
# This script will fix line 1030 in UBECtt/UBECtt_protocol.py

echo "🔧 Fixing UBECtt Protocol cursor issue..."

# Backup the file first
cp UBECtt/UBECtt_protocol.py UBECtt/UBECtt_protocol.py.backup
echo "✓ Backup created: UBECtt/UBECtt_protocol.py.backup"

# Show the problematic section
echo ""
echo "Current code around line 1030:"
sed -n '1025,1040p' UBECtt/UBECtt_protocol.py

echo ""
echo "=========================================="
echo "MANUAL FIX REQUIRED"
echo "=========================================="
echo ""
echo "Open UBECtt/UBECtt_protocol.py and find line 1030."
echo ""
echo "It probably looks like this:"
echo ""
echo "  cursor = self.db.cursor()  # ❌ WRONG"
echo "  cursor.execute(query)"
echo "  results = cursor.fetchall()"
echo ""
echo "Replace it with:"
echo ""
echo "  results = self.db.execute_query(query, fetch_all=True)  # ✅ RIGHT"
echo ""
echo "=========================================="
echo ""
echo "After fixing, run: python main.py sync"
