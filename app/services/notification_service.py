from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import time
from typing import Iterable, Sequence

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

    def __init__(self, *, timezone: str = "UTC", scheduler: AsyncIOScheduler | None = None) -> None:
        self._scheduler = scheduler or AsyncIOScheduler(timezone=timezone)
        self._started = False

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
        for job in list(self._scheduler.get_jobs()):
            if job.id.startswith(prefix):
                self._scheduler.remove_job(job.id)
        logger.debug("Unscheduled all reminders for telegram_id=%s", telegram_id)

    def schedule_user(self, telegram_id: int, times: Sequence[time], *, callback) -> None:
        self.unschedule_user(telegram_id)
        for t in times:
            rj = ReminderJob(telegram_id=telegram_id, at=t)
            trigger = CronTrigger(hour=t.hour, minute=t.minute)
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
        logger.info("Scheduled %s reminder(s) for telegram_id=%s", len(times), telegram_id)

    @staticmethod
    def parse_times(value: str | None) -> list[time]:
        if not value:
            return []

        value = value.strip()
        items: Iterable[str]

        if value.startswith("["):
            try:
                raw = json.loads(value)
                if isinstance(raw, list):
                    items = [str(x) for x in raw]
                else:
                    return []
            except json.JSONDecodeError:
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
            except Exception:
                continue
        return out