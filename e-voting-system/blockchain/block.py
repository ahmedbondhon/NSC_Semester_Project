import hashlib
import time
import json

class Block:
    def __init__(self, index, votes, previous_hash):
        """
        Initializes a new block in the blockchain.
        
        :param index: The position of the block in the chain (e.g., 0, 1, 2...)
        :param votes: A list of verified vote transactions included in this block
        :param previous_hash: The SHA-256 hash of the block immediately before this one
        """
        self.index = index
        self.timestamp = time.time()  # Records exactly when the block was created
        self.votes = votes            # The actual voting data
        self.previous_hash = previous_hash
        self.nonce = 0                # A number used if we want to add "mining" (Proof of Work) later
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Creates a completely unique SHA-256 hash based on the block's contents.
        If even a single vote is changed, this hash will change completely!
        """
        # 1. Package all the block's data into a dictionary
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "votes": self.votes,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        
        # 2. Convert the dictionary into a standardized JSON string
        # sort_keys=True is crucial! It ensures the data is always in the exact same order.
        block_string = json.dumps(block_data, sort_keys=True).encode()
        
        # 3. Pass the string through the SHA-256 algorithm
        return hashlib.sha256(block_string).hexdigest()

    def __repr__(self):
        return f"Block(Index: {self.index}, Hash: {self.hash[:10]}...)"