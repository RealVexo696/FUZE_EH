# 📖 FUSE Bot - Komplette Setup Anleitung

## Inhaltsverzeichnis
1. [Discord Bot erstellen](#1-discord-bot-erstellen)
2. [GitHub Repository einrichten](#2-github-repository-einrichten)
3. [Railway Deployment](#3-railway-deployment)
4. [Bot auf dem Server einrichten](#4-bot-auf-dem-server-einrichten)

---

## 1. Discord Bot erstellen

### 1.1 Discord Developer Portal
1. Gehe zu: https://discord.com/developers/applications
2. Klicke auf "New Application"
3. Gib einen Namen ein (z.B. "FUSE Bot")
4. Klicke auf "Create"

### 1.2 Bot erstellen
1. Gehe zu "Bot" in der linken Sidebar
2. Klicke auf "Add Bot"
3. Klicke auf "Yes, do it"

### 1.3 Bot Token kopieren
1. Klicke unter "Token" auf "Reset Token"
2. Kopiere den Token und speichere ihn sicher!
3. **WICHTIG**: Teile diesen Token niemals öffentlich!

### 1.4 Intents aktivieren
1. Gehe zu "Bot" → "Privileged Gateway Intents"
2. Aktiviere:
   - ✅ **PRESENCE INTENT**
   - ✅ **SERVER MEMBERS INTENT**
   - ✅ **MESSAGE CONTENT INTENT**

### 1.5 OAuth2 für Bot-Invite
1. Gehe zu "OAuth2" → "URL Generator"
2. Wähle scopes:
   - ✅ bot
   - ✅ applications.commands
3. Wähle Permissions:
   - ✅ Administrator (oder die spezifischen Permissions unten)
   
   Oder spezifisch:
   - Manage Roles
   - Manage Channels
   - View Channels
   - Send Messages
   - Manage Messages
   - Embed Links
   - Read Message History
   - Add Reactions
   - Connect (für Voice)
   - Speak (für Voice)

4. Kopiere die generierte URL und öffne sie im Browser
5. Wähle deinen Server aus und authorize den Bot

---

## 2. GitHub Repository einrichten

### 2.1 GitHub Account erstellen
1. Gehe zu https://github.com
2. Erstelle einen Account oder logge dich ein

### 2.2 Neues Repository erstellen
1. Klicke auf "New repository"
2. Repository Name: `fuse-discord-bot`
3. Wähle "Private" (empfohlen)
4. Klicke "Create repository"

### 2.3 Lokal Git einrichten (Windows/Mac/Linux)

```bash
# In den Projekt-Ordner wechseln
cd fuse-discord-bot

# Git initialisieren
git init

# Alle Dateien hinzufügen
git add .

# Ersten Commit erstellen
git commit -m "Initial commit - FUSE Bot"

# Remote hinzufügen (ersetze mit deiner URL)
git remote add origin https://github.com/DEIN_USERNAME/fuse-discord-bot.git

# Auf GitHub pushen
git branch -M main
git push -u origin main
```

---

## 3. Railway Deployment

### 3.1 Railway Account erstellen
1. Gehe zu https://railway.app
2. Logge dich mit GitHub ein
3. Erlaube den Zugriff auf deine Repositories

### 3.2 Neues Projekt erstellen
1. Klicke "New Project"
2. Wähle "Deploy from GitHub repo"
3. Wähle dein `fuse-discord-bot` Repository
4. Railway erkennt automatisch Python

### 3.3 Environment Variables setzen
1. Klicke auf dein Projekt
2. Gehe zu "Variables"
3. Füge eine neue Variable hinzu:
   - Name: `DISCORD_BOT_TOKEN`
   - Value: Dein Bot Token (aus Schritt 1.3)

### 3.4 Deployment starten
1. Railway erkennt automatisch `bot.py` und `requirements.txt`
2. Klicke "Deploy" oder warte bis es automatisch startet
3. Logge in Railway die Konsole aus um den Status zu sehen

### 3.5 Updates deployen
```bash
# Nach Änderungen
git add .
git commit -m "Deine Änderung"
git push origin main
```
Railway erkennt den Push automatisch und deployed neu!

---

## 4. Bot auf dem Server einrichten

### 4.1 Bot einladen (falls noch nicht done)
Verwende die OAuth2 URL aus Schritt 1.5 um den Bot auf deinen Server einzuladen.

### 4.2 !start Befehl nutzen
1. Finde einen Kanal wo der Bot Nachrichten senden kann
2. Schreibe `!start`
3. Der Bot zeigt einEmbed mit 3 Optionen:
   - 🇦 Abbruch
   - 🇧 Nur Hinzufügen (fehlende Sachen hinzufügen)
   - 🇨 Komplett neu aufsetzen (alles neu erstellen)
4. Wähle eine Option durch Reagieren

### 4.3 Setup abwarten
Der Bot erstellt nun:
- ✅ 48+ Rollen
- ✅ Alle Kategorien
- ✅ Alle Textkanäle
- ✅ Alle Sprachkanäle
- ✅ Log-Kanäle
- ✅ Admin-Kanäle
- ✅ Büros für hohe Ränge

### 4.4 Verifizierung aktivieren
1. Füge dich selbst als Owner/Admin Rolle ein
2. Teste das Verify-System mit einem neuen Account

---

## 🎮 Commands Übersicht

| Befehl | Beschreibung | Permission |
|--------|--------------|------------|
| `!start` | Interaktives Setup | Admin+ |
| `!setup` | Sofort Setup | Admin+ |
| `!help` | Hilfe anzeigen | Alle |
| `!ticket [Grund]` | Ticket erstellen | Alle |
| `!roles` | Alle Rollen anzeigen | Alle |
| `!membercount` | Member Anzahl | Alle |
| `!broadcast [Text]` | Ankündigung senden | Admin+ |
| `!kick [User] [Grund]` | User kicken | Admin+ |
| `!ban [User] [Grund]` | User bannen | Admin+ |
| `!mute [User] [Grund]` | User muten | Admin+ |
| `!warn [User] [Grund]` | User verwarnen | Admin+ |

---

## 🔧 Troubleshooting

### Bot startet nicht?
- Prüfe ob der Token korrekt ist
- Prüfe ob `requirements.txt` existiert
- Prüfe Railway Logs für Fehler

### Commands funktionieren nicht?
- Bot muss ADMIN Rechte haben
- User muss die richtige Rolle haben

### Kanäle werden nicht erstellt?
- Bot muss ADMIN Rechte haben
- Server kann max. 500 Channels haben

### Verification funktioniert nicht?
- Prüfe ob "Unverified" Rolle existiert
- Prüfe ob "Member" Rolle existiert

---

## 📞 Support

Bei Problemen:
1. Erstelle ein Issue auf GitHub
2. Prüfe Railway Logs
3. Überprüfe Bot Permissions