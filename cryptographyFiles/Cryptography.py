from cryptography.fernet import Fernet
from hashlib import sha256
import base64
import os
from pathlib import Path

class Cryptography:
    def __init__(self,path = None):
        self.encryptDir = path
    def derive_key(self,password: str) -> bytes:
        """
        Derives a key from the given password using SHA-256.
        """
        return base64.urlsafe_b64encode(sha256(password.encode()).digest())

    def encrypt_file(self,input_file: str, output_file: str, password: str):
        filePath = os.path.join(self.encryptDir,output_file)
        key = self.derive_key(password)
        cipher = Fernet(key)
        
        with open(input_file, 'rb') as f:
            file_data = f.read()
        
        encrypted_data = cipher.encrypt(file_data)
        
        with open(filePath, 'wb') as f:
            f.write(encrypted_data)
        
        size_bytes = os.path.getsize(filePath)
        if size_bytes/(1024 * 1024) > 1:
            filesize = "{:.2f} MB".format(size_bytes / (1024 * 1024))
        else:
            filesize = "{:.2f} KB".format(size_bytes / (1024))
        return filesize
        

    def decrypt_file(self,filePath,fileName,password ):
        
        home_dir = Path.home()
        downloads_dir = home_dir / 'Downloads' / fileName
        
        key = self.derive_key(password)
        cipher = Fernet(key)
        
        with open(filePath, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = cipher.decrypt(encrypted_data)
        
        with open(downloads_dir, 'wb') as f:
            f.write(decrypted_data)

    # if __name__ == "__main__":
    #     action = input("Enter 'encrypt' or 'decrypt': ").strip().lower()
    #     input_file = input("Enter input file path: ").strip()
    #     output_file = input("Enter output file path: ").strip()
    #     password = input("Enter password: ").strip()
        
    #     if action == 'encrypt':
    #         encrypt_file(input_file, output_file, password)
    #     elif action == 'decrypt':
    #         decrypt_file(input_file, output_file, password)
    #     else:
    #         print("Invalid action. Please enter 'encrypt' or 'decrypt'.")
