from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

user_training_days = Table(
    'user_training_days',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('training_day', String, primary_key=True)  # YYYY-MM-DD
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)

    total_problems_solved = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    incorrect_answers = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    max_streak = Column(Integer, default=0, nullable=False)
    last_training_date = Column(DateTime(timezone=True), nullable=True)

    language = Column(String, default="ru", nullable=True)  # ru, en

    show_in_top = Column(Boolean, default=False, nullable=False)

    notification_enabled = Column(Boolean, default=True, nullable=False)
    notification_preset = Column(String, default="three_times", nullable=False)
    custom_notification_times = Column(Text, default="", nullable=True)  # JSON string with HH:MM list

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    training_sessions = relationship("TrainingSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User {self.telegram_id}>"


class TrainingSession(Base):
    __tablename__ = "training_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    difficulty = Column(String, nullable=False)  # easy, medium, hard
    mode = Column(String, nullable=False)  # choose, mult, div, mixed, add, sub, div_rem, pow, sqrt

    total_problems = Column(Integer, default=0, nullable=False)
    correct = Column(Integer, default=0, nullable=False)
    incorrect = Column(Integer, default=0, nullable=False)
    completed = Column(Boolean, default=False, nullable=False)

    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

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
    operation = Column(String, nullable=False)  # +, -, *, /, %, ^, sqrt
    correct_answer = Column(Integer, nullable=False)
    user_answer = Column(Integer, nullable=True)

    is_correct = Column(Boolean, default=False, nullable=False)

    # op-specific extras: remainder, display_form, etc.
    metadata_json = Column(Text, nullable=True)

    # Per-problem timing — populated by record_problem_shown / _answered.
    # NULL on rows created before migration 0002 or on skipped problems.
    shown_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("TrainingSession", back_populates="problems")

    def __repr__(self) -> str:
        return f"<Problem {self.first_number} {self.operation} {self.second_number}>"


class DailyChallenge(Base):
    """One shared set of 10 problems per calendar day (Europe/Moscow).

    Lazily created on the first user request via
    ``get_or_create_daily_challenge``; the UNIQUE constraint on
    ``challenge_date`` together with ``ON CONFLICT DO NOTHING`` makes
    concurrent first-clicks safe.
    """

    __tablename__ = "daily_challenges"

    id = Column(Integer, primary_key=True)
    challenge_date = Column(Date, nullable=False, unique=True)
    seed = Column(BigInteger, nullable=False)
    # List[dict] of frozen Problem specs; consumed by the daily handler.
    problem_specs = Column(JSONB, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<DailyChallenge {self.challenge_date}>"


class DailyChallengeAttempt(Base):
    """One row per (user, calendar day). UNIQUE enforces single attempt."""

    __tablename__ = "daily_challenge_attempts"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_date", name="uq_dca_user_date"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_date = Column(Date, nullable=False)
    started_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    correct = Column(Integer, default=0, nullable=False)
    incorrect = Column(Integer, default=0, nullable=False)
    total_time_ms = Column(BigInteger, default=0, nullable=False)

    user = relationship("User")

    def __repr__(self) -> str:
        return f"<DailyChallengeAttempt user={self.user_id} date={self.challenge_date}>"
