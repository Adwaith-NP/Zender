from cryptography.fernet import Fernet
from hashlib import sha256
import base64

def derive_key(password: str) -> bytes:
    """
    Derives a key from the given password using SHA-256.
    """
    return base64.urlsafe_b64encode(sha256(password.encode()).digest())

def encrypt_file(input_file: str, output_file: str, password: str):
    key = derive_key(password)
    cipher = Fernet(key)
    
    with open(input_file, 'rb') as f:
        file_data = f.read()
    
    encrypted_data = cipher.encrypt(file_data)
    
    with open(output_file, 'wb') as f:
        f.write(encrypted_data)
    
    print(f"File '{input_file}' encrypted and saved as '{output_file}'.")

def decrypt_file(input_file: str, output_file: str, password: str):
    key = derive_key(password)
    cipher = Fernet(key)
    
    with open(input_file, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = cipher.decrypt(encrypted_data)
    
    with open(output_file, 'wb') as f:
        f.write(decrypted_data)
    
    print(f"File '{input_file}' decrypted and saved as '{output_file}'.")

if __name__ == "__main__":
    action = input("Enter 'encrypt' or 'decrypt': ").strip().lower()
    input_file = input("Enter input file path: ").strip()
    output_file = input("Enter output file path: ").strip()
    password = input("Enter password: ").strip()
    
    if action == 'encrypt':
        encrypt_file(input_file, output_file, password)
    elif action == 'decrypt':
        decrypt_file(input_file, output_file, password)
    else:
        print("Invalid action. Please enter 'encrypt' or 'decrypt'.")
