from blockchain.block import Block

class Blockchain:
    def __init__(self):
        """
        Initializes the blockchain, creates the Genesis Block, 
        and sets up tracking for votes to prevent double voting.
        """
        self.chain = [self.create_genesis_block()]
        self.pending_votes = []    # Votes waiting to be packed into the next block
        self.voted_voters = set()  # A fast lookup set to track who has already voted

    def create_genesis_block(self):
        """
        The very first block in the chain must be created manually 
        since it has no previous block to link to.
        """
        return Block(0, ["Genesis Block - Election Started"], "0")

    def get_latest_block(self):
        """Returns the most recent block added to the chain."""
        return self.chain[-1]

    def add_vote(self, voter_id, vote_data):
        """
        Adds a new vote to the pending pool, but ONLY if the voter hasn't voted yet.
        This explicitly prevents double-voting.
        """
        if voter_id in self.voted_voters:
            return False, "Error: This voter has already cast a vote! Double voting prevented."
        
        # If they haven't voted, record their vote and mark them as 'voted'
        self.pending_votes.append({
            "voter_id": voter_id,
            "vote": vote_data
        })
        self.voted_voters.add(voter_id)
        
        return True, "Vote successfully recorded and is pending confirmation."

    def mine_block(self):
        """
        Takes all pending votes and securely packs them into a new Block,
        linking it to the previous block's hash.
        """
        if not self.pending_votes:
            return False  # No votes to add

        # Create a new block with the pending votes and the previous block's hash
        new_block = Block(
            index=len(self.chain),
            votes=self.pending_votes,
            previous_hash=self.get_latest_block().hash
        )
        
        # Add the block to the chain and clear the pending pool for the next round
        self.chain.append(new_block)
        self.pending_votes = [] 
        
        return new_block

    def is_chain_valid(self):
        """
        The core security check. It sweeps through the entire chain to ensure 
        no block has been altered and all cryptographic links are intact.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # 1. Check if anyone tampered with the data inside the current block
            if current_block.hash != current_block.calculate_hash():
                return False

            # 2. Check if the block correctly links to the previous block
            if current_block.previous_hash != previous_block.hash:
                return False

        return True