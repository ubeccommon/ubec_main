"""
UBECtt Token Verification Script
Verifies that your UBECtt token is set up correctly

This script checks:
1. Issuer account exists and is funded
2. Distributor account exists and is funded
3. Trustline exists from distributor to issuer
4. Tokens have been issued
5. Authorization flags (if set)
6. Multi-signature configuration (if set)
"""

from stellar_sdk import Server, Asset
import json

# Your token configuration
TOKEN_CODE = "UBECtt"
ISSUER_PUBLIC = "GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC"
DISTRIBUTOR_PUBLIC = "GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC"
HORIZON_URL = "https://horizon.stellar.org"

def check_mark(condition):
    """Return check or X mark based on condition"""
    return "✓" if condition else "✗"

def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def check_account(server, public_key, account_name):
    """Check account status"""
    try:
        account = server.accounts().account_id(public_key).call()
        
        print(f"\n{check_mark(True)} {account_name} Account")
        print(f"  Address: {public_key}")
        
        # Get XLM balance
        for balance in account['balances']:
            if balance['asset_type'] == 'native':
                xlm_balance = float(balance['balance'])
                print(f"  XLM Balance: {xlm_balance}")
                
                if xlm_balance < 2.0:
                    print(f"  ⚠️  Low balance! Recommended: 3+ XLM")
        
        return account
        
    except Exception as e:
        print(f"\n{check_mark(False)} {account_name} Account")
        print(f"  Error: {e}")
        return None

def check_trustline(server, distributor_account):
    """Check if trustline exists"""
    print_section("2. Trustline Check")
    
    try:
        found_trustline = False
        ubectt_balance = 0
        
        for balance in distributor_account['balances']:
            if (balance.get('asset_code') == TOKEN_CODE and 
                balance.get('asset_issuer') == ISSUER_PUBLIC):
                found_trustline = True
                ubectt_balance = float(balance['balance'])
                break
        
        if found_trustline:
            print(f"\n{check_mark(True)} Trustline exists")
            print(f"  From: {DISTRIBUTOR_PUBLIC}")
            print(f"  To:   {ISSUER_PUBLIC}")
            print(f"  Token: {TOKEN_CODE}")
            print(f"  Balance: {ubectt_balance} {TOKEN_CODE}")
            
            if ubectt_balance > 0:
                print(f"\n{check_mark(True)} Tokens issued successfully!")
            else:
                print(f"\n{check_mark(False)} No tokens in distributor account yet")
                print(f"  Run the setup script to issue tokens")
        else:
            print(f"\n{check_mark(False)} Trustline not found")
            print(f"  Run the setup script to create trustline")
        
        return found_trustline, ubectt_balance
        
    except Exception as e:
        print(f"\n{check_mark(False)} Error checking trustline: {e}")
        return False, 0

def check_authorization_flags(server, issuer_account):
    """Check authorization flags on issuer account"""
    print_section("3. Authorization Flags")
    
    try:
        flags = issuer_account.get('flags', {})
        
        auth_required = flags.get('auth_required', False)
        auth_revocable = flags.get('auth_revocable', False)
        auth_immutable = flags.get('auth_immutable', False)
        
        print(f"\n  {check_mark(auth_required)} AUTHORIZATION_REQUIRED")
        if auth_required:
            print(f"      Accounts need approval to hold {TOKEN_CODE}")
        else:
            print(f"      Anyone can hold {TOKEN_CODE} (not recommended)")
        
        print(f"\n  {check_mark(auth_revocable)} AUTHORIZATION_REVOCABLE")
        if auth_revocable:
            print(f"      Can revoke authorization if needed")
        else:
            print(f"      Cannot revoke once granted")
        
        print(f"\n  {check_mark(auth_immutable)} AUTHORIZATION_IMMUTABLE")
        if auth_immutable:
            print(f"      Flags cannot be changed (locked)")
        else:
            print(f"      Flags can still be modified")
        
        if auth_required and auth_revocable and auth_immutable:
            print(f"\n✅ Recommended configuration active!")
        elif not any([auth_required, auth_revocable, auth_immutable]):
            print(f"\n⚠️  No authorization flags set")
            print(f"   Consider setting them for better control")
        else:
            print(f"\n⚠️  Partial configuration")
            print(f"   Recommended: All three flags enabled")
        
        return auth_required, auth_revocable, auth_immutable
        
    except Exception as e:
        print(f"\n{check_mark(False)} Error checking flags: {e}")
        return False, False, False

def check_multisig(server, distributor_account):
    """Check multi-signature configuration"""
    print_section("4. Multi-Signature Configuration")
    
    try:
        signers = distributor_account.get('signers', [])
        thresholds = distributor_account.get('thresholds', {})
        
        low = thresholds.get('low_threshold', 0)
        med = thresholds.get('med_threshold', 0)
        high = thresholds.get('high_threshold', 0)
        
        print(f"\n  Number of signers: {len(signers)}")
        print(f"\n  Signature Thresholds:")
        print(f"    Low:    {low} (payments, trustlines)")
        print(f"    Medium: {med} (offers, data)")
        print(f"    High:   {high} (account settings)")
        
        if len(signers) > 1:
            print(f"\n{check_mark(True)} Multi-signature is configured!")
            print(f"\n  Signers:")
            for i, signer in enumerate(signers, 1):
                pub_key = signer.get('key', '')
                weight = signer.get('weight', 0)
                signer_type = signer.get('type', '')
                
                if signer_type == 'ed25519_public_key':
                    if pub_key == DISTRIBUTOR_PUBLIC:
                        print(f"    {i}. Master Key (weight: {weight})")
                    else:
                        print(f"    {i}. {pub_key[:10]}... (weight: {weight})")
            
            # Determine configuration
            if len(signers) == 3 and med == 2:
                print(f"\n  Configuration: 2-of-3 (small community)")
            elif len(signers) == 5 and med == 3:
                print(f"\n  Configuration: 3-of-5 (medium community)")
            elif len(signers) == 7 and med == 5:
                print(f"\n  Configuration: 5-of-7 (large community)")
            else:
                print(f"\n  Configuration: {med}-of-{len(signers)} (custom)")
        else:
            print(f"\n{check_mark(False)} Multi-signature not configured")
            print(f"  Single-signature account (only master key)")
            print(f"  Consider setting up multi-sig for governance")
        
        return len(signers), med
        
    except Exception as e:
        print(f"\n{check_mark(False)} Error checking multi-sig: {e}")
        return 0, 0

def check_token_holders(server):
    """Check who holds the token"""
    print_section("5. Token Holders")
    
    try:
        # Query assets for this token
        assets = server.assets().for_code(TOKEN_CODE).for_issuer(ISSUER_PUBLIC).call()
        
        if assets['_embedded']['records']:
            asset_info = assets['_embedded']['records'][0]
            num_accounts = int(asset_info.get('num_accounts', 0))
            total_amount = float(asset_info.get('amount', 0))
            
            print(f"\n  {check_mark(True)} Token is active")
            print(f"  Total accounts holding {TOKEN_CODE}: {num_accounts}")
            print(f"  Total amount in circulation: {total_amount} {TOKEN_CODE}")
            
            if num_accounts == 1:
                print(f"\n  ℹ️  Only distributor holds tokens (expected at start)")
            else:
                print(f"\n  {check_mark(True)} Tokens have been distributed!")
                print(f"  Communities or accounts: {num_accounts - 1}")
        else:
            print(f"\n  {check_mark(False)} Token not found in network")
            print(f"  This might be a new token with no issuance yet")
        
    except Exception as e:
        print(f"\n  ℹ️  Cannot query token statistics: {e}")

def generate_summary_report():
    """Generate a summary report"""
    print_section("Summary Report")
    
    server = Server(horizon_url=HORIZON_URL)
    
    print("\nToken Configuration:")
    print(f"  Token Code:      {TOKEN_CODE}")
    print(f"  Issuer:          {ISSUER_PUBLIC}")
    print(f"  Distributor:     {DISTRIBUTOR_PUBLIC}")
    print(f"  Network:         Stellar Public (MAINNET)")
    
    # Check accounts
    print_section("1. Account Status")
    issuer_account = check_account(server, ISSUER_PUBLIC, "Issuer")
    distributor_account = check_account(server, DISTRIBUTOR_PUBLIC, "Distributor")
    
    if not issuer_account or not distributor_account:
        print("\n❌ Cannot proceed with verification - accounts not found")
        print("   Make sure both accounts are funded with XLM")
        return False
    
    # Check trustline and tokens
    trustline_exists, token_balance = check_trustline(server, distributor_account)
    
    # Check authorization flags
    auth_flags = check_authorization_flags(server, issuer_account)
    
    # Check multi-signature
    num_signers, threshold = check_multisig(server, distributor_account)
    
    # Check token holders
    check_token_holders(server)
    
    # Overall assessment
    print_section("Overall Assessment")
    
    checks = {
        "Issuer account exists": issuer_account is not None,
        "Distributor account exists": distributor_account is not None,
        "Trustline created": trustline_exists,
        "Tokens issued": token_balance > 0,
        "Authorization flags set": all(auth_flags),
        "Multi-signature configured": num_signers > 1
    }
    
    print()
    for check, status in checks.items():
        print(f"  {check_mark(status)} {check}")
    
    required_checks = ["Issuer account exists", "Distributor account exists", 
                      "Trustline created", "Tokens issued"]
    optional_checks = ["Authorization flags set", "Multi-signature configured"]
    
    required_passed = all(checks[check] for check in required_checks)
    optional_passed = all(checks[check] for check in optional_checks)
    
    print("\n" + "=" * 70)
    if required_passed and optional_passed:
        print("🎉 PERFECT! All checks passed!")
        print("   Your UBECtt token is fully configured and ready!")
    elif required_passed:
        print("✅ GOOD! Core setup complete!")
        print("   Consider setting optional features:")
        if not checks["Authorization flags set"]:
            print("   • Authorization flags for better control")
        if not checks["Multi-signature configured"]:
            print("   • Multi-signature for governance")
    else:
        print("⚠️  INCOMPLETE SETUP")
        print("   Please complete the following:")
        for check in required_checks:
            if not checks[check]:
                print(f"   • {check}")
    print("=" * 70)
    
    # Next steps
    print("\nNext Steps:")
    if not required_passed:
        print("  1. Run setup_ubectt_token.py to complete core setup")
        print("  2. Run this verification script again")
    else:
        print("  1. Document all configuration details")
        print("  2. Backup all secret keys securely")
        print("  3. Train Keepers on procedures")
        print("  4. Identify pilot communities")
        print("  5. Begin allocation process")
    
    print("\nResources:")
    print(f"  • Token on Explorer: https://stellar.expert/explorer/public/asset/{TOKEN_CODE}-{ISSUER_PUBLIC}")
    print(f"  • Issuer Account: https://stellar.expert/explorer/public/account/{ISSUER_PUBLIC}")
    print(f"  • Distributor Account: https://stellar.expert/explorer/public/account/{DISTRIBUTOR_PUBLIC}")
    print(f"  • Setup Guide: SETUP_GUIDE_FOR_YOUR_TOKEN.md")
    print(f"  • Full Specs: UBECtt_Token_Creation_Specifications.md")
    
    print("\n" + "=" * 70)
    print("Verification Complete")
    print("=" * 70)
    print()
    
    return required_passed

def main():
    """Main verification process"""
    print("=" * 70)
    print("UBECtt Token Verification")
    print("Transform Token (Fire Element) 🜂")
    print("=" * 70)
    print("\nThis script will verify your UBECtt token configuration.")
    print("No secret keys needed - this is read-only verification.")
    print()
    
    input("Press Enter to begin verification...")
    
    try:
        success = generate_summary_report()
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ Verification failed with error:")
        print(f"   {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
