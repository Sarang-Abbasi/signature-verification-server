from web3 import Web3
import os
import hashlib

# --- CONFIGURATION ---
provider_url = "https://eth-sepolia.g.alchemy.com/v2/ebSETHhOtPTM6eJS5YlXV1P9M74LFUDV"         # e.g. "http://127.0.0.1:7545" (Ganache)
private_key = "7c772515104efbf5c3db2847c886f9754145555d9c7854fdae1495230661e5fb"
account_address = "0x5Be319F6d0F57f58049D6631D12F3B20D7b3FA24"
contract_address = "0x7B27Eb430777A591C3f4895aF053E65855d373AE"

contract_abi = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_userId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_resultLabel",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_resultHash",
				"type": "string"
			}
		],
		"name": "addSignatureResult",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_index",
				"type": "uint256"
			}
		],
		"name": "getSignatureResult",
		"outputs": [
			{
				"internalType": "string",
				"name": "userId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "_resultLabel",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "resultHash",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getTotalRecords",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "signatureResults",
		"outputs": [
			{
				"internalType": "string",
				"name": "userId",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "resultLabel",
				"type": "string"
			},
			{
				"internalType": "string",
				"name": "resultHash",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]

# --- CONNECT TO BLOCKCHAIN ---
w3 = Web3(Web3.HTTPProvider(provider_url))
assert w3.is_connected(), "Web3 is not connected!"

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# --- STORE A NEW RECORD ---
def store_signature_result(user_id, result_label, result_hash):
    txn = contract.functions.addSignatureResult(user_id, result_label, result_hash).build_transaction({
        'chainId': w3.eth.chain_id,
        'from': account_address,
        'nonce': w3.eth.get_transaction_count(account_address),
        'gas': 300000,
        'gasPrice': w3.eth.gas_price,
    })
    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print("Transaction sent! Hash:", txn_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
    print("Transaction mined in block:", receipt.blockNumber)


# --- GET TOTAL RECORDS ---
def get_total_records():
    return contract.functions.getTotalRecords().call()

# --- READ A RECORD BY INDEX ---
def get_signature_result(index):
    user_id, result_label, result_hash, timestamp = contract.functions.getSignatureResult(index).call()
    return {
        "user_id": user_id,
		"result_label": result_label,
        "result_hash": result_hash,
        "timestamp": timestamp
    }

# ----------- USAGE EXAMPLE -----------
if __name__ == "__main__":
    user_id = input("Enter user ID: ").strip()

    # Generate random 32 bytes and hash with SHA256
    random_bytes = os.urandom(32)
    sha256_hash = hashlib.sha256(random_bytes).hexdigest()

    print(f"Generated hash for {user_id}: {sha256_hash}")

    try:
        store_signature_result(user_id, sha256_hash)
    except Exception as e:
        print("Error storing on blockchain:", e)


    # Get total number of records
    total = get_total_records()
    print(f"Total records on chain: {total}")

    # Print all records
    for i in range(total):
        rec = get_signature_result(i)
        print(f"Record #{i}: {rec}")
