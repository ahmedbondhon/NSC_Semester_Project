import hashlib
import json

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce

    def compute_hash(self):
        """
        Returns the SHA-256 hash of the block contents.
        """
        # Create a dictionary of the block's contents.
        # We don't include a 'hash' field here to avoid issues with hashing the hash itself.
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        # Serialize the dictionary to a JSON string, ensuring keys are sorted for consistent hashing
        block_string = json.dumps(block_dict, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()
