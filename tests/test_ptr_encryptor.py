import os
import pytest
from ptr_encryptor import PTREncryptor


def setup_module(module):
    # Ensure deterministic env for tests
    os.environ['ENCRYPTION_KEY'] = 'testkey123456'
    os.environ['ENCRYPTION_SECRET'] = 'testsecret123456'


def test_round_trip_basic():
    obj = {'a': 1, 'b': 'x'}
    blob = PTREncryptor.get_encrypted_data(obj)
    assert isinstance(blob, str)
    got = PTREncryptor.get_decrypted_data(blob)
    assert got == obj


def test_invalid_format_raises():
    with pytest.raises(ValueError):
        PTREncryptor.get_decrypted_data('not-a-valid-blob')


def test_tampered_blob_fails_auth():
    obj = {'k': 'v'}
    blob = PTREncryptor.get_encrypted_data(obj)
    # tamper: flip a byte in the ciphertext portion
    parts = blob.split('--')
    assert len(parts) == 3
    ct = bytearray(__import__('base64').b64decode(parts[0]))
    ct[0] = (ct[0] + 1) % 256
    parts[0] = __import__('base64').b64encode(bytes(ct)).decode('utf-8')
    tampered = '--'.join(parts)
    with pytest.raises(ValueError):
        PTREncryptor.get_decrypted_data(tampered)


def test_wrong_key_fails_auth(monkeypatch):
    obj = {'z': 3}
    blob = PTREncryptor.get_encrypted_data(obj)
    # change env to a wrong key
    monkeypatch.setenv('ENCRYPTION_KEY', 'wrongkey')
    with pytest.raises(ValueError):
        PTREncryptor.get_decrypted_data(blob)
