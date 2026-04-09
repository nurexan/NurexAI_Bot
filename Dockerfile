# Python 3.12 yengil versiyasi
FROM python:3.12-slim

# FFmpeg o'rnatish (Videolarni birlashtirish uchun juda muhim)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Ishchi papka
WORKDIR /app

# Kutubxonalarni ko'chirish va o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Barcha kodlarni ko'chirish
COPY . .

# Botni ishga tushirish
CMD ["python", "bot.py"]
