#!/usr/bin/env python3
"""
Distribution Service - Double Initialization Fix
Fixes line 328 to make initialize() idempotent
"""

import os
import sys
from datetime import datetime

# File path
FILE_PATH = '/home/triag/UBEC/projects/UBEC/services/distribution/distribution_service.py'

print("=" * 70)
print("Distribution Service - Double Initialization Fix")
print("=" * 70)
print()

# Check if file exists
if not os.path.exists(FILE_PATH):
    print(f"✗ Error: File not found: {FILE_PATH}")
    sys.exit(1)

# Create backup
backup_path = f"{FILE_PATH}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"Creating backup: {os.path.basename(backup_path)}")

try:
    with open(FILE_PATH, 'r') as f:
        content = f.read()
    
    with open(backup_path, 'w') as f:
        f.write(content)
    
    print("✓ Backup created")
    print()
except Exception as e:
    print(f"✗ Error creating backup: {e}")
    sys.exit(1)

# Read the file
print("Reading file...")
with open(FILE_PATH, 'r') as f:
    lines = f.readlines()

# Find and fix the line
print("Looking for the error line...")
fixed = False
line_num = None

for i, line in enumerate(lines, 1):
    if 'raise RuntimeError("Service already initialized")' in line:
        line_num = i
        indent = len(line) - len(line.lstrip())
        
        print(f"✓ Found at line {line_num}")
        print()
        print("BEFORE:")
        print(f"  {line.rstrip()}")
        print()
        
        # Replace with idempotent version
        lines[i-1] = ' ' * indent + 'self.logger.debug("Distribution service already initialized, skipping")\n'
        lines.insert(i, ' ' * indent + 'return\n')
        
        print("AFTER:")
        print(f"  {lines[i-1].rstrip()}")
        print(f"  {lines[i].rstrip()}")
        print()
        
        fixed = True
        break

if not fixed:
    print("✗ Error: Could not find the line to fix")
    print()
    print("Expected to find:")
    print('  raise RuntimeError("Service already initialized")')
    print()
    print(f"Backup preserved at: {backup_path}")
    sys.exit(1)

# Write the fixed file
print("Writing fixed file...")
try:
    with open(FILE_PATH, 'w') as f:
        f.writelines(lines)
    
    print("✓ File updated successfully")
    print()
except Exception as e:
    print(f"✗ Error writing file: {e}")
    print()
    print("Restoring from backup...")
    with open(backup_path, 'r') as f:
        content = f.read()
    with open(FILE_PATH, 'w') as f:
        f.write(content)
    print("✓ Backup restored")
    sys.exit(1)

# Success
print("=" * 70)
print("FIX APPLIED SUCCESSFULLY")
print("=" * 70)
print()
print(f"✓ Fixed line {line_num}")
print("✓ Initialize() method is now idempotent")
print(f"✓ Backup saved: {os.path.basename(backup_path)}")
print()
print("Next step: Test the system")
print("  $ python main.py --mode health")
print()
print("Expected result:")
print("  ✓ All services initialized")
print("  ✓ System fully operational")
print()
