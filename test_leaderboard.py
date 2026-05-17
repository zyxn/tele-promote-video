"""
Test script untuk fitur leaderboard
"""
from database import crud
from database.models import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_leaderboard():
    """Test leaderboard functionality"""
    
    logger.info("=== Testing Leaderboard Functionality ===\n")
    
    with crud.get_db_session() as session:
        # Test 1: Add sample user clicks
        logger.info("Test 1: Adding sample user clicks...")
        
        sample_users = [
            {
                'user_id': 123456789,
                'username': 'john_doe',
                'first_name': 'John',
                'last_name': 'Doe',
                'video_random_id': 'test_video_1'
            },
            {
                'user_id': 987654321,
                'username': 'jane_smith',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'video_random_id': 'test_video_2'
            },
            {
                'user_id': 555555555,
                'username': None,
                'first_name': 'Ahmad',
                'last_name': None,
                'video_random_id': 'test_video_3'
            }
        ]
        
        # Simulate multiple clicks
        for i in range(5):
            crud.record_user_click(session, **sample_users[0])
        logger.info("✅ Added 5 clicks for John Doe")
        
        for i in range(3):
            crud.record_user_click(session, **sample_users[1])
        logger.info("✅ Added 3 clicks for Jane Smith")
        
        for i in range(7):
            crud.record_user_click(session, **sample_users[2])
        logger.info("✅ Added 7 clicks for Ahmad")
        
        # Test 2: Get leaderboard
        logger.info("\nTest 2: Getting leaderboard...")
        leaderboard = crud.get_leaderboard(session, limit=10)
        
        logger.info("\n🏆 LEADERBOARD:")
        logger.info("=" * 50)
        for user in leaderboard:
            logger.info(f"Rank {user['rank']}: {user['full_name']} (@{user['username']})")
            logger.info(f"  User ID: {user['user_id']}")
            logger.info(f"  Total Clicks: {user['total_clicks']}")
            logger.info("-" * 50)
        
        # Test 3: Get specific user stats
        logger.info("\nTest 3: Getting user stats...")
        for user_data in sample_users:
            stats = crud.get_user_stats(session, user_data['user_id'])
            if stats:
                logger.info(f"\n📊 Stats for {stats['full_name']}:")
                logger.info(f"  Username: @{stats['username']}")
                logger.info(f"  User ID: {stats['user_id']}")
                logger.info(f"  Rank: #{stats['rank']}")
                logger.info(f"  Total Clicks: {stats['total_clicks']}")
        
        logger.info("\n✅ All tests completed successfully!")

if __name__ == '__main__':
    test_leaderboard()
