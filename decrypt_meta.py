#!/usr/bin/env python3
"""
Decrypt Uma Musume PC meta file

The PC version encrypts the meta file using SQLCipher with a custom key.
This script decrypts it and saves an unencrypted version.

Requirements:
- Linux/macOS: sqlcipher command-line tool (apt-get install sqlcipher / brew install sqlcipher)
- NOT recommended for Windows (use download_meta.py instead)

Keys extracted from: https://github.com/daydreamer-json/uma-db-stuff
"""
import subprocess
from pathlib import Path


def generate_decryption_key():
    """Generate the decryption key by XORing plainKey and baseKey"""
    # Keys from uma-db-stuff config
    base_key_hex = 'f170cea4dfcea3e1a5d8c70bd1'
    plain_key_hex = '6d5b65336336632554712d73505363386d34377b356370233734532973433633'

    # Convert hex strings to bytes
    base_key = bytes.fromhex(base_key_hex)
    plain_key = bytes.fromhex(plain_key_hex)

    # XOR operation
    result = bytearray(len(plain_key))
    for i in range(len(plain_key)):
        result[i] = plain_key[i] ^ base_key[i % len(base_key)]

    return result


def decrypt_meta_with_sqlcipher(encrypted_path, decrypted_path):
    """Decrypt the meta file using sqlcipher command line tool"""
    key = generate_decryption_key()
    key_hex = key.hex()

    print(f"Decrypting {encrypted_path} -> {decrypted_path}")
    print(f"Using decryption key (hex): {key_hex}")

    # Use sqlcipher command line tool
    sql_commands = f"""
PRAGMA cipher_compatibility = 4;
PRAGMA key = "x'{key_hex}'";
ATTACH DATABASE '{decrypted_path}' AS plaintext KEY '';
SELECT sqlcipher_export('plaintext');
DETACH DATABASE plaintext;
"""

    try:
        result = subprocess.run(
            ['sqlcipher', str(encrypted_path)],
            input=sql_commands,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ Successfully decrypted meta file!")
        print(f"  Saved to: {decrypted_path}")
        return True
    except FileNotFoundError:
        print("✗ Error: sqlcipher not found")
        print("\nPlease install sqlcipher:")
        print("  Windows: Download from https://www.zetetic.net/sqlcipher/open-source/")
        print("  Linux: sudo apt-get install sqlcipher")
        print("  macOS: brew install sqlcipher")
        return False
    except subprocess.CalledProcessError as e:
        print(f"✗ Error decrypting database: {e}")
        print(f"  stdout: {e.stdout}")
        print(f"  stderr: {e.stderr}")
        return False




if __name__ == "__main__":
    import platform

    # Check if Windows
    if platform.system() == "Windows":
        print("=== Windows Not Supported ===\n")
        print("SQLCipher decryption on Windows requires complex setup.")
        print("\n✓ Recommended: Use the Android meta file instead:")
        print("  uv run python download_meta.py")
        print("\nThis is easier and works reliably on Windows.")
        exit(1)

    encrypted_path = Path("./meta")
    decrypted_path = Path("./meta_decrypted")

    if not encrypted_path.exists():
        print(f"✗ Error: meta file not found at {encrypted_path}")
        print("\nPlease copy your PC meta file to the project directory")
        exit(1)

    if decrypted_path.exists():
        response = input(f"Decrypted meta already exists at {decrypted_path}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            exit(0)

    print("=== Uma Musume Meta Decryption ===\n")
    print("Using sqlcipher command line tool...")

    if decrypt_meta_with_sqlcipher(encrypted_path, decrypted_path):
        print("\n✓ Done! You can now use the decrypted meta file:")
        print(f"  mv {decrypted_path} meta")
        print("  uv run main.py assets dump --kind supportcard")
    else:
        print("\n✗ Decryption failed")
        print("\nPlease ensure sqlcipher is installed:")
        print("  Linux: sudo apt-get install sqlcipher")
        print("  macOS: brew install sqlcipher")
