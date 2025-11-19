#!/usr/bin/env python3
"""Check how many assets from meta file exist in the local dat folder"""
import sqlite3
from pathlib import Path

def check_hash_match():
    """Check if meta file hashes match local dat files"""
    meta_path = Path("./meta")
    appdata_path = Path.home() / "AppData/LocalLow/Cygames/Umamusume"
    dat_path = appdata_path / "dat"

    if not meta_path.exists():
        print("Error: meta file not found")
        return

    if not dat_path.exists():
        print(f"Error: dat folder not found at {dat_path}")
        return

    print("=== Hash Match Check ===\n")
    print("Checking if meta file hashes match your PC installation...\n")

    conn = sqlite3.connect(meta_path)
    cursor = conn.cursor()

    # Check supportcard specifically
    cursor.execute("SELECT n, h, m FROM a WHERE m = 'supportcard' LIMIT 100")
    rows = cursor.fetchall()

    found = 0
    missing = 0
    missing_examples = []

    for path, hash_val, kind in rows:
        asset_file = dat_path / hash_val[:2] / hash_val
        if asset_file.exists():
            found += 1
        else:
            missing += 1
            if len(missing_examples) < 5:
                missing_examples.append((path, hash_val))

    print(f"Checked: {len(rows)} supportcard assets")
    print(f"✓ Found: {found} ({found/len(rows)*100:.1f}%)")
    print(f"✗ Missing: {missing} ({missing/len(rows)*100:.1f}%)")

    if missing > 0:
        print("\n=== Problem Identified ===")
        print("The Android meta file references assets that don't exist in your")
        print("PC installation. This happens when the Android and PC versions are")
        print("out of sync.")
        print("\nMissing asset examples:")
        for path, hash_val in missing_examples:
            print(f"  - {path}")
            print(f"    Hash: {hash_val}")
            print(f"    Expected: {dat_path / hash_val[:2] / hash_val}")

        print("\n=== Solution ===")
        print("You need to use the meta file from your PC installation instead.")
        print("However, the PC version encrypts the meta file.")
        print("\nOptions:")
        print("1. Decrypt the PC meta file (requires reverse engineering)")
        print("2. Wait for the Android meta file to be updated")
        print("3. Use asset downloading instead (TODO in the project)")
    else:
        print("\n✓ All checked assets exist! The extraction should work.")

    conn.close()

if __name__ == "__main__":
    check_hash_match()
