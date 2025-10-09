# UBECtt Token Creation - Pre-Flight Checklist
## Everything You Need Before Creating the Token

**Date:** October 9, 2025

---

## ✅ Account Keys

### Issuer Account
- [ ] **Public Key:** `GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC`
- [ ] **Secret Key:** Secured (starts with 'S')
- [ ] **Backup:** Secret key backed up in 2+ secure locations
- [ ] **Test:** Can derive public key from secret key

### Distributor Account
- [ ] **Public Key:** `GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC`
- [ ] **Secret Key:** Secured (starts with 'S')
- [ ] **Backup:** Secret key backed up in 2+ secure locations
- [ ] **Test:** Can derive public key from secret key

---

## 💰 Account Funding

### For Testnet (Testing)
- [ ] Issuer funded with test XLM (use Friendbot)
- [ ] Distributor funded with test XLM (use Friendbot)
- [ ] Both accounts have ≥2 XLM balance

### For Mainnet (Production)
- [ ] Issuer funded with real XLM
- [ ] Distributor funded with real XLM
- [ ] Both accounts have ≥5 XLM balance (recommended)
- [ ] Verified on Stellar Expert

**Quick Check Links:**
- Testnet Issuer: https://stellar.expert/explorer/testnet/account/GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC
- Testnet Distributor: https://stellar.expert/explorer/testnet/account/GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC
- Mainnet Issuer: https://stellar.expert/explorer/public/account/GBWYGECRQ7R5E6QQKWBTVNYSCFVTIYZLF6MGDHJQBHP2KU2U65Z5UBEC
- Mainnet Distributor: https://stellar.expert/explorer/public/account/GDWO2HUXDKQTZC3KIXLO5HEG5HMNA5FZW75ZURMKVPXQJ6CUPT4OUBEC

---

## 🖥️ Technical Setup

### Software Installation
- [ ] Python 3.7 or higher installed
- [ ] `pip` package manager working
- [ ] `stellar-sdk` installed (`pip install stellar-sdk`)
- [ ] Can import stellar_sdk without errors

**Test Command:**
```bash
python -c "from stellar_sdk import Asset, Keypair, Server; print('✓ All imports work')"
```

### Files Downloaded
- [ ] `create_ubectt_token.py` script downloaded
- [ ] `manage_ubectt_token.py` script downloaded
- [ ] `requirements.txt` downloaded
- [ ] All documentation files downloaded

---

## 📚 Knowledge & Understanding

### Token Specifications
- [ ] Understand UBECtt is the Transform Token (Fire element)
- [ ] Know allocation rate: 10 UBECtt per hectare
- [ ] Understand "Keeper of the Fire" governance model
- [ ] Know 10:1 catalytic multiplier mechanism
- [ ] Read Quick Reference guide
- [ ] Read Full Specifications document

### Governance
- [ ] Community governance model decided
- [ ] "Keeper of the Fire" identified
- [ ] Multi-signature requirements understood
- [ ] Authorization flags decision made
- [ ] Accountability mechanisms planned

### Integration
- [ ] Understand relationship to other tokens (UBEC, UBECrc, UBECgpi)
- [ ] Know how transformation workflow works
- [ ] Understand use cases and restrictions
- [ ] Read case studies and examples

---

## 🎯 Decision Points

### Network Choice
- [ ] **Decision made:** Testnet first OR Mainnet directly
- [ ] If Testnet: Ready to test completely before Mainnet
- [ ] If Mainnet: Understand this uses real XLM
- [ ] Comfortable with choice

### Initial Issuance
- [ ] **Decision made:** How many tokens to issue initially (default: 1,000,000)
- [ ] Understand more can be issued later
- [ ] Know whether to lock issuer eventually

### Authorization Flags
- [ ] **Decision made:** AUTHORIZATION_REQUIRED? (Yes/No)
- [ ] **Decision made:** AUTHORIZATION_REVOCABLE? (Yes/No)
- [ ] **Decision made:** AUTHORIZATION_IMMUTABLE? (Yes/No/Later)
- [ ] Understand implications of each flag
- [ ] Tested on testnet if using flags

---

## 🛡️ Security

### Key Management
- [ ] Secret keys never shared with anyone
- [ ] Secret keys never stored in email
- [ ] Secret keys never stored in cloud
- [ ] Secret keys backed up in 2+ secure locations
- [ ] Hardware wallet available (optional but recommended)
- [ ] Paper backup in fireproof safe (optional but recommended)

### Access Control
- [ ] Know who has access to keys
- [ ] Multi-signature planned if appropriate
- [ ] Succession plan documented
- [ ] Emergency procedures defined

---

## 📋 Operational Readiness

### Monitoring
- [ ] Stellar Expert bookmarked for monitoring
- [ ] Transaction notification method decided
- [ ] Regular monitoring schedule planned

### Distribution
- [ ] First recipient accounts identified
- [ ] Process for creating trustlines documented
- [ ] Token distribution procedure written
- [ ] Test distribution planned

### Documentation
- [ ] Governance procedures documented
- [ ] Token usage guidelines written
- [ ] Reporting procedures defined
- [ ] Community onboarding materials prepared

---

## 🧪 Testing Plan (for Testnet)

If testing on Testnet first (recommended):

### Testnet Tests
- [ ] Create token on testnet
- [ ] Verify token appears on testnet explorer
- [ ] Create test community account
- [ ] Have test account create trustline
- [ ] Send tokens to test account
- [ ] Test authorization flags (if using)
- [ ] Test multi-signature (if using)
- [ ] Verify all operations work as expected

### Transition to Mainnet
- [ ] All testnet tests passed
- [ ] Documentation updated with learnings
- [ ] Confident in process
- [ ] Ready for production deployment

---

## ⚠️ Final Pre-Launch Checks

### Before Running the Script
- [ ] All above sections completed
- [ ] Double-checked all keys are correct
- [ ] Verified accounts are funded
- [ ] Decided on testnet vs mainnet
- [ ] Read through step-by-step guide
- [ ] Have all secret keys ready to paste
- [ ] In a secure, private location
- [ ] Not rushed or distracted
- [ ] Ready to pay full attention

### Critical Questions
- [ ] **Are the accounts funded?** (Minimum 2 XLM each)
- [ ] **Do I have both secret keys?** (Ready to paste)
- [ ] **Am I testing on testnet first?** (Recommended)
- [ ] **Do I understand what will happen?** (Read guide)
- [ ] **Is this the right time?** (Not rushed)

---

## 🚀 Ready to Launch?

If you've checked ALL boxes above:

### You Are Ready to Create UBECtt! 🎉

**Next step:**
```bash
python create_ubectt_token.py
```

### If Any Boxes Unchecked

**Stop and complete them first.** Creating a token is permanent. Better to be over-prepared than to make mistakes.

---

## 📞 Need Help?

### Before Creating
If you're unsure about any item:
- Re-read the documentation
- Test on testnet first
- Ask in community channels
- Consult with technical advisor

### During Creation
If something goes wrong:
- Don't panic
- Read error messages carefully
- Check troubleshooting section
- Verify accounts are funded
- Try again if needed

### After Creating
- Verify on Stellar Expert
- Save all transaction hashes
- Document the process
- Begin next steps

---

## ✅ Success Indicators

You'll know the creation was successful when:

1. ✓ Script completes without errors
2. ✓ Two transaction hashes displayed
3. ✓ Token visible on Stellar Expert
4. ✓ Distributor has UBECtt balance
5. ✓ All properties match expectations

---

## 🎯 Final Reminder

**You're about to:**
- Create a permanent asset on Stellar blockchain
- Issue the Transform Token for community sovereignty
- Enable the 10:1 catalytic multiplier
- Launch the Fire element of Ubuntu Economic Commons

**This is significant!** Take your time, do it right, and celebrate when successful.

*"You never change things by fighting the existing reality. To change something, build a new model that makes the existing model obsolete."*

You're building that new model. Right now. Today.

**Ready? Let's create UBECtt! 🔥**

---

**Checklist Version:** 1.0  
**Last Updated:** October 9, 2025

---

**When all boxes are checked, proceed to:**  
[UBECtt Creation Step-by-Step Guide](UBECTT_CREATION_STEP_BY_STEP.md)

---

**END OF CHECKLIST**
