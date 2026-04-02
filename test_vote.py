import requests
from wallet import Wallet

# Generate a new random voter wallet
print("Generating new Wallet...")
voter_wallet = Wallet()

# Prepare payload data
voter_id = voter_wallet.get_voter_id()
public_key_pem = voter_wallet.export_public_key_pem().decode('utf-8')
vote_choice = "Candidate A"

# Sign the vote mathematically
print(f"Signing vote for '{vote_choice}'...")
signature_bytes = voter_wallet.sign_message(vote_choice)
signature_hex = signature_bytes.hex()

payload = {
    "voter_id": voter_id,
    "vote": vote_choice,
    "public_key_pem": public_key_pem,
    "signature": signature_hex
}

# 1. Cast the vote
print("\n--- 1. Casting Vote ---")
try:
    response = requests.post("http://127.0.0.1:5000/api/vote", json=payload)
    print("Response Status:", response.status_code)
    print("Response Body:", response.json())
except requests.exceptions.ConnectionError:
    print("ERROR: Connection refused. Is app.py running?")
    exit()

# 2. View the Blockchain Ledger
print("\n--- 2. Fetching Blockchain Ledger ---")
chain_resp = requests.get("http://127.0.0.1:5000/api/chain")
print("Chain Length:", chain_resp.json()["length"])
print("Is Blockchain Valid?", chain_resp.json()["is_valid"])

# 3. View the Result Tally
print("\n--- 3. Fetching Election Results ---")
results_resp = requests.get("http://127.0.0.1:5000/api/results")
print("Current Tally:", results_resp.json()["results"])
print("Total Votes Cast:", results_resp.json()["total_votes"])
