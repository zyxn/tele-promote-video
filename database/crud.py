from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from sqlalchemy.exc import OperationalError, DBAPIError
from .models import Video, AdminSetting, UserClick, SessionLocal
from typing import Optional, List, Dict
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

def retry_on_db_error(max_retries=3, delay=1):
    """Decorator to retry database operations on connection errors"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DBAPIError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Database error in {func.__name__}, attempt {attempt + 1}/{max_retries}: {str(e)}")
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
                        # Try to rollback the session if it exists in args
                        for arg in args:
                            if isinstance(arg, Session):
                                try:
                                    arg.rollback()
                                except:
                                    pass
                    else:
                        logger.error(f"Database error in {func.__name__} after {max_retries} attempts: {str(e)}")
            raise last_exception
        return wrapper
    return decorator

def get_db_session():
    """Get a new database session"""
    return SessionLocal()

@retry_on_db_error(max_retries=3, delay=1)
def add_video(session: Session, message_id: int,ch_id:int, title: str,random_id:str, is_vip: bool = False) -> Video:
    """Add a new video to database"""
    video = Video(
        message_id=message_id,
        random_id=random_id,
        ch_id=ch_id,
        title=title,
        posted=False,
        is_vip=is_vip,
        click_count=0
    )
    session.add(video)
    session.commit()
    session.refresh(video)
    return video

@retry_on_db_error(max_retries=3, delay=1)
def get_unposted_videos(session: Session, limit: int = 1) -> List[Video]:
    """Get unposted videos ordered by creation time"""
    return session.query(Video)\
        .filter(Video.posted == False)\
        .order_by(Video.created_at)\
        .limit(limit)\
        .all()

@retry_on_db_error(max_retries=3, delay=1)
def mark_video_posted(session: Session, video_id: int):
    """Mark video as posted with current timestamp"""
    video = session.get(Video, video_id)
    if video:
        video.posted = True
        video.post_date = datetime.now()
        session.commit()

@retry_on_db_error(max_retries=3, delay=1)
def increment_click_count(session: Session, random_id: str):
    """Increment video's click count"""
    video = session.query(Video).filter_by(random_id=random_id).first()
    if video:
        video.click_count += 1
        session.commit()

def get_admin_setting(session: Session, key: str) -> Optional[AdminSetting]:
    """Get admin setting by key"""
    return session.get(AdminSetting, key)

def set_admin_setting(session: Session, key: str, value: str):
    """Create or update admin setting"""
    setting = session.get(AdminSetting, key)
    if setting:
        setting.value = value
    else:
        setting = AdminSetting(key=key, value=value)
        session.add(setting)
    session.commit()


@retry_on_db_error(max_retries=3, delay=1)
def record_user_click(session: Session, user_id: int, username: Optional[str], 
                      first_name: Optional[str], last_name: Optional[str], 
                      video_random_id: str) -> UserClick:
    """Record a user click on a video"""
    user_click = UserClick(
        user_id=user_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        video_random_id=video_random_id
    )
    session.add(user_click)
    session.commit()
    session.refresh(user_click)
    return user_click

@retry_on_db_error(max_retries=3, delay=1)
def get_leaderboard(session: Session, limit: int = 10) -> List[Dict]:
    """Get top users by click count with their details"""
    # Query untuk menghitung total klik per user
    leaderboard = session.query(
        UserClick.user_id,
        UserClick.username,
        UserClick.first_name,
        UserClick.last_name,
        func.count(UserClick.id).label('total_clicks')
    ).group_by(
        UserClick.user_id,
        UserClick.username,
        UserClick.first_name,
        UserClick.last_name
    ).order_by(
        desc('total_clicks')
    ).limit(limit).all()
    
    # Format hasil
    result = []
    for rank, (user_id, username, first_name, last_name, total_clicks) in enumerate(leaderboard, 1):
        full_name = ""
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
        elif first_name:
            full_name = first_name
        elif last_name:
            full_name = last_name
        else:
            full_name = "Unknown"
        
        result.append({
            'rank': rank,
            'user_id': user_id,
            'username': username or "No username",
            'full_name': full_name,
            'total_clicks': total_clicks
        })
    
    return result

@retry_on_db_error(max_retries=3, delay=1)
def get_user_stats(session: Session, user_id: int) -> Optional[Dict]:
    """Get statistics for a specific user"""
    total_clicks = session.query(func.count(UserClick.id))\
        .filter(UserClick.user_id == user_id)\
        .scalar()
    
    if total_clicks == 0:
        return None
    
    user_data = session.query(UserClick)\
        .filter(UserClick.user_id == user_id)\
        .order_by(desc(UserClick.clicked_at))\
        .first()
    
    if not user_data:
        return None
    
    # Get user's rank
    all_users = session.query(
        UserClick.user_id,
        func.count(UserClick.id).label('total_clicks')
    ).group_by(UserClick.user_id)\
     .order_by(desc('total_clicks'))\
     .all()
    
    rank = None
    for idx, (uid, _) in enumerate(all_users, 1):
        if uid == user_id:
            rank = idx
            break
    
    full_name = ""
    if user_data.first_name and user_data.last_name:
        full_name = f"{user_data.first_name} {user_data.last_name}"
    elif user_data.first_name:
        full_name = user_data.first_name
    elif user_data.last_name:
        full_name = user_data.last_name
    else:
        full_name = "Unknown"
    
    return {
        'user_id': user_id,
        'username': user_data.username or "No username",
        'full_name': full_name,
        'total_clicks': total_clicks,
        'rank': rank
    }
