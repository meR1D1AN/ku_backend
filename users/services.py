from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from django.utils.timezone import localtime

from users.models import LoginAttempt, User

# Также переопределила в settings.py:
# LOGIN_ATTEMPTS_LIMIT = 5
# LOGIN_BAN_STEPS = [timedelta(...), ...]

LOGIN_ATTEMPTS_LIMIT = getattr(settings, "LOGIN_ATTEMPTS_LIMIT", 5)

DEFAULT_BAN_STEPS = [
    timedelta(minutes=15),
    timedelta(hours=1),
    timedelta(days=1),
    timedelta(days=7),
]
BAN_STEPS = getattr(settings, "LOGIN_BAN_STEPS", DEFAULT_BAN_STEPS)


@dataclass
class AttemptState:
    remaining_attempts: int
    blocked_until: str | None  # ISO-8601 в локальной TZ, либо None


def _iso_local(dt) -> str:
    """ISO-строка с учётом локальной таймзоны Django (TIME_ZONE)."""
    return localtime(dt).isoformat()


def get_login_state(user: User) -> AttemptState:
    """Вернёт текущее состояние счётчиков/блокировки для ответа фронту."""
    if user.is_banned() and user.ban_until:
        return AttemptState(remaining_attempts=0, blocked_until=_iso_local(user.ban_until))
    remaining = max(0, LOGIN_ATTEMPTS_LIMIT - int(user.failed_login_count or 0))
    return AttemptState(remaining_attempts=remaining, blocked_until=None)


def record_login_attempt(user: User, success: bool, ip: str | None = None) -> AttemptState:
    """Логируем попытку, обновляем счётчики/блокировку и возвращаем текущее состояние."""
    LoginAttempt.objects.create(user=user, success=success, ip=ip)

    if success:
        # Сброс при успешном входе
        user.failed_login_count = 0
        user.ban_level = 0
        user.ban_until = None
    else:
        # Неуспешная попытка
        user.failed_login_count = int(user.failed_login_count or 0) + 1
        if user.failed_login_count >= LOGIN_ATTEMPTS_LIMIT:
            # Эскалация временной блокировки
            level = min(int(user.ban_level or 0), len(BAN_STEPS) - 1)
            user.ban_until = timezone.now() + BAN_STEPS[level]
            user.ban_level = min(level + 1, len(BAN_STEPS) - 1)
            user.failed_login_count = 0

    user.save(update_fields=["failed_login_count", "ban_level", "ban_until"])
    return get_login_state(user)


def check_ban(user: User):
    """Поднимет PermissionError при активной блокировке (используется в вьюхе)."""
    if user.is_banned():
        raise PermissionError(f"Аккаунт заблокирован до {_iso_local(user.ban_until)}")
