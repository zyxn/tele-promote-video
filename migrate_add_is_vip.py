"""
Migration script to add is_vip column to videos table
"""
from sqlalchemy import create_engine, text
from config import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Add is_vip column to videos table"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.begin() as conn:  # Use begin() for auto-commit
            # Check if column already exists (PostgreSQL syntax)
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name='videos' AND column_name='is_vip'
            """))
            
            exists = result.scalar() > 0
            
            if exists:
                logger.info("Column 'is_vip' already exists in videos table")
                return
            
            # Add the column (PostgreSQL syntax)
            logger.info("Adding 'is_vip' column to videos table...")
            conn.execute(text("""
                ALTER TABLE videos 
                ADD COLUMN is_vip BOOLEAN DEFAULT FALSE
            """))
            
            logger.info("✅ Migration completed successfully!")
            logger.info("Column 'is_vip' added to videos table with default value FALSE")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == '__main__':
    migrate()
