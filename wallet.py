import hashlib
import re
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

class Wallet:
    def __init__(self, private_key=None, public_key=None):
        """
        Initializes a Wallet. If no keys are provided, generates a new RSA keypair.
        """
        if private_key is None and public_key is None:
            self.private_key = self.generate_new_keypair()
            self.public_key = self.private_key.public_key()
        else:
            self.private_key = private_key
            self.public_key = public_key

    @staticmethod
    def generate_new_keypair():
        """
        Generates a new RSA private key (2048 bits).
        """
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

    def sign_message(self, message: str) -> bytes:
        """
        Signs a string message (e.g., a vote) and returns the signature.
        Combines PSS padding and SHA-256.
        """
        if self.private_key is None:
            raise ValueError("No private key available for signing.")
            
        message_bytes = message.encode('utf-8')
        signature = self.private_key.sign(
            message_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    @staticmethod
    def verify_signature(public_key, message: str, signature: bytes) -> bool:
        """
        Verifies a signature using a given public key.
        Uses PSS.AUTO to detect the actual salt length used during signing.
        This ensures compatibility with the Web Crypto API (JS) which uses saltLength=32
        while Python's sign() uses MAX_LENGTH.
        """
        message_bytes = message.encode('utf-8')
        try:
            public_key.verify(
                signature,
                message_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.AUTO  # Auto-detect salt length from signature
                ),
                hashes.SHA256()
            )
            # If no InvalidSignature exception is raised, the signature is valid
            return True
        except InvalidSignature:
            return False

    def export_private_key_pem(self) -> bytes:
        """
        Exports the private key to PEM format as bytes without encryption for simplicity.
        """
        if self.private_key is None:
            raise ValueError("No private key available to export.")
            
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

    def export_public_key_pem(self) -> bytes:
        """
        Exports the public key to PEM format as bytes.
        """
        if self.public_key is None:
            raise ValueError("No public key available to export.")
            
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def import_private_key_pem(pem_bytes: bytes) -> 'Wallet':
        """
        Imports an unencrypted private key from PEM bytes and returns a new Wallet instance.
        """
        private_key = serialization.load_pem_private_key(
            pem_bytes,
            password=None,
        )
        return Wallet(private_key=private_key, public_key=private_key.public_key())

    @staticmethod
    def import_public_key_pem(pem_bytes: bytes):
        """
        Imports a public key from PEM bytes. Returns the cryptographic key object.
        """
        return serialization.load_pem_public_key(pem_bytes)

    def get_voter_id(self) -> str:
        """
        Hashes the PEM exported public key using SHA-256 to create a reproducible, unique Voter ID.
        """
        if self.public_key is None:
             raise ValueError("No public key available to generate Voter ID.")
             
        public_pem = self.export_public_key_pem()
        stripped_pem = re.sub(b'\s+', b'', public_pem)
        return hashlib.sha256(stripped_pem).hexdigest()
