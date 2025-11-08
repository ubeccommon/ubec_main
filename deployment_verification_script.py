#!/usr/bin/env python3
"""
Simple Health Check Script for UBEC Protocol Suite

This script runs the built-in health check and reports the results.
It's simpler and more reliable than recreating the service registry.

Usage:
    python simple_health_check.py
"""

import subprocess
import sys
from datetime import datetime

def main():
    print("=" * 70)
    print("UBEC DEPLOYMENT VERIFICATION")
    print("=" * 70)
    print(f"Verification Time: {datetime.now().isoformat()}")
    print()
    print("Running built-in health check...")
    print()
    
    try:
        # Run main.py health command
        result = subprocess.run(
            [sys.executable, "main.py", "health"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Print the output
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print()
        print("=" * 70)
        
        # Check for success indicators
        if result.returncode == 0:
            # Look for healthy services in output
            healthy_count = result.stdout.count("healthy")
            unhealthy_count = result.stdout.count("unhealthy")
            
            if "ALL SYSTEMS OPERATIONAL" in result.stdout or "ALL SYSTEMS HEALTHY" in result.stdout:
                print("✅ VERIFICATION PASSED")
                print()
                print("All critical services are operational.")
                return 0
            elif healthy_count > 0 and unhealthy_count == 0:
                print("✅ VERIFICATION PASSED")
                print()
                print(f"Found {healthy_count} healthy services, 0 unhealthy.")
                return 0
            else:
                print("⚠️ VERIFICATION COMPLETED WITH WARNINGS")
                print()
                print("Some services may not be healthy. Review output above.")
                return 1
        else:
            print("❌ VERIFICATION FAILED")
            print()
            print(f"Health check exited with code {result.returncode}")
            return 1
            
    except subprocess.TimeoutExpired:
        print("❌ VERIFICATION FAILED")
        print()
        print("Health check timed out after 60 seconds.")
        return 1
    except FileNotFoundError:
        print("❌ VERIFICATION FAILED")
        print()
        print("Could not find main.py. Are you in the correct directory?")
        print("Expected: ~/UBEC/projects/UBEC")
        return 1
    except Exception as e:
        print("❌ VERIFICATION FAILED")
        print()
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
