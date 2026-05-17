"""
Test untuk memverifikasi bahwa scheduler langsung posting ketika queue kosong
"""
import asyncio
from datetime import datetime, timedelta
from services.scheduler import schedule_next_post, scheduler
from database import crud
from database.models import Video
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_immediate_post_when_queue_empty():
    """Test: Ketika queue kosong dan video ditambahkan, harus schedule immediate"""
    logger.info("\n=== TEST: Immediate Post When Queue Empty ===")
    
    # Setup: Pastikan queue kosong
    with crud.get_db_session() as session:
        videos = crud.get_unposted_videos(session)
        logger.info(f"Current queue: {len(videos)} videos")
    
    # Simulate: Admin menambahkan video ke queue kosong
    logger.info("Simulating: Adding video to empty queue...")
    schedule_next_post(immediate=True)
    
    # Verify: Job harus dijadwalkan dalam 5 detik
    job = scheduler.get_job('auto_post')
    if job:
        next_run = job.next_run_time
        time_diff = (next_run - datetime.now()).total_seconds()
        logger.info(f"✅ Job scheduled at: {next_run}")
        logger.info(f"✅ Time until next run: {time_diff:.1f} seconds")
        
        if time_diff <= 10:  # Should be ~5 seconds
            logger.info("✅ PASS: Job scheduled immediately (within 10 seconds)")
        else:
            logger.error(f"❌ FAIL: Job scheduled too far in future ({time_diff:.1f}s)")
    else:
        logger.error("❌ FAIL: No job scheduled!")

def test_normal_interval_when_queue_has_videos():
    """Test: Ketika queue sudah ada video, harus schedule dengan interval normal"""
    logger.info("\n=== TEST: Normal Interval When Queue Has Videos ===")
    
    # Simulate: Ada video di queue, schedule next post
    logger.info("Simulating: Scheduling next post with videos in queue...")
    schedule_next_post(immediate=False)
    
    # Verify: Job harus dijadwalkan sesuai POSTING_INTERVAL_MINUTES
    job = scheduler.get_job('auto_post')
    if job:
        next_run = job.next_run_time
        time_diff = (next_run - datetime.now()).total_seconds()
        logger.info(f"✅ Job scheduled at: {next_run}")
        logger.info(f"✅ Time until next run: {time_diff:.1f} seconds")
        
        # Assuming POSTING_INTERVAL_MINUTES = 30
        expected_min = 25 * 60  # 25 minutes
        expected_max = 35 * 60  # 35 minutes
        
        if expected_min <= time_diff <= expected_max:
            logger.info(f"✅ PASS: Job scheduled at normal interval (~30 minutes)")
        else:
            logger.warning(f"⚠️ WARNING: Job scheduled at {time_diff/60:.1f} minutes (expected ~30)")
    else:
        logger.error("❌ FAIL: No job scheduled!")

if __name__ == "__main__":
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started for testing\n")
    
    try:
        # Run tests
        test_immediate_post_when_queue_empty()
        test_normal_interval_when_queue_has_videos()
        
        logger.info("\n=== All Tests Completed ===")
        
    finally:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
