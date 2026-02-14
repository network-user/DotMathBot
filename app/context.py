"""
Application context: holds shared services (e.g. NotificationService) set at startup.
Use this instead of global variables so handlers can access services without importing main.
"""
from __future__ import annotations

from app.services.notification_service import NotificationService

_notification_service: NotificationService | None = None


def set_notification_service(service: NotificationService) -> None:
    """Set the NotificationService instance (called from bootstrap)."""
    global _notification_service
    _notification_service = service


def get_notification_service() -> NotificationService:
    """Get the NotificationService instance. Raises RuntimeError if not initialized."""
    if _notification_service is None:
        raise RuntimeError("NotificationService not initialized")
    return _notification_service


def has_notification_service() -> bool:
    """Return True if NotificationService has been set."""
    return _notification_service is not None
