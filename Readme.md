# PTREncryptor — Python To Ruby Encryptor

Lightweight, secure AES-GCM encryptor intended to provide compatibility for data interchange between Python and Ruby projects.

PTREncryptor (Python To Ruby Encryptor) offers an easy way to encrypt and decrypt arbitrary Python objects using AES-GCM via PyCryptodome. It serializes data with pickle, derives a 256-bit key with PBKDF2-HMAC-SHA1 from two environment variables, and emits a simple three-part base64 blob: <ciphertext>--<nonce>--<tag>.

## Why this library

- Simple: one-file implementation and a tiny public API.
- Safe defaults: AES GCM with a 12-byte nonce and 128-bit tag.
- Interoperable: the compact base64 blob can be transported in text channels.

> Note: The library uses Python's `pickle` to preserve arbitrary Python objects. Do not decrypt untrusted data — use JSON or another safe format for data received from external parties.

## Quick start

Prerequisites

- Python 3.8+ (works with 3.11 as tested)
- PyCryptodome
- python-dotenv (optional, for local .env files)

Install dependencies (use the same python interpreter you'll run the script with):

```bash
python3 -m pip install --upgrade pycryptodome python-dotenv
```

Set environment variables (example using an interactive shell or a `.env` file):

```bash
export ENCRYPTION_KEY="my-secret-key"
export ENCRYPTION_SECRET="my-secret-salt"
```

Or create a `.env` file at repo root with:

```
ENCRYPTION_KEY=testkey123456
ENCRYPTION_SECRET=testsecret123456
```

Run the example `main.py` included in this repo:

```bash
python3 main.py
```

You should see an encrypted blob printed and, immediately after, the decrypted Python object.

## API

Public class: `PTREncryptor` (in `ptr_encryptor.py`)

- `PTREncryptor.get_encrypted_data(data) -> str`
	- Serializes `data` with `pickle` and returns a single string: `<ct_b64>--<nonce_b64>--<tag_b64>`.

- `PTREncryptor.get_decrypted_data(blob) -> object`
	- Accepts a blob produced by `get_encrypted_data` and returns the original Python object.
	- Raises `ValueError` on malformed input or authentication failures.

Key derivation

The implementation derives a 32-byte (256-bit) AES key using PBKDF2-HMAC-SHA1 with 65,536 iterations from `ENCRYPTION_KEY` and `ENCRYPTION_SECRET` environment variables.

## Security notes & recommendations

- Pickle is powerful but unsafe for untrusted input. Never feed ciphertext from an untrusted source into `get_decrypted_data`.
- Consider using a safer serialization format (JSON, msgpack) if you need to decrypt untrusted or cross-language data.
- For new projects consider a stronger KDF (PBKDF2-SHA256, scrypt, or Argon2) and storing secrets in a secure secrets manager rather than raw environment variables.
- Use long, high-entropy values for `ENCRYPTION_KEY` and `ENCRYPTION_SECRET`.

## Troubleshooting

- ImportError: `No module named Crypto`
	- Install PyCryptodome (use the same interpreter as your project):

		```bash
		python3 -m pip install --upgrade pycryptodome
		```

	- Verify the package and location:

		```bash
		python3 -c "import Crypto; print(Crypto.__file__)"
		python3 -c "from Crypto.Cipher import AES; print('AES OK')"
		```

	- Common root causes:
		- A local file named `crypto.py` or a directory `Crypto/` shadowing the package. Remove or rename it.
		- Having the old `pycrypto` package installed. If present, uninstall it:

			```bash
			python3 -m pip uninstall pycrypto
			```

- Virtualenv / interpreter mismatch
	- If you see imports that work in one shell but not another, activate the same virtual environment used to install packages.

		```bash
		# macOS / zsh example
		source /path/to/venv/bin/activate
		python -c "from Crypto.Cipher import AES; print('OK')"
		```

- Verifying ENCRYPTION_KEY / ENCRYPTION_SECRET
	- Ensure both env vars are set in the environment where `main.py` or your app runs:

		```bash
		echo "$ENCRYPTION_KEY" "$ENCRYPTION_SECRET"
		# or
		python3 -c "import os; print(os.getenv('ENCRYPTION_KEY'), os.getenv('ENCRYPTION_SECRET'))"
		```

- `ValueError: Invalid encrypted data format`
	- The blob must be exactly three base64 parts separated by `--` (two dashes). Quick check:

		```bash
		python3 - <<'PY'
		blob = '...your blob here...'
		parts = blob.split('--')
		print('parts', len(parts))
		PY
		```

- `ValueError: Decryption failed or authentication tag is invalid`
	- Common causes: wrong key/secret, truncated/corrupted blob, or tampering.
	- Reproduce and inspect by encrypting + immediately decrypting in the same environment (sanity check):

		```bash
		python3 - <<'PY'
		from ptr_encryptor import PTREncryptor
		import os
		os.environ.setdefault('ENCRYPTION_KEY','testkey123456')
		os.environ.setdefault('ENCRYPTION_SECRET','testsecret123456')
		blob = PTREncryptor.get_encrypted_data({'x':1})
		print('blob', blob)
		print('plain', PTREncryptor.get_decrypted_data(blob))
		PY
		```

	- If this round-trip fails, confirm the KDF-derived key is stable and your env vars are accessible to the running process.

If you want, I can add a small `scripts/verify_env.sh` or tests that run these checks automatically.

## Example

main.py in this repo demonstrates a minimal example:

```python
import os
from ptr_encryptor import PTREncryptor

os.environ.setdefault("ENCRYPTION_KEY", "testkey123456")
os.environ.setdefault("ENCRYPTION_SECRET", "testsecret123456")

obj = {"hello": "world"}
blob = PTREncryptor.get_encrypted_data(obj)
print("Encrypted blob:", blob)

plain = PTREncryptor.get_decrypted_data(blob)
print("Decrypted:", plain)
```

## Development notes

- Tested on macOS with Python 3.11.
- If you plan to package this, rename the file to a package module and publish with proper versioning.

## Next steps (optional)

- Add a JSON-safe API to avoid pickle for external input.
- Add unit tests that validate round-trip encryption and authentication failure cases.
- Consider switching KDF to PBKDF2-SHA256 or Argon2 and exposing iteration count via env/config.

---

If you'd like, I can also add a `.env.example`, unit tests, or switch `pickle` to `json` (with limited object support). Tell me which next step you prefer.

## Testing

Run the unit tests with the same Python interpreter you use to run the project. This repository includes `pytest` tests under `tests/` that verify round-trip encryption, handling of malformed blobs, and authentication failure scenarios.

Install test/runtime dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run tests:

```bash
python3 -m pytest -q
```

If you prefer not to install globally, create and activate a virtualenv first:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 -m pytest -q
```

