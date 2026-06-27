# Fuse Discord Setup Bot

Ein Discord-Bot in Python für Railway/GitHub, der mit `!start` einen kompletten Roblox-/Crime-Gang-Server grob wie in den Screenshots aufsetzt.

## Features
- Erstellt Kategorien, Textkanäle, Sprachkanäle und Büro-Channels
- Erstellt ca. 50 Rollen in richtiger Reihenfolge
- Verify-System per Button
- Begrüßungs- und Tschüss-Nachrichten
- Log-Kanäle für Join, Leave, Verify, Tickets, Bewerbung, Moderation, Setup
- Setup-Auswahl mit Buttons:
  - Abbruch
  - Nur hinzufügen
  - Komplett neu aufsetzen

## Railway Setup
1. Repository auf GitHub hochladen
2. Neues Railway-Projekt erstellen
3. GitHub-Repo verbinden
4. Umgebungsvariable setzen:
   - `DISCORD_TOKEN=dein_bot_token`
5. Start Command ist automatisch `python bot.py`

## Discord Bot Einstellungen
Im Discord Developer Portal aktivieren:
- Server Members Intent
- Message Content Intent

## Rechte
Der Bot sollte Administrator-Rechte haben, damit Rollen/Kanäle/Permissions sauber erstellt werden können.

## Start
Im Server als Admin eingeben:
```txt
!start
```

Dann eine der 3 Optionen im Embed anklicken.

## Hinweis
Der Bot ist auf deinen Wunsch für Roblox/FiveM-artiges Crime-Gang Styling aufgebaut, aber ausdrücklich nur für ein Spiel-/Community-Setting.
