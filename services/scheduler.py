from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
from telethon.tl.custom import Button
import random
import os
import logging
from database import crud
import config
from utils.helpers import create_video_caption
from services.media import get_clickbait_image

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()
_client = None  # Store client reference

async def post_video_to_public(client=None):
    """Posting video ke channel publik"""
    if client is None:
        client = _client
    
    try:
        logger.info("=== Starting post_video_to_public ===")
        with crud.get_db_session() as session:
            # Cek mode posting
            setting = crud.get_admin_setting(session, 'auto_post')
            logger.info(f"Auto-post setting: {setting.value if setting else 'None'}")
            
            if setting and setting.value.lower() == 'off':
                logger.info("Auto-post is OFF, skipping...")
                return
                
            # Ambil video yang belum diposting
            videos = crud.get_unposted_videos(session)
            logger.info(f"Found {len(videos) if videos else 0} unposted videos")
            
            if not videos:
                logger.info("No videos to post")
                return
                
            video = videos[0]
            logger.info(f"Selected video: ID={video.id}, Title={video.title}, VIP={video.is_vip}")
            
            # Ambil gambar clickbait lokal (default atau VIP)
            logger.info(f"Getting {'VIP' if video.is_vip else 'default'} clickbait image...")
            image_path = get_clickbait_image(is_vip=video.is_vip)
            
            if not image_path:
                logger.error("Failed to get clickbait image!")
                return
            
            logger.info(f"Using clickbait image: {image_path}")
                
            # Buat caption dengan link bot
            caption = create_video_caption(video)
            logger.info(f"Caption created: {caption[:50]}...")
            
            # Post ke channel publik
            try:
                logger.info(f"Sending to public channel: {config.CHANNELS['PUBLIC']}")
                # Kirim file dari path lokal
                await client.send_file(
                    entity=config.CHANNELS['PUBLIC'],
                    file=image_path,
                    caption=caption
                )
                logger.info("[SUCCESS] Image sent successfully!")
                
                # Forward VIP content to group chat
                if video.is_vip and config.VIP_GROUP_CHAT:
                    try:
                        logger.info(f"[VIP] Forwarding VIP content to group chat: {config.VIP_GROUP_CHAT}")
                        await client.forward_messages(
                            entity=config.VIP_GROUP_CHAT,
                            messages=video.message_id,
                            from_peer=config.CHANNELS['PRIVATE'],
                            drop_author=True
                        )
                        logger.info(f"[VIP SUCCESS] VIP content forwarded to group chat!")
                    except Exception as vip_err:
                        logger.error(f"[VIP ERROR] Failed to forward VIP to group chat: {str(vip_err)}", exc_info=True)
                
                crud.mark_video_posted(session, video.id)
                logger.info(f"[SUCCESS] Video marked as posted: {video.title}")
                
                # Schedule next post immediately if there are more videos
                schedule_next_post()
                
            except Exception as e:
                logger.error(f"[ERROR] Failed to post video: {str(e)}", exc_info=True)
                
    except Exception as e:
        logger.error(f"[ERROR] Error in post_video_to_public: {str(e)}", exc_info=True)

def schedule_next_post(immediate=False):
    """Schedule the next post based on queue status
    
    Args:
        immediate: If True, schedule immediately (for when queue was empty)
    """
    try:
        with crud.get_db_session() as session:
            videos = crud.get_unposted_videos(session)
            
            if videos:
                # Tentukan waktu posting berikutnya
                if immediate:
                    # Kirim langsung (5 detik dari sekarang untuk safety)
                    next_run = datetime.now() + timedelta(seconds=5)
                    logger.info(f"[IMMEDIATE] Queue was empty, scheduling immediate post")
                else:
                    # Ada video di queue, schedule untuk interval berikutnya
                    next_run = datetime.now() + timedelta(minutes=config.POSTING_INTERVAL_MINUTES)
                
                # Remove existing job if any
                if scheduler.get_job('auto_post'):
                    scheduler.remove_job('auto_post')
                
                # Add new job
                scheduler.add_job(
                    post_video_to_public,
                    trigger=DateTrigger(run_date=next_run),
                    id='auto_post',
                    replace_existing=True,
                    misfire_grace_time=60
                )
                logger.info(f"[SCHEDULED] Next post scheduled at {next_run.strftime('%Y-%m-%d %H:%M:%S')} ({len(videos)} videos in queue)")
            else:
                logger.info("[QUEUE EMPTY] Queue is empty, no next post scheduled")
                
    except Exception as e:
        logger.error(f"Error scheduling next post: {str(e)}", exc_info=True)

def setup_scheduler(client):
    """Setup scheduler untuk posting otomatis"""
    global _client
    _client = client
    
    logger.info("Setting up scheduler...")
    scheduler.start()
    logger.info("Scheduler started!")
    
    # Schedule first post immediately if there are videos
    schedule_next_post()