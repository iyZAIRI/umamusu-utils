#!/usr/bin/env python3
"""List all available asset kinds in the meta database"""
import sqlite3
from pathlib import Path

def list_kinds():
    """Show all asset types available in the meta database"""
    meta_path = Path("./meta")

    if not meta_path.exists():
        print("Error: meta file not found")
        print("Run: uv run python download_meta.py")
        return

    try:
        conn = sqlite3.connect(meta_path)
        cursor = conn.cursor()

        # Get all unique kinds with counts
        cursor.execute("""
            SELECT m as kind, COUNT(*) as count
            FROM a
            GROUP BY m
            ORDER BY count DESC
        """)

        results = cursor.fetchall()

        print("=== Available Asset Kinds ===\n")
        print(f"{'Kind':<30} {'Count':>10}")
        print("-" * 42)

        for kind, count in results:
            print(f"{kind:<30} {count:>10,}")

        print("-" * 42)
        print(f"{'Total':<30} {sum(c for _, c in results):>10,}")

        # Show some example paths for supportcard and skill
        print("\n=== Example Paths ===")
        for search_kind in ['supportcard', 'skill', 'support', 'icon']:
            cursor.execute("""
                SELECT m, n
                FROM a
                WHERE m LIKE ? OR n LIKE ?
                LIMIT 3
            """, (f'%{search_kind}%', f'%{search_kind}%'))

            results = cursor.fetchall()
            if results:
                print(f"\nMatching '{search_kind}':")
                for kind, path in results:
                    print(f"  [{kind}] {path}")

        conn.close()

    except Exception as e:
        print(f"Error reading meta database: {e}")

if __name__ == "__main__":
    list_kinds()
