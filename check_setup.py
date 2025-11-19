#!/usr/bin/env python3
"""Check if all required files and folders exist for asset extraction"""
import sqlite3
from pathlib import Path

def check_setup():
    """Verify the extraction environment is set up correctly"""
    print("=== Uma Musume Utils Setup Check ===\n")

    issues = []

    # Check 1: meta file
    meta_path = Path("./meta")
    print(f"1. Checking meta file: {meta_path}")
    if meta_path.exists():
        size_mb = meta_path.stat().st_size / 1024 / 1024
        print(f"   ✓ Meta file exists ({size_mb:.2f} MB)")

        # Try to open as SQLite
        try:
            conn = sqlite3.connect(meta_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM a")
            count = cursor.fetchone()[0]
            print(f"   ✓ Meta database is valid ({count:,} asset entries)")

            # Show some sample entries
            cursor.execute("SELECT m, COUNT(*) as cnt FROM a GROUP BY m ORDER BY cnt DESC LIMIT 5")
            print(f"   Asset types in database:")
            for kind, cnt in cursor.fetchall():
                print(f"     - {kind}: {cnt:,} files")

            conn.close()
        except Exception as e:
            print(f"   ✗ Error reading meta database: {e}")
            issues.append("Meta file is not a valid SQLite database")
    else:
        print(f"   ✗ Meta file not found")
        print(f"   Run: uv run python download_meta.py")
        issues.append("Meta file missing")

    print()

    # Check 2: AppData folder
    appdata_path = Path.home() / "AppData/LocalLow/Cygames/Umamusume"
    print(f"2. Checking game installation: {appdata_path}")
    if appdata_path.exists():
        print(f"   ✓ Game folder exists")

        # Check dat folder
        dat_path = appdata_path / "dat"
        if dat_path.exists():
            # Count subdirectories (should be 00, 01, 02, ... ff)
            subdirs = [d for d in dat_path.iterdir() if d.is_dir()]
            print(f"   ✓ dat folder exists with {len(subdirs)} subdirectories")

            # Count some files
            file_count = 0
            for subdir in subdirs[:5]:  # Check first 5 subdirs
                file_count += len(list(subdir.iterdir()))

            if file_count > 0:
                print(f"   ✓ Asset files found (sampled {file_count} files)")
            else:
                print(f"   ✗ No asset files found in dat folder")
                issues.append("dat folder exists but is empty")
        else:
            print(f"   ✗ dat folder not found: {dat_path}")
            issues.append("dat folder missing - game may not be installed")
    else:
        print(f"   ✗ Game folder not found")
        print(f"   Make sure Uma Musume is installed")
        issues.append("Game installation not found")

    print()

    # Check 3: storage folder
    storage_path = Path("./storage")
    print(f"3. Checking storage folder: {storage_path}")
    if storage_path.exists():
        print(f"   ✓ Storage folder exists")
        assets_path = storage_path / "assets"
        if assets_path.exists():
            # Count extracted files
            file_count = sum(1 for _ in assets_path.rglob("*") if _.is_file())
            print(f"   ✓ Assets folder exists with {file_count} extracted files")
        else:
            print(f"   ⚠ Assets folder not yet created (will be created on first dump)")
    else:
        print(f"   ⚠ Storage folder not yet created (will be created automatically)")

    print()
    print("=== Summary ===")
    if issues:
        print("❌ Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("✓ Setup looks good! You can run:")
        print("   uv run main.py assets dump --kind supportcard skill")

if __name__ == "__main__":
    check_setup()
