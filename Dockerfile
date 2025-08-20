FROM python:3.12.8

WORKDIR /app

RUN pip install uv

# Копируем только файл с зависимостями
COPY pyproject.toml ./

# Генерируем requirements.txt и устанавливаем зависимости с флагом --system
RUN uv pip compile pyproject.toml -o requirements.txt && \
    uv pip install --system -r requirements.txt && \
    pip cache purge

# Копируем остальной код проекта
COPY . .