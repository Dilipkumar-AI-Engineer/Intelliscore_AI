import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import engine, SessionLocal
from app.services.essay_service import process_essay_upload

def test():
    db = SessionLocal()
    dummy_text = b"This is a dummy essay text for testing upload."
    try:
        # Assuming user_id=1 exists or just pass 1 for a quick DB check.
        # It's better to just see if process_essay_upload raises an exception 
        # before the DB commit.
        essay = process_essay_upload(db, user_id=1, file_bytes=dummy_text, original_filename="test.txt")
        print("Success:", essay.id)
    except Exception as e:
        print("Exception caught:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
