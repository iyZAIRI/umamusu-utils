#!/usr/bin/env python3
"""
Test different SQLCipher configurations to decrypt Uma Musume meta file
"""
import subprocess
from pathlib import Path


def generate_decryption_key():
    """Generate the decryption key by XORing plainKey and baseKey"""
    base_key_hex = 'f170cea4dfcea3e1a5d8c70bd1'
    plain_key_hex = '6d5b65336336632554712d73505363386d34377b356370233734532973433633'

    base_key = bytes.fromhex(base_key_hex)
    plain_key = bytes.fromhex(plain_key_hex)

    result = bytearray(len(plain_key))
    for i in range(len(plain_key)):
        result[i] = plain_key[i] ^ base_key[i % len(base_key)]

    return bytes(result)


def test_decrypt(encrypted_path, compatibility_version, key_format):
    """Try to decrypt with specific settings"""
    key = generate_decryption_key()
    key_hex = key.hex()

    test_db = Path(f"test_v{compatibility_version}_{key_format}.db")

    if key_format == "hexkey":
        key_pragma = f"PRAGMA hexkey = '{key_hex}';"
    elif key_format == "key_hex":
        key_pragma = f"PRAGMA key = \"x'{key_hex}'\";"
    else:  # raw
        key_pragma = f"PRAGMA key = '{key_hex}';"

    sql_commands = f"""
PRAGMA cipher_compatibility = {compatibility_version};
{key_pragma}
SELECT count(*) FROM sqlite_master;
.quit
"""

    try:
        result = subprocess.run(
            ['sqlcipher', str(encrypted_path)],
            input=sql_commands,
            capture_output=True,
            text=True,
            timeout=5
        )

        # Check if query succeeded
        if result.returncode == 0 and "file is not a database" not in result.stderr:
            print(f"✓ SUCCESS with compatibility={compatibility_version}, format={key_format}")
            print(f"  Output: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ Failed: compatibility={compatibility_version}, format={key_format}")
            if result.stderr:
                print(f"  Error: {result.stderr.split(chr(10))[0]}")
            return False

    except Exception as e:
        print(f"✗ Error: compatibility={compatibility_version}, format={key_format}: {e}")
        return False


if __name__ == "__main__":
    encrypted_path = Path("./meta")

    if not encrypted_path.exists():
        print("✗ meta file not found")
        exit(1)

    print("=== Testing SQLCipher Decryption Configurations ===\n")
    print(f"Key: {generate_decryption_key().hex()}\n")

    # Try different compatibility versions and key formats
    for compat in [1, 2, 3, 4]:
        for key_fmt in ["hexkey", "key_hex", "raw"]:
            test_decrypt(encrypted_path, compat, key_fmt)

    print("\n=== Test Complete ===")
