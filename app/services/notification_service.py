from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import time
from typing import Callable, Awaitable, Sequence

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ReminderJob:
    telegram_id: int
    at: time

    @property
    def job_id(self) -> str:
        return f"reminder:{self.telegram_id}:{self.at.hour:02d}{self.at.minute:02d}"


class NotificationService:

    def __init__(
            self,
            *,
            timezone: str = "Europe/Moscow",
            scheduler: AsyncIOScheduler | None = None,
    ) -> None:
        self._scheduler = scheduler or AsyncIOScheduler(timezone=timezone)
        self._started = False
        logger.info(f"NotificationService initialized with timezone={timezone}")

    @property
    def scheduler(self) -> AsyncIOScheduler:
        return self._scheduler

    def start(self) -> None:
        if not self._started:
            self._scheduler.start()
            self._started = True
            logger.info("Notification scheduler started")

    def shutdown(self) -> None:
        if self._started:
            self._scheduler.shutdown(wait=False)
            self._started = False
            logger.info("Notification scheduler shut down")

    def unschedule_user(self, telegram_id: int) -> None:
        prefix = f"reminder:{telegram_id}:"
        removed_count = 0

        for job in list(self._scheduler.get_jobs()):
            if job.id.startswith(prefix):
                self._scheduler.remove_job(job.id)
                removed_count += 1

        if removed_count > 0:
            logger.info(f"Removed {removed_count} reminders for telegram_id={telegram_id}")

    def schedule_user(
            self,
            telegram_id: int,
            times: Sequence[time],
            *,
            callback: Callable[[int], Awaitable[None]],
    ) -> None:
        self.unschedule_user(telegram_id)

        if not times:
            logger.info(f"No times to schedule for telegram_id={telegram_id}")
            return

        for t in times:
            rj = ReminderJob(telegram_id=telegram_id, at=t)
            trigger = CronTrigger(hour=t.hour, minute=t.minute, timezone=self._scheduler.timezone)

            self._scheduler.add_job(
                callback,
                trigger=trigger,
                id=rj.job_id,
                replace_existing=True,
                kwargs={"telegram_id": telegram_id},
                max_instances=1,
                misfire_grace_time=60,
                coalesce=True,
            )
            logger.debug(f"Added reminder: {rj.job_id} at {t.strftime('%H:%M')}")

        logger.info(f"Scheduled {len(times)} reminders for telegram_id={telegram_id}")

    def get_user_jobs(self, telegram_id: int) -> list[str]:
        prefix = f"reminder:{telegram_id}:"
        return [job.id for job in self._scheduler.get_jobs() if job.id.startswith(prefix)]

    def get_all_jobs_count(self) -> int:
        return len(self._scheduler.get_jobs())

    @staticmethod
    def parse_times(value: str | None) -> list[time]:
        if not value:
            return []

        value = value.strip()

        if value.startswith("["):
            try:
                raw = json.loads(value)
                if isinstance(raw, list):
                    items = [str(x) for x in raw]
                else:
                    return []
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON: {value}")
                return []
        else:
            items = [x.strip() for x in value.split(",") if x.strip()]

        out: list[time] = []
        for s in items:
            try:
                hh, mm = s.split(":")
                h, m = int(hh), int(mm)
                if 0 <= h <= 23 and 0 <= m <= 59:
                    out.append(time(h, m))
                else:
                    logger.warning(f"Invalid time: {s}")
            except Exception as e:
                logger.warning(f"Failed to parse time '{s}': {e}")
                continue

        return out
