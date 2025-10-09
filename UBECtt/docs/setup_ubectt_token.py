"""
UBECtt Token Setup Script - Customized for Your Keys
Ubuntu Bioregional Economic Commons - Transform Token (Fire Element)

This script will:
1. Verify your accounts are funded
2. Create the trustline from distributor to issuer
3. Issue UBECtt tokens to the distributor
4. Set authorization flags on the issuer account
5. Optionally set up multi-signature on distributor account

Requirements:
    pip install stellar-sdk

IMPORTANT: Keep your secret keys secure!
"""

from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder
from stellar_sdk.operation import SetOptions, AuthorizationFlag
from stellar_sdk.exceptions import BadRequestError
import sys

# Configuration
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE  # Using MAINNET
HORIZON_URL = "https://horizon.stellar.org"  # MAINNET Horizon

# Your UBECtt Token Configuration
TOKEN_CODE = "UBECtt"  # Transform Token
ISSUER_PUBLIC = "GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC"
DISTRIBUTOR_PUBLIC = "GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC"

print("=" * 70)
print("UBECtt Transform Token Setup")
print("Ubuntu Bioregional Economic Commons - Fire Element 🜂")
print("=" * 70)
print()
print(f"Token Code:      {TOKEN_CODE}")
print(f"Issuer Public:   {ISSUER_PUBLIC}")
print(f"Distributor:     {DISTRIBUTOR_PUBLIC}")
print(f"Network:         Stellar Public (MAINNET)")
print()
print("⚠️  WARNING: You are using the LIVE Stellar network (MAINNET)")
print("⚠️  Make sure both accounts are funded with real XLM!")
print()

def check_account_balance(server, public_key, account_name):
    """Check if an account exists and is funded"""
    try:
        account = server.accounts().account_id(public_key).call()
        balances = account['balances']
        
        print(f"\n✓ {account_name} Account Found")
        print(f"  Address: {public_key}")
        
        for balance in balances:
            if balance['asset_type'] == 'native':
                xlm_balance = float(balance['balance'])
                print(f"  XLM Balance: {xlm_balance}")
                
                if xlm_balance < 2.0:
                    print(f"  ⚠️  WARNING: Low XLM balance! Need at least 2 XLM")
                    return False
                    
        return True
    except Exception as e:
        print(f"\n✗ {account_name} Account Not Found or Error:")
        print(f"  {e}")
        print(f"  Please fund this account with XLM first!")
        return False

def step1_create_trustline(server, distributor_secret):
    """Step 1: Create trustline from distributor to issuer for UBECtt"""
    print("\n" + "=" * 70)
    print("STEP 1: Creating Trustline")
    print("=" * 70)
    
    try:
        distributor_keypair = Keypair.from_secret(distributor_secret)
        distributor_account = server.load_account(DISTRIBUTOR_PUBLIC)
        ubectt_asset = Asset(TOKEN_CODE, ISSUER_PUBLIC)
        
        print(f"\nCreating trustline for {TOKEN_CODE}...")
        print(f"From: {DISTRIBUTOR_PUBLIC}")
        print(f"To:   {ISSUER_PUBLIC}")
        
        transaction = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_change_trust_op(
                asset=ubectt_asset,
                limit="922337203685.4775807",  # Maximum possible
            )
            .set_timeout(30)
            .build()
        )
        
        transaction.sign(distributor_keypair)
        response = server.submit_transaction(transaction)
        
        print(f"\n✅ Trustline Created Successfully!")
        print(f"Transaction Hash: {response['hash']}")
        print(f"View on Stellar Expert:")
        print(f"https://stellar.expert/explorer/public/tx/{response['hash']}")
        
        return True
        
    except BadRequestError as e:
        print(f"\n❌ Error creating trustline: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def step2_issue_tokens(server, issuer_secret, amount="1000000"):
    """Step 2: Issue UBECtt tokens from issuer to distributor"""
    print("\n" + "=" * 70)
    print("STEP 2: Issuing UBECtt Tokens")
    print("=" * 70)
    
    try:
        issuer_keypair = Keypair.from_secret(issuer_secret)
        issuer_account = server.load_account(ISSUER_PUBLIC)
        ubectt_asset = Asset(TOKEN_CODE, ISSUER_PUBLIC)
        
        print(f"\nIssuing {amount} {TOKEN_CODE} tokens...")
        print(f"From: {ISSUER_PUBLIC} (Issuer)")
        print(f"To:   {DISTRIBUTOR_PUBLIC} (Distributor)")
        
        transaction = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_payment_op(
                destination=DISTRIBUTOR_PUBLIC,
                asset=ubectt_asset,
                amount=amount,
            )
            .set_timeout(30)
            .build()
        )
        
        transaction.sign(issuer_keypair)
        response = server.submit_transaction(transaction)
        
        print(f"\n✅ Tokens Issued Successfully!")
        print(f"Amount: {amount} {TOKEN_CODE}")
        print(f"Transaction Hash: {response['hash']}")
        print(f"View on Stellar Expert:")
        print(f"https://stellar.expert/explorer/public/tx/{response['hash']}")
        
        return True
        
    except BadRequestError as e:
        print(f"\n❌ Error issuing tokens: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def step3_set_authorization_flags(server, issuer_secret):
    """Step 3: Set authorization flags on issuer account"""
    print("\n" + "=" * 70)
    print("STEP 3: Setting Authorization Flags")
    print("=" * 70)
    print("\nThis will set the following flags on the issuer account:")
    print("  • AUTHORIZATION_REQUIRED  - Accounts need approval to hold UBECtt")
    print("  • AUTHORIZATION_REVOCABLE - Can revoke authorization if misused")
    print("  • AUTHORIZATION_IMMUTABLE - Cannot change these flags later")
    print()
    print("⚠️  WARNING: This is PERMANENT and cannot be undone!")
    
    confirm = input("\nProceed with setting authorization flags? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Skipping authorization flags.")
        return False
    
    try:
        issuer_keypair = Keypair.from_secret(issuer_secret)
        issuer_account = server.load_account(ISSUER_PUBLIC)
        
        transaction = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_set_options_op(
                set_flags=(
                    AuthorizationFlag.AUTHORIZATION_REQUIRED |
                    AuthorizationFlag.AUTHORIZATION_REVOCABLE |
                    AuthorizationFlag.AUTHORIZATION_IMMUTABLE
                )
            )
            .set_timeout(30)
            .build()
        )
        
        transaction.sign(issuer_keypair)
        response = server.submit_transaction(transaction)
        
        print(f"\n✅ Authorization Flags Set Successfully!")
        print(f"Transaction Hash: {response['hash']}")
        print(f"View on Stellar Expert:")
        print(f"https://stellar.expert/explorer/public/tx/{response['hash']}")
        
        print("\n⚠️  IMPORTANT: From now on, all accounts need approval from")
        print("    the issuer to hold UBECtt tokens!")
        
        return True
        
    except BadRequestError as e:
        print(f"\n❌ Error setting authorization flags: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def step4_setup_multisig(server, distributor_secret):
    """Step 4 (Optional): Set up multi-signature on distributor account"""
    print("\n" + "=" * 70)
    print("STEP 4: Multi-Signature Setup (Optional)")
    print("=" * 70)
    print("\nMulti-signature allows multiple people (Keepers) to control")
    print("the distributor account, implementing the 'Keeper of the Fire'")
    print("governance model.")
    print()
    print("This step will:")
    print("  • Add additional signers to the distributor account")
    print("  • Set signature thresholds (e.g., 2-of-3, 3-of-5)")
    print("  • Optionally reduce master key weight")
    print()
    
    setup = input("Set up multi-signature now? (yes/no): ").strip().lower()
    if setup != 'yes':
        print("Skipping multi-signature setup.")
        print("You can set this up later using the Stellar Laboratory:")
        print("https://laboratory.stellar.org/")
        return False
    
    print("\n--- Multi-Signature Configuration ---")
    print("\nHow many signers (Keepers) in total? (e.g., 3 for 2-of-3, 5 for 3-of-5)")
    num_signers = int(input("Number of signers: ").strip())
    
    print("\nHow many signatures required for operations?")
    threshold = int(input("Required signatures: ").strip())
    
    if threshold > num_signers:
        print("❌ Error: Required signatures cannot exceed total signers!")
        return False
    
    print(f"\nYou'll be creating a {threshold}-of-{num_signers} multi-sig setup.")
    print("\nEnter the PUBLIC keys for each additional signer (Keeper):")
    print("(These should be the public keys of the other Keepers)")
    
    additional_signers = []
    for i in range(num_signers - 1):  # -1 because distributor account is already a signer
        signer_pub = input(f"Signer #{i+2} public key: ").strip()
        if len(signer_pub) == 56 and signer_pub.startswith('G'):
            additional_signers.append(signer_pub)
        else:
            print(f"❌ Invalid public key format!")
            return False
    
    try:
        distributor_keypair = Keypair.from_secret(distributor_secret)
        distributor_account = server.load_account(DISTRIBUTOR_PUBLIC)
        
        # Build transaction with all signers and thresholds
        transaction_builder = TransactionBuilder(
            source_account=distributor_account,
            network_passphrase=NETWORK_PASSPHRASE,
            base_fee=100 * (len(additional_signers) + 1),  # Account for multiple operations
        )
        
        # Add each additional signer
        for signer_pub in additional_signers:
            transaction_builder.append_set_options_op(
                signer={"ed25519_public_key": signer_pub, "weight": 1}
            )
        
        # Set thresholds (all operations require the threshold)
        transaction_builder.append_set_options_op(
            master_weight=1,
            low_threshold=threshold,
            med_threshold=threshold,
            high_threshold=threshold,
        )
        
        transaction = transaction_builder.set_timeout(30).build()
        transaction.sign(distributor_keypair)
        response = server.submit_transaction(transaction)
        
        print(f"\n✅ Multi-Signature Setup Complete!")
        print(f"Configuration: {threshold}-of-{num_signers}")
        print(f"Transaction Hash: {response['hash']}")
        print(f"View on Stellar Expert:")
        print(f"https://stellar.expert/explorer/public/tx/{response['hash']}")
        
        print("\n⚠️  IMPORTANT: From now on, this distributor account requires")
        print(f"    {threshold} signatures for all operations!")
        
        return True
        
    except BadRequestError as e:
        print(f"\n❌ Error setting up multi-signature: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

def main():
    """Main setup process"""
    server = Server(horizon_url=HORIZON_URL)
    
    # Check account balances
    print("\n" + "=" * 70)
    print("Checking Account Status")
    print("=" * 70)
    
    issuer_ok = check_account_balance(server, ISSUER_PUBLIC, "Issuer")
    distributor_ok = check_account_balance(server, DISTRIBUTOR_PUBLIC, "Distributor")
    
    if not (issuer_ok and distributor_ok):
        print("\n❌ One or more accounts need funding!")
        print("\nTo fund accounts on MAINNET:")
        print("  1. Purchase XLM on an exchange (Coinbase, Kraken, etc.)")
        print("  2. Send at least 3 XLM to each account")
        print("  3. Wait for confirmation")
        print("  4. Run this script again")
        sys.exit(1)
    
    print("\n✅ Both accounts are funded and ready!")
    
    # Get secret keys
    print("\n" + "=" * 70)
    print("Secret Keys Required")
    print("=" * 70)
    print("\n⚠️  Never share your secret keys with anyone!")
    print("⚠️  Make sure you're in a secure environment!")
    print()
    
    issuer_secret = input("Enter ISSUER secret key (starts with 'S'): ").strip()
    distributor_secret = input("Enter DISTRIBUTOR secret key (starts with 'S'): ").strip()
    
    # Validate secret keys
    if not (issuer_secret.startswith('S') and distributor_secret.startswith('S')):
        print("\n❌ Invalid secret key format!")
        sys.exit(1)
    
    # Verify keypairs match public keys
    try:
        issuer_kp = Keypair.from_secret(issuer_secret)
        dist_kp = Keypair.from_secret(distributor_secret)
        
        if issuer_kp.public_key != ISSUER_PUBLIC:
            print("\n❌ Issuer secret key doesn't match public key!")
            sys.exit(1)
        
        if dist_kp.public_key != DISTRIBUTOR_PUBLIC:
            print("\n❌ Distributor secret key doesn't match public key!")
            sys.exit(1)
            
        print("\n✅ Secret keys verified!")
        
    except Exception as e:
        print(f"\n❌ Error validating keys: {e}")
        sys.exit(1)
    
    # Confirm before proceeding
    print("\n" + "=" * 70)
    print("Ready to Begin Setup")
    print("=" * 70)
    print("\nThis script will:")
    print("  1. Create trustline from distributor to issuer")
    print("  2. Issue initial UBECtt tokens to distributor")
    print("  3. Set authorization flags on issuer (OPTIONAL)")
    print("  4. Set up multi-signature on distributor (OPTIONAL)")
    print()
    
    # Ask for initial token amount
    print("How many UBECtt tokens to issue initially?")
    print("(Recommendation: Issue conservatively, you can issue more later)")
    amount = input("Amount (default: 1000000): ").strip() or "1000000"
    
    proceed = input("\nProceed with setup? (yes/no): ").strip().lower()
    if proceed != 'yes':
        print("\nSetup cancelled.")
        sys.exit(0)
    
    # Execute setup steps
    success_steps = []
    
    # Step 1: Create trustline
    if step1_create_trustline(server, distributor_secret):
        success_steps.append("Trustline created")
    else:
        print("\n❌ Setup failed at Step 1")
        sys.exit(1)
    
    # Step 2: Issue tokens
    if step2_issue_tokens(server, issuer_secret, amount):
        success_steps.append(f"{amount} tokens issued")
    else:
        print("\n❌ Setup failed at Step 2")
        sys.exit(1)
    
    # Step 3: Authorization flags (optional)
    if step3_set_authorization_flags(server, issuer_secret):
        success_steps.append("Authorization flags set")
    
    # Step 4: Multi-signature (optional)
    if step4_setup_multisig(server, distributor_secret):
        success_steps.append("Multi-signature configured")
    
    # Final summary
    print("\n" + "=" * 70)
    print("🎉 UBECtt Token Setup Complete!")
    print("=" * 70)
    print("\nCompleted steps:")
    for step in success_steps:
        print(f"  ✓ {step}")
    
    print("\n" + "=" * 70)
    print("Important Information")
    print("=" * 70)
    print(f"\nToken Code:      {TOKEN_CODE}")
    print(f"Issuer:          {ISSUER_PUBLIC}")
    print(f"Distributor:     {DISTRIBUTOR_PUBLIC}")
    print(f"\nView on Stellar Expert:")
    print(f"https://stellar.expert/explorer/public/asset/{TOKEN_CODE}-{ISSUER_PUBLIC}")
    
    print("\n" + "=" * 70)
    print("Next Steps")
    print("=" * 70)
    print("\n1. Document your setup:")
    print("   - Save this information securely")
    print("   - Record all Keeper public keys")
    print("   - Document governance procedures")
    
    print("\n2. Test the system:")
    print("   - Create a test community governance account")
    print("   - Have that account create a trustline")
    print("   - Test token distribution")
    print("   - Verify multi-signature if configured")
    
    print("\n3. Begin governance:")
    print("   - Train all Keepers on procedures")
    print("   - Establish decision-making process")
    print("   - Set up monitoring and reporting")
    print("   - Create accountability mechanisms")
    
    print("\n4. Allocate to communities:")
    print("   - Identify pilot communities")
    print("   - Calculate allocations (10 UBECtt per hectare)")
    print("   - Distribute and train communities")
    print("   - Monitor and support")
    
    print("\n" + "=" * 70)
    print("🜂 Transform Token is now LIVE!")
    print("'I am because we are' - Ubuntu 🌍")
    print("=" * 70)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
