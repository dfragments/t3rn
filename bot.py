from web3 import Web3

# === Customizable Parameters (Fill in here) ===
PRIVATE_KEY = "0x1234567890"
AMOUNT_ETH = 0.3  # Amount per cross-chain transaction (unit: ETH)
TIMES = 10000000  # Number of times to bridge back and forth

# OP testnet RPC URL
OP_RPC_URL = "https://opt-sepolia.g.alchemy.com/v2/v5uHFK2iOUm-3mK6vqm2e1qxDUsNl_se"
# UNI testnet RPC URL
ARB_RPC_URL = "https://unichain-sepolia.drpc.org"

# OP testnet contract address
OP_CONTRACT_ADDRESS = "0xb6Def636914Ae60173d9007E732684a9eEDEF26E"
# UNI testnet contract address
ARB_CONTRACT_ADDRESS = "0x1cEAb5967E5f078Fa0FEC3DFfD0394Af1fEeBCC9"

# Data templates
OP_DATA_TEMPLATE = "0x56591d59756e6974000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000{address}0000000000000000000000000000000000000000000000000429bdd4db269f94000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000429d069189e0000"

UNI_DATA_TEMPLATE = "0x56591d596f707374000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000{address}0000000000000000000000000000000000000000000000000429ba43f915c4c0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000429d069189e0000"

# Initialize Web3 instances
w3_op = Web3(Web3.HTTPProvider(OP_RPC_URL))
w3_arb = Web3(Web3.HTTPProvider(ARB_RPC_URL))

if not w3_op.is_connected():
    raise Exception("Unable to connect to OP testnet")
if not w3_arb.is_connected():
    raise Exception("Unable to connect to UNI testnet")

# Generate account from private key
account = w3_op.eth.account.from_key(PRIVATE_KEY)
account_address = account.address[2:]  # Remove "0x" prefix to get a 40-character address

# Replace the address in the template with the generated address
OP_DATA = OP_DATA_TEMPLATE.format(address=account_address)
OP_TO_ARB_DATA = OP_DATA.replace("6f707374", "61726274")
UNI_DATA = UNI_DATA_TEMPLATE.format(address=account_address)

# Bridge from OP to UNI
def bridge_op_to_arb(amount_eth):
    try:
        amount_wei = w3_op.to_wei(amount_eth, 'ether')
        nonce = w3_op.eth.get_transaction_count(account.address)
        tx = {
            'from': account.address,
            'to': OP_CONTRACT_ADDRESS,
            'value': amount_wei,
            'nonce': nonce,
            'gas': 250000,
            'gasPrice': w3_op.to_wei(0.1, 'gwei'),
            'chainId': 11155420,
            'data': OP_TO_ARB_DATA
        }
        print(f"OP -> UNI: Sending {amount_eth} ETH")
        signed_tx = w3_op.eth.account.sign_transaction(tx, PRIVATE_KEY)
        raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx['raw']
        tx_hash = w3_op.eth.send_raw_transaction(raw_tx)
        print(f"OP -> UNI cross-chain transaction sent, Tx Hash: {w3_op.to_hex(tx_hash)}")
        tx_receipt = w3_op.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction confirmed, Block Number: {tx_receipt.blockNumber}")
    except Exception as e:
        print(f"OP -> UNI cross-chain failed, Error: {e}")
        return False  # Indicates failure
    return True  # Indicates success

# Bridge from UNI back to OP
def bridge_arb_to_op(amount_eth):
    try:
        amount_wei = w3_arb.to_wei(amount_eth, 'ether')
        nonce = w3_arb.eth.get_transaction_count(account.address)
        tx = {
            'from': account.address,
            'to': ARB_CONTRACT_ADDRESS,
            'value': amount_wei,
            'nonce': nonce,
            'gas': 400000,
            'gasPrice': w3_arb.to_wei(0.1, 'gwei'),
            'chainId': 1301,
            'data': UNI_DATA
        }
        print(f"UNI -> OP: Sending {amount_eth} ETH")
        signed_tx = w3_arb.eth.account.sign_transaction(tx, PRIVATE_KEY)
        raw_tx = signed_tx.raw_transaction if hasattr(signed_tx, 'raw_transaction') else signed_tx['raw']
        tx_hash = w3_arb.eth.send_raw_transaction(raw_tx)
        print(f"UNI -> OP cross-chain transaction sent, Tx Hash: {w3_arb.to_hex(tx_hash)}")
        tx_receipt = w3_arb.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Transaction confirmed, Block Number: {tx_receipt.blockNumber}")
    except Exception as e:
        print(f"UNI -> OP cross-chain failed, Error: {e}")
        return False  # Indicates failure
    return True  # Indicates success

# Execute back-and-forth bridging
print(f"Starting {TIMES} cross-chain transactions between OP and UNI, {AMOUNT_ETH} ETH each time")
for i in range(TIMES):
    print(f"\nCross-chain attempt {i+1}:")
    # OP -> UNI
    bridge_op_to_arb(AMOUNT_ETH)
    # UNI -> OP
    bridge_arb_to_op(AMOUNT_ETH)

print("\nAll cross-chain operations completed!")
