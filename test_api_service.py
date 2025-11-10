#!/usr/bin/env python3
"""
UBEC Backend API Service - Comprehensive Test Script
=====================================================
Tests all API endpoints with focus on new v2.2.0 enhancements:
- Token name and total_supply fields
- Holonic reciprocity_health and mutualism_capacity metrics

Design Principles Compliance:
════════════════════════════════════════════════════════════════════════════
    ✅ #5  Strict Async: 100% async/await throughout
    ✅ #11 Comprehensive Documentation: Full docstrings
    ✅ #12 Method Singularity: Each test method implemented once
════════════════════════════════════════════════════════════════════════════

Attribution: This project uses the services of Claude and Anthropic PBC to 
inform our decisions and recommendations. This project was made possible with 
the assistance of Claude and Anthropic PBC.

Usage:
    # Test against local development server
    python test_api_service.py
    
    # Test against specific host/port
    python test_api_service.py --host localhost --port 8000
    
    # Run specific test category
    python test_api_service.py --category tokens
    python test_api_service.py --category holonic
    python test_api_service.py --category all

Author: UBEC Protocol Development Team
Version: 1.0.0
Created: 2025-11-10
"""

import asyncio
import aiohttp
import sys
import argparse
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored output
init(autoreset=True)


class APITester:
    """
    Comprehensive API testing framework for UBEC Backend API.
    
    Tests all endpoints with particular focus on v2.2.0 enhancements:
    - Token name and total_supply validation
    - Holonic reciprocity_health and mutualism_capacity metrics
    
    Attributes:
        base_url: Base URL for API requests
        session: aiohttp ClientSession for requests
        results: Test results tracking
    """
    
    def __init__(self, host: str = "localhost", port: int = 8000):
        """
        Initialize API tester.
        
        Args:
            host: API server hostname
            port: API server port
        """
        self.base_url = f"http://{host}:{port}"
        self.session: Optional[aiohttp.ClientSession] = None
        self.results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    # ========================================================================
    # Test Execution Framework
    # ========================================================================
    
    def log_test_start(self, test_name: str):
        """Log test start."""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST: {test_name}")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}")
    
    def log_success(self, message: str):
        """Log success message."""
        print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")
        self.results['passed'] += 1
    
    def log_failure(self, message: str):
        """Log failure message."""
        print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")
        self.results['failed'] += 1
    
    def log_warning(self, message: str):
        """Log warning message."""
        print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")
        self.results['warnings'] += 1
    
    def log_info(self, message: str):
        """Log informational message."""
        print(f"{Fore.WHITE}  {message}{Style.RESET_ALL}")
    
    async def make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict] = None
    ) -> Tuple[Optional[Dict], Optional[int], Optional[Dict]]:
        """
        Make HTTP request to API endpoint.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            
        Returns:
            Tuple of (response_data, status_code, headers)
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(method, url, params=params) as response:
                headers = dict(response.headers)
                status = response.status
                
                try:
                    data = await response.json()
                except:
                    data = None
                
                return data, status, headers
                
        except aiohttp.ClientConnectorError:
            self.log_failure(f"Cannot connect to API server at {self.base_url}")
            self.log_info("Make sure the API server is running:")
            self.log_info("  uvicorn main:app --host 0.0.0.0 --port 8000")
            return None, None, None
        except Exception as e:
            self.log_failure(f"Request failed: {e}")
            return None, None, None
    
    # ========================================================================
    # Health Check Tests
    # ========================================================================
    
    async def test_health_endpoints(self):
        """Test health check endpoints."""
        self.log_test_start("Health Check Endpoints")
        
        # Test /health endpoint
        data, status, headers = await self.make_request("/health")
        
        if status == 200:
            self.log_success(f"GET /health returned status 200")
            
            if data and data.get('status') == 'healthy':
                self.log_success("Health status is 'healthy'")
            else:
                self.log_failure(f"Unexpected health status: {data.get('status')}")
            
            if data and data.get('version') == '2.2.0':
                self.log_success("API version is 2.2.0")
            else:
                self.log_warning(f"API version is {data.get('version')}, expected 2.2.0")
        else:
            self.log_failure(f"GET /health returned status {status}")
        
        # Test /api/v1/health endpoint
        data, status, headers = await self.make_request("/api/v1/health")
        
        if status == 200:
            self.log_success(f"GET /api/v1/health returned status 200")
        else:
            self.log_failure(f"GET /api/v1/health returned status {status}")
        
        # Check rate limit headers
        if headers:
            if 'X-RateLimit-Limit' in headers:
                self.log_success(f"Rate limit headers present: {headers.get('X-RateLimit-Limit')}/min")
            else:
                self.log_warning("Rate limit headers not present in response")
    
    # ========================================================================
    # Token Endpoint Tests (v2.2.0 Enhanced)
    # ========================================================================
    
    async def test_tokens_endpoint(self):
        """
        Test /api/v1/tokens endpoint with v2.2.0 enhancements.
        
        Validates:
        - Response structure
        - Presence of 'name' field (NEW in v2.2.0)
        - Presence of 'total_supply' field (NEW in v2.2.0)
        - All four element tokens present
        """
        self.log_test_start("Token Information Endpoint (v2.2.0 Enhanced)")
        
        data, status, headers = await self.make_request("/api/v1/tokens")
        
        if not status:
            return
        
        if status == 200:
            self.log_success("GET /api/v1/tokens returned status 200")
        else:
            self.log_failure(f"GET /api/v1/tokens returned status {status}")
            return
        
        # Validate response structure
        if not data:
            self.log_failure("No data returned from tokens endpoint")
            return
        
        if 'tokens' not in data:
            self.log_failure("Response missing 'tokens' field")
            return
        
        tokens = data['tokens']
        self.log_success(f"Response contains {len(tokens)} tokens")
        
        if data.get('count') != len(tokens):
            self.log_warning(f"Count mismatch: count={data.get('count')}, actual={len(tokens)}")
        
        # Validate all four element tokens present
        expected_tokens = ['UBEC', 'UBECrc', 'UBECgpi', 'UBECtt']
        found_tokens = [t.get('asset_code') for t in tokens]
        
        for expected in expected_tokens:
            if expected in found_tokens:
                self.log_success(f"Token {expected} present in response")
            else:
                self.log_failure(f"Token {expected} missing from response")
        
        # Validate v2.2.0 enhancements - NEW FIELDS
        self.log_info("\nValidating v2.2.0 NEW FIELDS:")
        
        for token in tokens:
            asset_code = token.get('asset_code', 'UNKNOWN')
            
            # Validate 'name' field (NEW in v2.2.0)
            if 'name' in token:
                self.log_success(f"{asset_code}: 'name' field present = '{token['name']}'")
                
                if token['name'] and len(token['name']) > 0:
                    self.log_success(f"{asset_code}: 'name' has valid value")
                else:
                    self.log_warning(f"{asset_code}: 'name' is empty")
            else:
                self.log_failure(f"{asset_code}: 'name' field MISSING (required in v2.2.0)")
            
            # Validate 'total_supply' field (NEW in v2.2.0)
            if 'total_supply' in token:
                self.log_success(f"{asset_code}: 'total_supply' field present = {token['total_supply']}")
                
                if isinstance(token['total_supply'], (int, float)):
                    if token['total_supply'] >= 0:
                        self.log_success(f"{asset_code}: 'total_supply' is valid number")
                    else:
                        self.log_warning(f"{asset_code}: 'total_supply' is negative")
                else:
                    self.log_failure(f"{asset_code}: 'total_supply' is not a number")
            else:
                self.log_failure(f"{asset_code}: 'total_supply' field MISSING (required in v2.2.0)")
            
            # Validate other expected fields
            required_fields = ['element', 'ubuntu_principle', 'issuer', 'description']
            for field in required_fields:
                if field in token:
                    self.log_success(f"{asset_code}: '{field}' field present")
                else:
                    self.log_failure(f"{asset_code}: '{field}' field missing")
    
    # ========================================================================
    # Holonic Scores Tests (v2.2.0 Enhanced)
    # ========================================================================
    
    async def test_holonic_scores_endpoint(self):
        """
        Test /api/v1/holonic-scores endpoint with v2.2.0 enhancements.
        
        Validates:
        - Response structure
        - Presence of 'reciprocity_health' (NEW in v2.2.0)
        - Presence of 'mutualism_capacity' (NEW in v2.2.0)
        - Score ranges (0.0-1.0)
        - Ubuntu principles object structure
        """
        self.log_test_start("Holonic Scores Endpoint (v2.2.0 Enhanced)")
        
        # Test basic endpoint
        data, status, headers = await self.make_request("/api/v1/holonic-scores")
        
        if not status:
            return
        
        if status == 200:
            self.log_success("GET /api/v1/holonic-scores returned status 200")
        else:
            self.log_failure(f"GET /api/v1/holonic-scores returned status {status}")
            return
        
        # Validate response structure
        if not data:
            self.log_failure("No data returned from holonic-scores endpoint")
            return
        
        required_top_level = ['summary', 'category_distribution', 'accounts', 'count']
        for field in required_top_level:
            if field in data:
                self.log_success(f"Response contains '{field}' field")
            else:
                self.log_failure(f"Response missing '{field}' field")
        
        # Validate accounts structure
        if 'accounts' not in data or not data['accounts']:
            self.log_warning("No accounts in response - cannot validate v2.2.0 enhancements")
            return
        
        accounts = data['accounts']
        self.log_success(f"Response contains {len(accounts)} accounts")
        
        # Validate v2.2.0 enhancements - NEW UBUNTU PRINCIPLE METRICS
        self.log_info("\nValidating v2.2.0 NEW UBUNTU PRINCIPLE METRICS:")
        
        accounts_tested = 0
        for account in accounts[:5]:  # Test first 5 accounts
            account_id = account.get('account_id', 'UNKNOWN')
            accounts_tested += 1
            
            self.log_info(f"\nAccount {accounts_tested}: {account_id[:10]}...")
            
            # Check for ubuntu_principles object (NEW in v2.2.0)
            if 'ubuntu_principles' in account:
                self.log_success("'ubuntu_principles' object present")
                
                ubuntu = account['ubuntu_principles']
                
                # Validate reciprocity_health (NEW in v2.2.0)
                if 'reciprocity_health' in ubuntu:
                    reciprocity = ubuntu['reciprocity_health']
                    self.log_success(f"'reciprocity_health' present = {reciprocity}")
                    
                    if isinstance(reciprocity, (int, float)):
                        if 0.0 <= reciprocity <= 1.0:
                            self.log_success("'reciprocity_health' in valid range [0.0-1.0]")
                        else:
                            self.log_failure(f"'reciprocity_health' out of range: {reciprocity}")
                    else:
                        self.log_failure(f"'reciprocity_health' is not a number: {type(reciprocity)}")
                else:
                    self.log_failure("'reciprocity_health' MISSING (required in v2.2.0)")
                
                # Validate mutualism_capacity (NEW in v2.2.0)
                if 'mutualism_capacity' in ubuntu:
                    mutualism = ubuntu['mutualism_capacity']
                    self.log_success(f"'mutualism_capacity' present = {mutualism}")
                    
                    if isinstance(mutualism, (int, float)):
                        if 0.0 <= mutualism <= 1.0:
                            self.log_success("'mutualism_capacity' in valid range [0.0-1.0]")
                        else:
                            self.log_failure(f"'mutualism_capacity' out of range: {mutualism}")
                    else:
                        self.log_failure(f"'mutualism_capacity' is not a number: {type(mutualism)}")
                else:
                    self.log_failure("'mutualism_capacity' MISSING (required in v2.2.0)")
            else:
                self.log_failure("'ubuntu_principles' object MISSING (required in v2.2.0)")
            
            # Validate existing score structure still present
            if 'scores' in account:
                self.log_success("'scores' object present")
                
                required_scores = [
                    'autonomy_integration',
                    'multi_scale_participation',
                    'regenerative_impact',
                    'network_contribution',
                    'ubuntu_alignment'
                ]
                
                for score_name in required_scores:
                    if score_name in account['scores']:
                        self.log_success(f"Score '{score_name}' present")
                    else:
                        self.log_failure(f"Score '{score_name}' missing")
            else:
                self.log_failure("'scores' object missing")
        
        # Test with filters
        self.log_info("\nTesting endpoint with filters:")
        
        data, status, headers = await self.make_request(
            "/api/v1/holonic-scores",
            params={'category': 'exemplar', 'limit': 10}
        )
        
        if status == 200:
            self.log_success("Endpoint accepts filter parameters")
            if data and 'filters' in data:
                self.log_success(f"Filters applied: {data['filters']}")
        else:
            self.log_warning(f"Filtered request returned status {status}")
    
    # ========================================================================
    # Network Status Tests
    # ========================================================================
    
    async def test_network_status_endpoint(self):
        """Test /api/v1/network-status endpoint."""
        self.log_test_start("Network Status Endpoint")
        
        data, status, headers = await self.make_request("/api/v1/network-status")
        
        if not status:
            return
        
        if status == 200:
            self.log_success("GET /api/v1/network-status returned status 200")
        else:
            self.log_failure(f"GET /api/v1/network-status returned status {status}")
            return
        
        if not data:
            self.log_failure("No data returned from network-status endpoint")
            return
        
        # Validate required fields
        required_fields = [
            'network_health',
            'total_supply',
            'total_holders',
            'active_bioregions',
            'overall_health_score',
            'transactions_24h'
        ]
        
        for field in required_fields:
            if field in data:
                value = data[field]
                self.log_success(f"Field '{field}' present = {value}")
            else:
                self.log_failure(f"Field '{field}' missing")
    
    # ========================================================================
    # Bioregion Tests
    # ========================================================================
    
    async def test_bioregion_endpoints(self):
        """Test bioregion-related endpoints."""
        self.log_test_start("Bioregion Endpoints")
        
        # Test count endpoint
        data, status, headers = await self.make_request("/api/v1/bioregions/count")
        
        if status == 200:
            self.log_success("GET /api/v1/bioregions/count returned status 200")
            if data and 'count' in data:
                self.log_success(f"Bioregion count: {data['count']}")
        else:
            self.log_failure(f"GET /api/v1/bioregions/count returned status {status}")
        
        # Test list endpoint
        data, status, headers = await self.make_request("/api/v1/bioregions")
        
        if status == 200:
            self.log_success("GET /api/v1/bioregions returned status 200")
            if data and 'bioregions' in data:
                count = len(data['bioregions'])
                self.log_success(f"Retrieved {count} bioregions")
        else:
            self.log_failure(f"GET /api/v1/bioregions returned status {status}")
    
    # ========================================================================
    # Transaction Tests
    # ========================================================================
    
    async def test_transactions_endpoint(self):
        """Test /api/v1/transactions/recent endpoint."""
        self.log_test_start("Recent Transactions Endpoint")
        
        data, status, headers = await self.make_request("/api/v1/transactions/recent")
        
        if not status:
            return
        
        if status == 200:
            self.log_success("GET /api/v1/transactions/recent returned status 200")
        else:
            self.log_failure(f"GET /api/v1/transactions/recent returned status {status}")
            return
        
        if not data:
            self.log_failure("No data returned from transactions endpoint")
            return
        
        required_fields = ['transactions', 'count', 'total', 'pagination']
        for field in required_fields:
            if field in data:
                self.log_success(f"Field '{field}' present")
            else:
                self.log_failure(f"Field '{field}' missing")
        
        # Test with pagination
        data, status, headers = await self.make_request(
            "/api/v1/transactions/recent",
            params={'limit': 5, 'offset': 0}
        )
        
        if status == 200:
            self.log_success("Endpoint accepts pagination parameters")
            if data and data.get('count', 0) <= 5:
                self.log_success("Pagination limit respected")
    
    # ========================================================================
    # Distribution Tests
    # ========================================================================
    
    async def test_distribution_endpoint(self):
        """Test /api/v1/distribution endpoint."""
        self.log_test_start("Distribution Statistics Endpoint")
        
        data, status, headers = await self.make_request("/api/v1/distribution")
        
        if not status:
            return
        
        if status == 200:
            self.log_success("GET /api/v1/distribution returned status 200")
        else:
            self.log_failure(f"GET /api/v1/distribution returned status {status}")
            return
        
        if not data:
            self.log_failure("No data returned from distribution endpoint")
            return
        
        if 'distributions' in data:
            self.log_success("Response contains 'distributions' field")
            
            distributions = data['distributions']
            self.log_success(f"Retrieved distribution stats for {len(distributions)} tokens")
            
            for dist in distributions:
                token = dist.get('token_code', 'UNKNOWN')
                compliance = dist.get('is_compliant', False)
                
                if compliance:
                    self.log_success(f"{token}: Compliant with distribution targets")
                else:
                    self.log_warning(f"{token}: NOT compliant with distribution targets")
        else:
            self.log_failure("Response missing 'distributions' field")
    
    # ========================================================================
    # Rate Limiting Tests
    # ========================================================================
    
    async def test_rate_limiting(self):
        """Test rate limiting functionality."""
        self.log_test_start("Rate Limiting")
        
        self.log_info("Making 10 rapid requests to test rate limiting...")
        
        statuses = []
        for i in range(10):
            data, status, headers = await self.make_request("/api/v1/health")
            statuses.append(status)
            
            if status == 429:
                self.log_success(f"Rate limit triggered on request {i+1}")
                break
        
        if 429 not in statuses:
            self.log_info("Rate limit not triggered in 10 requests (limit may be higher)")
        
        # Check for rate limit headers
        data, status, headers = await self.make_request("/api/v1/health")
        
        if headers:
            rate_headers = [k for k in headers.keys() if 'RateLimit' in k]
            if rate_headers:
                self.log_success(f"Rate limit headers present: {rate_headers}")
            else:
                self.log_warning("Rate limit headers not found")
    
    # ========================================================================
    # Results Summary
    # ========================================================================
    
    def print_summary(self):
        """Print test results summary."""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}TEST RESULTS SUMMARY")
        print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
        
        total = self.results['passed'] + self.results['failed']
        
        print(f"{Fore.GREEN}Passed:   {self.results['passed']}/{total}{Style.RESET_ALL}")
        print(f"{Fore.RED}Failed:   {self.results['failed']}/{total}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Warnings: {self.results['warnings']}{Style.RESET_ALL}\n")
        
        if self.results['failed'] == 0:
            print(f"{Fore.GREEN}✓ ALL TESTS PASSED!{Style.RESET_ALL}\n")
            return 0
        else:
            print(f"{Fore.RED}✗ SOME TESTS FAILED{Style.RESET_ALL}\n")
            return 1


# ============================================================================
# Main Test Runner
# ============================================================================

async def run_all_tests(host: str, port: int, category: str = "all"):
    """
    Run all API tests.
    
    Args:
        host: API server hostname
        port: API server port
        category: Test category to run (all, tokens, holonic, etc.)
    """
    print(f"{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}UBEC Backend API Test Suite v1.0.0")
    print(f"{Fore.CYAN}Testing: {host}:{port}")
    print(f"{Fore.CYAN}Category: {category}")
    print(f"{Fore.CYAN}{'='*70}{Style.RESET_ALL}\n")
    
    async with APITester(host, port) as tester:
        
        if category in ["all", "health"]:
            await tester.test_health_endpoints()
        
        if category in ["all", "tokens"]:
            await tester.test_tokens_endpoint()
        
        if category in ["all", "holonic"]:
            await tester.test_holonic_scores_endpoint()
        
        if category in ["all", "network"]:
            await tester.test_network_status_endpoint()
        
        if category in ["all", "bioregions"]:
            await tester.test_bioregion_endpoints()
        
        if category in ["all", "transactions"]:
            await tester.test_transactions_endpoint()
        
        if category in ["all", "distribution"]:
            await tester.test_distribution_endpoint()
        
        if category in ["all", "ratelimit"]:
            await tester.test_rate_limiting()
        
        return tester.print_summary()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Test UBEC Backend API Service',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_api_service.py
  python test_api_service.py --host localhost --port 8000
  python test_api_service.py --category tokens
  python test_api_service.py --category holonic
        """
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='API server hostname (default: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API server port (default: 8000)'
    )
    
    parser.add_argument(
        '--category',
        choices=['all', 'health', 'tokens', 'holonic', 'network', 'bioregions', 'transactions', 'distribution', 'ratelimit'],
        default='all',
        help='Test category to run (default: all)'
    )
    
    args = parser.parse_args()
    
    try:
        exit_code = asyncio.run(run_all_tests(args.host, args.port, args.category))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Fore.RED}Test suite failed: {e}{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()
