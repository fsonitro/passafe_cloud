from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64
import re
from collections import Counter

def derive_key(password: str, pin: str, salt: bytes) -> bytes:
    """
    Derives an encryption key using Scrypt KDF from password and PIN.
    
    Parameters:
        password: User's master password
        pin: User's PIN for additional entropy
        salt: Random bytes for key derivation
    
    Returns:
        32-byte key suitable for AES-256
    """
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

def generate_salt():
    """
    Generates a cryptographically secure random salt.
    
    Returns:
        16 bytes of random data for use as a salt
    """
    return os.urandom(16)

def encrypt_data(key: bytes, plaintext: str) -> dict:
    """
    Encrypts data using AES-GCM authenticated encryption.
    
    Parameters:
        key: 32-byte key derived from password
        plaintext: The data to encrypt
    
    Returns:
        Dictionary containing base64-encoded ciphertext, IV, and authentication tag
    """
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

def decrypt_data(key: bytes, encrypted_data: dict) -> str:
    """
    Decrypts data using AES-GCM authenticated encryption.
    
    Parameters:
        key: 32-byte key derived from password
        encrypted_data: Dict containing ciphertext, IV, and auth tag
    
    Returns:
        Decrypted plaintext string
    
    Raises:
        InvalidTag if authentication fails
    """
    iv = base64.urlsafe_b64decode(encrypted_data['iv'])
    tag = base64.urlsafe_b64decode(encrypted_data['tag'])
    ciphertext = base64.urlsafe_b64decode(encrypted_data['ciphertext'])
    
    decryptor = Cipher(
        algorithms.AES(key),
        modes.GCM(iv, tag),
        backend=default_backend()
    ).decryptor()
    return (decryptor.update(ciphertext) + decryptor.finalize()).decode()

def check_password_strength(password: str) -> str:
    """
    Evaluates password strength based on length and character composition.
    
    Criteria:
    - Weak: Less than 8 characters
    - Moderate: Missing uppercase, numbers, or special characters
    - Strong: 8+ chars with uppercase, numbers, and special characters
    
    Parameters:
        password: Password string to evaluate
    
    Returns:
        'weak', 'moderate', or 'strong'
    """
    if len(password) < 8:
        return 'weak'
    if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
        return 'moderate'
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return 'moderate'
    return 'strong'

def find_reused_passwords(passwords: list) -> list:
    """
    Identifies passwords that are used multiple times.
    
    Parameters:
        passwords: List of passwords to check
    
    Returns:
        List of passwords that appear more than once
    
    Security Note:
        This function should only be used with hashed passwords
        to avoid exposing plaintext passwords in memory
    """
    password_counts = Counter(passwords)
    reused = [password for password, count in password_counts.items() if count > 1]
    return reused
