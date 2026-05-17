"""
Script untuk migrasi database - menambahkan tabel user_clicks untuk leaderboard
"""
from database.models import Base, engine, UserClick
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Create user_clicks table without dropping existing tables"""
    try:
        logger.info("Starting database migration...")
        
        # Hanya create tabel UserClick tanpa drop existing tables
        UserClick.__table__.create(bind=engine, checkfirst=True)
        
        logger.info("✅ Migration completed successfully!")
        logger.info("✅ Table 'user_clicks' has been created")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == '__main__':
    migrate_database()
