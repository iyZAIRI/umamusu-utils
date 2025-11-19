#!/usr/bin/env python3
"""Diagnostic script to check the meta file format"""
import sys
from pathlib import Path

def check_file(filepath):
    """Check if file is a valid SQLite database and show file info"""
    path = Path(filepath)

    if not path.exists():
        print(f"Error: File does not exist: {path}")
        return

    # Read first bytes to check file signature
    with open(path, 'rb') as f:
        header = f.read(100)

    print(f"File: {path}")
    print(f"Size: {path.stat().st_size} bytes")
    print(f"\nFirst 16 bytes (hex): {header[:16].hex()}")
    print(f"First 16 bytes (ascii): {header[:16]}")

    # SQLite3 database files start with "SQLite format 3\x00"
    if header.startswith(b'SQLite format 3'):
        print("\n✓ This appears to be a valid SQLite database file")

        # Try to open it
        import sqlite3
        try:
            conn = sqlite3.connect(path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"\nTables found: {[t[0] for t in tables]}")

            # Check the 'a' table structure if it exists
            if any(t[0] == 'a' for t in tables):
                cursor.execute("PRAGMA table_info(a);")
                columns = cursor.fetchall()
                print(f"\nTable 'a' structure:")
                for col in columns:
                    print(f"  {col[1]} ({col[2]})")

            conn.close()
        except Exception as e:
            print(f"\n✗ Error opening as SQLite: {e}")
    else:
        print("\n✗ This does NOT appear to be a SQLite database file")
        print("   It might be encrypted or in a different format")

        # Check for common file signatures
        if header[:4] == b'\x50\x4b\x03\x04':
            print("   Looks like a ZIP file")
        elif header[:2] == b'\x1f\x8b':
            print("   Looks like a GZIP file")
        elif header[:4] == b'\x04\x22\x4d\x18':
            print("   Looks like an LZ4 file")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_meta.py <path-to-meta-file>")
        print("\nExample:")
        print("  python check_meta.py meta")
        print("  python check_meta.py 'C:\\Users\\mega\\AppData\\LocalLow\\Cygames\\Umamusume\\meta'")
        sys.exit(1)

    check_file(sys.argv[1])
