"""
UBECtt Token Management Utilities
This script provides helper functions for managing and distributing your token.
"""

from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder
from stellar_sdk.exceptions import BadRequestError

# Configuration
NETWORK_PASSPHRASE = Network.TESTNET_NETWORK_PASSPHRASE
HORIZON_URL = "https://horizon-testnet.stellar.org"
TOKEN_CODE = "UBECtt"


class TokenManager:
    def __init__(self, issuer_public_key, distributor_secret_key):
        """
        Initialize token manager.
        
        Args:
            issuer_public_key: Public key of token issuer
            distributor_secret_key: Secret key of distributor account
        """
        self.server = Server(horizon_url=HORIZON_URL)
        self.issuer_public = issuer_public_key
        self.distributor_keypair = Keypair.from_secret(distributor_secret_key)
        self.asset = Asset(TOKEN_CODE, issuer_public_key)
    
    def check_balance(self, public_key=None):
        """Check token balance for an account"""
        account_key = public_key or self.distributor_keypair.public_key
        
        try:
            account = self.server.accounts().account_id(account_key).call()
            print(f"\n{'='*60}")
            print(f"Account: {account_key}")
            print(f"{'='*60}")
            
            for balance in account['balances']:
                if balance['asset_type'] == 'native':
                    print(f"XLM: {balance['balance']}")
                else:
                    asset_code = balance.get('asset_code', 'Unknown')
                    asset_issuer = balance.get('asset_issuer', 'Unknown')[:10] + '...'
                    print(f"{asset_code}: {balance['balance']} (Issuer: {asset_issuer})")
            
            return True
        except Exception as e:
            print(f"❌ Error checking balance: {e}")
            return False
    
    def distribute_tokens(self, recipient_public_key, amount):
        """
        Send tokens to a recipient.
        
        Args:
            recipient_public_key: Recipient's public key
            amount: Amount of tokens to send
        """
        try:
            # Load distributor account
            distributor_account = self.server.load_account(
                self.distributor_keypair.public_key
            )
            
            # Build payment transaction
            transaction = (
                TransactionBuilder(
                    source_account=distributor_account,
                    network_passphrase=NETWORK_PASSPHRASE,
                    base_fee=100,
                )
                .append_payment_op(
                    destination=recipient_public_key,
                    asset=self.asset,
                    amount=str(amount),
                )
                .set_timeout(30)
                .build()
            )
            
            # Sign and submit
            transaction.sign(self.distributor_keypair)
            response = self.server.submit_transaction(transaction)
            
            print(f"\n✅ Sent {amount} {TOKEN_CODE} to {recipient_public_key}")
            print(f"Transaction hash: {response['hash']}")
            return True
            
        except BadRequestError as e:
            print(f"\n❌ Error distributing tokens: {e}")
            print("\nPossible issues:")
            print("  - Recipient hasn't created a trustline")
            print("  - Insufficient token balance")
            print("  - Recipient account doesn't exist")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False
    
    def create_trustline_template(self, recipient_public_key):
        """
        Generate code for recipient to create a trustline.
        This code should be run by the recipient.
        """
        template = f"""
# Trustline Creation Code for Recipient
# The recipient should run this code to create a trustline to {TOKEN_CODE}

from stellar_sdk import Asset, Keypair, Network, Server, TransactionBuilder

HORIZON_URL = "{HORIZON_URL}"
NETWORK_PASSPHRASE = {repr(NETWORK_PASSPHRASE)}

# Recipient must provide their secret key
recipient_secret = "YOUR_SECRET_KEY_HERE"
recipient_keypair = Keypair.from_secret(recipient_secret)

# Token details
token_code = "{TOKEN_CODE}"
issuer_public = "{self.issuer_public}"
custom_asset = Asset(token_code, issuer_public)

# Create trustline
server = Server(horizon_url=HORIZON_URL)
recipient_account = server.load_account(recipient_keypair.public_key)

transaction = (
    TransactionBuilder(
        source_account=recipient_account,
        network_passphrase=NETWORK_PASSPHRASE,
        base_fee=100,
    )
    .append_change_trust_op(
        asset=custom_asset,
        limit="1000000000",
    )
    .set_timeout(30)
    .build()
)

transaction.sign(recipient_keypair)
response = server.submit_transaction(transaction)
print(f"Trustline created! Hash: {{response['hash']}}")
"""
        return template
    
    def get_token_holders(self):
        """Get list of accounts holding the token"""
        try:
            assets = self.server.assets().for_code(TOKEN_CODE).for_issuer(
                self.issuer_public
            ).call()
            
            if assets['_embedded']['records']:
                asset_data = assets['_embedded']['records'][0]
                print(f"\n{TOKEN_CODE} Token Statistics:")
                print(f"  Total Accounts: {asset_data.get('num_accounts', 'N/A')}")
                print(f"  Total Amount: {asset_data.get('amount', 'N/A')}")
                print(f"  Authorization Required: {asset_data.get('flags', {}).get('auth_required', False)}")
                print(f"  Authorization Revocable: {asset_data.get('flags', {}).get('auth_revocable', False)}")
            else:
                print(f"\nNo statistics available for {TOKEN_CODE} yet.")
                
        except Exception as e:
            print(f"❌ Error fetching token statistics: {e}")
    
    def batch_distribute(self, recipients_dict):
        """
        Distribute tokens to multiple recipients.
        
        Args:
            recipients_dict: Dictionary of {public_key: amount}
        """
        print(f"\n{'='*60}")
        print(f"Batch Token Distribution")
        print(f"{'='*60}")
        
        results = {"success": [], "failed": []}
        
        for recipient, amount in recipients_dict.items():
            print(f"\nSending {amount} {TOKEN_CODE} to {recipient[:10]}...")
            if self.distribute_tokens(recipient, amount):
                results["success"].append(recipient)
            else:
                results["failed"].append(recipient)
        
        print(f"\n{'='*60}")
        print(f"Batch Distribution Complete")
        print(f"{'='*60}")
        print(f"Successful: {len(results['success'])}")
        print(f"Failed: {len(results['failed'])}")
        
        return results


def main_menu():
    """Interactive menu for token management"""
    print("=" * 60)
    print("UBECtt Token Management Tool")
    print("=" * 60)
    
    issuer_public = input("\nEnter ISSUER public key: ").strip()
    distributor_secret = input("Enter DISTRIBUTOR secret key: ").strip()
    
    if not issuer_public or not distributor_secret.startswith('S'):
        print("❌ Invalid keys provided")
        return
    
    manager = TokenManager(issuer_public, distributor_secret)
    
    while True:
        print("\n" + "=" * 60)
        print("Options:")
        print("=" * 60)
        print("1. Check distributor balance")
        print("2. Check any account balance")
        print("3. Distribute tokens to single recipient")
        print("4. Generate trustline code for recipient")
        print("5. View token statistics")
        print("6. Batch distribute tokens")
        print("0. Exit")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == "1":
            manager.check_balance()
        
        elif choice == "2":
            public_key = input("Enter public key to check: ").strip()
            manager.check_balance(public_key)
        
        elif choice == "3":
            recipient = input("Enter recipient public key: ").strip()
            amount = input("Enter amount to send: ").strip()
            try:
                manager.distribute_tokens(recipient, amount)
            except ValueError:
                print("❌ Invalid amount")
        
        elif choice == "4":
            recipient = input("Enter recipient public key (or press Enter for template): ").strip()
            code = manager.create_trustline_template(recipient or "RECIPIENT_PUBLIC_KEY")
            print("\n" + "=" * 60)
            print("Share this code with the recipient:")
            print("=" * 60)
            print(code)
        
        elif choice == "5":
            manager.get_token_holders()
        
        elif choice == "6":
            print("\nEnter recipients (format: PUBLIC_KEY AMOUNT, one per line)")
            print("Press Enter twice when done:")
            recipients = {}
            while True:
                line = input().strip()
                if not line:
                    break
                try:
                    pub_key, amount = line.split()
                    recipients[pub_key] = amount
                except ValueError:
                    print("❌ Invalid format. Use: PUBLIC_KEY AMOUNT")
            
            if recipients:
                manager.batch_distribute(recipients)
        
        elif choice == "0":
            print("\nGoodbye! 🌟")
            break
        
        else:
            print("❌ Invalid option")


if __name__ == "__main__":
    main_menu()
