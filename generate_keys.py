import os
from wallet import Wallet

def generate():
    print("Generating a new secure 2048-bit RSA keypair for voting...")
    
    # Instantiate a new wallet which automatically generates the keys
    user_wallet = Wallet()
    
    # Export the keys in standard PEM format bytes
    private_pem_bytes = user_wallet.export_private_key_pem()
    public_pem_bytes = user_wallet.export_public_key_pem()
    
    # Write them to disk so they can be easily uploaded in the browser
    with open("private_key.pem", "wb") as priv_file:
        priv_file.write(private_pem_bytes)
        
    with open("public_key.pem", "wb") as pub_file:
        pub_file.write(public_pem_bytes)
        
    print("\n✅ Successfully generated keys!")
    print(f"🔑 Private Key saved to: {os.path.abspath('private_key.pem')}")
    print(f"🌍 Public Key saved to:  {os.path.abspath('public_key.pem')}")
    print("\nGo to http://localhost:8000 and upload these two files to authenticate!")

if __name__ == "__main__":
    generate()
