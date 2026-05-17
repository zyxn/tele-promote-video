from telethon import events
from telethon.tl.custom import Button
from database import crud
from services import verification
from utils.helpers import create_video_caption
import config
import logging
from database.models import Video

logger = logging.getLogger(__name__)

async def setup_user_handlers(client):
    @client.on(events.NewMessage(pattern='/start'))
    async def start_handler(event):
        try:
            logger.info("=== /start command received ===")
            logger.info(f"User ID: {event.sender_id}")
            logger.info(f"Message text: {event.message.text}")
            logger.info(f"Chat ID: {event.chat_id}")
            
            # Cek subscription
            logger.info("Checking user subscriptions...")
            missing = await verification.check_user_subscriptions(client, event.sender_id)
            logger.info(f"Missing subscriptions: {missing}")
            
            if missing:
                logger.info("User has missing subscriptions, sending subscription request")
                await verification.send_subscription_request(event, missing)
                return

            logger.info("User has all required subscriptions")
            
            # Proses parameter start
            args = event.message.text.split()
            logger.info(f"Command args: {args}")
            
            if len(args) > 1:
                video_id = args[1]
                logger.info(f"Video ID from link: {video_id}")
                
                with crud.get_db_session() as session:
                    video = session.query(Video).filter_by(random_id=video_id).first()
                    logger.info(f"Video found in database: {video is not None}")
                    
                    if video:
                        logger.info(f"Video details - ID: {video.id}, Title: {video.title}, Message ID: {video.message_id}, Channel ID: {video.ch_id}")
                        
                        # Forward video ke user
                        logger.info(f"Attempting to forward message {video.message_id} from channel {config.CHANNELS['PRIVATE']}")
                        
                        try:
                            forwarded = await client.forward_messages(
                                entity=event.sender_id,
                                messages=video.message_id,
                                from_peer=config.CHANNELS['PRIVATE'],
                                drop_author=True
                            )
                            logger.info(f"[SUCCESS] Video forwarded successfully! Forwarded message ID: {forwarded.id if forwarded else 'None'}")
                            
                            # Increment click count
                            crud.increment_click_count(session, video_id)
                            logger.info(f"Click count incremented for video {video_id}")
                            
                            # Record user click dengan data lengkap
                            user = await event.get_sender()
                            crud.record_user_click(
                                session=session,
                                user_id=event.sender_id,
                                username=user.username,
                                first_name=user.first_name,
                                last_name=user.last_name,
                                video_random_id=video_id
                            )
                            logger.info(f"User click recorded for user {event.sender_id} ({user.first_name})")
                            return
                            
                        except Exception as forward_error:
                            logger.error(f"[ERROR] Error forwarding video: {str(forward_error)}", exc_info=True)
                            await event.reply("❌ Maaf, terjadi kesalahan saat mengirim video. Silakan coba lagi nanti.")
                            return
                    else:
                        logger.warning(f"Video with random_id {video_id} not found in database")
            else:
                logger.info("No video ID parameter provided")
            
            # Jika tidak ada parameter atau video tidak ditemukan
            logger.info("Sending default welcome message")
            await event.reply(
                "Halo! Gunakan link dari channel viral untuk menonton video.",
                buttons=Button.clear()
            )
            
        except Exception as e:
            logger.error(f"[ERROR] Error in start_handler: {str(e)}", exc_info=True)
            await event.reply("❌ Terjadi kesalahan. Silakan coba lagi nanti.")

    @client.on(events.CallbackQuery(data=b'subscribed'))
    async def handle_subscription_callback(event):
        """
        Handle callback saat user klik button 'Sudah Subscribe'
        """
        try:
            logger.info("=== Subscription callback received ===")
            user_id = event.sender_id
            logger.info(f"User ID: {user_id}")
            
            # Check semua subscription lagi
            logger.info("Validating all subscriptions...")
            validation_result = await verification.validate_all_subscriptions(client, user_id)
            logger.info(f"Validation result: {validation_result}")
            
            if validation_result['all_subscribed']:
                logger.info("[SUCCESS] All subscriptions validated successfully")
                await event.answer("✅ Terima kasih! Sekarang kamu bisa melanjutkan.", alert=True)
                
                # Edit message untuk menunjukkan verifikasi berhasil
                try:
                    await event.edit("✅ **Verifikasi Berhasil!**\n\nSekarang kamu sudah subscribe ke semua channel yang diperlukan.\n\n📌 Silakan klik link video lagi untuk menonton.")
                    logger.info("Success message edited")
                except Exception as edit_error:
                    logger.warning(f"Could not edit message: {edit_error}")
                    await event.respond("✅ **Verifikasi Berhasil!**\n\nSekarang kamu sudah subscribe ke semua channel yang diperlukan.\n\n📌 Silakan klik link video lagi untuk menonton.")
                    
            else:
                missing_channels = validation_result['unsubscribed_channels']
                channel_names = [ch.lstrip('@') for ch in missing_channels]
                logger.warning(f"[FAILED] User still missing subscriptions: {channel_names}")
                
                await event.answer(
                    f"❌ Kamu masih belum subscribe ke: {', '.join(channel_names)}. Silakan subscribe terlebih dahulu!",
                    alert=True
                )
                
        except Exception as e:
            logger.error(f"[ERROR] Error handling subscription callback: {e}", exc_info=True)
            await event.answer("❌ Terjadi kesalahan. Silakan coba lagi.", alert=True)

    @client.on(events.NewMessage(pattern='/leaderboard'))
    async def leaderboard_handler(event):
        """
        Handler untuk menampilkan leaderboard user dengan klik terbanyak
        """
        try:
            logger.info("=== /leaderboard command received ===")
            logger.info(f"User ID: {event.sender_id}")
            
            with crud.get_db_session() as session:
                # Get top 10 users
                leaderboard = crud.get_leaderboard(session, limit=10)
                
                if not leaderboard:
                    await event.reply("📊 **Leaderboard**\n\n❌ Belum ada data klik. Jadilah yang pertama!")
                    return
                
                # Build leaderboard message
                message = "🏆 **LEADERBOARD** 🏆\n"
                message += "━━━━━━━━━━━━━━━━━━━━\n\n"
                message += "Top 10 User dengan Klik Terbanyak:\n\n"
                
                medals = {1: "🥇", 2: "🥈", 3: "🥉"}
                
                for user in leaderboard:
                    rank = user['rank']
                    medal = medals.get(rank, f"{rank}.")
                    username_display = f"@{user['username']}" if user['username'] != "No username" else "No username"
                    
                    message += f"{medal} **{user['full_name']}**\n"
                    message += f"   └ {username_display}\n"
                    message += f"   └ ID: `{user['user_id']}`\n"
                    message += f"   └ 🎯 {user['total_clicks']} klik\n\n"
                
                message += "━━━━━━━━━━━━━━━━━━━━\n"
                
                # Get current user stats
                user_stats = crud.get_user_stats(session, event.sender_id)
                if user_stats:
                    message += f"\n📍 **Posisi Kamu:**\n"
                    message += f"Rank: #{user_stats['rank']}\n"
                    message += f"Total Klik: {user_stats['total_clicks']}\n"
                else:
                    message += f"\n📍 Kamu belum ada di leaderboard.\n"
                    message += f"Klik video untuk masuk leaderboard! 🚀\n"
                
                await event.reply(message)
                logger.info(f"Leaderboard sent to user {event.sender_id}")
                
        except Exception as e:
            logger.error(f"[ERROR] Error in leaderboard_handler: {str(e)}", exc_info=True)
            await event.reply("❌ Terjadi kesalahan saat mengambil leaderboard. Silakan coba lagi nanti.")

    @client.on(events.NewMessage(pattern='/mystats'))
    async def mystats_handler(event):
        """
        Handler untuk menampilkan statistik user sendiri
        """
        try:
            logger.info("=== /mystats command received ===")
            logger.info(f"User ID: {event.sender_id}")
            
            with crud.get_db_session() as session:
                user_stats = crud.get_user_stats(session, event.sender_id)
                
                if not user_stats:
                    await event.reply(
                        "📊 **Statistik Kamu**\n\n"
                        "❌ Kamu belum pernah klik video.\n"
                        "Mulai klik video untuk masuk leaderboard! 🚀"
                    )
                    return
                
                user = await event.get_sender()
                message = "📊 **STATISTIK KAMU** 📊\n"
                message += "━━━━━━━━━━━━━━━━━━━━\n\n"
                message += f"👤 **Nama:** {user_stats['full_name']}\n"
                message += f"🆔 **Username:** @{user_stats['username']}\n" if user_stats['username'] != "No username" else f"🆔 **Username:** Tidak ada\n"
                message += f"🔢 **User ID:** `{user_stats['user_id']}`\n\n"
                message += f"🏆 **Rank:** #{user_stats['rank']}\n"
                message += f"🎯 **Total Klik:** {user_stats['total_clicks']}\n\n"
                message += "━━━━━━━━━━━━━━━━━━━━\n"
                message += "Terus klik untuk naik peringkat! 💪"
                
                await event.reply(message)
                logger.info(f"Stats sent to user {event.sender_id}")
                
        except Exception as e:
            logger.error(f"[ERROR] Error in mystats_handler: {str(e)}", exc_info=True)
            await event.reply("❌ Terjadi kesalahan saat mengambil statistik. Silakan coba lagi nanti.")