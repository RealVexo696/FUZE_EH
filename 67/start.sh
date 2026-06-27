#!/bin/bash

# FUSE | Crime Hamburg - Bot Start Script

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  FUSE | Crime Hamburg - Discord Bot                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Prüfe ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 nicht gefunden. Bitte installiere Python 3.8+"
    exit 1
fi

# Prüfe ob pip installiert ist
if ! command -v pip &> /dev/null; then
    echo "❌ pip nicht gefunden. Bitte installiere pip"
    exit 1
fi

# Installiere Abhängigkeiten
echo "📦 Installiere Abhängigkeiten..."
pip install -r requirements.txt

# Starte den Bot
echo "🚀 Starte FUSE Bot..."
python3 bot.py