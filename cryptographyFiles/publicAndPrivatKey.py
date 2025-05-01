from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    return private_key, public_key


def save_keys(private_key, public_key, private_key_file, public_key_file):
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
        

def createNewKey(private_key_file,public_key_file):
    private_key, public_key = generate_keys()
    save_keys(private_key,public_key,private_key_file,public_key_file)
