from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

user_training_days = Table(
    'user_training_days',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('training_day', String, primary_key=True)  # Дата в формате YYYY-MM-DD
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)

    total_problems_solved = Column(Integer, default=0)
    correct_answers = Column(Integer, default=0)
    incorrect_answers = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    max_streak = Column(Integer, default=0)
    last_training_date = Column(DateTime, nullable=True)

    language = Column(String, default="ru", nullable=True)  # ru, en

    notification_enabled = Column(Boolean, default=True)
    notification_preset = Column(String, default="three_times")  # morning, lunch, evening, three_times, custom, disabled
    custom_notification_times = Column(Text, default="")  # JSON string with times HH:MM,HH:MM,...

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    training_sessions = relationship("TrainingSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.telegram_id}>"


class TrainingSession(Base):
    """Модель сессии тренировки"""
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    difficulty = Column(String, nullable=False)  # easy, medium, hard
    mode = Column(String, nullable=False)  # choose, mult, div, mixed

    total_problems = Column(Integer, default=0)
    correct = Column(Integer, default=0)
    incorrect = Column(Integer, default=0)
    completed = Column(Boolean, default=False)

    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="training_sessions")
    problems = relationship("Problem", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<TrainingSession {self.id}>"


class Problem(Base):
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("training_sessions.id"), nullable=False)

    first_number = Column(Integer, nullable=False)
    second_number = Column(Integer, nullable=False)
    operation = Column(String, nullable=False)  # *, /
    correct_answer = Column(Integer, nullable=False)
    user_answer = Column(Integer, nullable=True)

    is_correct = Column(Boolean, default=False)

    session = relationship("TrainingSession", back_populates="problems")

    def __repr__(self) -> str:
        return f"<Problem {self.first_number} {self.operation} {self.second_number}>"