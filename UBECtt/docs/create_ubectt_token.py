"""
Stellar Token Creation Script for UBECtt Transform Token
This script creates the UBECtt custom token on the Stellar network.

Requirements:
    pip install stellar-sdk

IMPORTANT: This script is configured for PRODUCTION (Public Network).
If you want to test first, change to TESTNET settings below.
"""

from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder
from stellar_sdk.exceptions import BadRequestError

# Configuration
NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE  # Change to Network.PUBLIC_NETWORK_PASSPHRASE for mainnet
HORIZON_URL = "https://horizon-testnet.stellar.org"  # Change to "https://horizon.stellar.org" for mainnet

# Token Details - UBECtt Transform Token (Fire Element)
TOKEN_CODE = "UBECtt"  # Transform Token code (max 12 characters)
# UBECtt represents transformative actions, catalytic change, and community sovereignty

def create_token(issuer_secret_key, distributor_secret_key=None, distributor_public=None):
    """
    Create a new token on the Stellar network.
    
    Args:
        issuer_secret_key: Secret key of the issuing account (starts with 'S')
        distributor_secret_key: Optional secret key for distributor account
        distributor_public: Optional public key for existing distributor account
    """
    
    # Initialize server connection
    server = Server(horizon_url=HORIZON_URL)
    
    # Load issuer account
    issuer_keypair = Keypair.from_secret(issuer_secret_key)
    issuer_public = issuer_keypair.public_key
    
    # Verify issuer public key matches expected
    expected_issuer = "GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC"
    if issuer_public != expected_issuer:
        print(f"⚠️  WARNING: Issuer public key mismatch!")
        print(f"Expected: {expected_issuer}")
        print(f"Got:      {issuer_public}")
        proceed = input("Continue anyway? (yes/no): ").lower()
        if proceed != 'yes':
            return {"success": False, "error": "Issuer key mismatch"}
    
    print(f"✓ Issuer Public Key: {issuer_public}")
    
    # Create or use distributor account
    if distributor_public:
        # Use provided distributor public key
        if distributor_secret_key:
            distributor_keypair = Keypair.from_secret(distributor_secret_key)
            if distributor_keypair.public_key != distributor_public:
                print(f"⚠️  WARNING: Distributor keys don't match!")
                print(f"Public key from secret: {distributor_keypair.public_key}")
                print(f"Provided public key:    {distributor_public}")
                return {"success": False, "error": "Distributor key mismatch"}
        else:
            print(f"⚠️  Using distributor public key without secret key")
            print(f"   You will not be able to sign transactions for this account")
            distributor_keypair = None
        
        distributor_public_key = distributor_public
        print(f"✓ Using Distributor: {distributor_public_key}")
        
    elif distributor_secret_key:
        distributor_keypair = Keypair.from_secret(distributor_secret_key)
        distributor_public_key = distributor_keypair.public_key
        print(f"✓ Using Distributor: {distributor_public_key}")
    else:
        # Generate a new distributor account
        distributor_keypair = Keypair.random()
        distributor_public_key = distributor_keypair.public_key
        print(f"\n⚠️  Generated new Distributor Account:")
        print(f"Public Key: {distributor_public_key}")
        print(f"Secret Key: {distributor_keypair.secret} (SAVE THIS SECURELY!)")
    
    # Create the custom asset
    custom_asset = Asset(TOKEN_CODE, issuer_public)
    
    try:
        # Load distributor account
        distributor_account = server.load_account(distributor_public_key)
        
        # Step 1: Create trustline from distributor to issuer for the custom token
        print(f"\n📝 Creating trustline for {TOKEN_CODE}...")
        
        trustline_tx = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_change_trust_op(
                asset=custom_asset,
                limit="1000000000",  # Maximum amount of tokens that can be held
            )
            .set_timeout(30)
            .build()
        )
        
        trustline_tx.sign(distributor_keypair)
        response = server.submit_transaction(trustline_tx)
        print(f"✅ Trustline created! Transaction hash: {response['hash']}")
        
        # Step 2: Issue tokens from issuer to distributor
        print(f"\n💰 Issuing {TOKEN_CODE} tokens...")
        
        issuer_account = server.load_account(issuer_public)
        
        payment_tx = (
            TransactionBuilder(
                source_account=issuer_account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=100,
            )
            .append_payment_op(
                destination=distributor_public_key,
                asset=custom_asset,
                amount="1000000",  # Amount of tokens to issue
            )
            .set_timeout(30)
            .build()
        )
        
        payment_tx.sign(issuer_keypair)
        response = server.submit_transaction(payment_tx)
        print(f"✅ Tokens issued! Transaction hash: {response['hash']}")
        
        print(f"\n🎉 Success! {TOKEN_CODE} token created on Stellar!")
        print(f"\nToken Details:")
        print(f"  Code: {TOKEN_CODE}")
        print(f"  Issuer: {issuer_public}")
        print(f"  Distributor: {distributor_public_key}")
        
        return {
            "success": True,
            "token_code": TOKEN_CODE,
            "issuer": issuer_public,
            "distributor": distributor_public_key,
        }
        
    except BadRequestError as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("  - Distributor account doesn't exist or isn't funded")
        print("  - Issuer account doesn't exist or isn't funded")
        print("  - Network connectivity issues")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return {"success": False, "error": str(e)}


def check_account_balance(public_key):
    """Check the balance of an account"""
    server = Server(horizon_url=HORIZON_URL)
    
    try:
        account = server.accounts().account_id(public_key).call()
        print(f"\nAccount: {public_key}")
        print("Balances:")
        for balance in account['balances']:
            if balance['asset_type'] == 'native':
                print(f"  XLM: {balance['balance']}")
            else:
                print(f"  {balance['asset_code']}: {balance['balance']}")
    except Exception as e:
        print(f"Error checking balance: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Stellar Token Creation Tool - UBECtt Transform Token")
    print("=" * 60)
    
    # Network selection
    print("\n⚠️  NETWORK SELECTION")
    print("1. PUBLIC NETWORK (Mainnet) - Real XLM required")
    print("2. TESTNET (Testing only) - Free test XLM")
    
    network_choice = input("\nSelect network (1/2, default=1): ").strip()
    
    global NETWORK_PASSPHRASE, HORIZON_URL
    
    if network_choice == '2':
        NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE
        HORIZON_URL = "https://horizon-testnet.stellar.org"
        print("✓ Using TESTNET")
    else:
        NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
        HORIZON_URL = "https://horizon.stellar.org"
        print("✓ Using PUBLIC NETWORK (Mainnet)")
        confirm = input("\n⚠️  Are you sure you want to create on MAINNET? (yes/no): ").lower()
        if confirm != 'yes':
            print("Cancelled.")
            exit(0)
    
    print("\nExpected Issuer: GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC")
    print("Expected Distributor: GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC")
    
    # Get issuer secret key
    issuer_secret = input("\nEnter ISSUER account SECRET KEY (starts with 'S'): ").strip()
    
    if not issuer_secret or not issuer_secret.startswith('S'):
        print("❌ Invalid secret key. Must start with 'S'")
        exit(1)
    
    # Get distributor information
    print("\n--- Distributor Account Options ---")
    print("1. I have the distributor SECRET KEY")
    print("2. I only have the distributor PUBLIC KEY")  
    print("3. Generate a new distributor account")
    
    choice = input("\nSelect option (1/2/3): ").strip()
    
    distributor_secret = None
    distributor_public = None
    
    if choice == '1':
        distributor_secret = input("Enter distributor SECRET KEY: ").strip()
        if not distributor_secret.startswith('S'):
            print("❌ Invalid secret key. Must start with 'S'")
            exit(1)
    elif choice == '2':
        distributor_public = input("Enter distributor PUBLIC KEY (default: GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC): ").strip()
        if not distributor_public:
            distributor_public = "GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC"
        print(f"⚠️  Note: You will need the secret key to sign transactions")
    elif choice == '3':
        print("Will generate a new distributor account...")
    else:
        print("❌ Invalid choice")
        exit(1)
    
    # Create the token
    print("\n" + "=" * 60)
    print("Creating UBECtt Token...")
    print("=" * 60)
    result = create_token(issuer_secret, distributor_secret, distributor_public)
    
    if result["success"]:
        print("\n" + "=" * 60)
        print("Next Steps:")
        print("=" * 60)
        print("1. Save your distributor account keys securely")
        print("2. You can now distribute tokens to other accounts")
        print("3. Recipients must create a trustline before receiving tokens")
        print("4. Consider setting up additional properties (home domain, etc.)")
        print("\nFor Mainnet deployment:")
        print("  - Change NETWORK_PASSPHRASE to Network.PUBLIC_NETWORK_PASSPHRASE")
        print("  - Change HORIZON_URL to 'https://horizon.stellar.org'")
        print("  - Ensure accounts are funded with real XLM")
