FROM python:3.11-slim

WORKDIR /app

# Kopiere requirements
COPY requirements.txt .

# Installiere dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere alle Dateien
COPY . .

# Setze Umgebungsvariable für Railway
ENV DISCORD_BOT_TOKEN=

# Starte den Bot
CMD ["python", "bot.py"]