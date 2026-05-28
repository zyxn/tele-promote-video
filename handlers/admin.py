from telethon import events
from telethon.tl.custom import Button
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from database import crud
import config
import time
import os
import logging
from pathlib import Path
from telethon.tl.types import DocumentAttributeVideo
import secrets
import string
from services.scheduler import schedule_next_post

logger = logging.getLogger(__name__)


def generate_random_id(length=15):
    # Kombinasi huruf besar, huruf kecil, dan angka
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

async def setup_admin_handlers(client):
    
    @client.on(events.NewMessage(pattern='/toggle', from_users=config.ADMIN_IDS))
    async def toggle_handler(event):
        """Toggle automatic posting mode"""
        try:
            logger.info(f"Toggle request from {event.sender_id} with args: {event.text}")
            args = event.text.split()
            
            if len(args) < 2:
                msg = "Usage: /toggle on|off"
                await event.reply(msg)
                logger.warning(f"Insufficient arguments: {event.text}")
                return
                
            mode = args[1].lower()
            if mode not in ['on', 'off']:
                msg = "Mode must be 'on' or 'off'"
                await event.reply(msg)
                logger.warning(f"Invalid mode: {mode}")
                return
                
            with crud.get_db_session() as session:
                crud.set_admin_setting(session, 'auto_post', mode)
                msg = f"🔄 Auto-post mode set to: {mode.upper()}"
                await event.reply(msg)
                logger.info(f"Auto-post mode changed to {mode.upper()} by {event.sender_id}")
                
        except Exception as e:
            logger.error(f"Error in toggle_handler: {str(e)}", exc_info=True)
            await event.reply("❌ An error occurred while processing your request")

    @client.on(events.NewMessage(from_users=config.ADMIN_IDS))
    async def photo_handler(event):
        """Handle photo uploads with /add_photo in caption - Now using API"""
        try:
            # Check if message has media and contains /add_photo in text
            if event.media and isinstance(event.media, MessageMediaPhoto) and event.text and '/add_photo' in event.text:
                await event.reply("ℹ️ Bot sekarang menggunakan anime-api untuk gambar clickbait.\nTidak perlu upload gambar manual lagi!")
                logger.info(f"Photo upload attempt by {event.sender_id} - informed about API usage")

        except Exception as e:
            logger.error(f"Error in photo_handler: {str(e)}", exc_info=True)
            await event.reply(f"💥 Gagal: {str(e)}")

    @client.on(events.NewMessage())
    async def private_group_handler(event):
        """Handle videos/images posted in private admin group with reply /add_video or /add_video_vip "caption" """
        # Only process if message contains /add_video or /add_video_vip
        if not event.text or ('/add_video' not in event.text and '/add_video_vip' not in event.text):
            return
        
        # Check if sender is admin
        if event.sender_id not in config.ADMIN_IDS:
            logger.warning(f"Non-admin {event.sender_id} tried to use /add_video")
            return
        
        # Determine if this is VIP video
        is_vip = '/add_video_vip' in event.text
            
        try:
            logger.info(f"New media add request from {event.sender_id}")
            logger.info(f"Event text: {event.text}")
            logger.info(f"Chat ID: {event.chat_id}")
            logger.info(f"Chat type: {type(event.chat)}")
            logger.info(f"Is reply: {event.is_reply}")
            logger.info(f"Reply to msg id: {event.reply_to_msg_id}")
            
            # Check if this is a reply to a media message using reply_to_msg_id
            if not event.reply_to_msg_id:
                cmd = "/add_video_vip" if is_vip else "/add_video"
                msg = f"❌ Gunakan dengan cara:\nReply sebuah video/gambar dengan {cmd} \"judul\""
                await event.reply(msg)
                logger.warning("Not a reply message")
                return
            
            logger.info("Getting reply message...")
            reply_msg = await client.get_messages(event.chat_id, ids=event.reply_to_msg_id)
            logger.info(f"Reply message: {reply_msg}")
            logger.info(f"Reply has media: {reply_msg.media if reply_msg else 'No reply_msg'}")
            
            # Check if replied message contains media (video or photo)
            if not reply_msg or not reply_msg.media:
                msg = "❌ Pesan yang dibalas harus mengandung video atau gambar"
                await event.reply(msg)
                logger.warning("Reply message has no media")
                return
            
            logger.info(f"Media type: {type(reply_msg.media)}")
            
            # Extract media title from command
            command_used = '/add_video_vip' if is_vip else '/add_video'
            video_title = event.text.split(command_used, 1)[1].strip()
            logger.info(f"Extracted title: '{video_title}' (VIP: {is_vip})")
            
            if not video_title:
                cmd = "/add_video_vip" if is_vip else "/add_video"
                msg = f"❌ Harap berikan judul setelah {cmd}"
                await event.reply(msg)
                logger.warning("No media title provided")
                return
            
            # Check if media is video or photo
            is_valid_media = False
            media_type = "unknown"
            
            # Check for photo
            if isinstance(reply_msg.media, MessageMediaPhoto):
                is_valid_media = True
                media_type = "photo"
                logger.info("Photo media detected!")
            # Check for video
            elif isinstance(reply_msg.media, MessageMediaDocument):
                doc = reply_msg.media.document
                logger.info(f"Document attributes: {doc.attributes}")
                for attr in doc.attributes:
                    if isinstance(attr, DocumentAttributeVideo):
                        is_valid_media = True
                        media_type = "video"
                        logger.info("Video attribute found!")
                        break
            
            if not is_valid_media:
                msg = "❌ Pesan yang dibalas harus berupa video atau gambar"
                await event.reply(msg)
                logger.warning(f"Media is not a video or photo. Media type: {type(reply_msg.media)}")
                return
            
            # Forward media to private channel
            logger.info(f"Forwarding {media_type} to private channel: {config.CHANNELS['PRIVATE']}")
            private_channel = config.CHANNELS['PRIVATE']
            forwarded_msg = await client.forward_messages(private_channel, reply_msg, drop_author=True)
            logger.info(f"{media_type.capitalize()} forwarded! Message ID: {forwarded_msg.id}")

            with crud.get_db_session() as session:
                # Check if queue was empty before adding
                unposted_videos = crud.get_unposted_videos(session, limit=999)
                queue_was_empty = len(unposted_videos) == 0
                queue_position = len(unposted_videos) + 1  # Position after adding this video
                
                random_id = generate_random_id(15)
                logger.info(f"Generated random_id: {random_id}")
                
                video = crud.add_video(
                    session,
                    message_id=forwarded_msg.id,
                    random_id=random_id,
                    ch_id=forwarded_msg.chat.id,
                    title=video_title,
                    is_vip=is_vip
                )
                logger.info(f"New video saved: ID {video.id}, Title: {video.title}")
                
                # Calculate estimated posting time in WIB (+7)
                from datetime import datetime, timedelta
                
                if queue_was_empty:
                    # Will post immediately (5 seconds from now)
                    estimated_post_time = datetime.now() + timedelta(seconds=5)
                else:
                    # Calculate based on queue position and interval
                    minutes_until_post = (queue_position - 1) * config.POSTING_INTERVAL_MINUTES
                    estimated_post_time = datetime.now() + timedelta(minutes=minutes_until_post)
                
                # Convert to WIB (+7)
                wib_time = estimated_post_time + timedelta(hours=7)
                time_str = wib_time.strftime("%H:%M WIB")
                date_str = wib_time.strftime("%d/%m/%Y")
                
                # Get message link di channel private
                msg_link = f"https://t.me/c/{str(forwarded_msg.chat.id).replace('-100', '')}/{forwarded_msg.id}"
                
                media_emoji = "🎬" if media_type == "video" else "🖼️"
                vip_badge = "👑 VIP" if is_vip else "📦 Regular"
                msg = (
                    f"✅ {media_type.capitalize()} saved successfully!\n"
                    f"{media_emoji} Type: {media_type.upper()}\n"
                    f"🏷️ Tier: {vip_badge}\n"
                    f"🆔 ID: {video.id}\n"
                    f"📝 Title: {video.title}\n"
                    f"🔗 Link: {msg_link}\n\n"
                    f"📊 Queue Info:\n"
                    f"📍 Position: #{queue_position}\n"
                    f"⏰ Estimated Post: {time_str}\n"
                    f"📅 Date: {date_str}"
                )
                    
                await event.reply(msg)
                logger.info(f"Success message sent to admin - {media_type} added")
                
                # Always schedule with immediate=False so video goes to queue
                # If we use immediate=True, video will post in 5 seconds and won't be in queue
                schedule_next_post(immediate=False)
                logger.info(f"Scheduler triggered after adding {media_type} (immediate=False to keep in queue)")
                
        except Exception as e:
            logger.error(f"Error in private_group_handler: {str(e)}", exc_info=True)
            await event.reply(f"❌ Failed to process media: {str(e)}")
        
    @client.on(events.NewMessage(
        pattern='/stats',
        from_users=config.ADMIN_IDS
    ))
    async def stats_handler(event):
        """Get bot statistics"""
        try:
            logger.info(f"Stats request from {event.sender_id}")
            
            with crud.get_db_session() as session:
                # Count unposted videos
                unposted = session.query(crud.Video)\
                    .filter_by(posted=False)\
                    .count()
                    
                # Count total videos
                total = session.query(crud.Video).count()
                
                # Get most popular video
                popular = session.query(crud.Video)\
                    .order_by(crud.Video.click_count.desc())\
                    .first()
                
                stats_msg = (
                    f"📊 Bot Statistics\n\n"
                    f"📥 Videos in queue: {unposted}\n"
                    f"📤 Total videos: {total}\n"
                    f"🔥 Most popular: {popular.title if popular else 'N/A'} "
                    f"({popular.click_count if popular else 0} clicks)"
                )
                
                await event.reply(stats_msg)
                logger.info(f"Stats delivered to {event.sender_id}")
                
        except Exception as e:
            logger.error(f"Error in stats_handler: {str(e)}", exc_info=True)
            await event.reply("❌ Failed to retrieve statistics")

    logger.info("Admin handlers setup completed")