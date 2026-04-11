import os
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from blockchain import Blockchain
from wallet import Wallet

# Load configuration from .env file
load_dotenv()

app = Flask(__name__, template_folder='.')
# Enable Cross-Origin Resource Sharing
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/api/generate_keys', methods=['POST'])
def generate_keys():
    """
    Generates a fresh RSA-2048 keypair on the server using the Wallet class
    and returns both the private and public keys in PEM format as JSON strings.
    The client downloads them as files.
    """
    wallet = Wallet()
    private_pem = wallet.export_private_key_pem().decode('utf-8')
    public_pem = wallet.export_public_key_pem().decode('utf-8')
    return jsonify({
        "private_key_pem": private_pem,
        "public_key_pem": public_pem
    }), 201


# Initialize the blockchain with difficulty from .env (default 2)
difficulty = int(os.environ.get("MINING_DIFFICULTY", 2))
blockchain = Blockchain(difficulty=difficulty)

@app.route('/api/vote', methods=['POST'])
def receive_vote():
    """
    Receives a signed vote, verifies the signature using the user's public key,
    ensures the voter hasn't already voted, and adds the vote to the blockchain.
    """
    req_data = request.get_json()

    if not req_data:
        return jsonify({"error": "Invalid request format. JSON body required."}), 400

    required_fields = ["voter_id", "vote", "public_key_pem", "signature"]
    if not all(k in req_data for k in required_fields):
        return jsonify({"error": f"Missing required fields. The request must contain: {', '.join(required_fields)}"}), 400

    voter_id = req_data["voter_id"]
    vote_choice = req_data["vote"]
    public_key_pem_str = req_data["public_key_pem"]
    signature_hex = req_data["signature"]

    print(f"DEBUG: Received voter_id: {voter_id}")
    print(f"DEBUG: Received public_key_pem_str (first 100 chars): {public_key_pem_str[:100]}")

    # 1. Decode the public key PEM
    public_key_pem_bytes = public_key_pem_str.encode('utf-8')
    try:
        public_key = Wallet.import_public_key_pem(public_key_pem_bytes)
    except Exception as e:
        print(f"DEBUG: Failed to load public key: {e}")
        return jsonify({"error": f"Failed to load public key: {str(e)}"}), 400

    # 2. Re-calculate the expected voter_id from public key and ensure it matches
    expected_voter_id = Wallet(public_key=public_key).get_voter_id()
    print(f"DEBUG: Calculated expected_voter_id: {expected_voter_id}")
    print(f"DEBUG: Voter ID match: {voter_id == expected_voter_id}")
    if voter_id != expected_voter_id:
        return jsonify({"error": f"Voter ID does not match the provided public key. Received: {voter_id}, Expected: {expected_voter_id}"}), 400

    # 3. Decode the signature from hex
    try:
        signature_bytes = bytes.fromhex(signature_hex)
    except ValueError:
        return jsonify({"error": "Invalid signature format. Must be a hex string."}), 400

    print(f"DEBUG: Signature hex (first 50): {signature_hex[:50]}")
    print(f"DEBUG: Vote choice: {vote_choice}")

    # 4. Verify the cryptographic signature on the vote choice
    is_valid_sig = Wallet.verify_signature(public_key, vote_choice, signature_bytes)
    print(f"DEBUG: Signature valid: {is_valid_sig}")
    if not is_valid_sig:
        return jsonify({"error": "Invalid signature. Cannot verify vote authenticity."}), 400

    # 5. Ensure the voter hasn't already voted (Iterate over the chain to find voter_id)
    # We also check the pending_data to prevent double voting within the same block
    for block in blockchain.chain:
        # Skip Genesis block, which typically does not contain a list of vote dictionaries
        if not isinstance(block.data, list):
            continue
        for tx in block.data:
            if tx.get("voter_id") == voter_id:
                return jsonify({"error": "Voter has already cast a vote on the blockchain."}), 400

    for pending_tx in blockchain.pending_data:
        if pending_tx.get("voter_id") == voter_id:
            return jsonify({"error": "Voter already has a pending vote awaiting mining."}), 400

    # 6. Add the vote to the blockchain 
    vote_record = {
        "voter_id": voter_id,
        "vote": vote_choice,
        "signature": signature_hex  # store the hex for auditing later
    }

    blockchain.add_data(vote_record)
    
    # In a real-world decentralized system, mining is asynchronous. 
    # For this secure API, we'll mine immediately to simplify the transaction flow.
    mined_index = blockchain.mine()
    if mined_index is False:
        return jsonify({"error": "Failed to mine block."}), 500

    return jsonify({
        "message": "Vote successfully verified and added to the blockchain.",
        "block_index": mined_index
    }), 201


@app.route('/api/chain', methods=['GET'])
def get_chain():
    """
    Returns the entirety of the blockchain ledger and verifies its validity.
    """
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "previous_hash": block.previous_hash,
            "nonce": block.nonce,
            "hash": block.hash
        })

    return jsonify({
        "length": len(chain_data),
        "chain": chain_data,
        "is_valid": blockchain.is_chain_valid()
    }), 200


@app.route('/api/results', methods=['GET'])
def tally_votes():
    """
    Tallies the final votes directly from the verified blockchain ledger.
    """
    tally = {}
    total_votes = 0

    for block in blockchain.chain:
        if not isinstance(block.data, list):
             continue  # Skip genesis block
             
        for tx in block.data:
            vote = tx.get("vote")
            if vote:
                tally[vote] = tally.get(vote, 0) + 1
                total_votes += 1

    return jsonify({
        "total_votes": total_votes,
        "results": tally,
        "tally_is_valid": blockchain.is_chain_valid()
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("\n🔒 Starting HTTPS server — other devices must accept the self-signed certificate warning.")
    app.run(host='0.0.0.0', port=port, debug=True, ssl_context='adhoc')
