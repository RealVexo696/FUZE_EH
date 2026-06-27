"""
╔══════════════════════════════════════════════════════════════╗
║  FUSE | Crime Hamburg - Discord Bot                          ║
║  Ein umfassender Discord-Server-Management Bot               ║
╚══════════════════════════════════════════════════════════════╝
"""

import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import asyncio

# ============================================================
# KONFIGURATION
# ============================================================

with open('config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ============================================================
# VARIABLEN FÜR SERVER SETUP
# ============================================================

# Rollen Liste (von unten nach oben sortiert - Owner ganz oben)
ROLES_DATA = [
    {"name": "Unverified", "color": 0x808080, "position": 0, "permissions": 0},
    {"name": "Member", "color": 0x00FF00, "position": 1, "permissions": 104320},
    {"name": "Gast", "color": 0xFFFF00, "position": 2, "permissions": 104320},
    {"name": "Recruit", "color": 0x00FFFF, "position": 3, "permissions": 104320},
    {"name": "Probemitglied", "color": 0xFF6600, "position": 4, "permissions": 104320},
    {"name": "Vollmitglied", "color": 0x00FF00, "position": 5, "permissions": 108544},
    {"name": "Operator", "color": 0xFF0000, "position": 6, "permissions": 108544},
    {"name": "Sicherheit", "color": 0x990000, "position": 7, "permissions": 108544},
    {"name": "Bodyguard", "color": 0x800000, "position": 8, "permissions": 108544},
    {"name": "Straßenposten", "color": 0x666666, "position": 9, "permissions": 104320},
    {"name": "Dealer", "color": 0xCC0000, "position": 10, "permissions": 108544},
    {"name": "Läufer", "color": 0x993300, "position": 11, "permissions": 104320},
    {"name": "Beschatter", "color": 0x996600, "position": 12, "permissions": 108544},
    {"name": "Spitzel", "color": 0x669900, "position": 13, "permissions": 108544},
    {"name": "Informant", "color": 0x009966, "position": 14, "permissions": 104320},
    {"name": "Geldfahrer", "color": 0x009999, "position": 15, "permissions": 108544},
    {"name": "Watchlist", "color": 0xFF0066, "position": 16, "permissions": 104320},
    {"name": "Untergrund", "color": 0x333333, "position": 17, "permissions": 104320},
    {"name": "Struktur", "color": 0x444444, "position": 18, "permissions": 108544},
    {"name": "Logistik", "color": 0x555555, "position": 19, "permissions": 108544},
    {"name": "Finanzen", "color": 0xFFD700, "position": 20, "permissions": 108544},
    {"name": "Buchhaltung", "color": 0xFFA500, "position": 21, "permissions": 108544},
    {"name": "Schatzmeister", "color": 0xFFCC00, "position": 22, "permissions": 108544},
    {"name": "Kassierer", "color": 0xFF9900, "position": 23, "permissions": 108544},
    {"name": "Organisator", "color": 0xCC9900, "position": 24, "permissions": 108544},
    {"name": "Planer", "color": 0xFF5500, "position": 25, "permissions": 108544},
    {"name": "Strategist", "color": 0xFF3300, "position": 26, "permissions": 108544},
    {"name": "Taktiker", "color": 0xFF1100, "position": 27, "permissions": 108544},
    {"name": "Kontaktmann", "color": 0xCC0000, "position": 28, "permissions": 108544},
    {"name": "Vermittler", "color": 0xDD0000, "position": 29, "permissions": 108544},
    {"name": "Moderator", "color": 0xFF0000, "position": 30, "permissions": 108544},
    {"name": "Supporter", "color": 0xEE0000, "position": 31, "permissions": 108544},
    {"name": "Techniker", "color": 0xAA0000, "position": 32, "permissions": 108544},
    {"name": "IT-Spezialist", "color": 0x880000, "position": 33, "permissions": 108544},
    {"name": "Admin", "color": 0xFF0000, "position": 34, "permissions": 8},
    {"name": "Co-Admin", "color": 0xEE0000, "position": 35, "permissions": 8},
    {"name": "Stellvertreter", "color": 0xDD0000, "position": 36, "permissions": 8},
    {"name": "Leutnant", "color": 0xCC0000, "position": 37, "permissions": 8},
    {"name": "Captain", "color": 0xBB0000, "position": 38, "permissions": 8},
    {"name": "Major", "color": 0xAA0000, "position": 39, "permissions": 8},
    {"name": "Oberst", "color": 0x990000, "position": 40, "permissions": 8},
    {"name": "Brigade General", "color": 0x880000, "position": 41, "permissions": 8},
    {"name": "Division General", "color": 0x770000, "position": 42, "permissions": 8},
    {"name": "General", "color": 0x660000, "position": 43, "permissions": 8},
    {"name": "Vize Boss", "color": 0x550000, "position": 44, "permissions": 8},
    {"name": "Boss", "color": 0x440000, "position": 45, "permissions": 8},
    {"name": "Co-Owner", "color": 0x330000, "position": 46, "permissions": 8},
    {"name": "Owner", "color": 0xFF0000, "position": 47, "permissions": 8},
]

# Kanäle die erstellt werden sollen
CHANNELS_DATA = {
    "text_channels": [
        # Willkommen Bereich
        {"name": "willkommen", "category": "🏠 Willkommen", "topic": "Willkommen bei FUSE | Crime Hamburg"},
        {"name": "regeln", "category": "🏠 Willkommen", "topic": "Bitte lies die Regeln sorgfältig durch"},
        {"name": "ankündigungen", "category": "🏠 Willkommen", "topic": "Wichtige Ankündigungen hier"},
        {"name": "news", "category": "🏠 Willkommen", "topic": "Neuigkeiten und Updates"},
        {"name": "crew-vorstellung", "category": "🏠 Willkommen", "topic": "Stelle dich der Crew vor"},
        
        # Verify Bereich
        {"name": "verify", "category": "🔐 Verify", "topic": "Verifiziere dich hier um Zugang zu erhalten"},
        {"name": "bewerbung", "category": "🔐 Verify", "topic": "Bewirb dich hier für eine Rolle"},
        {"name": "faq", "category": "🔐 Verify", "topic": "Häufig gestellte Fragen"},
        
        # Chat Bereich
        {"name": "allgemein", "category": "💬 Chat", "topic": "Allgemeiner Chat für alle Mitglieder"},
        {"name": "smalltalk", "category": "💬 Chat", "topic": "Entspannter Smalltalk"},
        {"name": "spam", "category": "💬 Chat", "topic": "Spam-Kanal für lustige Sachen"},
        {"name": "bilder", "category": "💬 Chat", "topic": "Bilder und Memes teilen"},
        {"name": "memes", "category": "💬 Chat", "topic": "Memes und lustige Sachen"},
        {"name": "witz-des-tages", "category": "💬 Chat", "topic": "Täglicher Witz"},
        {"name": "daily-chat", "category": "💬 Chat", "topic": "Täglicher Chat"},
        {"name": "ounge-chat", "category": "💬 Chat", "topic": "Lounge Gespräche"},
        {"name": "nighthawk", "category": "💬 Chat", "topic": "Nachtsactiv"},
        {"name": "cannabis-talk", "category": "💬 Chat", "topic": "Cannabis Talk"},
        {"name": "bohlen-tipps", "category": "💬 Chat", "topic": "Bohlen Tipps und Tricks"},
        {"name": "geschichten", "category": "💬 Chat", "topic": "Echte Geschichten erzählen"},
        {"name": "trip-report", "category": "💬 Chat", "topic": "Trip Reports teilen"},
        {"name": "deal-stories", "category": "💬 Chat", "topic": "Deal Geschichten"},
        
        # Unterhaltung
        {"name": "musik", "category": "🎵 Unterhaltung", "topic": "Musik teilen und hören"},
        {"name": "musik-recommendations", "category": "🎵 Unterhaltung", "topic": "Musik Empfehlungen"},
        {"name": "beats-produktion", "category": "🎵 Unterhaltung", "topic": "Beats und Produktion"},
        {"name": "lyrics", "category": "🎵 Unterhaltung", "topic": "Lyrics und Texte"},
        {"name": "radio-fuse", "category": "🎵 Unterhaltung", "topic": "FUSE Radio"},
        
        # Gaming
        {"name": "gaming", "category": "🎮 Gaming", "topic": "Gaming-Diskussionen und LFG"},
        {"name": "gaming-lfg", "category": "🎮 Gaming", "topic": "Looking for Group"},
        {"name": "gta-rp", "category": "🎮 Gaming", "topic": "GTA Roleplay"},
        {"name": "fortnite", "category": "🎮 Gaming", "topic": "Fortnite"},
        {"name": "cod", "category": "🎮 Gaming", "topic": "Call of Duty"},
        {"name": "apex", "category": "🎮 Gaming", "topic": "Apex Legends"},
        {"name": "minecraft", "category": "🎮 Gaming", "topic": "Minecraft"},
        {"name": "fifa", "category": "🎮 Gaming", "topic": "FIFA"},
        {"name": "valheim", "category": "🎮 Gaming", "topic": "Valheim"},
        {"name": "overwatch", "category": "🎮 Gaming", "topic": "Overwatch"},
        {"name": "valorant", "category": "🎮 Gaming", "topic": "Valorant"},
        
        # Entertainment
        {"name": "film-serien", "category": "🎬 Entertainment", "topic": "Filme und Serien besprechen"},
        {"name": "anime", "category": "🎬 Entertainment", "topic": "Anime Diskussionen"},
        {"name": "dokumentationen", "category": "🎬 Entertainment", "topic": "Dokumentationen"},
        {"name": "netflix", "category": "🎬 Entertainment", "topic": "Netflix Diskussionen"},
        
        # Tech
        {"name": "tech-talk", "category": "💻 Tech", "topic": "Technik-Diskussionen"},
        {"name": "handy-tipps", "category": "💻 Tech", "topic": "Handy Tipps"},
        {"name": "pc-building", "category": "💻 Tech", "topic": "PC Building"},
        {"name": "software", "category": "💻 Tech", "topic": "Software Diskussionen"},
        {"name": "coding", "category": "💻 Tech", "topic": "Programmierung"},
        {"name": "crypto", "category": "💻 Tech", "topic": "Krypto Talk"},
        
        # Marktplatz
        {"name": "marktplatz", "category": "🛒 Marktplatz", "topic": "Kaufen und Verkaufen"},
        {"name": "trading", "category": "🛒 Marktplatz", "topic": "Trading Bereich"},
        {"name": "biete", "category": "🛒 Marktplatz", "topic": "Biete Sachen an"},
        {"name": "suche", "category": "🛒 Marktplatz", "topic": "Suche Sachen"},
        
        # Ticket System
        {"name": "ticket-support", "category": "🎫 Tickets", "topic": "Erstelle ein Ticket für Support"},
        {"name": "ticket-bewerbung", "category": "🎫 Tickets", "topic": "Bewerbungs Tickets"},
        {"name": "ticket-beschwerde", "category": "🎫 Tickets", "topic": "Beschwerden"},
        
        # Finanzen & Wirtschaft
        {"name": "finanzen", "category": "💰 Finanzen", "topic": "Finanz Talk"},
        {"name": "investments", "category": "💰 Finanzen", "topic": "Investment Talk"},
        {"name": "business", "category": "💰 Finanzen", "topic": "Business Diskussionen"},
        {"name": "geld-was tun", "category": "💰 Finanzen", "topic": "Geld Tipps"},
        
        # Crew Bereiche
        {"name": "crew-chat", "category": "👥 Crew", "topic": "Crew intern"},
        {"name": "crew-events", "category": "👥 Crew", "topic": "Crew Events"},
        {"name": "crew-geheim", "category": "👥 Crew", "topic": "Geheime Crew Infos"},
        {"name": "crew-tipps", "category": "👥 Crew", "topic": "Tipps für die Crew"},
        {"name": "crew-kontakte", "category": "👥 Crew", "topic": "Wichtige Kontakte"},
        
        # Auto & Motorrad
        {"name": "auto-talk", "category": "🚗 Auto & Moto", "topic": "Auto Diskussionen"},
        {"name": "motorrad", "category": "🚗 Auto & Moto", "topic": "Motorrad Talk"},
        {"name": "tuning", "category": "🚗 Auto & Moto", "topic": "Tuning Tipps"},
        {"name": "car-showroom", "category": "🚗 Auto & Moto", "topic": "Car Showroom"},
        {"name": "ps-beats", "category": "🚗 Auto & Moto", "topic": "PS Beats"},
        
        # Real Life
        {"name": "reallife-tipps", "category": "🌍 Real Life", "topic": "Real Life Tipps"},
        {"name": "sports", "category": "🌍 Real Life", "topic": "Sport Talk"},
        {"name": "fitness", "category": "🌍 Real Life", "topic": "Fitness Talk"},
        {"name": "ernährung", "category": "🌍 Real Life", "topic": "Ernährung"},
        {"name": "hamburg-life", "category": "🌍 Real Life", "topic": "Leben in Hamburg"},
        
        # Politik & Welt
        {"name": "politik", "category": "🌐 Welt", "topic": "Politik Diskussion"},
        {"name": "welt-news", "category": "🌐 Welt", "topic": "Welt Nachrichten"},
        
        # Sonstiges
        {"name": "vorschläge", "category": "💡 Sonstiges", "topic": "Vorschläge für den Server"},
        {"name": "feedback", "category": "💡 Sonstiges", "topic": "Feedback geben"},
        {"name": "bug-report", "category": "💡 Sonstiges", "topic": "Fehler melden"},
        {"name": "off-topic", "category": "💡 Sonstiges", "topic": "Off-Topic Chat"},
    ],
    "voice_channels": [
        # Verify Warteraum
        {"name": "🔊 Warteraum", "category": "🔐 Verify"},
        
        # Allgemeine Voice Channels
        {"name": "🔊 Allgemein 1", "category": "💬 Voice"},
        {"name": "🔊 Allgemein 2", "category": "💬 Voice"},
        {"name": "🔊 Allgemein 3", "category": "💬 Voice"},
        {"name": "🔊 Allgemein 4", "category": "💬 Voice"},
        {"name": "🔊 Lounge", "category": "💬 Voice"},
        {"name": "🔊 Entspannung", "category": "💬 Voice"},
        {"name": "🔊 Chill Zone", "category": "💬 Voice"},
        
        # Musik Voice
        {"name": "🔊 Musikraum", "category": "🎵 Voice"},
        {"name": "🔊 Konzert Raum", "category": "🎵 Voice"},
        
        # Gaming Voice
        {"name": "🔊 Gaming 1", "category": "🎮 Voice"},
        {"name": "🔊 Gaming 2", "category": "🎮 Voice"},
        {"name": "🔊 Gaming 3", "category": "🎮 Voice"},
        {"name": "🔊 Gaming 4", "category": "🎮 Voice"},
        {"name": "🔊 Gaming 5", "category": "🎮 Voice"},
        {"name": "🔊 Turnier Raum", "category": "🎮 Voice"},
        
        # Geheime Räume
        {"name": "🔊 Geheimraum 1", "category": "🔒 Geheim"},
        {"name": "🔊 Geheimraum 2", "category": "🔒 Geheim"},
        {"name": "🔊 Tresor", "category": "🔒 Geheim"},
        
        # Büros für hohe Ränge
        {"name": "🔊 Besprechung", "category": "📋 Büros"},
        {"name": "🔊 Büro Owner", "category": "📋 Büros"},
        {"name": "🔊 Büro Co-Owner", "category": "📋 Büros"},
        {"name": "🔊 Büro General", "category": "📋 Büros"},
        {"name": "🔊 Büro Boss", "category": "📋 Büros"},
        {"name": "🔊 Büro Vize-Boss", "category": "📋 Büros"},
        {"name": "🔊 Büro Division General", "category": "📋 Büros"},
        {"name": "🔊 Konferenz Raum", "category": "📋 Büros"},
        {"name": "🔊 Kriegsrat", "category": "📋 Büros"},
        
        # Crew Voice
        {"name": "🔊 Crew Hangout", "category": "👥 Crew"},
        {"name": "🔊 Crew Meeting", "category": "👥 Crew"},
        {"name": "🔊 Crew Event", "category": "👥 Crew"},
        
        # Finanzen Voice
        {"name": "🔊 Finanzen Besprechung", "category": "💰 Finanzen"},
        
        # Radio Voice
        {"name": "🔊 FUSE Radio Live", "category": "🎵 Unterhaltung"},
        
        # AFK
        {"name": "🔊 AFK Room", "category": "💬 Voice"},
        {"name": "🔊 Wartesaal", "category": "💬 Voice"},
        
        # 18+ Bereiche
        {"name": "🔊 Private 1", "category": "🔞 Private"},
        {"name": "🔊 Private 2", "category": "🔞 Private"},
        {"name": "🔊 Club Hamburg", "category": "🔞 Private"},
    ]
}

# Log-Kanäle
LOG_CHANNELS = [
    {"name": "log-willkommen", "category": "📝 Logs", "topic": "Willkommen Log"},
    {"name": "log-verify", "category": "📝 Logs", "topic": "Verify Log"},
    {"name": "log-leave", "category": "📝 Logs", "topic": "Leave Log"},
    {"name": "log-message", "category": "📝 Logs", "topic": "Nachrichten Log"},
    {"name": "log-message-delete", "category": "📝 Logs", "topic": "Gelöschte Nachrichten Log"},
    {"name": "log-message-edit", "category": "📝 Logs", "topic": "Bearbeitete Nachrichten Log"},
    {"name": "log-channel", "category": "📝 Logs", "topic": "Kanal Log"},
    {"name": "log-role", "category": "📝 Logs", "topic": "Rollen Log"},
    {"name": "log-ticket", "category": "📝 Logs", "topic": "Ticket Log"},
    {"name": "log-ban", "category": "📝 Logs", "topic": "Ban Log"},
    {"name": "log-mute", "category": "📝 Logs", "topic": "Mute Log"},
    {"name": "log-warn", "category": "📝 Logs", "topic": "Warn Log"},
]

# Admin Kanäle
ADMIN_CHANNELS = [
    {"name": "admin-chat", "category": "🔒 Admin", "topic": "Admin Chat", "permission_view": ["Admin", "Owner", "Co-Owner", "General", "Boss"]},
    {"name": "admin-bewerbungen", "category": "🔒 Admin", "topic": "Admin Bewerbungen"},
    {"name": "admin-announcements", "category": "🔒 Admin", "topic": "Admin Ankündigungen"},
    {"name": "admin-logs", "category": "🔒 Admin", "topic": "Admin Logs"},
    {"name": "admin-team-chat", "category": "🔒 Admin", "topic": "Admin Team Chat"},
    {"name": "admin-warnungen", "category": "🔒 Admin", "topic": "Admin Verwarnungen"},
    {"name": "admin-bans", "category": "🔒 Admin", "topic": "Admin Bans und Kicks"},
    {"name": "admin-mutes", "category": "🔒 Admin", "topic": "Admin Mutes"},
    {"name": "admin-disciplinary", "category": "🔒 Admin", "topic": "Disziplinarische Maßnahmen"},
    {"name": "admin-meetings", "category": "🔒 Admin", "topic": "Admin Meetings"},
    {"name": "admin-reports", "category": "🔒 Admin", "topic": "Reports bearbeiten"},
    {"name": "admin-server-setup", "category": "🔒 Admin", "topic": "Server Setup und Änderungen"},
    {"name": "admin-changes", "category": "🔒 Admin", "topic": "Kanal/Rollen Änderungen"},
    {"name": "admin-verify-log", "category": "🔒 Admin", "topic": "Verify Log"},
    {"name": "admin-security", "category": "🔒 Admin", "topic": "Security und Safety"},
    {"name": "admin-internal", "category": "🔒 Admin", "topic": "Interne Kommunikation"},
    {"name": "admin-critiques", "category": "🔒 Admin", "topic": "Kritik und Verbesserungen"},
]

# Kategorien die erstellt werden sollen
CATEGORIES = [
    "🏠 Willkommen",
    "🔐 Verify",
    "💬 Chat",
    "💬 Voice",
    "🎵 Voice",
    "🎵 Unterhaltung",
    "🎮 Gaming",
    "🎮 Voice",
    "🎬 Entertainment",
    "💻 Tech",
    "🛒 Marktplatz",
    "🎫 Tickets",
    "📝 Logs",
    "🔒 Geheim",
    "📋 Büros",
    "🔒 Admin",
    "📋 Admin",
    "💰 Finanzen",
    "👥 Crew",
    "🚗 Auto & Moto",
    "🌍 Real Life",
    "🌐 Welt",
    "💡 Sonstiges",
    "🔞 Private",
]

# ============================================================
# UTILITY FUNKTIONEN
# ============================================================

def load_data():
    """Lädt gespeicherte Daten"""
    if os.path.exists('server_data.json'):
        with open('server_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    """Speichert Daten"""
    with open('server_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

async def create_category(guild, name):
    """Erstellt eine Kategorie oder gibt sie zurück falls sie existiert"""
    existing = discord.utils.get(guild.categories, name=name)
    if existing:
        return existing
    return await guild.create_category(name)

async def create_channel(guild, name, category, topic=None, overwrites=None):
    """Erstellt einen Textkanal"""
    cat = await create_category(guild, category)
    existing = discord.utils.get(guild.text_channels, name=name)
    if existing:
        return existing
    return await cat.create_text_channel(name, topic=topic, overwrites=overwrites)

async def create_voice_channel(guild, name, category):
    """Erstellt einen Sprachkanal"""
    cat = await create_category(guild, category)
    existing = discord.utils.get(guild.voice_channels, name=name)
    if existing:
        return existing
    return await cat.create_voice_channel(name)

async def create_role(guild, role_data):
    """Erstellt eine Rolle"""
    existing = discord.utils.get(guild.roles, name=role_data["name"])
    if existing:
        return existing
    permissions = discord.Permissions(role_data.get("permissions", 104320))
    return await guild.create_role(
        name=role_data["name"],
        color=discord.Color(role_data["color"]),
        permissions=permissions,
        hoist=True
    )

async def log_action(guild, log_type, message):
    """Loggt eine Aktion in den entsprechenden Log-Kanal"""
    data = load_data()
    log_channel_name = f"log-{log_type}"
    
    for channel in guild.text_channels:
        if channel.name == log_channel_name:
            embed = discord.Embed(
                description=message,
                color=0xFF0000,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"FUSE | Crime Hamburg - {log_type.upper()} Log")
            await channel.send(embed=embed)
            return

# ============================================================
# BOT EVENT HANDLER
# ============================================================

@bot.event
async def on_ready():
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║  FUSE | Crime Hamburg Bot ist online!                    ║
    ║  Bot: {bot.user.name}#{bot.user.discriminator}
    ║  ID: {bot.user.id}
    ╚══════════════════════════════════════════════════════════╝
    """)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="FUSE | Crime Hamburg"))
    
    # Überprüfe ob Server-Daten existieren
    data = load_data()
    if not data.get('initialized'):
        print("⚠️  Server noch nicht initialisiert. Nutze !start um zu beginnen.")

@bot.event
async def on_member_join(member):
    """Wird ausgeführt wenn ein Member dem Server beitritt"""
    data = load_data()
    guild = member.guild
    
    # Finde den Willkommen-Channel
    welcome_channel = discord.utils.get(guild.text_channels, name="willkommen")
    if not welcome_channel:
        return
    
    # Hole die Member-Anzahl
    member_count = len([m for m in guild.members if not m.bot])
    
    # Erstelle Willkommen-Embed
    embed = discord.Embed(
        title="🎉 WILLKOMMEN IN FUSE | FS!",
        description=f"Hey **{member.mention}**! Willkommen bei **FUSE**!\n\nDu bist unser **{member_count}** Member! 🎊\n\nBitte halte dich an die Regeln und geh freundlich mit allen Mitgliedern um.",
        color=0xFF0000
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="📋 Was du tun musst:", value="Verifiziere dich um Zugang zu allen Kanälen zu erhalten!", inline=False)
    embed.set_footer(text="FUSE | Crime Hamburg - Nicht verifizierte Nutzer haben eingeschränkten Zugang")
    
    await welcome_channel.send(embed=embed)
    await log_action(guild, "willkommen", f"**{member.name}** ist dem Server beigetreten! Member #{member_count}")
    
    # Setze Unverified Rolle falls vorhanden
    unverified_role = discord.utils.get(guild.roles, name="Unverified")
    if unverified_role:
        await member.add_roles(unverified_role)

@bot.event
async def on_member_remove(member):
    """Wird ausgeführt wenn ein Member den Server verlässt"""
    guild = member.guild
    await log_action(guild, "leave", f"**{member.name}** hat den Server verlassen 😢")
    
    # Versuche einen Leave-Channel zu finden
    leave_embed = discord.Embed(
        title="👋 Member Verlassen",
        description=f"**{member.name}** hat uns verlassen...",
        color=0xFF6600,
        timestamp=datetime.now()
    )
    
    for channel in guild.text_channels:
        if channel.name == "log-leave":
            await channel.send(embed=leave_embed)
            break

@bot.event
async def on_message(message):
    """Behandelt eingehende Nachrichten"""
    if message.author.bot:
        return
    
    # Verify System
    if message.channel.name == "verify":
        if message.content.lower() == "!verify":
            guild = message.guild
            
            # Finde/Unverified Rolle entfernen
            unverified_role = discord.utils.get(guild.roles, name="Unverified")
            member_role = discord.utils.get(guild.roles, name="Member")
            
            if unverified_role in message.author.roles:
                await message.author.remove_roles(unverified_role)
            if member_role:
                await message.author.add_roles(member_role)
            
            # Bestätigungsnachricht
            embed = discord.Embed(
                title="✅ Verifizierung erfolgreich!",
                description=f"**{message.author.name}** wurde erfolgreich verifiziert!\n\nDu hast jetzt Zugang zu allen allgemeinen Kanälen.\n\n📝 **Nächster Schritt:** Bewirb dich für eine Rolle in <#bewerbung>",
                color=0x00FF00
            )
            await message.channel.send(embed=embed, delete_after=10)
            
            await log_action(guild, "verify", f"**{message.author.name}** hat sich verifiziert!")
            
            # Lösche die Verify-Nachricht
            await message.delete(delay=2)
            
            # Setze View Permissions für nicht verifizierte User
            for channel in guild.text_channels:
                if channel.name not in ["willkommen", "verify", "regeln", "ankündigungen"]:
                    await channel.set_permissions(message.author, read_messages=True, send_messages=True)
    
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    """Wird ausgeführt wenn eine Nachricht gelöscht wird"""
    if message.author.bot:
        return
    
    guild = message.guild
    embed = discord.Embed(
        title="🗑️ Nachricht gelöscht",
        description=f"**{message.author.name}** hat eine Nachricht in {message.channel.mention} gelöscht.\n\n**Inhalt:** {message.content[:1024]}",
        color=0xFF0000,
        timestamp=datetime.now()
    )
    
    for channel in guild.text_channels:
        if channel.name == "log-message-delete":
            await channel.send(embed=embed)
            break

@bot.event
async def on_message_edit(before, after):
    """Wird ausgeführt wenn eine Nachricht bearbeitet wird"""
    if before.author.bot or before.content == after.content:
        return
    
    guild = before.guild
    embed = discord.Embed(
        title="✏️ Nachricht bearbeitet",
        description=f"**{before.author.name}** hat eine Nachricht in {before.channel.mention} bearbeitet.\n\n**Vorher:** {before.content[:1024]}\n\n**Nachher:** {after.content[:1024]}",
        color=0xFFA500,
        timestamp=datetime.now()
    )
    
    for channel in guild.text_channels:
        if channel.name == "log-message-edit":
            await channel.send(embed=embed)
            break

# ============================================================
# COMMANDS
# ============================================================

@bot.command(name="start")
async def start_command(ctx):
    """Startet das Server-Setup mit Optionen"""
    # Überprüfe ob der User Admin/Owner ist
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ["Admin", "Owner", "Co-Owner"]):
        embed = discord.Embed(
            title="⛔ Keine Berechtigung",
            description="Du musst Admin oder Owner sein um diesen Befehl zu nutzen.",
            color=0xFF0000
        )
        await ctx.send(embed=embed)
        return
    
    # Erstelle das Auswahl-Embed
    embed = discord.Embed(
        title="🚀 FUSE | Server Setup",
        description="**Wähle eine Option:**\n\n"
                    "🇦 **Abbruch** - Nichts tun\n"
                    "🇧 **Nur Hinzufügen** - Nur fehlende Kanäle/Rollen hinzufügen\n"
                    "🇨 **Komplett neu aufsetzen** - Alles neu erstellen (Löscht nichts!)",
        color=0xFF0000
    )
    embed.set_footer(text="FUSE | Crime Hamburg - Server Setup")
    
    message = await ctx.send(embed=embed)
    
    # Füge Reactions hinzu
    await message.add_reaction("🇦")
    await message.add_reaction("🇧")
    await message.add_reaction("🇨")
    
    # Warte auf Reaction
    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["🇦", "🇧", "🇨"] and reaction.message.id == message.id
    
    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        emoji = str(reaction.emoji)
        
        if emoji == "🇦":
            # Abbruch
            embed = discord.Embed(
                title="❌ Abbruch",
                description="Setup wurde abgebrochen.",
                color=0x808080
            )
            await message.edit(embed=embed)
            await message.clear_reactions()
            return
        
        elif emoji == "🇧":
            # Nur Hinzufügen
            await ctx.send("⏳ **Nur Hinzufügen** Modus gestartet...")
            await setup_server(ctx.guild, mode="add")
        
        elif emoji == "🇨":
            # Komplett neu
            await ctx.send("⏳ **Komplett neu** Modus gestartet...")
            await setup_server(ctx.guild, mode="new")
            
    except asyncio.TimeoutError:
        await ctx.send("⏰ Zeit abgelaufen. Bitte versuche es erneut.")
        await message.clear_reactions()

@bot.command(name="setup")
async def setup_command(ctx):
    """Manuelles Setup ohne interaktive Auswahl"""
    await ctx.send("🔧 Starte manuelles Setup...")
    await setup_server(ctx.guild, mode="new")

@bot.command(name="help")
async def help_command(ctx):
    """Zeigt die Hilfe an"""
    embed = discord.Embed(
        title="📚 FUSE Bot - Hilfe",
        description="**Verfügbare Commands:**\n\n"
                    "🇱 **!start** - Startet das interaktive Server-Setup\n"
                    "🇸 **!setup** - Manuelles Setup (sofort)\n"
                    "🇭 **!help** - Zeigt diese Hilfe\n"
                    "🇹 **!ticket** - Erstellt ein Ticket\n"
                    "🇷 **!roles** - Zeigt alle verfügbaren Rollen\n"
                    "🇲 **!membercount** - Zeigt die Member-Anzahl\n"
                    "🇧 **!broadcast** <nachricht> - Sendet eine Ankündigung (Admin only)\n"
                    "🇰 **!kick** <user> - Kickt einen User (Admin only)\n"
                    "🇧 **!ban** <user> - Bannt einen User (Admin only)\n"
                    "🇲 **!mute** <user> - Muted einen User (Admin only)",
        color=0xFF0000
    )
    embed.set_footer(text="FUSE | Crime Hamburg")
    await ctx.send(embed=embed)

@bot.command(name="ticket")
async def ticket_command(ctx, *, reason="Allgemeine Anfrage"):
    """Erstellt ein Ticket"""
    guild = ctx.guild
    category = discord.utils.get(guild.categories, name="🎫 Tickets")
    
    if not category:
        await ctx.send("❌ Ticket-Kategorie existiert nicht. Nutze !start um den Server einzurichten.")
        return
    
    # Erstelle einen eindeutigen Kanalnamen
    ticket_number = len([c for c in guild.text_channels if c.name.startswith("ticket-")]) + 1
    channel_name = f"ticket-{ctx.author.name.lower().replace(' ', '-')}-{ticket_number}"
    
    # Setze Permissions
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    
    # Füge Admin-Rollen hinzu
    admin_roles = ["Admin", "Owner", "Co-Owner", "Moderator", "Supporter"]
    for role_name in admin_roles:
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    ticket_channel = await category.create_text_channel(
        channel_name,
        topic=f"Ticket von {ctx.author.name} - {reason}"
    )
    
    embed = discord.Embed(
        title="🎫 Ticket erstellt",
        description=f"**{ctx.author.mention}** hat ein Ticket erstellt!\n\n**Grund:** {reason}\n\nEin Admin wird sich bald melden.",
        color=0xFF0000
    )
    await ticket_channel.send(embed=embed)
    await ctx.send(f"✅ Ticket erstellt: {ticket_channel.mention}")
    
    # Log das Ticket
    await log_action(guild, "ticket", f"**{ctx.author.name}** hat ein Ticket erstellt: {reason}")

@bot.command(name="roles")
async def roles_command(ctx):
    """Zeigt alle verfügbaren Rollen"""
    embed = discord.Embed(
        title="📋 Verfügbare Rollen",
        description="Bewirb dich für eine Rolle im <#bewerbung> Kanal!",
        color=0xFF0000
    )
    
    guild_roles = sorted(ctx.guild.roles, key=lambda x: x.position, reverse=True)
    
    for role in guild_roles:
        if role.name not in ["everyone", "FUSE Bot"]:
            embed.add_field(name=f"{role.name}", value=f"Farbe: {role.color}", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name="membercount")
async def membercount_command(ctx):
    """Zeigt die Member-Anzahl"""
    total_members = len([m for m in ctx.guild.members if not m.bot])
    bots = len([m for m in ctx.guild.members if m.bot])
    
    embed = discord.Embed(
        title="👥 Member Count",
        description=f"**Menschen:** {total_members}\n**Bots:** {bots}\n**Gesamt:** {ctx.guild.member_count}",
        color=0x00FF00
    )
    await ctx.send(embed=embed)

@bot.command(name="broadcast")
async def broadcast_command(ctx, *, message):
    """Sendet eine Ankündigung"""
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ["Admin", "Owner", "Co-Owner"]):
        await ctx.send("⛔ Keine Berechtigung!")
        return
    
    embed = discord.Embed(
        title="📢 Ankündigung",
        description=message,
        color=0xFF0000,
        timestamp=datetime.now()
    )
    embed.set_footer(text=f"Angekündigt von {ctx.author.name}")
    
    announcement_channel = discord.utils.get(ctx.guild.text_channels, name="ankündigungen")
    if announcement_channel:
        await announcement_channel.send(embed=embed)
        await ctx.send("✅ Ankündigung gesendet!")
    else:
        await ctx.send("❌ Ankündigungs-Kanal nicht gefunden!")

@bot.command(name="kick")
async def kick_command(ctx, member: discord.Member, *, reason="Kein Grund angegeben"):
    """Kickt einen User"""
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ["Admin", "Owner", "Co-Owner"]):
        await ctx.send("⛔ Keine Berechtigung!")
        return
    
    await member.kick(reason=reason)
    
    embed = discord.Embed(
        title="👢 User gekickt",
        description=f"**{member.name}** wurde gekickt!\n\n**Grund:** {reason}\n**Admin:** {ctx.author.name}",
        color=0xFF6600
    )
    await ctx.send(embed=embed)
    
    await log_action(ctx.guild, "kick", f"**{member.name}** wurde von **{ctx.author.name}** gekickt. Grund: {reason}")

@bot.command(name="ban")
async def ban_command(ctx, member: discord.Member, *, reason="Kein Grund angegeben"):
    """Bannt einen User"""
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ["Admin", "Owner", "Co-Owner"]):
        await ctx.send("⛔ Keine Berechtigung!")
        return
    
    await member.ban(reason=reason, delete_message_days=7)
    
    embed = discord.Embed(
        title="🔨 User gebannt",
        description=f"**{member.name}** wurde gebannt!\n\n**Grund:** {reason}\n**Admin:** {ctx.author.name}",
        color=0xFF0000
    )
    await ctx.send(embed=embed)
    
    await log_action(ctx.guild, "ban", f"**{member.name}** wurde von **{ctx.author.name}** gebannt. Grund: {reason}")

@bot.command(name="mute")
async def mute_command(ctx, member: discord.Member, *, reason="Kein Grund angegeben"):
    """Muted einen User"""
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ["Admin", "Owner", "Co-Owner", "Moderator"]):
        await ctx.send("⛔ Keine Berechtigung!")
        return
    
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    
    if not muted_role:
        # Erstelle Muted Rolle
        muted_role = await ctx.guild.create_role(
            name="Muted",
            color=0x808080,
            permissions=discord.Permissions(1024)
        )
        
        # Setze Muted Permission für alle Kanäle
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)
    
    await member.add_roles(muted_role)
    
    embed = discord.Embed(
        title="🔇 User gemuted",
        description=f"**{member.name}** wurde gemuted!\n\n**Grund:** {reason}\n**Admin:** {ctx.author.name}",
        color=0x808080
    )
    await ctx.send(embed=embed)
    
    await log_action(ctx.guild, "mute", f"**{member.name}** wurde von **{ctx.author.name}** gemuted. Grund: {reason}")

@bot.command(name="warn")
async def warn_command(ctx, member: discord.Member, *, reason="Kein Grund angegeben"):
    """Verwarnt einen User"""
    user_roles = [role.name for role in ctx.author.roles]
    if not any(role in user_roles for role in ["Admin", "Owner", "Co-Owner", "Moderator"]):
        await ctx.send("⛔ Keine Berechtigung!")
        return
    
    embed = discord.Embed(
        title="⚠️ Verwarnung",
        description=f"**{member.mention}** wurde verwarnt!\n\n**Grund:** {reason}\n**Admin:** {ctx.author.name}",
        color=0xFFFF00
    )
    await ctx.send(embed=embed)
    
    await log_action(ctx.guild, "warn", f"**{member.name}** wurde von **{ctx.author.name}** verwarnt. Grund: {reason}")

# ============================================================
# SETUP FUNKTION
# ============================================================

async def setup_server(guild, mode="new"):
    """Richtet den kompletten Server ein"""
    status_msg = await guild.text_channels[0].send("⏳ Setup wird gestartet...") if guild.text_channels else None
    
    try:
        # ---- ROLLEN ERSTELLEN ----
        await (status_msg or guild.system_channel).edit(content="📋 Erstelle Rollen...")
        
        created_roles = []
        for i, role_data in enumerate(ROLES_DATA):
            try:
                role = await create_role(guild, role_data)
                created_roles.append(role)
                await asyncio.sleep(0.5)  # Rate limiting vermeiden
            except Exception as e:
                print(f"Fehler beim Erstellen der Rolle {role_data['name']}: {e}")
        
        # Setze Rollen-Positionen (von unten nach oben)
        # Die letzte Rolle in der Liste sollte ganz oben sein
        for i, role in enumerate(created_roles):
            try:
                await role.edit(position=i)
            except:
                pass
        
        # ---- CATEGORIES ERSTELLEN ----
        await (status_msg or guild.system_channel).edit(content="📁 Erstelle Kategorien...")
        
        for cat_name in CATEGORIES:
            await create_category(guild, cat_name)
            await asyncio.sleep(0.3)
        
        # ---- TEXT CHANNELS ERSTELLEN ----
        await (status_msg or guild.system_channel).edit(content="💬 Erstelle Textkanäle...")
        
        for channel_data in CHANNELS_DATA["text_channels"]:
            # Standard overwrites - Unverified kann nur bestimmtes sehen
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
            }
            
            # Füge Verify-Kanal und Willkommen-Kanal für alle lesbar hinzu
            if channel_data["name"] in ["willkommen", "regeln", "ankündigungen"]:
                overwrites[guild.default_role] = discord.PermissionOverwrite(
                    read_messages=True, 
                    send_messages=False
                )
            
            # Verify-Kanal für Unverified und Member
            if channel_data["name"] == "verify":
                unverified_role = discord.utils.get(guild.roles, name="Unverified")
                if unverified_role:
                    overwrites[unverified_role] = discord.PermissionOverwrite(
                        read_messages=True, 
                        send_messages=True
                    )
            
            await create_channel(
                guild, 
                channel_data["name"], 
                channel_data["category"], 
                topic=channel_data.get("topic"),
                overwrites=overwrites
            )
            await asyncio.sleep(0.3)
        
        # ---- VOICE CHANNELS ERSTELLEN ----
        await (status_msg or guild.system_channel).edit(content="🔊 Erstelle Sprachkanäle...")
        
        for channel_data in CHANNELS_DATA["voice_channels"]:
            await create_voice_channel(guild, channel_data["name"], channel_data["category"])
            await asyncio.sleep(0.3)
        
        # ---- LOG CHANNELS ERSTELLEN ----
        await (status_msg or guild.system_channel).edit(content="📝 Erstelle Log-Kanäle...")
        
        for log_data in LOG_CHANNELS:
            await create_channel(
                guild, 
                log_data["name"], 
                log_data["category"], 
                topic=log_data.get("topic")
            )
            await asyncio.sleep(0.3)
        
        # ---- ADMIN CHANNELS ERSTELLEN ----
        await (status_msg or guild.system_channel).edit(content="🔒 Erstelle Admin-Kanäle...")
        
        for admin_data in ADMIN_CHANNELS:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            }
            
            # Füge Admin-Rollen hinzu
            admin_role_names = admin_data.get("permission_view", ["Admin", "Owner", "Co-Owner"])
            for role_name in admin_role_names:
                role = discord.utils.get(guild.roles, name=role_name)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(
                        read_messages=True, 
                        send_messages=True
                    )
            
            await create_channel(
                guild,
                admin_data["name"],
                admin_data["category"],
                topic=admin_data.get("topic"),
                overwrites=overwrites
            )
            await asyncio.sleep(0.3)
        
        # ---- BÜROS FÜR HÖHERE RANGEN ----
        await (status_msg or guild.system_channel).edit(content="🏢 Erstelle Büros...")
        
        office_roles = ["Owner", "Co-Owner", "Boss", "General", "Vize Boss"]
        for role_name in office_roles:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                # Erstelle privaten Sprachkanal
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    role: discord.PermissionOverwrite(read_messages=True, connect=True, speak=True),
                }
                
                cat = await create_category(guild, f"🏢 Büro {role_name}")
                await cat.create_voice_channel(
                    f"🔒 Büro {role_name}",
                    overwrites=overwrites
                )
        
        # ---- SETUP ABSCHLIESSEN ----
        # Speichere Server-Daten
        data = {
            "initialized": True,
            "guild_id": guild.id,
            "roles_created": len(created_roles),
            "setup_date": datetime.now().isoformat()
        }
        save_data(data)
        
        # Finale Nachricht
        success_embed = discord.Embed(
            title="✅ Setup abgeschlossen!",
            description=f"**FUSE | Crime Hamburg** Server wurde erfolgreich eingerichtet!\n\n"
                        f"📋 **Erstellt:**\n"
                        f"• {len(created_roles)} Rollen\n"
                        f"• {len(CHANNELS_DATA['text_channels'])} Textkanäle\n"
                        f"• {len(CHANNELS_DATA['voice_channels'])} Sprachkanäle\n"
                        f"• {len(LOG_CHANNELS)} Log-Kanäle\n"
                        f"• {len(ADMIN_CHANNELS)} Admin-Kanäle\n"
                        f"• {len(CATEGORIES)} Kategorien\n\n"
                        f"🎉 **Willkommen bei FUSE!**",
            color=0x00FF00
        )
        success_embed.set_footer(text="FUSE | Crime Hamburg - Setup Complete")
        
        if status_msg:
            await status_msg.edit(content="", embed=success_embed)
        else:
            channel = discord.utils.get(guild.text_channels, name="willkommen")
            if channel:
                await channel.send(embed=success_embed)
        
        print(f"✅ Setup abgeschlossen! {len(created_roles)} Rollen erstellt.")
        
    except Exception as e:
        error_embed = discord.Embed(
            title="❌ Setup fehlgeschlagen",
            description=f"Ein Fehler ist aufgetreten: {str(e)}",
            color=0xFF0000
        )
        if status_msg:
            await status_msg.edit(content="", embed=error_embed)
        print(f"❌ Setup Fehler: {e}")

# ============================================================
# BOT STARTEN
# ============================================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║  FUSE | Crime Hamburg - Discord Bot                      ║
    ║  Starte Bot...                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Lade Token aus Umgebungsvariable oder config
    token = os.environ.get('DISCORD_BOT_TOKEN') or CONFIG.get('token')
    
    if token == "DEIN_BOT_TOKEN_HIER":
        print("⚠️  Bitte trage deinen Bot Token in config.json ein!")
        print("    oder setze die Umgebungsvariable DISCORD_BOT_TOKEN")
    else:
        bot.run(token)