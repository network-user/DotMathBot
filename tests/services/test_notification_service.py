"""Tests for app.services.notification_service."""
import pytest

from app.services.notification_service import NotificationService, ReminderJob
from datetime import time


class TestReminderJob:
    def test_job_id_format(self):
        rj = ReminderJob(telegram_id=123, at=time(7, 30))
        assert rj.job_id == "reminder:123:0730"

    def test_job_id_midnight(self):
        rj = ReminderJob(telegram_id=1, at=time(0, 0))
        assert "00" in rj.job_id


class TestNotificationService:
    def test_start_and_shutdown(self):
        svc = NotificationService()
        assert not svc._started
        svc.start()
        assert svc._started
        svc.shutdown()
        assert not svc._started

    def test_double_start_idempotent(self):
        svc = NotificationService()
        svc.start()
        svc.start()
        assert svc._started
        svc.shutdown()

    def test_unschedule_user_no_jobs(self):
        svc = NotificationService()
        svc.unschedule_user(999)

    def test_schedule_user_adds_jobs(self):
        svc = NotificationService()
        calls = []

        def callback(telegram_id):
            calls.append(telegram_id)

        svc.schedule_user(123, [time(7, 30), time(12, 0)], callback=callback)
        jobs = svc.scheduler.get_jobs()
        assert len(jobs) == 2
        svc.shutdown()


class TestParseTimes:
    def test_empty_or_none(self):
        assert NotificationService.parse_times(None) == []
        assert NotificationService.parse_times("") == []
        assert NotificationService.parse_times("   ") == []

    def test_comma_separated(self):
        result = NotificationService.parse_times("07:30, 12:00, 19:00")
        assert result == [time(7, 30), time(12, 0), time(19, 0)]

    def test_single_time(self):
        result = NotificationService.parse_times("23:59")
        assert result == [time(23, 59)]

    def test_invalid_skipped(self):
        result = NotificationService.parse_times("07:30, invalid, 12:00")
        assert time(7, 30) in result
        assert time(12, 0) in result
        assert len(result) == 2

    def test_out_of_range_skipped(self):
        result = NotificationService.parse_times("25:00, 12:60")
        assert result == []

    def test_json_array(self):
        result = NotificationService.parse_times('["07:30", "12:00"]')
        assert result == [time(7, 30), time(12, 0)]

    def test_invalid_json_returns_empty(self):
        result = NotificationService.parse_times("[invalid")
        assert result == []
