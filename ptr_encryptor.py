import base64
import hashlib
import os
import pickle

from Crypto.Cipher import AES
from dotenv import load_dotenv

load_dotenv()

class PTREncryptor:
    """
    Python3 encryptor.
    - Uses PyCryptodome AES-GCM correctly (encrypt_and_digest / decrypt_and_verify).
    - Uses pickle for serialization instead of rubymarshal.
    """

    @classmethod
    def get_encrypted_data(cls, data):
        """
        Serialize `data` with pickle and return a blob: "<ciphertext_b64>--<iv_b64>--<tag_b64>"
        """
        key = cls.get_key()
        plaintext = pickle.dumps(data, protocol=3)
        nonce = os.urandom(12)  # recommended size for GCM
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)

        return (
            f"{base64.b64encode(ciphertext).decode('utf-8')}"
            f"--{base64.b64encode(nonce).decode('utf-8')}"
            f"--{base64.b64encode(tag).decode('utf-8')}"
        )

    @classmethod
    def get_decrypted_data(cls, blob):
        """
        Decrypt a blob produced by get_encrypted_data and return the original Python object.
        Raises ValueError on malformed input or authentication failure.
        """
        key = cls.get_key()
        try:
            ct_b64, nonce_b64, tag_b64 = blob.split("--")
        except ValueError:
            raise ValueError("Invalid encrypted data format; expected '<ct>--<iv>--<tag>'")

        ciphertext = base64.b64decode(ct_b64)
        nonce = base64.b64decode(nonce_b64)
        tag = base64.b64decode(tag_b64)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        try:
            plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        except (ValueError, KeyError) as exc:
            raise ValueError("Decryption failed or authentication tag is invalid") from exc

        return pickle.loads(plaintext)

    @classmethod
    def get_key(cls):
        """
        Derive a 32-byte key using PBKDF2-HMAC-SHA1 from ENCRYPTION_KEY and ENCRYPTION_SECRET env vars.
        """
        enc_key = os.getenv("ENCRYPTION_KEY")
        enc_secret = os.getenv("ENCRYPTION_SECRET")
        if not enc_key or not enc_secret:
            raise EnvironmentError("ENCRYPTION_KEY and ENCRYPTION_SECRET must be set in the environment")
        return hashlib.pbkdf2_hmac(
            "sha1",
            enc_key.encode("utf-8"),
            enc_secret.encode("utf-8"),
            65536,
            32,
        )
