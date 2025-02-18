from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import re
from collections import Counter

# Key derivation function to generate a unique encryption key from password and PIN
def derive_key(password: str, pin: str, salt: bytes) -> bytes:
    combined_input = f"{password}{pin}".encode()
    kdf = Scrypt(
        salt=salt,
        length=32,  # 32 bytes for AES-256
        n=2**17,
        r=8,
        p=1,
        backend=default_backend()
    )
    return kdf.derive(combined_input)  # Return raw bytes (not base64-encoded)

# Generate a random salt for each user
def generate_salt():
    return os.urandom(16)

# Encrypt data with AES-GCM using the provided key
def encrypt_data(key: bytes, plaintext: str) -> dict:
    iv = os.urandom(16)  # 16 bytes for AES-GCM
    encryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv),
        backend=default_backend()
    ).encryptor()
    ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
    return {
        'ciphertext': base64.urlsafe_b64encode(ciphertext).decode(),
        'iv': base64.urlsafe_b64encode(iv).decode(),
        'tag': base64.urlsafe_b64encode(encryptor.tag).decode()
    }

# Decrypt data with AES-GCM using the provided key and encrypted data
def decrypt_data(key: bytes, encrypted_data: dict) -> str:
    iv = base64.urlsafe_b64decode(encrypted_data['iv'])
    tag = base64.urlsafe_b64decode(encrypted_data['tag'])
    ciphertext = base64.urlsafe_b64decode(encrypted_data['ciphertext'])
    
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    return (decryptor.update(ciphertext) + decryptor.finalize()).decode()

# Check password strength
def check_password_strength(password: str) -> str:
    """
    Evaluate password strength.
    Returns 'weak', 'moderate', or 'strong'.
    """
    if len(password) < 8:
        return 'weak'
    if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
        return 'moderate'
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return 'moderate'
    return 'strong'

# Find reused passwords
def find_reused_passwords(passwords: list) -> list:
    """
    Identify reused passwords in a list.
    Returns a list of passwords reused more than once.
    """
    password_counts = Counter(passwords)
    reused = [password for password, count in password_counts.items() if count > 1]
    return reused
