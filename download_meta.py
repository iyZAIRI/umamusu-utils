#!/usr/bin/env python3
"""Download the Android version of the Uma Musume meta file"""
import urllib.request
from pathlib import Path

META_URL = "https://github.com/hker9527/umeta/raw/master/meta"
META_PATH = Path("./meta")

def download_meta():
    """Download the meta file from the Android version repository"""
    print(f"Downloading meta file from {META_URL}...")
    print("This may take a while as the file is ~50MB...")

    try:
        urllib.request.urlretrieve(META_URL, META_PATH)
        print(f"\n✓ Successfully downloaded meta file to: {META_PATH}")
        print(f"  File size: {META_PATH.stat().st_size / 1024 / 1024:.2f} MB")

        # Verify it's a valid SQLite database
        with open(META_PATH, 'rb') as f:
            header = f.read(16)

        if header.startswith(b'SQLite format 3'):
            print("\n✓ Verified: This is a valid SQLite database file")
            print("\nYou can now run:")
            print("  uv run main.py assets dump --kind supportcard skill")
        else:
            print("\n✗ Warning: File doesn't appear to be a standard SQLite database")
            print(f"  Header: {header[:16].hex()}")

    except Exception as e:
        print(f"\n✗ Error downloading meta file: {e}")
        print("\nAlternative: Manually download from:")
        print(f"  {META_URL}")
        print(f"  Save to: {META_PATH.absolute()}")

if __name__ == "__main__":
    if META_PATH.exists():
        response = input(f"Meta file already exists at {META_PATH}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled.")
            exit(0)

    download_meta()
