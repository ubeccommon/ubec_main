#!/usr/bin/env python3
"""
Fix Syntax Error in main.py
============================
Repairs the misplaced status mode handler.

Usage:
    python fix_syntax_error.py
"""

import sys
from pathlib import Path


def fix_syntax_error():
    """Fix the syntax error caused by misplaced elif."""
    
    print("=" * 70)
    print("Fixing Syntax Error in main.py")
    print("=" * 70)
    print()
    
    main_path = Path('main.py')
    
    if not main_path.exists():
        print("❌ main.py not found")
        return 1
    
    # Read file
    with open(main_path, 'r') as f:
        lines = f.readlines()
    
    print(f"File has {len(lines)} lines")
    print()
    
    # Find the problematic line
    problem_line = None
    for i, line in enumerate(lines):
        if "elif args.mode == 'status':" in line and "SyntaxError" not in line:
            problem_line = i
            break
    
    if problem_line is None:
        print("❌ Could not find the problematic line")
        print("   The file may have been modified")
        return 1
    
    print(f"Found problematic elif at line {problem_line + 1}")
    print()
    
    # Show context
    print("Context around the error:")
    start = max(0, problem_line - 3)
    end = min(len(lines), problem_line + 4)
    for i in range(start, end):
        marker = ">>> " if i == problem_line else "    "
        print(f"{marker}{i+1:4d}: {lines[i]}", end='')
    print()
    
    # Check if we're inside a try block
    in_try = False
    try_line = None
    for i in range(problem_line - 1, max(0, problem_line - 50), -1):
        if 'try:' in lines[i] and not lines[i].strip().startswith('#'):
            in_try = True
            try_line = i
            break
        if 'except' in lines[i] or 'finally' in lines[i]:
            in_try = False
            break
    
    if in_try:
        print(f"⚠ The elif is inside a try block (starting at line {try_line + 1})")
        print("   This causes the syntax error")
        print()
    
    # Find the correct insertion point (after try-except-finally block)
    correct_line = None
    
    # Look backwards from problem_line to find where the try block ends
    for i in range(problem_line - 1, max(0, problem_line - 100), -1):
        line = lines[i].strip()
        
        # Look for the end of an except or finally block
        # This would be where we can safely add the elif
        if line and not line.startswith('#'):
            # Check indentation - if this line is at the same level as 'if args.mode'
            # and comes after an except/finally block, it's a good spot
            if 'if args.mode ==' in line:
                # Found the start of mode handling
                # We need to find after the sync mode handling
                for j in range(i, min(len(lines), i + 100)):
                    if "elif args.mode == 'sync':" in lines[j]:
                        # Found sync handler, look for next good insertion point
                        # Skip ahead to find the next elif or else at same indentation
                        sync_indent = len(lines[j]) - len(lines[j].lstrip())
                        for k in range(j + 1, min(len(lines), j + 50)):
                            k_line = lines[k].strip()
                            k_indent = len(lines[k]) - len(lines[k].lstrip())
                            if k_indent == sync_indent and (k_line.startswith('elif') or k_line.startswith('else:')):
                                correct_line = k
                                break
                        break
                break
    
    if correct_line is None:
        print("❌ Could not determine correct insertion point")
        print()
        print("MANUAL FIX REQUIRED:")
        print("1. Restore from backup: cp main.py.status_backup main.py")
        print("2. Open main.py in editor")
        print("3. Find line ~890: elif args.mode == 'sync':")
        print("4. Look for the NEXT elif or else at the SAME indentation")
        print("5. Insert BEFORE that line:")
        print()
        print("            elif args.mode == 'status':")
        print("                result = await run_status()")
        print()
        return 1
    
    print(f"Correct insertion point: line {correct_line + 1}")
    print()
    
    # Remove from wrong location
    print("Removing from wrong location...")
    status_handler_lines = []
    i = problem_line
    while i < len(lines) and (
        "elif args.mode == 'status':" in lines[i] or 
        "result = await run_status()" in lines[i]
    ):
        status_handler_lines.append(lines[i])
        lines.pop(i)
    
    print(f"Removed {len(status_handler_lines)} lines")
    
    # Insert at correct location
    print(f"Inserting at line {correct_line + 1}")
    for j, line in enumerate(status_handler_lines):
        lines.insert(correct_line + j, line)
    
    # Write fixed file
    print()
    print("Writing fixed main.py...")
    with open(main_path, 'w') as f:
        f.writelines(lines)
    
    print("✓ File written")
    print()
    
    # Verify syntax
    print("Verifying syntax...")
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'py_compile', 'main.py'],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✓ Syntax is now valid!")
        print()
        print("=" * 70)
        print("SUCCESS!")
        print("=" * 70)
        print()
        print("Test it: python main.py --mode status")
        return 0
    else:
        print("❌ Syntax still has errors:")
        print(result.stderr)
        print()
        print("Restoring from backup...")
        subprocess.run(['cp', 'main.py.status_backup', 'main.py'])
        print("✓ Restored")
        print()
        print("MANUAL FIX REQUIRED - See instructions above")
        return 1


if __name__ == '__main__':
    sys.exit(fix_syntax_error())
