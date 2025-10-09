"""
Add Multi-Signature to UBECtt Distributor Account
Ubuntu Bioregional Economic Commons - Transform Token (Fire Element)

This script adds multi-signature governance to your existing distributor account.
Use this AFTER you've completed the initial token setup and are ready to
implement the "Keeper of the Fire" governance model.

Your Configuration:
    Distributor: GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC
    Network: Stellar Public (MAINNET)

Requirements:
    pip install stellar-sdk

IMPORTANT: This is a ONE-WAY operation!
Once multi-sig is set up, you'll need multiple signatures for all operations.
Make sure you have all Keeper information ready before proceeding.
"""

from stellar_sdk import Keypair, Network, Server, TransactionBuilder
from stellar_sdk.operation import SetOptions
from stellar_sdk.exceptions import BadRequestError
import sys

# Your UBECtt Configuration
DISTRIBUTOR_PUBLIC = "GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC"
HORIZON_URL = "https://horizon.stellar.org"
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE

# Common multi-sig configurations
PRESET_CONFIGS = {
    "1": {
        "name": "2-of-3 (Small Community)",
        "description": "3 total Keepers, any 2 must approve operations",
        "total_signers": 3,
        "threshold": 2,
        "recommended_for": "Communities managing <100 hectares (1,000 UBECtt)"
    },
    "2": {
        "name": "3-of-5 (Medium Community)",
        "description": "5 total Keepers, any 3 must approve operations",
        "total_signers": 5,
        "threshold": 3,
        "recommended_for": "Communities managing 100-1000 hectares (1,000-10,000 UBECtt)"
    },
    "3": {
        "name": "5-of-7 (Large Community)",
        "description": "7 total Keepers, any 5 must approve operations",
        "total_signers": 7,
        "threshold": 5,
        "recommended_for": "Communities managing >1000 hectares (>10,000 UBECtt)"
    },
    "4": {
        "name": "Custom Configuration",
        "description": "Define your own signer count and threshold",
        "total_signers": None,
        "threshold": None,
        "recommended_for": "Advanced users with specific governance needs"
    }
}

def print_header():
    """Print script header"""
    print("=" * 70)
    print("UBECtt Multi-Signature Setup")
    print("Transform Token (Fire Element) 🜂")
    print("=" * 70)
    print("\nThis script will add multi-signature governance to your distributor account.")
    print("This implements the 'Keeper of the Fire' governance model.")
    print()
    print(f"Distributor Account: {DISTRIBUTOR_PUBLIC}")
    print(f"Network: Stellar Public (MAINNET)")
    print()

def print_warning():
    """Print important warnings"""
    print("⚠️  CRITICAL WARNINGS:")
    print("=" * 70)
    print("1. This is a ONE-WAY operation - cannot easily undo")
    print("2. After setup, you'll need MULTIPLE signatures for ALL operations")
    print("3. If you lose Keeper keys, you may lose access to the account")
    print("4. Make sure ALL Keepers understand their responsibilities")
    print("5. Test the process on testnet first if unsure")
    print("6. Have emergency recovery procedures documented")
    print("=" * 70)
    print()

def check_current_account(server):
    """Check current account status"""
    print("Checking current account status...")
    print()
    
    try:
        account = server.accounts().account_id(DISTRIBUTOR_PUBLIC).call()
        
        current_signers = account.get('signers', [])
        thresholds = account.get('thresholds', {})
        
        print("✓ Distributor account found")
        print(f"\nCurrent Configuration:")
        print(f"  Signers: {len(current_signers)}")
        print(f"  Thresholds: Low={thresholds.get('low_threshold', 0)}, "
              f"Med={thresholds.get('med_threshold', 0)}, "
              f"High={thresholds.get('high_threshold', 0)}")
        
        # Check for XLM balance
        for balance in account['balances']:
            if balance['asset_type'] == 'native':
                xlm = float(balance['balance'])
                print(f"  XLM Balance: {xlm}")
                
                if xlm < 2.0:
                    print(f"\n⚠️  WARNING: Low XLM balance!")
                    print(f"  You need at least 2 XLM for operations")
                    print(f"  Each signer requires 0.5 XLM reserve")
                    return None
        
        # Check if already multi-sig
        if len(current_signers) > 1:
            print(f"\n⚠️  This account already has {len(current_signers)} signers!")
            print(f"  Current signers:")
            for i, signer in enumerate(current_signers, 1):
                key = signer.get('key', '')
                weight = signer.get('weight', 0)
                if key == DISTRIBUTOR_PUBLIC:
                    print(f"    {i}. Master Key (weight: {weight})")
                else:
                    print(f"    {i}. {key} (weight: {weight})")
            print()
            
            proceed = input("Do you want to ADD MORE signers or MODIFY thresholds? (yes/no): ").strip().lower()
            if proceed != 'yes':
                return None
        
        print()
        return account
        
    except Exception as e:
        print(f"✗ Error checking account: {e}")
        return None

def display_preset_configs():
    """Display preset multi-sig configurations"""
    print("\nSelect a multi-signature configuration:")
    print("=" * 70)
    
    for key, config in PRESET_CONFIGS.items():
        print(f"\n{key}. {config['name']}")
        print(f"   {config['description']}")
        print(f"   Recommended for: {config['recommended_for']}")
    
    print("\n" + "=" * 70)

def get_configuration():
    """Get multi-sig configuration from user"""
    display_preset_configs()
    
    choice = input("\nSelect configuration (1-4): ").strip()
    
    if choice not in PRESET_CONFIGS:
        print("Invalid choice!")
        return None, None
    
    config = PRESET_CONFIGS[choice]
    
    if choice == "4":  # Custom
        print("\nCustom Configuration:")
        try:
            total = int(input("Total number of signers (including current account): "))
            threshold = int(input("Required signatures for operations: "))
            
            if threshold > total:
                print("Error: Required signatures cannot exceed total signers!")
                return None, None
            
            if threshold < 2:
                print("Error: Multi-sig requires at least 2 signatures!")
                return None, None
                
            return total, threshold
            
        except ValueError:
            print("Invalid numbers entered!")
            return None, None
    else:
        return config['total_signers'], config['threshold']

def get_keeper_keys(num_additional_keepers):
    """Get public keys for additional Keepers"""
    print(f"\nEnter public keys for {num_additional_keepers} additional Keeper(s):")
    print("(The current distributor account is already Keeper #1)")
    print()
    
    keepers = []
    for i in range(num_additional_keepers):
        while True:
            print(f"\nKeeper #{i+2}:")
            pub_key = input("  Public key (starts with 'G'): ").strip()
            
            # Validate format
            if len(pub_key) != 56 or not pub_key.startswith('G'):
                print("  ✗ Invalid public key format!")
                retry = input("  Try again? (yes/no): ").strip().lower()
                if retry != 'yes':
                    return None
                continue
            
            # Check if duplicate
            if pub_key == DISTRIBUTOR_PUBLIC:
                print("  ✗ This is the distributor account (already Keeper #1)!")
                continue
            
            if pub_key in keepers:
                print("  ✗ This key was already entered!")
                continue
            
            # Optional: Name for this Keeper
            name = input("  Keeper name/role (optional): ").strip() or f"Keeper {i+2}"
            
            keepers.append({
                'public_key': pub_key,
                'name': name,
                'weight': 1
            })
            print(f"  ✓ Added: {name}")
            break
    
    return keepers

def confirm_configuration(total_signers, threshold, keepers):
    """Display configuration and get confirmation"""
    print("\n" + "=" * 70)
    print("Multi-Signature Configuration Summary")
    print("=" * 70)
    
    print(f"\nConfiguration: {threshold}-of-{total_signers}")
    print(f"Required signatures for operations: {threshold}")
    print()
    
    print("Keepers:")
    print(f"  1. Master Key (current distributor)")
    print(f"     {DISTRIBUTOR_PUBLIC}")
    print(f"     Weight: 1")
    
    for i, keeper in enumerate(keepers, 2):
        print(f"\n  {i}. {keeper['name']}")
        print(f"     {keeper['public_key']}")
        print(f"     Weight: {keeper['weight']}")
    
    print(f"\nThresholds (will be set to {threshold}):")
    print(f"  • Low Threshold:    {threshold} (payments, trustlines)")
    print(f"  • Medium Threshold: {threshold} (offers, data entries)")
    print(f"  • High Threshold:   {threshold} (account settings, signers)")
    
    print("\n" + "=" * 70)
    print("Impact:")
    print("=" * 70)
    print(f"• ALL operations will require {threshold} signatures")
    print(f"• You'll need to coordinate with {threshold-1} other Keeper(s)")
    print(f"• Single Keeper can no longer act alone")
    print(f"• Enhanced security and accountability")
    print(f"• Implements 'Keeper of the Fire' governance")
    print("=" * 70)
    print()
    
    print("⚠️  FINAL WARNING:")
    print(f"    After this, you need {threshold} Keepers to sign ALL operations!")
    print(f"    Make sure ALL Keepers:")
    print(f"      • Have their secret keys secured")
    print(f"      • Understand their responsibilities")
    print(f"      • Have tested the signing process")
    print(f"      • Are committed to the community")
    print()
    
    confirm = input("Proceed with this configuration? Type 'YES' in all caps to confirm: ").strip()
    return confirm == "YES"

def setup_multisig(server, distributor_secret, keepers, threshold):
    """Execute multi-sig setup"""
    print("\n" + "=" * 70)
    print("Setting Up Multi-Signature...")
    print("=" * 70)
    
    try:
        distributor_keypair = Keypair.from_secret(distributor_secret)
        
        # Verify secret key matches public key
        if distributor_keypair.public_key != DISTRIBUTOR_PUBLIC:
            print("\n✗ Secret key doesn't match distributor public key!")
            return False
        
        # Load account
        account = server.load_account(DISTRIBUTOR_PUBLIC)
        
        # Build transaction with multiple operations
        print("\nBuilding transaction...")
        
        # Calculate fee (100 stroops per operation)
        num_operations = len(keepers) + 1  # +1 for threshold operation
        base_fee = 100
        
        transaction_builder = TransactionBuilder(
            source_account=account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=base_fee,
        )
        
        # Add each Keeper as a signer
        print(f"\nAdding {len(keepers)} Keeper(s)...")
        for i, keeper in enumerate(keepers, 1):
            print(f"  • Adding Keeper {i+1}: {keeper['name']}")
            transaction_builder.append_set_options_op(
                signer={
                    "ed25519_public_key": keeper['public_key'],
                    "weight": keeper['weight']
                }
            )
        
        # Set thresholds
        print(f"\nSetting thresholds to {threshold}...")
        transaction_builder.append_set_options_op(
            master_weight=1,  # Keep master key weight at 1
            low_threshold=threshold,
            med_threshold=threshold,
            high_threshold=threshold,
        )
        
        # Build, sign, and submit
        print("\nBuilding and signing transaction...")
        transaction = transaction_builder.set_timeout(30).build()
        transaction.sign(distributor_keypair)
        
        print("Submitting to Stellar network...")
        response = server.submit_transaction(transaction)
        
        print("\n" + "=" * 70)
        print("✅ Multi-Signature Setup Complete!")
        print("=" * 70)
        
        tx_hash = response['hash']
        print(f"\nTransaction Hash: {tx_hash}")
        print(f"\nView on Stellar Expert:")
        print(f"https://stellar.expert/explorer/public/tx/{tx_hash}")
        
        print(f"\nYour account now requires {threshold} signatures for all operations!")
        
        return True
        
    except BadRequestError as e:
        print(f"\n✗ Transaction failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False

def verify_setup(server, threshold):
    """Verify multi-sig was set up correctly"""
    print("\n" + "=" * 70)
    print("Verifying Setup...")
    print("=" * 70)
    
    try:
        account = server.accounts().account_id(DISTRIBUTOR_PUBLIC).call()
        
        signers = account.get('signers', [])
        thresholds = account.get('thresholds', {})
        
        print(f"\n✓ Account configuration updated")
        print(f"\nNew Configuration:")
        print(f"  Total Signers: {len(signers)}")
        print(f"  Thresholds: Low={thresholds.get('low_threshold')}, "
              f"Med={thresholds.get('med_threshold')}, "
              f"High={thresholds.get('high_threshold')}")
        
        print(f"\n  Signers:")
        for i, signer in enumerate(signers, 1):
            key = signer.get('key', '')
            weight = signer.get('weight', 0)
            if key == DISTRIBUTOR_PUBLIC:
                print(f"    {i}. Master Key (weight: {weight})")
            else:
                print(f"    {i}. {key[:10]}... (weight: {weight})")
        
        # Verify thresholds match
        if (thresholds.get('low_threshold') == threshold and
            thresholds.get('med_threshold') == threshold and
            thresholds.get('high_threshold') == threshold):
            print(f"\n✅ All thresholds correctly set to {threshold}")
            return True
        else:
            print(f"\n⚠️  Thresholds don't all match expected value of {threshold}")
            return False
            
    except Exception as e:
        print(f"\n✗ Error verifying: {e}")
        return False

def print_next_steps(threshold, keepers):
    """Print what to do next"""
    print("\n" + "=" * 70)
    print("Next Steps & Important Information")
    print("=" * 70)
    
    print(f"\n1. INFORM ALL KEEPERS")
    print(f"   • Multi-sig is now active")
    print(f"   • {threshold} signatures required for all operations")
    print(f"   • Share this configuration with all Keepers")
    
    print(f"\n2. TEST THE SETUP")
    print(f"   • Create a small test transaction")
    print(f"   • Practice the multi-signature process")
    print(f"   • Ensure all Keepers can sign successfully")
    
    print(f"\n3. DOCUMENT PROCEDURES")
    print(f"   • How to coordinate signatures")
    print(f"   • Communication channels")
    print(f"   • Emergency procedures")
    print(f"   • Keeper responsibilities")
    
    print(f"\n4. ESTABLISH GOVERNANCE")
    print(f"   • Decision-making process")
    print(f"   • Voting mechanisms")
    print(f"   • Accountability measures")
    print(f"   • Regular reporting schedule")
    
    print(f"\n5. SECURITY MEASURES")
    print(f"   • All Keepers: secure secret keys in hardware wallets")
    print(f"   • Multiple backups in secure locations")
    print(f"   • Never share secret keys")
    print(f"   • Test recovery procedures")
    
    print("\n" + "=" * 70)
    print("How Multi-Signature Operations Work:")
    print("=" * 70)
    
    print(f"\n1. One Keeper creates and signs a transaction")
    print(f"2. Transaction XDR is shared with other Keepers")
    print(f"3. Each Keeper adds their signature")
    print(f"4. Once {threshold} signatures collected, anyone submits")
    print(f"5. Transaction executes on Stellar network")
    
    print("\nTools for Multi-Sig:")
    print("  • Stellar Laboratory: https://laboratory.stellar.org/")
    print("  • SEP-0007 (Tx Signing Request Protocol)")
    print("  • Custom coordination tools")
    
    print("\n" + "=" * 70)
    print("Emergency Contacts:")
    print("=" * 70)
    
    print("\nKeeper Contact Information:")
    for i, keeper in enumerate(keepers, 2):
        print(f"  Keeper {i}: {keeper['name']}")
        print(f"    Public Key: {keeper['public_key']}")
        print(f"    Contact: [Add contact information]")
    
    print("\n⚠️  REMEMBER: You can no longer operate this account alone!")
    print(f"   All operations now require {threshold} Keeper signatures.")
    
    print("\n" + "=" * 70)
    print("🔥 'Keeper of the Fire' Governance is Now Active!")
    print("'I am because we are' - Ubuntu 🌍")
    print("=" * 70)

def main():
    """Main setup process"""
    print_header()
    print_warning()
    
    # Ask if user is ready
    ready = input("Are you ready to proceed? (yes/no): ").strip().lower()
    if ready != 'yes':
        print("\nSetup cancelled. Come back when you're ready!")
        return 0
    
    # Initialize server
    server = Server(horizon_url=HORIZON_URL)
    
    # Check current account
    print("\n" + "=" * 70)
    print("Step 1: Checking Account")
    print("=" * 70)
    
    account = check_current_account(server)
    if not account:
        print("\n❌ Cannot proceed. Please fix the issues above.")
        return 1
    
    # Get configuration
    print("\n" + "=" * 70)
    print("Step 2: Choose Configuration")
    print("=" * 70)
    
    total_signers, threshold = get_configuration()
    if not total_signers or not threshold:
        print("\n❌ Configuration cancelled.")
        return 1
    
    # Get Keeper keys
    print("\n" + "=" * 70)
    print("Step 3: Add Keeper Public Keys")
    print("=" * 70)
    
    num_additional = total_signers - 1  # -1 for current account
    keepers = get_keeper_keys(num_additional)
    if not keepers:
        print("\n❌ Keeper entry cancelled.")
        return 1
    
    # Confirm configuration
    print("\n" + "=" * 70)
    print("Step 4: Confirm Configuration")
    print("=" * 70)
    
    if not confirm_configuration(total_signers, threshold, keepers):
        print("\nSetup cancelled by user.")
        return 0
    
    # Get secret key
    print("\n" + "=" * 70)
    print("Step 5: Execute Setup")
    print("=" * 70)
    print("\n⚠️  You'll need the CURRENT distributor secret key to proceed.")
    print("This is the last time you'll be able to use a single signature!")
    print()
    
    distributor_secret = input("Enter DISTRIBUTOR secret key (starts with 'S'): ").strip()
    
    if not distributor_secret.startswith('S'):
        print("\n❌ Invalid secret key format!")
        return 1
    
    # Execute setup
    success = setup_multisig(server, distributor_secret, keepers, threshold)
    
    if not success:
        print("\n❌ Multi-sig setup failed!")
        return 1
    
    # Verify
    print("\n" + "=" * 70)
    print("Step 6: Verification")
    print("=" * 70)
    
    verify_setup(server, threshold)
    
    # Print next steps
    print_next_steps(threshold, keepers)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
