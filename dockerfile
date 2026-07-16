FROM python:3.12-slim

# 安裝 Chromium 瀏覽器與對應的 driver（Debian 官方 repo 已內建，支援 arm64）
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV DB_DIR=/app/data

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]