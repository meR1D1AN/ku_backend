from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property

from blogs.constants import (
    ALLOWED_VIDEO_EXT,
    MAX_FILE_SIZE_BYTES,
    MAX_PHOTOS,
)


# ───────────────────────────── forbidden-words ──────────────────────────────
class DynamicForbiddenWordValidator:
    """Проверяет текст на наличие запрещённых слов из файла."""

    def __init__(self, field_name: str | None = None) -> None:
        self.field_name = field_name

    @cached_property
    def forbidden_words(self) -> set[str]:
        words_file = Path(settings.BASE_DIR) / "all_fixture" / "validators" / "forbidden_words.txt"
        if not words_file.exists():
            raise FileNotFoundError(f"Не найден {words_file.relative_to(settings.BASE_DIR)}")
        return {w.strip().lower() for w in words_file.read_text(encoding="utf-8").splitlines() if w.strip()}

    def __call__(self, value: str) -> str:
        if isinstance(value, str) and any(bad in value.lower() for bad in self.forbidden_words):
            field = f" в поле «{self.field_name}»" if self.field_name else ""
            raise ValidationError(f"Недопустимое слово{field}.")
        return value


# ───────────────────────── media-helpers (size / count) ─────────────────────
def validate_media_file(file, *, is_video: bool = False) -> None:
    """Размер ≤ 10 МБ; для видео — ещё и расширение."""
    if file.size > MAX_FILE_SIZE_BYTES:
        raise ValidationError("Файл весит больше 10 МБ")
    if is_video and Path(file.name).suffix.lower() not in ALLOWED_VIDEO_EXT:
        raise ValidationError("Видео допускается только в MP4 / WebM")


def enforce_media_limit(article) -> None:
    """Не более 10 фото/видео на одну статью."""
    if article.media.count() >= MAX_PHOTOS:
        raise ValidationError(f"Лимит {MAX_PHOTOS} файлов на статью превышен")
