# Adding Multi-Signature to Your UBECtt Distributor Account
## Guide for Setting Up "Keeper of the Fire" Governance

**When to use this:** After initial token setup, when you're ready to implement community governance

---

## 📋 When You're Ready

You should add multi-signature when you have:

✅ **Completed initial token setup** - Token is operational  
✅ **Tested basic operations** - Know how everything works  
✅ **Identified your Keepers** - Know who will hold the keys  
✅ **Trained your Keepers** - They understand responsibilities  
✅ **Documented governance** - Decision-making process is clear  
✅ **Established procedures** - Communication channels set up  
✅ **Tested on testnet** - Practiced the multi-sig workflow  

**Don't rush this!** It's perfectly fine to operate with single-signature for weeks or months while you prepare.

---

## 🎯 Preset Configurations

The script offers 4 preset configurations:

### 1. Small Community (2-of-3)
- **Total Keepers:** 3
- **Required Signatures:** 2
- **Best for:** <100 hectares (<1,000 UBECtt)
- **Example:** Small farm with 3 trusted community members

### 2. Medium Community (3-of-5)
- **Total Keepers:** 5
- **Required Signatures:** 3
- **Best for:** 100-1,000 hectares (1,000-10,000 UBECtt)
- **Example:** Bioregional cooperative with broader governance

### 3. Large Community (5-of-7)
- **Total Keepers:** 7
- **Required Signatures:** 5
- **Best for:** >1,000 hectares (>10,000 UBECtt)
- **Example:** Large bioregion with distributed leadership

### 4. Custom Configuration
- **Your choice** of total signers and threshold
- **Best for:** Unique governance structures
- **Example:** 4-of-6, 6-of-9, etc.

---

## 🚀 How to Use the Script

### Prerequisites

Before running the script:

```bash
# 1. Ensure you have stellar-sdk installed
pip install stellar-sdk

# 2. Gather all Keeper public keys
# Each Keeper should have created their own account

# 3. Have your current distributor secret key ready
# This is the LAST time you'll use it alone!
```

### Running the Script

```bash
python add_multisig_later.py
```

### What the Script Will Do

**Step 1: Check Account**
- Verifies distributor account exists
- Shows current configuration
- Checks XLM balance (need enough for reserves)

**Step 2: Choose Configuration**
- Shows preset options (2-of-3, 3-of-5, 5-of-7, custom)
- You select which model fits your community

**Step 3: Enter Keeper Keys**
- Input public key for each additional Keeper
- Optionally name each Keeper (e.g., "Alice - Farm Manager")
- Script validates each key

**Step 4: Confirm Configuration**
- Reviews complete setup
- Shows what will change
- Requires explicit "YES" to proceed

**Step 5: Execute**
- Asks for current distributor secret key
- Creates and signs transaction
- Submits to Stellar network

**Step 6: Verify**
- Confirms setup worked correctly
- Shows new configuration
- Provides next steps

---

## 📝 Example Session

```
UBECtt Multi-Signature Setup
====================================================================

Select a multi-signature configuration:
====================================================================

1. 2-of-3 (Small Community)
   3 total Keepers, any 2 must approve operations
   Recommended for: Communities managing <100 hectares

2. 3-of-5 (Medium Community)
   5 total Keepers, any 3 must approve operations
   Recommended for: Communities managing 100-1000 hectares

3. 5-of-7 (Large Community)
   7 total Keepers, any 5 must approve operations
   Recommended for: Communities managing >1000 hectares

4. Custom Configuration
   Define your own signer count and threshold
   Recommended for: Advanced users

====================================================================

Select configuration (1-4): 2

Enter public keys for 4 additional Keeper(s):
(The current distributor account is already Keeper #1)

Keeper #2:
  Public key: GCRK4QNR5A2FDM3ER6GBJPQO4ZVJD3MTCIFHPDW7TCZVMZQP2ZPRUBEC
  Keeper name/role: Alice - Farm Manager
  ✓ Added: Alice - Farm Manager

Keeper #3:
  Public key: GDLZS4VQM6FN2HQWBQQ5Z7K2YLQC2RWXJTP4XNMVR7PKWBQX3AIDUBEC
  Keeper name/role: Bob - Community Council
  ✓ Added: Bob - Community Council

...

Configuration: 3-of-5
Required signatures for operations: 3

Keepers:
  1. Master Key (current distributor)
     GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC
     Weight: 1

  2. Alice - Farm Manager
     GCRK4QNR5A2FDM3ER6GBJPQO4ZVJD3MTCIFHPDW7TCZVMZQP2ZPRUBEC
     Weight: 1

  3. Bob - Community Council
     GDLZS4VQM6FN2HQWBQQ5Z7K2YLQC2RWXJTP4XNMVR7PKWBQX3AIDUBEC
     Weight: 1

...

⚠️  FINAL WARNING:
    After this, you need 3 Keepers to sign ALL operations!
    
Proceed with this configuration? Type 'YES' in all caps to confirm: YES

✅ Multi-Signature Setup Complete!

Transaction Hash: a7f3e9d2c8b5a1f6...

Your account now requires 3 signatures for all operations!
```

---

## ⚙️ What Changes After Setup

### Before Multi-Sig (Single Signature)
```
You alone can:
✓ Distribute tokens
✓ Modify account settings
✓ Add/remove trustlines
✓ Make payments

All operations: 1 signature (you)
```

### After Multi-Sig (e.g., 3-of-5)
```
Operations require:
✓ 3 Keeper signatures
✓ Coordination among Keepers
✓ Shared transaction signing

All operations: 3 of 5 signatures required
```

---

## 🔐 Security Implications

### Advantages
✅ **Enhanced Security** - No single point of failure  
✅ **Accountability** - Multiple people must agree  
✅ **Community Control** - Implements true governance  
✅ **Protection** - Against key compromise or misuse  

### Requirements
⚠️ **Coordination** - Need to coordinate with other Keepers  
⚠️ **Complexity** - More steps for every operation  
⚠️ **Key Management** - Each Keeper must secure their key  
⚠️ **Communication** - Need reliable communication channels  

---

## 🛠️ How Multi-Sig Operations Work

After setup, here's how you'll operate:

### Step 1: Create Transaction
One Keeper creates and signs a transaction using:
- Stellar Laboratory
- Stellar CLI
- Custom tools

### Step 2: Share Transaction XDR
First Keeper shares the transaction XDR with other Keepers:
```
Example XDR:
AAAAAgAAAABSy7hKXk7QWHH8yl2Yc3uLMpBZCyDAM1...
```

### Step 3: Additional Signatures
Each additional Keeper:
1. Receives the transaction XDR
2. Reviews what it does
3. Signs with their key (if they approve)
4. Passes to next Keeper or submits

### Step 4: Submit Transaction
Once threshold signatures collected (e.g., 3 of 5):
- Anyone can submit the transaction
- It executes on Stellar network
- All signers are recorded

---

## 📋 Best Practices

### Before Setup
- [ ] Test on testnet first
- [ ] Document all Keeper information
- [ ] Establish communication channels
- [ ] Define decision-making process
- [ ] Create emergency procedures
- [ ] Train all Keepers

### During Setup
- [ ] Verify all public keys carefully
- [ ] Double-check threshold settings
- [ ] Save transaction hash
- [ ] Document new configuration
- [ ] Inform all Keepers immediately

### After Setup
- [ ] Test with small operation
- [ ] Verify all Keepers can sign
- [ ] Update procedures documentation
- [ ] Establish regular check-ins
- [ ] Monitor account activity
- [ ] Review governance quarterly

---

## 🆘 Troubleshooting

### "Account not found"
**Problem:** Distributor account doesn't exist or isn't funded  
**Solution:** Ensure initial setup completed successfully

### "Low XLM balance"
**Problem:** Not enough XLM for reserves  
**Solution:** Add XLM (0.5 XLM reserve per signer)  
**Formula:** Need at least `2 + (0.5 × number_of_signers)` XLM

### "Already has signers"
**Problem:** Multi-sig already configured  
**Solution:** Script will ask if you want to modify or add more

### "Invalid public key"
**Problem:** Keeper key format incorrect  
**Solution:** Must be 56 characters, start with 'G'

### "Transaction failed"
**Problem:** Various possible causes  
**Solution:** Check error message, ensure enough XLM, verify keys

---

## 🔄 Can I Change It Later?

### Adding MORE Signers
✅ **Yes** - Can add more Keepers anytime
- Requires current threshold of signatures
- Run this script again
- Common when community grows

### Removing Signers
✅ **Yes** - Can remove Keepers
- Requires current threshold of signatures
- Use Stellar Laboratory or custom script
- Common for retired Keepers

### Changing Threshold
✅ **Yes** - Can adjust required signatures
- Requires current threshold of signatures
- Use Stellar Laboratory or custom script
- Example: Change from 3-of-5 to 4-of-7

### Removing Multi-Sig Entirely
⚠️ **Difficult** - Requires threshold signatures to remove signers
- Must coordinate with enough Keepers
- Not recommended without good reason
- Consider emergency procedures instead

---

## 📞 Emergency Scenarios

### Lost Keeper Key
**If you lose ONE key:**
- Still operational (if threshold allows)
- Example: Lose 1 of 5 keys in 3-of-5 setup
- Can still operate with remaining 4 keys
- Should remove lost key and add new Keeper

**If you lose TOO MANY keys:**
- Cannot operate account
- Example: Lose 3 keys in 3-of-5 setup
- Account is locked
- **This is why key management is critical!**

### Keeper Becomes Unavailable
- Plan for replacements
- Document succession procedures
- Consider having backup Keepers
- Regular key audits

### Keeper Acts Maliciously
- Other Keepers refuse to sign
- Community can vote to remove
- Requires threshold to remove signer
- Why REVOCABLE authorization flag matters

---

## 🎓 Understanding Your Role as Keeper

### Keeper Responsibilities
✅ Secure their secret key (hardware wallet!)  
✅ Respond to signature requests promptly  
✅ Review transactions before signing  
✅ Communicate with other Keepers  
✅ Serve the community's decisions  
✅ Maintain accountability  

### Keeper is NOT:
❌ A dictator - serves community  
❌ Unilateral decision-maker  
❌ Owner of funds  
❌ Above accountability  

### "Keeper of the Fire" Means:
🔥 **Facilitate**, don't control  
🔥 **Enable**, don't block  
🔥 **Serve**, don't rule  
🔥 **Empower**, don't limit  

---

## 🌟 Benefits of Multi-Sig for Communities

**Sovereignty Through Shared Power**
- No single person controls transformation funds
- Community decisions require community support
- Protection against corruption or mistakes
- Transparent and accountable process

**Trust Through Transparency**
- All signatures visible on blockchain
- Cannot hide who approved what
- Community can verify governance works
- External funders see proper controls

**Resilience Through Distribution**
- One lost key doesn't break system
- One compromised key doesn't enable theft
- Geographic distribution possible
- Organizational diversity achievable

---

## ✅ Ready to Add Multi-Sig?

**Final Checklist:**
- [ ] Initial token setup complete and tested
- [ ] All Keepers identified and trained
- [ ] Keeper public keys collected and verified
- [ ] Governance procedures documented
- [ ] Communication channels established
- [ ] Emergency procedures defined
- [ ] Tested on testnet (optional but recommended)
- [ ] All Keepers committed and available
- [ ] Current distributor secret key available
- [ ] Enough XLM for reserves (check script output)

**If all checked, you're ready!**

```bash
python add_multisig_later.py
```

---

## 📚 Additional Resources

- **Stellar Multi-Sig Docs:** https://developers.stellar.org/docs/encyclopedia/signatures-multisig
- **Stellar Laboratory:** https://laboratory.stellar.org/
- **Transaction Signing:** https://developers.stellar.org/docs/encyclopedia/transaction-flow
- **Your Token Info:** SETUP_GUIDE_FOR_YOUR_TOKEN.md

---

**"The fire transforms, but the community directs that transformation."**

*"I am because we are" - Ubuntu* 🌍

---

**Document Version:** 1.0  
**Script:** add_multisig_later.py  
**Date:** October 9, 2025
