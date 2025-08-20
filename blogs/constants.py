# Константы политики медиа для приложения «Блог»
from typing import Final

# Количество
MAX_PHOTOS: Final[int] = 10
MAX_VIDEOS: Final[int] = 1

# Размеры
MAX_FILE_SIZE_MB: Final[int] = 10
MAX_FILE_SIZE_BYTES: Final[int] = MAX_FILE_SIZE_MB * 1024 * 1024  # 10 МБ

# Видео
ALLOWED_VIDEO_EXT: Final[tuple[str, ...]] = (".mp4", ".webm")
MAX_VIDEO_DURATION_SEC: Final[int] = 2 * 60  # 120 секунд

# Эти имена используются в all_fixture/views_fixture.py (ВРЕМЕННО)
MAX_PHOTO_SIZE_MB = MAX_FILE_SIZE_MB
MAX_VIDEO_SIZE_MB = MAX_FILE_SIZE_MB
MAX_MEDIA_PER_ARTICLE = MAX_PHOTOS
MAX_NUM_VIDEOS = MAX_VIDEOS
MAX_VIDEO_DURATION = MAX_VIDEO_DURATION_SEC
# Если где-то ждут размер в байтах под старым именем:
MAX_FILE_SIZE = MAX_FILE_SIZE_BYTES
