"""
Migration script to add 'category' column to existing SQLite database table 'essays'
and re-classify all existing essays using the new Category Classifier service.
"""

import sqlite3
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.services.category_classifier import classify_essay_category, ALL_CATEGORIES

DB_PATH = REPO_ROOT / "data" / "intelliscore.db"
if not DB_PATH.exists():
    DB_PATH = REPO_ROOT / "backend" / "intelliscore.db"

def run_migration_and_classification():
    if not DB_PATH.exists():
        print(f"Database not found at {DB_PATH}, skipping migration.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check if 'category' column exists in 'essays' table
    cursor.execute("PRAGMA table_info(essays)")
    columns = [col[1] for col in cursor.fetchall()]

    if "category" not in columns:
        print("Adding 'category' column to 'essays' table...")
        cursor.execute("ALTER TABLE essays ADD COLUMN category TEXT DEFAULT 'General Essay'")
        conn.commit()
        print("Column 'category' added successfully.")
    else:
        print("'category' column already exists in 'essays' table.")

    # Fetch all essays and re-classify
    cursor.execute("SELECT id, title, raw_text, category FROM essays")
    rows = cursor.fetchall()

    print(f"\nProcessing {len(rows)} essays in database...")
    updated_count = 0

    for essay_id, title, raw_text, current_cat in rows:
        new_cat = classify_essay_category(title or "", raw_text or "")
        print(f"ID {essay_id}: Title='{title[:30]}' -> Classified as: '{new_cat}' (was: '{current_cat}')")
        cursor.execute("UPDATE essays SET category = ? WHERE id = ?", (new_cat, essay_id))
        updated_count += 1

    conn.commit()
    conn.close()
    print(f"\nSuccessfully migrated and re-classified {updated_count} essays.")

if __name__ == "__main__":
    run_migration_and_classification()
