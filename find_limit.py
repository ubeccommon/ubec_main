#!/usr/bin/env python3
"""
UBEC Evaluation Limit Finder
Diagnostic script to locate where the 5-account limit is set
"""

import os
import re
from pathlib import Path

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

def find_in_file(filepath, patterns):
    """Search for patterns in a file and return matches with context."""
    matches = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for i, line in enumerate(lines, 1):
                for pattern_name, pattern in patterns.items():
                    if re.search(pattern, line, re.IGNORECASE):
                        # Get context (3 lines before and after)
                        context_start = max(0, i-4)
                        context_end = min(len(lines), i+3)
                        context = ''.join(lines[context_start:context_end])
                        
                        matches.append({
                            'file': filepath,
                            'line': i,
                            'pattern': pattern_name,
                            'content': line.strip(),
                            'context': context
                        })
    except Exception as e:
        pass  # Skip files that can't be read
    
    return matches

def main():
    print(f"{BOLD}{BLUE}🔍 UBEC Evaluation Limit Diagnostic Tool{RESET}")
    print("=" * 70)
    print()
    
    # Define base path
    base_path = Path.home() / "UBEC" / "projects" / "UBEC"
    
    if not base_path.exists():
        print(f"{RED}❌ Error: UBEC project directory not found at {base_path}{RESET}")
        print(f"{YELLOW}Please update the base_path in this script to match your installation.{RESET}")
        return
    
    print(f"{GREEN}✓ Found project directory: {base_path}{RESET}")
    print()
    
    # Patterns to search for
    patterns = {
        'limit=5': r'limit\s*=\s*5\b',
        'limit = 5': r'limit\s*=\s*5\b',
        'LIMIT 5': r'LIMIT\s+5\b',
        'limit 5': r'limit\s+5\b',
        'evaluate_network(limit': r'evaluate_network\([^)]*limit',
        'load_account_holders(limit': r'load_account_holders\([^)]*limit',
        'min_balance limit pattern': r'min_balance[^,]*,\s*limit',
    }
    
    # Files to search
    search_patterns = [
        'main.py',
        '*cli*.py',
        'core/holonic/*.py',
        'config/*.py',
        'core/**/*.py',
    ]
    
    all_matches = []
    files_checked = 0
    
    print(f"{YELLOW}Scanning files...{RESET}")
    
    for pattern in search_patterns:
        for filepath in base_path.glob(pattern):
            if filepath.is_file() and filepath.suffix == '.py':
                files_checked += 1
                matches = find_in_file(filepath, patterns)
                all_matches.extend(matches)
    
    print(f"{GREEN}✓ Checked {files_checked} Python files{RESET}")
    print()
    
    # Display results
    if all_matches:
        print(f"{RED}{BOLD}🎯 FOUND {len(all_matches)} POTENTIAL LIMIT LOCATIONS:{RESET}")
        print("=" * 70)
        print()
        
        for i, match in enumerate(all_matches, 1):
            rel_path = os.path.relpath(match['file'], base_path)
            print(f"{BOLD}{YELLOW}Match #{i}:{RESET}")
            print(f"{BLUE}File:{RESET} {rel_path}")
            print(f"{BLUE}Line:{RESET} {match['line']}")
            print(f"{BLUE}Pattern:{RESET} {match['pattern']}")
            print(f"{BLUE}Content:{RESET} {GREEN}{match['content']}{RESET}")
            print(f"\n{BLUE}Context:{RESET}")
            print("-" * 70)
            print(match['context'])
            print("=" * 70)
            print()
    else:
        print(f"{YELLOW}⚠️  No explicit limit=5 found in Python files.{RESET}")
        print()
        print(f"{BOLD}Possible reasons:{RESET}")
        print(f"  1. The limit might be set in a configuration file (.env, config.yaml)")
        print(f"  2. The limit might be a default parameter value in a function definition")
        print(f"  3. The limit might be calculated dynamically")
        print()
        
    # Additional checks
    print(f"{BOLD}{BLUE}📝 Additional Checks:{RESET}")
    print("=" * 70)
    
    # Check for default parameter in function definitions
    print(f"\n{YELLOW}Checking function definitions with default limits...{RESET}")
    func_pattern = r'def.*evaluate.*\([^)]*limit\s*=\s*\d+'
    
    func_matches = []
    for pattern in search_patterns:
        for filepath in base_path.glob(pattern):
            if filepath.is_file() and filepath.suffix == '.py':
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        for match in re.finditer(func_pattern, content):
                            func_matches.append({
                                'file': filepath,
                                'content': match.group()
                            })
                except:
                    pass
    
    if func_matches:
        print(f"{RED}Found function definitions with default limits:{RESET}")
        for match in func_matches:
            rel_path = os.path.relpath(match['file'], base_path)
            print(f"  📄 {rel_path}")
            print(f"     {GREEN}{match['content']}{RESET}")
            print()
    
    # Recommendations
    print(f"\n{BOLD}{BLUE}💡 Recommendations:{RESET}")
    print("=" * 70)
    print(f"""
{BOLD}To fix the 5-account limit:{RESET}

1. {GREEN}If a limit was found above:{RESET}
   - Remove the limit parameter entirely, OR
   - Change it to a much higher value (e.g., limit=2000)
   
2. {GREEN}If NO limit was found:{RESET}
   - Check the evaluator's load_account_holders() function
   - Look for default parameter values in function definitions
   - Check if it's using SQL LIMIT in a query
   
3. {GREEN}Recommended change locations:{RESET}
   - main.py: Look for run_evaluation() function
   - core/holonic/ubec_holonic_evaluator.py: Check evaluate_network() 
   - Look for: await evaluator.evaluate_network(limit=5)
   
4. {GREEN}Ideal fix:{RESET}
   - Remove any hardcoded limits
   - Let it evaluate ALL 1,263 available accounts
   - Add a configurable limit via environment variable if needed

{BOLD}Example fix:{RESET}
   {RED}# OLD (limiting to 5):{RESET}
   result = await evaluator.evaluate_network(limit=5)
   
   {GREEN}# NEW (evaluate all):{RESET}
   result = await evaluator.evaluate_network()
   
   {BLUE}# OR (configurable):{RESET}
   limit = int(os.getenv('EVALUATION_LIMIT', 0)) or None
   result = await evaluator.evaluate_network(limit=limit)
""")
    
    print("=" * 70)
    print(f"{BOLD}{GREEN}✅ Diagnostic complete!{RESET}")
    print()

if __name__ == "__main__":
    main()
