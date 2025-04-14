import argparse
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_file(file_path: str, password: str):
    salt = os.urandom(16)
    key = generate_key_from_password(password, salt)
    fernet = Fernet(key)

    with open(file_path, 'rb') as f:
        data = f.read()
    encrypted = fernet.encrypt(data)

    with open(file_path + ".enc", 'wb') as f:
        f.write(salt + encrypted)

    print(f"[+] Encrypted: {file_path} -> {file_path}.enc")

def decrypt_file(enc_file_path: str, password: str):
    with open(enc_file_path, 'rb') as f:
        content = f.read()
    salt = content[:16]
    encrypted = content[16:]
    key = generate_key_from_password(password, salt)
    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted)

    out_path = enc_file_path.replace(".enc", ".dec")
    with open(out_path, 'wb') as f:
        f.write(decrypted)

    print(f"[+] Decrypted: {enc_file_path} -> {out_path}")

def main():
    parser = argparse.ArgumentParser(description="Encrypt or decrypt a file using a password.")
    parser.add_argument("mode", choices=["encrypt", "decrypt"], help="Mode: encrypt or decrypt")
    parser.add_argument("file", help="File path to encrypt or decrypt")
    parser.add_argument("password", help="Password to use for encryption/decryption")

    args = parser.parse_args()

    if args.mode == "encrypt":
        encrypt_file(args.file, args.password)
    elif args.mode == "decrypt":
        decrypt_file(args.file, args.password)

if __name__ == "__main__":
    main()
