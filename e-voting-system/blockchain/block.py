import hashlib
import time
import json

class Block:
    def __init__(self, index, votes, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.votes = votes
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "votes": self.votes,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }


        block_string = json.dumps(block_data, sort_keys=True).encode()
      
        return hashlib.sha256(block_string).hexdigest()

    def __repr__(self):
        return f"Block(Index: {self.index}, Hash: {self.hash[:10]}...)"