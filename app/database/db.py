import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timedelta, timezone
import json

from app.config import DATABASE_URL, DB_PATH
from app.database.models import Base, User, TrainingSession, Problem

DIFFICULTY_WEIGHTS = {"easy": 1, "medium": 2, "hard": 3}

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
logger = logging.getLogger(__name__)

async def init_db() -> None:
    DB_PATH.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.debug("Database schema created/verified at %s", DB_PATH)


async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        return session



async def get_or_create_user(
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None
) -> tuple[User, bool]:
    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == str(telegram_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            return user, False

        user = User(
            telegram_id=str(telegram_id),
            username=username,
            first_name=first_name
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        return user, True

async def get_user(telegram_id: int) -> Optional[User]:
    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == str(telegram_id))
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


async def get_user_language(telegram_id: int) -> str:
    """Return user language (ru/en). Default ru if user not found."""
    user = await get_user(telegram_id)
    if not user or not getattr(user, "language", None):
        return "ru"
    return user.language or "ru"


async def get_all_users_with_notifications() -> list[User]:
    async with async_session_maker() as session:
        stmt = select(User).where(
            User.notification_enabled == True,
            User.notification_preset != "disabled"
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


async def update_user_language(telegram_id: int, lang: str) -> None:
    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == str(telegram_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            user.language = lang
            await session.commit()


async def update_user_notifications(
        telegram_id: int,
        preset: str,
        custom_times: list[str] | None = None
) -> None:
    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == str(telegram_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            logger.warning("update_user_notifications: user not found, telegram_id=%s", telegram_id)
            return

        user.notification_preset = preset
        user.notification_enabled = preset != "disabled"

        if custom_times:
            import json
            user.custom_notification_times = json.dumps(custom_times)
            logger.info(f"Custom times saved for user {telegram_id}: {custom_times}")

        await session.commit()
        logger.info(f"Notifications updated: user={telegram_id}, preset={preset}, enabled={user.notification_enabled}")


async def create_training_session(telegram_id: int, difficulty: str, mode: str, total_problems: int) -> TrainingSession:
    async with async_session_maker() as session:
        stmt = select(User).where(User.telegram_id == str(telegram_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if not user:
            logger.error("create_training_session: user not found, telegram_id=%s", telegram_id)
            raise ValueError(f"User not found: telegram_id={telegram_id}")

        session_obj = TrainingSession(
            user_id=user.id,
            difficulty=difficulty,
            mode=mode,
            total_problems=total_problems
        )
        session.add(session_obj)
        await session.commit()
        await session.refresh(session_obj)

        return session_obj


async def complete_training_session(session_id: int, correct: int, incorrect: int) -> None:
    logger.info("Completing session id=%s: correct=%s incorrect=%s", session_id, correct, incorrect)
    async with async_session_maker() as session:
        stmt = (
            select(TrainingSession)
            .options(selectinload(TrainingSession.user))
            .where(TrainingSession.id == session_id)
        )
        result = await session.execute(stmt)
        training_session = result.scalar_one()

        user = training_session.user

        training_session.correct = correct
        training_session.incorrect = incorrect
        training_session.completed = True
        training_session.completed_at = datetime.now(timezone.utc)

        user.total_problems_solved += training_session.total_problems
        user.correct_answers += correct
        user.incorrect_answers += incorrect

        today = date.today()
        last_training = user.last_training_date.date() if user.last_training_date else None

        if last_training:
            days_diff = (today - last_training).days

            if days_diff == 0:
                pass
            elif days_diff == 1:
                if correct >= 1:  # At least one correct answer for streak
                    user.current_streak += 1
            else:
                user.current_streak = 1 if correct >= 1 else 0
        else:
            user.current_streak = 1 if correct >= 1 else 0

        if user.current_streak > user.max_streak:
            user.max_streak = user.current_streak

        user.last_training_date = datetime.now(timezone.utc)

        await session.commit()


async def _get_difficulty_stats_map(session: AsyncSession) -> dict[int, dict[str, int]]:
    stmt = (
        select(User.id, TrainingSession.difficulty, func.sum(TrainingSession.correct).label("correct_sum"))
        .select_from(User)
        .join(TrainingSession, User.id == TrainingSession.user_id)
        .where(TrainingSession.completed == True)
        .group_by(User.id, TrainingSession.difficulty)
    )
    result = await session.execute(stmt)
    rows = result.all()
    out: dict[int, dict[str, int]] = {}
    for user_id, difficulty, correct_sum in rows:
        if user_id not in out:
            out[user_id] = {"easy": 0, "medium": 0, "hard": 0}
        if difficulty in out[user_id]:
            out[user_id][difficulty] = int(correct_sum or 0)
        else:
            out[user_id][difficulty] = int(correct_sum or 0)
    return out


async def get_user_difficulty_stats(telegram_id: int) -> dict[str, int]:
    user = await get_user(telegram_id)
    if not user:
        return {"easy": 0, "medium": 0, "hard": 0}
    async with async_session_maker() as session:
        stmt = (
            select(TrainingSession.difficulty, func.sum(TrainingSession.correct).label("correct_sum"))
            .select_from(TrainingSession)
            .where(TrainingSession.user_id == user.id, TrainingSession.completed == True)
            .group_by(TrainingSession.difficulty)
        )
        result = await session.execute(stmt)
        rows = result.all()
        out = {"easy": 0, "medium": 0, "hard": 0}
        for difficulty, correct_sum in rows:
            if difficulty in out:
                out[difficulty] = int(correct_sum or 0)
        return out


async def get_top_users(limit: int = 10) -> list[tuple[User, int]]:
    top = await get_top_users_by_streak(limit)
    return [(u, value) for u, value, _ in top]


async def get_top_users_by_streak(limit: int = 10) -> list[tuple[User, int, dict[str, int]]]:
    async with async_session_maker() as session:
        stmt = (
            select(User)
            .order_by(desc(User.max_streak), desc(User.total_problems_solved), User.id)
            .limit(limit * 2)
        )
        result = await session.execute(stmt)
        users = result.scalars().all()
        diff_map = await _get_difficulty_stats_map(session)
        out = []
        for user in users[:limit]:
            stats = diff_map.get(user.id, {"easy": 0, "medium": 0, "hard": 0})
            out.append((user, user.max_streak, stats))
        return out


async def get_top_users_by_solved(limit: int = 10) -> list[tuple[User, int, dict[str, int]]]:
    async with async_session_maker() as session:
        stmt = (
            select(User)
            .order_by(desc(User.total_problems_solved), desc(User.correct_answers), User.id)
            .limit(limit * 2)
        )
        result = await session.execute(stmt)
        users = result.scalars().all()
        diff_map = await _get_difficulty_stats_map(session)
        return [
            (u, u.total_problems_solved, diff_map.get(u.id, {"easy": 0, "medium": 0, "hard": 0}))
            for u in users[:limit]
        ]


async def get_top_users_by_accuracy(limit: int = 10) -> list[tuple[User, float, dict[str, int]]]:
    async with async_session_maker() as session:
        acc_expr = (User.correct_answers * 1.0) / func.nullif(
            User.correct_answers + User.incorrect_answers, 0
        )
        stmt = (
            select(User)
            .where(User.total_problems_solved >= 1)
            .order_by(desc(acc_expr), desc(User.total_problems_solved), User.id)
            .limit(limit * 2)
        )
        result = await session.execute(stmt)
        users = result.scalars().all()
        diff_map = await _get_difficulty_stats_map(session)
        out = []
        for user in users[:limit]:
            total = user.correct_answers + user.incorrect_answers
            acc = round((user.correct_answers / total * 100), 1) if total else 0.0
            stats = diff_map.get(user.id, {"easy": 0, "medium": 0, "hard": 0})
            out.append((user, acc, stats))
        return out


def _weighted_score(stats: dict[str, int]) -> int:
    return (
        stats.get("easy", 0) * DIFFICULTY_WEIGHTS["easy"]
        + stats.get("medium", 0) * DIFFICULTY_WEIGHTS["medium"]
        + stats.get("hard", 0) * DIFFICULTY_WEIGHTS["hard"]
    )


async def get_top_users_by_weighted(limit: int = 10) -> list[tuple[User, int, dict[str, int]]]:
    async with async_session_maker() as session:
        diff_map = await _get_difficulty_stats_map(session)
        stmt = select(User).where(User.id.in_(list(diff_map.keys())))
        result = await session.execute(stmt)
        users_by_id = {u.id: u for u in result.scalars().all()}
        # Сортировка: очки (убыв.), решённых (убыв.), id (возр.) для стабильного порядка
        rows = []
        for uid in diff_map:
            u = users_by_id.get(uid)
            if not u:
                continue
            score = _weighted_score(diff_map[uid])
            rows.append((u, score, diff_map[uid]))
        rows.sort(key=lambda r: (-r[1], -r[0].total_problems_solved, r[0].id))
        return rows[:limit]


async def get_user_rank(
    telegram_id: int, mode: str
) -> tuple[int | None, int]:
    user = await get_user(telegram_id)
    if not user:
        return None, 0
    async with async_session_maker() as session:
        diff_map = await _get_difficulty_stats_map(session)
        if mode == "streak":
            stmt = select(User).order_by(
                desc(User.max_streak), desc(User.total_problems_solved), User.id
            )
        elif mode == "solved":
            stmt = select(User).order_by(
                desc(User.total_problems_solved), desc(User.correct_answers), User.id
            )
        elif mode == "accuracy":
            acc_expr = (User.correct_answers * 1.0) / func.nullif(
                User.correct_answers + User.incorrect_answers, 0
            )
            stmt = (
                select(User)
                .where(User.total_problems_solved >= 1)
                .order_by(desc(acc_expr), desc(User.total_problems_solved), User.id)
            )
        elif mode == "weighted":
            stmt = select(User).where(User.id.in_(list(diff_map.keys())))
            result = await session.execute(stmt)
            users_list = result.scalars().all()
            rows = [
                (u, _weighted_score(diff_map.get(u.id, {"easy": 0, "medium": 0, "hard": 0})))
                for u in users_list
            ]
            rows.sort(key=lambda r: (-r[1], -r[0].total_problems_solved, r[0].id))
            total = len(rows)
            for rank, (u, _) in enumerate(rows, 1):
                if u.id == user.id:
                    return rank, total
            return None, total
        else:
            return None, 0
        result = await session.execute(stmt)
        users = result.scalars().all()
        total = len(users)
        for rank, u in enumerate(users, 1):
            if u.id == user.id:
                return rank, total
        return None, total


async def get_user_stats(telegram_id: int) -> dict:
    user = await get_user(telegram_id)
    if not user:
        return {}

    return {
        "correct": user.correct_answers,
        "incorrect": user.incorrect_answers,
        "total": user.total_problems_solved,
        "current_streak": user.current_streak,
        "max_streak": user.max_streak,
        "last_training": user.last_training_date
    }
