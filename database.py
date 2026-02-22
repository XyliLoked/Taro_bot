from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import config

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    daily_readings = Column(Integer, default=0)
    last_reading_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class Reading(Base):
    __tablename__ = 'readings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    spread_type = Column(String(50))
    question = Column(Text)
    cards = Column(Text)  # JSON строка с картами
    interpretation = Column(Text)
    ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Database:
    def __init__(self):
        self.engine = create_engine(config.DATABASE_URL)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_or_create_user(self, telegram_id, username=None, first_name=None, last_name=None):
        session = self.Session()
        try:
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            
            if not user:
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
                session.add(user)
                session.commit()
            
            return user
        finally:
            session.close()
    
    def can_user_get_reading(self, user_id):
        session = self.Session()
        try:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            
            if not user:
                return True
            
            # Сбрасываем счетчик если новый день
            today = datetime.now().date()
            if user.last_reading_date and user.last_reading_date.date() != today:
                user.daily_readings = 0
                session.commit()
                return True
            
            return user.daily_readings < config.MAX_DAILY_READINGS
        finally:
            session.close()
    
    def increment_reading_count(self, user_id):
        session = self.Session()
        try:
            user = session.query(User).filter_by(telegram_id=user_id).first()
            if user:
                user.daily_readings += 1
                user.last_reading_date = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
    def save_reading(self, user_id, spread_type, question, cards, interpretation, ai_generated):
        session = self.Session()
        try:
            import json
            cards_json = json.dumps([
                {
                    'card': card['card'].name,
                    'position': card['position'],
                    'is_upright': card['is_upright']
                }
                for card in cards
            ])
            
            reading = Reading(
                user_id=user_id,
                spread_type=spread_type,
                question=question,
                cards=cards_json,
                interpretation=interpretation,
                ai_generated=ai_generated
            )
            
            session.add(reading)
            session.commit()
            return reading.id
        finally:
            session.close()
    
    def get_user_history(self, user_id, limit=10):
        session = self.Session()
        try:
            readings = session.query(Reading).filter_by(user_id=user_id)\
                .order_by(Reading.created_at.desc())\
                .limit(limit)\
                .all()
            return readings
        finally:
            session.close()

# Глобальный экземпляр базы данных
db = Database()