# 🎮 FUSE | FS – Discord Setup Bot

Ein kompletter Discord-Bot für eine **Roblox / Notruf-Hamburg Crime-Gang** Community.  
Erstellt mit einem einzigen Befehl den **gesamten Server** mit Rollen, Kategorien, Kanälen, Logs, Verify-System, Tickets und mehr.

> ⚠️ Hinweis: Dieser Server ist ausschließlich für **Roblox-Roleplay** – nichts davon hat einen Real-Life-Bezug.

---

## ✨ Features

- **`!start` Setup-Wizard** mit 3 Buttons (Embed):
  - 🛑 **Abbruch**
  - ➕ **Nur Hinzufügen** (ergänzt fehlendes, lässt vorhandenes)
  - ♻️ **Komplett neu aufsetzen** (löscht & erstellt alles neu, mit Sicherheitsabfrage)
- **~52 Rollen** in korrekter Hierarchie (Owner → Unverified) mit passenden Permissions, Farben & Hoist
- **10+ Kategorien** angelehnt an die Vorlagen-Screenshots (Willkommen, Bewerbung, Infos, Community, Socialmedia, Talks, Bros-Merch, Gang-Infos, Lounges, Büros, Admin, Logs)
- **Admin-Bereich**: Owner-Chat, Admin-Chat, Mod-Chat, Support-Chat, Team-Todo, Reports …
- **Komplettes Log-System**: Join, Leave, Verify, Message, Voice, Role, Channel, Server, Ticket, Moderation, Bot
- **Welcome-Nachricht** mit Member-Counter
- **Verify-System** per Button (Unverified → Verified → Bewerber sichtbar; Member sieht alles)
- **Ticket-System** per Button mit Schließen-Button & Log
- **Auto-Befüllung** wichtiger Kanäle: Regelwerk, Verify, Willkommen, Formular, Ticket, Ankündigung, Boosts, Owner-Chat
- **Büros** für hohe Rollen
- **Sprachkanäle**: FFA-Voice, Gaming, Musik, AFK, Stage, Bewerbungs-Warteraum, Einreise 1/2
- **Locked-Lounges** für Booster / engste Crew

---

## 🚀 Deployment (Railway + GitHub)

### 1. Bot anlegen
1. Gehe auf <https://discord.com/developers/applications>
2. **New Application** → Name eingeben → **Bot** Tab
3. **Reset Token** und Token kopieren
4. **Privileged Gateway Intents** aktivieren:
   - ✅ PRESENCE INTENT
   - ✅ SERVER MEMBERS INTENT
   - ✅ MESSAGE CONTENT INTENT
5. **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Permissions: **Administrator**
6. Bot mit dem generierten Link auf deinen Server einladen

### 2. GitHub
```bash
git init
git add .
git commit -m "fuse bot init"
git branch -M main
git remote add origin https://github.com/<dein-user>/fuse-bot.git
git push -u origin main
```

### 3. Railway
1. <https://railway.app> → **New Project** → **Deploy from GitHub Repo** → Repo wählen
2. Im Tab **Variables** anlegen:
   - `DISCORD_TOKEN` = `dein_token`
   - `PREFIX` = `!` (optional)
   - `SERVER_NAME` = `FUSE | FS` (optional)
3. Deploy startet automatisch. Logs siehst du im **Deployments**-Tab.

### 4. Auf deinem Server
- Bot-Rolle **ganz nach oben** in der Rollen-Liste schieben!
- In einem beliebigen Kanal eingeben:
  ```
  !start
  ```
- Eine der 3 Optionen wählen → fertig 🎉

---

## ⚙️ Befehle

| Befehl | Berechtigung | Beschreibung |
|---|---|---|
| `!start` | Administrator | Öffnet den Setup-Wizard |
| `!resend-verify` | Administrator | Sendet den Verify-Button erneut im aktuellen Kanal |

---

## 📁 Projekt-Struktur

```
fuse-bot/
├── bot.py             ← Hauptdatei
├── requirements.txt   ← Python-Abhängigkeiten
├── Procfile           ← für Railway/Heroku
├── runtime.txt        ← Python-Version
├── railway.json       ← Railway-Config
├── .env.example       ← Vorlage für Env-Vars
├── .gitignore
└── README.md
```

---

## 🛠️ Lokal testen

```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# DISCORD_TOKEN in .env eintragen
python bot.py
```

---

## ❓ Troubleshooting

- **Bot reagiert nicht** → Intents aktiviert? Token korrekt?
- **„Forbidden: Missing Permissions"** → Bot-Rolle ist nicht hoch genug. Sie muss **über** allen Rollen stehen, die er erstellt/verändert.
- **Manche Rollen fehlen** → `!start` nochmal ausführen mit **Nur Hinzufügen**.
- **Welcome funktioniert nicht** → `SERVER MEMBERS INTENT` aktivieren (Discord Developer Portal).

Viel Spaß mit deinem **FUSE | FS** Server! 💎
