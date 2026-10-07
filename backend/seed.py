"""Seed script to create demo users and data"""
from app.database import SessionLocal, create_tables
from app.models import User
from app.auth.security import hash_password

def seed_demo_data():
    """Create demo users for testing"""
    create_tables()
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == "demo@example.com").first()
        if existing_user:
            print("Demo user already exists!")
            return

        db.add_all([
            User(
                name="Demo User",
                email="demo@example.com",
                password_hash=hash_password("demo1234"),
            ),
            User(
                name="Test User",
                email="test@example.com",
                password_hash=hash_password("test1234"),
            ),
        ])
        db.commit()
        print("[OK] Demo users created successfully!")
        print("Demo user: demo@example.com / demo1234")
        print("Test user: test@example.com / test1234")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
