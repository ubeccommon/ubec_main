#!/usr/bin/env python3
"""
Find SQL LIMIT clauses in UBEC evaluator
"""

import re
from pathlib import Path

def main():
    evaluator_path = Path.home() / "UBEC" / "projects" / "UBEC" / "core" / "holonic" / "ubec_holonic_evaluator.py"
    
    if not evaluator_path.exists():
        print(f"❌ File not found: {evaluator_path}")
        return
    
    print("🔍 Searching for SQL LIMIT clauses and evaluate_network calls...")
    print("=" * 70)
    print()
    
    with open(evaluator_path, 'r') as f:
        lines = f.readlines()
    
    # Find SQL LIMIT clauses
    print("1️⃣ SQL LIMIT CLAUSES:")
    print("-" * 70)
    for i, line in enumerate(lines, 1):
        if re.search(r'LIMIT\s+\$?\d+', line, re.IGNORECASE) or re.search(r'LIMIT\s+\d+', line, re.IGNORECASE):
            print(f"Line {i}: {line.strip()}")
            # Show context
            context_start = max(0, i-3)
            context_end = min(len(lines), i+2)
            print("Context:")
            for j in range(context_start, context_end):
                prefix = ">>> " if j == i-1 else "    "
                print(f"{prefix}{lines[j].rstrip()}")
            print()
    
    # Find load_account_holders function definition
    print("\n2️⃣ load_account_holders FUNCTION:")
    print("-" * 70)
    in_function = False
    function_lines = []
    brace_count = 0
    
    for i, line in enumerate(lines, 1):
        if 'async def load_account_holders' in line or 'def load_account_holders' in line:
            in_function = True
            function_lines = [(i, line)]
            if ':' in line:
                brace_count = 1
        elif in_function:
            function_lines.append((i, line))
            # Count indentation to know when function ends
            if line.strip() and not line.strip().startswith('#'):
                if line[0] not in (' ', '\t') and len(function_lines) > 10:
                    break
                if len(function_lines) > 100:  # Safety limit
                    break
    
    if function_lines:
        print("Function definition found:")
        for line_num, line in function_lines[:50]:  # Show first 50 lines
            print(f"{line_num:4d}: {line.rstrip()}")
    
    # Find evaluate_network function definition
    print("\n3️⃣ evaluate_network FUNCTION DEFINITION:")
    print("-" * 70)
    for i, line in enumerate(lines, 1):
        if 'async def evaluate_network' in line or 'def evaluate_network' in line:
            # Show function signature and first few lines
            context_start = i
            context_end = min(len(lines), i+20)
            for j in range(context_start-1, context_end):
                print(f"{j+1:4d}: {lines[j].rstrip()}")
            break
    
    # Search main.py for evaluate_network calls
    print("\n4️⃣ SEARCHING main.py:")
    print("-" * 70)
    main_path = Path.home() / "UBEC" / "projects" / "UBEC" / "main.py"
    
    if main_path.exists():
        with open(main_path, 'r') as f:
            main_lines = f.readlines()
        
        for i, line in enumerate(main_lines, 1):
            if 'evaluate_network' in line.lower() or 'run_evaluation' in line.lower():
                print(f"Line {i}: {line.strip()}")
                # Show context
                context_start = max(0, i-3)
                context_end = min(len(main_lines), i+3)
                print("Context:")
                for j in range(context_start, context_end):
                    prefix = ">>> " if j == i-1 else "    "
                    print(f"{prefix}{main_lines[j].rstrip()}")
                print()
    
    print("=" * 70)
    print("✅ Search complete!")
    print()
    print("🎯 KEY THINGS TO CHECK:")
    print("  1. Look for 'LIMIT 5' or 'LIMIT $3' in SQL queries")
    print("  2. Check if load_account_holders has a default limit parameter")
    print("  3. Check if evaluate_network is called with limit=5 in main.py")

if __name__ == "__main__":
    main()
