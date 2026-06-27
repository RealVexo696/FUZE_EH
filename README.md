# 🤖 FUSE | Crime Hamburg - Discord Bot

## 📋 Beschreibung

Ein umfassender Discord-Bot für einen **Crime/Gang-themed** Discord-Server mit automatisiertem Server-Setup, Verifizierungssystem, Ticket-System und vielem mehr.

---

## 🚀 Features

### 🎯 Server-Setup
- **48+ Rollen** automatisch erstellt (vom Member bis zum Owner)
- **Textkanäle**: Willkommen, Verify, Chat, Gaming, Support, etc.
- **Sprachkanäle**: Allgemein, Gaming, Lounge, Büros
- **Log-Kanäle**: Für jede Aktion (Join, Leave, Messages, etc.)
- **Admin-Bereiche**: Private Channels für Admins
- **Büros**: Private Sprachkanäle für hohe Ränge

### 🔐 Verifizierungssystem
- Unverifizierte User sehen nur Willkommen & Verify
- Nach Verification Zugang zu allgemeinen Kanälen
- Bewerbungs-System für Rollen

### 🎫 Ticket-System
- Automatische Ticket-Erstellung
- Private Tickets pro User
- Admin-Benachrichtigungen

### 📝 Logging
- Willkommen Logs
- Verify Logs
- Leave Logs
- Message Logs (Erstellen, Bearbeiten, Löschen)
- Ticket Logs
- Ban/Kick/Mute Logs

---

## 🛠️ Installation

### Voraussetzungen
- Python 3.8+
- Discord Bot Token

### Setup

```bash
# Repository klonen
git clone https://github.com/DEIN-USERNAME/fuse-discord-bot.git
cd fuse-discord-bot

# Abhängigkeiten installieren
pip install -r requirements.txt

# Bot Token setzen
export DISCORD_BOT_TOKEN=dein_bot_token_hier
```

---

## 🚂 Railway Deployment

### 1. GitHub Repository erstellen
```bash
# Git initialisieren
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/DEIN-USERNAME/fuse-discord-bot.git
git push -u origin main
```

### 2. Railway Deployment

1. Gehe zu [railway.app](https://railway.app)
2. Login mit GitHub
3. "New Project" → "Deploy from GitHub Repo"
4. Wähle dein Repository
5. Füge Environment Variable hinzu:
   - `DISCORD_BOT_TOKEN` = dein_bot_token
6. Railway erkennt automatisch `bot.py` als Python-Projekt

---

## 📁 Projekt-Struktur

```
fuse-discord-bot/
├── bot.py              # Hauptbot Code
├── config.json         # Konfiguration
├── requirements.txt    # Python Dependencies
├── README.md           # Diese Datei
├── server_data.json    # (Automatisch erstellt)
└── .gitignore          # Git Ignores
```

---

## 🎮 Commands

| Command | Beschreibung |
|---------|-------------|
| `!start` | Startet interaktives Setup (3 Optionen) |
| `!setup` | Manuelles Setup (sofort) |
| `!help` | Zeigt Hilfe |
| `!ticket <grund>` | Erstellt ein Ticket |
| `!roles` | Zeigt alle Rollen |
| `!membercount` | Zeigt Member-Anzahl |
| `!broadcast <nachricht>` | Sendet Ankündigung (Admin) |
| `!kick <user> [grund]` | Kickt User (Admin) |
| `!ban <user> [grund]` | Bannt User (Admin) |
| `!mute <user> [grund]` | Muted User (Admin) |
| `!warn <user> [grund]` | Verwarnt User (Admin) |

---

## 🔧 Konfiguration

Bearbeite `config.json`:

```json
{
    "token": "DEIN_BOT_TOKEN",
    "guild_name": "FUSE | Crime Hamburg",
    "welcome_channel_name": "willkommen",
    "verify_channel_name": "verify",
    "log_channel_name": "logs",
    "ticket_category_name": "Tickets",
    "admin_role_name": "Admin",
    "owner_role_name": "Owner",
    "verified_role_name": "Member",
    "unverified_role_name": "Unverified",
    "embed_color": 16711680,
    "embed_footer": "FUSE | Crime Hamburg"
}
```

---

## ⚠️ Wichtige Hinweise

1. **Der Bot muss ADMIN Rechte haben** um alle Funktionen nutzen zu können
2. **Bevor `!start` ausgeführt wird**, sollte der Bot bereits auf dem Server sein
3. **Erstelle den Bot mit allen Intents** im Discord Developer Portal

---

## 📜 Rollen-Übersicht

| Rolle | Position | Farbe |
|-------|----------|-------|
| Owner | 1 (Oberste) | 🔴 Rot |
| Co-Owner | 2 | Dunkelrot |
| Boss | 3 | Dunkelrot |
| Vize Boss | 4 | Dunkelrot |
| General | 5 | Dunkelrot |
| Division General | 6 | Dunkelrot |
| Brigade General | 7 | Dunkelrot |
| Oberst | 8 | Dunkelrot |
| Major | 9 | Dunkelrot |
| Captain | 10 | Dunkelrot |
| Leutnant | 11 | Dunkelrot |
| ... | ... | ... |
| Member | Vorletzte | 🟢 Grün |
| Unverified | Letzte | ⚪ Grau |

---

## 🤝 Support

Bei Fragen oder Problemen, erstelle ein Issue auf GitHub oder kontaktiere den Entwickler.

---

**Made with ❤️ for FUSE | Crime Hamburg**