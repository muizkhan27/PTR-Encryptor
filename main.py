import os
from ptr_encryptor import PTREncryptor

# For quick testing you can set env vars here instead of export:
os.environ.setdefault("ENCRYPTION_KEY", "testkey123456")
os.environ.setdefault("ENCRYPTION_SECRET", "testsecret123456")

obj = {"hello": "world"}
blob = PTREncryptor.get_encrypted_data(obj)
print("Encrypted blob:", blob)

plain = PTREncryptor.get_decrypted_data(blob)
print("Decrypted:", plain)
