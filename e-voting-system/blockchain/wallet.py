from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
import json
import base64

class Wallet:
    def __init__(self):
        """
        Automatically generates a new RSA public/private key pair 
        as soon as a new Wallet is created for a voter.
        """
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_string(self):
        """
        Converts the public key into a readable string format (PEM) 
        so it can be easily stored or transmitted over the web.
        """
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def sign_vote(self, vote_data):
        """
        Uses the voter's private key to create a unique digital signature for their vote.
        If anyone alters the vote_data later, this signature will become invalid.
        """
        # Convert the vote dictionary into a standardized, sort-ordered string
        vote_string = json.dumps(vote_data, sort_keys=True).encode('utf-8')
        
        # Create the cryptographic signature using SHA-256
        signature = self.private_key.sign(
            vote_string,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        # Return the signature as a base64 encoded string so it's easy to store in JSON
        return base64.b64encode(signature).decode('utf-8')

    @staticmethod
    def verify_signature(public_key_string, signature_base64, vote_data):
        """
        A static method that the Blockchain can use to verify a vote.
        It checks if the signature matches the vote data using the voter's public key.
        """
        try:
            # 1. Reconstruct the public key from the string
            public_key = serialization.load_pem_public_key(
                public_key_string.encode('utf-8')
            )
            
            # 2. Decode the signature back into bytes
            signature_bytes = base64.b64decode(signature_base64)
            
            # 3. Standardize the vote data back into a string
            vote_string = json.dumps(vote_data, sort_keys=True).encode('utf-8')
            
            # 4. Verify the signature
            public_key.verify(
                signature_bytes,
                vote_string,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True # If no error is thrown, the signature is 100% valid!
            
        except InvalidSignature:
            return False # The signature was fake or the vote was tampered with
        except Exception as e:
            return False # Something else went wrong (e.g., malformed data)