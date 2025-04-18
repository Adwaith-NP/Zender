from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key

def encrypt_text(text, public_key):
    ciphertext = public_key.encrypt(
        text.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def decrypt_text(ciphertext, private_key):
    plaintext = private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext.decode()

def save_keys(private_key, public_key, private_key_file="private_key.pem", public_key_file="public_key.pem"):
    # Save private key
    with open(private_key_file, "wb") as priv_file:
        priv_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()  # No password
        ))

    # Save public key
    with open(public_key_file, "wb") as pub_file:
        pub_file.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
        
def load_keys(private_key_file="private_key.pem", public_key_file="public_key.pem"):
    # Load private key
    with open(private_key_file, "rb") as priv_file:
        private_key = serialization.load_pem_private_key(
            priv_file.read(),
            password=None
        )

    # Load public key
    with open(public_key_file, "rb") as pub_file:
        public_key = serialization.load_pem_public_key(pub_file.read())

    return private_key, public_key

if __name__ == "__main__":
    private_key, public_key = generate_keys()
    text = "Hello, this is a secret message!"
    print("Original Text:", text)
    save_keys(private_key,public_key)
    encrypted_text = encrypt_text(text, public_key)
    # print("Encrypted Text:", encrypted_text)
    
    decrypted_text = decrypt_text(encrypted_text, private_key)
    print("Decrypted Text:", decrypted_text)
