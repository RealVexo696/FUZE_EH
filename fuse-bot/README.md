# 🎮 FUSE | FS — Discord Bot v4 (Ultimate Edition)

Ein kompletter Roblox-RP / Notruf-Hamburg Crime-Gang Discord-Bot mit **allem drin**.

---

## ✨ Features

### 🛠 Setup
- **`!start`** Wizard (3 Buttons: Abbruch / Hinzufügen / Komplett neu)
- ~52 Rollen mit **Divider-Rollen** für cleane Optik
- 13+ Kategorien mit ~80 Kanälen
- Owner-Hierarchie wird automatisch erzwungen

### 🛡️ Moderation & Security
- **🤖 AutoMod** — Bad-Words, Discord-Invites, Scam-Links, Caps-Spam, Message-Spam, Anti-Raid
- **⚖️ Warn-System** (`/warn`, `/warnings`, `/clearwarn`) — Auto-Mute bei 3, Auto-Ban bei 5
- **🕵️ Alt-Detection** — Junge Accounts / kein Avatar → Quarantäne + Staff-Ping

### 📊 Statistik & Analytics
- **📈 Stats-Dashboard** (`!stats-setup`) — Live-Voice-Channels: Member, Online, In Voice, Bots
- **🏅 Leaderboard** (`/top xp/messages/voice/monthly`)
- **📊 Profile** (`/profile @user`) — Level, XP, Warns, Voice-Zeit, Geburtstag
- **🏆 Spieler des Monats** — automatisch am 1. des Monats

### 🎉 Community
- **🎁 Giveaway-System** (`/giveaway`) — mit 🎉-Button, Re-Roll, Rollen-Requirement
- **🎂 Geburtstage** (`/birthday set/remove/list`) — Auto-Ping + Rolle für 24h
- **✅ Verify** + **📋 Bewerbungs-System** mit Modal + Accept/Deny Buttons
- **🎫 Ticket-System** (5 Kategorien, Player-Meldung mit Modal, Transcript bei Close)

### ⏰ Automatisierung
- **Bewerbungs-Reminder** nach 48h, Auto-Close nach 7 Tagen
- **Ticket-Transcripts** als HTML beim Schließen → Log + DM
- **XP via Messages + Voice** mit Auto-Rollen (Level 5/25/50/100/200)

### 🎛️ Web-Dashboard
- Flask-App auf gleichem Port → Discord OAuth Login
- Übersicht: Members, Warns, Bewerbungen, XP-Leaderboard
- Erreichbar unter `https://deinapp.railway.app`

### 📋 Logging
11 Log-Kanäle: join/leave/verify/message/voice/role/channel/server/ticket/moderation/bot

---

## 🚀 Deployment auf Railway

### 1. Discord-Bot anlegen
1. <https://discord.com/developers/applications> → **New Application**
2. **Bot** → Token kopieren
3. **Privileged Gateway Intents** alle 3 aktivieren
4. **OAuth2 → URL Generator** → Scopes: `bot`, `applications.commands` → Permissions: **Administrator** → Bot einladen

### 2. Code zu GitHub pushen
```bash
git init && git add . && git commit -m "init" && git push
```

### 3. Railway konfigurieren
1. **New Project → Deploy from GitHub**
2. **Variables** anlegen (aus `.env.example`):
   - `DISCORD_TOKEN` (Pflicht)
   - `ENABLE_DASHBOARD=1` + OAuth-Variablen (optional)
3. **Domain generieren** in Settings → wenn Dashboard aktiv

### 4. Im Server
- Bot-Rolle **ganz nach oben** schieben
- `!start` → „Komplett neu aufsetzen"

---

## ⚙️ Befehle

### Slash-Commands
| Command | Beschreibung |
|---|---|
| `/warn @user reason` | User verwarnen |
| `/warnings @user` | Verwarnungen ansehen |
| `/clearwarn @user [index]` | Verwarnung löschen |
| `/profile [@user]` | Benutzer-Profil |
| `/top kategorie` | Leaderboard |
| `/giveaway prize duration winners [role]` | Giveaway starten |
| `/birthday set tag monat` | Geburtstag setzen |

### Prefix-Commands
| Command | Beschreibung |
|---|---|
| `!start` | Setup-Wizard |
| `!stats-setup` | Stats-Channels erstellen |
| `!fix-hierarchie` | Rollen-Reihenfolge fixen |
| `!resend-verify` / `!resend-apply` / `!resend-ticket` | Buttons neu posten |
| `!clear-cooldown @user` | Bewerbungs-Sperre löschen |
| `!raid-off` | Raid-Lockdown deaktivieren |

---

## 📁 Struktur

```
fuse-bot/
├── bot.py                 ← Hauptdatei
├── db.py                  ← JSON-Datenbank
├── utils.py               ← geteilte Helper
├── dashboard.py           ← Flask Web-Dashboard
├── cogs/
│   ├── automod.py         ← AutoMod
│   ├── warns.py           ← Warn-System
│   ├── alt_detection.py   ← Alt-Account-Schutz
│   ├── stats.py           ← Live-Stats-Channels
│   ├── xp.py              ← XP/Level/Leaderboard
│   ├── giveaway.py        ← Giveaways
│   ├── birthday.py        ← Geburtstage
│   ├── application_tasks.py ← Bewerbungs-Reminder
│   └── transcripts.py     ← HTML-Transcripts
├── requirements.txt
├── railway.json / Procfile
└── data.json              ← Auto-erstellt (in .gitignore)
```

---

## 🐞 Troubleshooting

| Problem | Lösung |
|---|---|
| Bot reagiert nicht | Intents aktiviert? Token richtig? |
| „Missing Permissions" | Bot-Rolle ganz nach oben + Administrator |
| Slash-Commands fehlen | 1-5 Minuten warten nach Start (Discord cached) |
| Dashboard 404 | `OAUTH_REDIRECT_URI` muss exakt mit Railway-Domain + `/callback` matchen |
| Stats-Channels updaten nicht | `!stats-setup` einmalig ausführen |

Viel Spaß mit deinem **FUSE | FS** Ultimate Bot! 💎
