"""
Standalone script to seed 100 default candidates into the database.
Usage:
    python seed_candidates.py
"""
import sys
import os

# Ensure backend root is on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.services.seed_data import seed_candidates

def main():
    print("=" * 70)
    print("SEEDING 100 DIVERSE CANDIDATES INTO TALENTMATCH AI PLATFORM")
    print("=" * 70)

    db = SessionLocal()
    try:
        res = seed_candidates(db, target_count=100)
        print(f"Status: {res['message']}")
        print(f"Total Created: {res['total_created']}")
        print(f"Total Skipped: {res['total_skipped']}")
        print("\nSample Created Candidates:")
        for c in res['sample']:
            print(f"  - #{c['id']}: {c['name']} ({c['email']}) | {c['department']} | CGPA: {c['cgpa']} | Skills: {c['skills_count']}")
    except Exception as e:
        print(f"Error seeding candidates: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    print("=" * 70)

if __name__ == "__main__":
    main()
