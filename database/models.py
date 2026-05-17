from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from config import DATABASE_URL
from sqlalchemy import BigInteger
Base = declarative_base()

class Video(Base):
    __tablename__ = 'videos'
    
    id = Column(BigInteger, primary_key=True, index=True,autoincrement=True)
    random_id = Column(String(50), unique=True, nullable=False)  # ID unik untuk video
    message_id = Column(BigInteger, nullable=False)  # ID pesan di channel private
    ch_id = Column(BigInteger, nullable=False)  # ID channel private
    title = Column(String(255), nullable=False)  # Judul video
    posted = Column(Boolean, default=False)  # Sudah diposting ke publik atau belum
    is_vip = Column(Boolean, default=False)  # VIP video (menggunakan clickbait vip.PNG)
    post_date = Column(DateTime, nullable=True)  # Waktu posting
    click_count = Column(Integer, default=0)  # Jumlah klik dari bot
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class AdminSetting(Base):
    __tablename__ = 'admin_settings'
    
    key = Column(String(50), primary_key=True)
    value = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class UserClick(Base):
    __tablename__ = 'user_clicks'
    
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False, index=True)  # Telegram user ID
    username = Column(String(255), nullable=True)  # Username Telegram (@username)
    first_name = Column(String(255), nullable=True)  # Nama depan user
    last_name = Column(String(255), nullable=True)  # Nama belakang user
    video_random_id = Column(String(50), nullable=False)  # ID video yang diklik
    clicked_at = Column(DateTime, server_default=func.now())  # Waktu klik
    
    def get_full_name(self):
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return "Unknown"

# Database engine and session setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_and_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
if __name__ == '__main__':
    create_db_and_tables()