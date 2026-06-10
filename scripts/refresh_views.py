"""Script to create and refresh materialized views."""
from app.db.database import SessionLocal
from app.db.materialized_views import create_materialized_views, refresh_materialized_views


def main():
    """Create and refresh all materialized views."""
    db = SessionLocal()
    try:
        print("Creating materialized views...")
        create_materialized_views(db)
        print("Done. Views are ready for analytics queries.")
    except Exception as e:
        print(f"Error: {e}")
        # If views already exist, try refresh
        try:
            print("Attempting refresh instead...")
            refresh_materialized_views(db)
            print("Views refreshed successfully.")
        except Exception as e2:
            print(f"Refresh also failed: {e2}")
    finally:
        db.close()


if __name__ == "__main__":
    main()