import time
from block import Block

class Blockchain:
    def __init__(self, difficulty=2):
        self.chain = []
        self.pending_data = []  # Data/Transactions to be included in the next block
        self.difficulty = difficulty
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Generates the Genesis Block and appends it to the chain.
        """
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """
        Returns the most recent block in the chain.
        """
        return self.chain[-1]

    def add_data(self, data):
        """
        Adds new data to the list of pending data items.
        """
        self.pending_data.append(data)

    def proof_of_work(self, block):
        """
        A proof-of-work algorithm that tries different values of nonce 
        until it gets a hash that satisfies the difficulty (starts with N zeros).
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        
        target_prefix = '0' * self.difficulty
        while not computed_hash.startswith(target_prefix):
            block.nonce += 1
            computed_hash = block.compute_hash()
            
        return computed_hash

    def add_block(self, block, proof):
        """
        Verifies the block and its proof, and if valid, appends it to the chain.
        """
        previous_hash = self.last_block.hash
        
        # Check against the previous block's hash
        if previous_hash != block.previous_hash:
            return False
            
        # Check if the proof is valid
        if not self.is_valid_proof(block, proof):
            return False
            
        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        """
        Checks if the provided block_hash satisfies the difficulty criteria
        and strictly matches the block's current computed hash.
        """
        target_prefix = '0' * self.difficulty
        return (block_hash.startswith(target_prefix) and 
                block_hash == block.compute_hash())

    def mine(self):
        """
        Commits pending data to the blockchain by wrapping it in a Block,
        calculating the proof_of_work, and appending to the chain.
        """
        if not self.pending_data:
            return False

        last_block = self.last_block
        
        new_block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            data=self.pending_data,
            previous_hash=last_block.hash
        )

        # Mining process
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        
        # Clear out pending internal mempool once successfully mined
        self.pending_data = [] 
        
        return new_block.index

    def is_chain_valid(self):
        """
        Validates the entire blockchain checking every hash linkage
        and validating the work proofs.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Validate structural linkage
            if current.previous_hash != previous.hash:
                return False

            # Validate that the work satisfies difficulty, 
            # and that it hasn't been tampered with.
            if not self.is_valid_proof(current, current.hash):
                return False
                
        return True
