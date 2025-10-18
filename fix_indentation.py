#!/usr/bin/env python3
"""
Fix Status Mode Indentation
============================
Properly adds status mode with correct indentation.

Usage: python fix_indentation.py
"""

import sys
from pathlib import Path

def fix_status_mode():
    """Fix the status mode handler with proper indentation."""
    
    print("Fixing status mode in main.py...")
    
    # Read the file
    main_path = Path('main.py')
    if not main_path.exists():
        print("❌ main.py not found")
        return 1
    
    with open(main_path, 'r') as f:
        lines = f.readlines()
    
    # Find the line with sync mode
    sync_line = None
    for i, line in enumerate(lines):
        if "elif args.mode == 'sync':" in line:
            sync_line = i
            break
    
    if sync_line is None:
        print("❌ Could not find 'elif args.mode == 'sync':' line")
        return 1
    
    print(f"Found sync mode at line {sync_line + 1}")
    
    # Get the indentation from the sync line
    indent = len(lines[sync_line]) - len(lines[sync_line].lstrip())
    indent_str = ' ' * indent
    
    print(f"Indentation: {indent} spaces")
    
    # Find where to insert (after the result = line following sync)
    insert_line = sync_line + 1
    while insert_line < len(lines) and 'result = await run_sync' not in lines[insert_line]:
        insert_line += 1
    
    if insert_line >= len(lines):
        print("❌ Could not find insertion point")
        return 1
    
    # Move to after that line
    insert_line += 1
    
    # Skip any empty lines
    while insert_line < len(lines) and lines[insert_line].strip() == '':
        insert_line += 1
    
    print(f"Will insert at line {insert_line + 1}")
    
    # Check if status mode already exists
    for i in range(max(0, insert_line - 5), min(len(lines), insert_line + 10)):
        if "args.mode == 'status'" in lines[i]:
            print("⚠ Status mode already exists, removing old version...")
            # Remove it
            if i < len(lines):
                lines.pop(i)
                if i < len(lines) and 'result = await run_status()' in lines[i]:
                    lines.pop(i)
            break
    
    # Create the new lines with proper indentation
    new_lines = [
        f"{indent_str}elif args.mode == 'status':\n",
        f"{indent_str}    result = await run_status()\n",
        f"\n"
    ]
    
    # Insert the lines
    for i, new_line in enumerate(new_lines):
        lines.insert(insert_line + i, new_line)
    
    # Write the file
    with open(main_path, 'w') as f:
        f.writelines(lines)
    
    print("✓ Status mode added")
    
    # Verify syntax
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'main.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Syntax is valid!")
        print()
        print("=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print()
        print("Test it: python main.py --mode status")
        return 0
    else:
        print("❌ Syntax error:")
        print(result.stderr)
        print()
        print("Restoring from backup...")
        subprocess.run(['cp', 'main.py.status_backup', 'main.py'])
        print("✓ Restored")
        return 1

if __name__ == '__main__':
    sys.exit(fix_status_mode())
