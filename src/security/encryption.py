"""
File encryption utilities for secure CV storage
Uses AES encryption via Fernet (symmetric encryption)
"""

import os
from pathlib import Path
from typing import Union, Optional
import logging
from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class FileEncryption:
    """
    Handle file encryption and decryption for CV documents
    Uses Fernet (symmetric encryption) for secure file storage
    """
    
    def __init__(self, encryption_key: Optional[bytes] = None):
        """
        Initialize file encryption
        
        Args:
            encryption_key: 32-byte encryption key (base64 encoded). 
                          If None, will get from secrets manager
        """
        if encryption_key:
            self.key = encryption_key
        else:
            # Get from secrets manager
            from .secrets_manager import get_secrets_manager
            secrets_mgr = get_secrets_manager()
            self.key = secrets_mgr.get_encryption_key()
        
        try:
            self.cipher = Fernet(self.key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise ValueError("Invalid encryption key")
    
    def encrypt_file(self, file_path: Union[str, Path]) -> Path:
        """
        Encrypt a file in place
        
        Args:
            file_path: Path to file to encrypt
            
        Returns:
            Path to encrypted file (with .enc extension)
            
        Raises:
            FileNotFoundError: If file doesn't exist
            IOError: If encryption fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            # Read file content
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encrypt
            encrypted_data = self.cipher.encrypt(data)
            
            # Write to encrypted file
            encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"File encrypted: {file_path} -> {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            logger.error(f"Encryption failed for {file_path}: {e}")
            raise IOError(f"Failed to encrypt file: {e}")
    
    def decrypt_file(self, encrypted_path: Union[str, Path], output_path: Optional[Union[str, Path]] = None) -> Path:
        """
        Decrypt an encrypted file
        
        Args:
            encrypted_path: Path to encrypted file
            output_path: Output path (default: remove .enc extension)
            
        Returns:
            Path to decrypted file
            
        Raises:
            FileNotFoundError: If encrypted file doesn't exist
            InvalidToken: If decryption fails (wrong key or corrupted)
            IOError: If decryption fails
        """
        encrypted_path = Path(encrypted_path)
        
        if not encrypted_path.exists():
            raise FileNotFoundError(f"Encrypted file not found: {encrypted_path}")
        
        # Determine output path
        if output_path is None:
            if encrypted_path.suffix == '.enc':
                output_path = encrypted_path.with_suffix('')
            else:
                output_path = encrypted_path.with_suffix('.decrypted')
        else:
            output_path = Path(output_path)
        
        try:
            # Read encrypted data
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"File decrypted: {encrypted_path} -> {output_path}")
            return output_path
            
        except InvalidToken:
            logger.error(f"Decryption failed for {encrypted_path}: Invalid key or corrupted file")
            raise InvalidToken("Invalid encryption key or file is corrupted")
        except Exception as e:
            logger.error(f"Decryption failed for {encrypted_path}: {e}")
            raise IOError(f"Failed to decrypt file: {e}")
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
        Encrypt raw bytes data
        
        Args:
            data: Raw bytes to encrypt
            
        Returns:
            Encrypted bytes
        """
        try:
            return self.cipher.encrypt(data)
        except Exception as e:
            logger.error(f"Data encryption failed: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt raw bytes data
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            Decrypted bytes
        """
        try:
            return self.cipher.decrypt(encrypted_data)
        except InvalidToken:
            logger.error("Data decryption failed: Invalid key or corrupted data")
            raise InvalidToken("Invalid encryption key or data is corrupted")
        except Exception as e:
            logger.error(f"Data decryption failed: {e}")
            raise
    
    @staticmethod
    def generate_key() -> bytes:
        """
        Generate a new encryption key
        
        Returns:
            32-byte encryption key (base64 encoded)
        """
        return Fernet.generate_key()
    
    @staticmethod
    def save_key(key: bytes, key_file: Union[str, Path]):
        """
        Save encryption key to file
        
        Args:
            key: Encryption key
            key_file: Path to save key
        """
        key_file = Path(key_file)
        key_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(key_file, 'wb') as f:
            f.write(key)
        
        # Set restrictive permissions (owner only)
        os.chmod(key_file, 0o600)
        logger.info(f"Encryption key saved to {key_file}")
    
    @staticmethod
    def load_key(key_file: Union[str, Path]) -> bytes:
        """
        Load encryption key from file
        
        Args:
            key_file: Path to key file
            
        Returns:
            Encryption key
        """
        key_file = Path(key_file)
        
        if not key_file.exists():
            raise FileNotFoundError(f"Key file not found: {key_file}")
        
        with open(key_file, 'rb') as f:
            key = f.read()
        
        logger.info(f"Encryption key loaded from {key_file}")
        return key


# Convenience functions
def encrypt_file(file_path: Union[str, Path], encryption_key: Optional[bytes] = None) -> Path:
    """
    Convenience function to encrypt a file
    
    Args:
        file_path: Path to file to encrypt
        encryption_key: Optional encryption key
        
    Returns:
        Path to encrypted file
    """
    encryptor = FileEncryption(encryption_key)
    return encryptor.encrypt_file(file_path)


def decrypt_file(encrypted_path: Union[str, Path], 
                output_path: Optional[Union[str, Path]] = None,
                encryption_key: Optional[bytes] = None) -> Path:
    """
    Convenience function to decrypt a file
    
    Args:
        encrypted_path: Path to encrypted file
        output_path: Optional output path
        encryption_key: Optional encryption key
        
    Returns:
        Path to decrypted file
    """
    encryptor = FileEncryption(encryption_key)
    return encryptor.decrypt_file(encrypted_path, output_path)


def generate_and_save_key(key_file: Union[str, Path]) -> bytes:
    """
    Generate a new encryption key and save it
    
    Args:
        key_file: Path to save key
        
    Returns:
        Generated encryption key
    """
    key = FileEncryption.generate_key()
    FileEncryption.save_key(key, key_file)
    return key
