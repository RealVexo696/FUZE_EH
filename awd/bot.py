"""
FUSE | FS - Discord Setup & Management Bot
==========================================
Erstellt einen kompletten Roblox-RP / "Notruf Hamburg Crime Gang"-Discord:
- ~52 Rollen (Unverified -> Owner) in korrekter Hierarchie
- Alle Kategorien & Kanäle aus den Vorlagen-Screenshots
- Admin-Bereich + komplette Log-Kanäle
- Welcome-System mit Member-Counter
- Verify-System per Button (Unverified -> Verified -> Member sichtbar)
- Setup-Wizard via !start mit 3 Buttons (Abbruch / Nur Hinzufügen / Neu aufsetzen)
- Befüllt wichtige Kanäle mit Embeds (Regeln, Verify-Button, Info etc.)

Hosting:  Railway  |  Repository: GitHub
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# --------------------------------------------------------------------------- #
# ENV & LOGGING
# --------------------------------------------------------------------------- #
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")
SERVER_NAME = os.getenv("SERVER_NAME", "FUSE | FS")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fuse")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# --------------------------------------------------------------------------- #
# BRANDING / FARBEN
# --------------------------------------------------------------------------- #
BRAND_COLOR   = 0xE91E63   # FUSE Pink
SUCCESS_COLOR = 0x2ECC71
ERROR_COLOR   = 0xE74C3C
INFO_COLOR    = 0x3498DB
GOLD          = 0xF1C40F

# --------------------------------------------------------------------------- #
# ROLLEN  (Index 0 = ganz oben in der Hierarchie)
# Owner bekommt Administrator. Staff hat Mod-Rechte. Member nur Basic.
# --------------------------------------------------------------------------- #
ADMIN_PERMS = discord.Permissions(administrator=True)
MOD_PERMS = discord.Permissions(
    kick_members=True, ban_members=True, manage_messages=True,
    manage_channels=True, manage_nicknames=True, mute_members=True,
    deafen_members=True, move_members=True, view_audit_log=True,
    manage_threads=True, moderate_members=True, read_message_history=True,
    send_messages=True, embed_links=True, attach_files=True,
)
TRIAL_MOD_PERMS = discord.Permissions(
    manage_messages=True, manage_nicknames=True, mute_members=True,
    move_members=True, view_audit_log=True, moderate_members=True,
    read_message_history=True, send_messages=True, embed_links=True,
    attach_files=True,
)
MEMBER_PERMS = discord.Permissions(
    read_message_history=True, send_messages=True, embed_links=True,
    attach_files=True, add_reactions=True, use_external_emojis=True,
    connect=True, speak=True, stream=True, use_voice_activation=True,
    change_nickname=True,
)
BASIC_PERMS = discord.Permissions(read_message_history=True, send_messages=True, connect=True, speak=True)

# Hierarchie von oben (Owner) nach unten (Unverified)
ROLES: list[dict] = [
    # Leitung
    {"name": "👑 Owner",            "color": 0xFF0000, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "👑 Co-Owner",         "color": 0xFF1A1A, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "🛡️ Server-Manager",   "color": 0xFF4500, "hoist": True, "perms": ADMIN_PERMS},
    # Admin Team
    {"name": "⚡ Head-Admin",        "color": 0xFF6600, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "⚡ Admin",             "color": 0xFF8000, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "⚡ Vize-Admin",        "color": 0xFF9933, "hoist": True, "perms": MOD_PERMS},
    # Mod Team
    {"name": "🔨 Head-Moderator",   "color": 0xFFAA00, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Senior-Moderator", "color": 0xFFC04D, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Moderator",        "color": 0xFFD580, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Trial-Moderator",  "color": 0xFFE0B3, "hoist": True, "perms": TRIAL_MOD_PERMS},
    # Support
    {"name": "🎧 Support-Lead",     "color": 0x00CED1, "hoist": True, "perms": TRIAL_MOD_PERMS},
    {"name": "🎧 Supporter",        "color": 0x40E0D0, "hoist": True, "perms": TRIAL_MOD_PERMS},
    {"name": "🎧 Trial-Supporter",  "color": 0x7FFFD4, "hoist": True, "perms": MEMBER_PERMS},
    # Spezial-Team
    {"name": "💻 Developer",        "color": 0x9B59B6, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "🤖 Bot-Manager",      "color": 0x8E44AD, "hoist": True, "perms": MOD_PERMS},
    {"name": "🎨 Designer",         "color": 0xE67E22, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎉 Event-Manager",    "color": 0xD35400, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "📝 Recruiter",        "color": 0x16A085, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🤝 Partner-Manager",  "color": 0x1ABC9C, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "📱 SocialMedia-Team", "color": 0xE91E63, "hoist": True, "perms": MEMBER_PERMS},
    # Gang / Roblox-Crew (Notruf HH Style)
    {"name": "💎 Boss",             "color": 0x800080, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Underboss",        "color": 0x8B008B, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Consigliere",      "color": 0x9932CC, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Capo",             "color": 0xA020F0, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Soldato",          "color": 0xBA55D3, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🔫 Hitman",           "color": 0x4B0082, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🔫 Enforcer",         "color": 0x483D8B, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💊 Dealer",           "color": 0x2F4F4F, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🚚 Smuggler",         "color": 0x556B2F, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🏎️ Driver",           "color": 0x6B8E23, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🔧 Mechanic",         "color": 0x808000, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🛡️ Bodyguard",        "color": 0x708090, "hoist": True, "perms": MEMBER_PERMS},
    # Member Stufen
    {"name": "🏆 Veteran",          "color": 0xFFD700, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "⭐ Elite",             "color": 0xFFC125, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💠 Member+",          "color": 0x00BFFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💠 Member",           "color": 0x1E90FF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🧪 Trial-Member",     "color": 0x87CEEB, "hoist": True, "perms": MEMBER_PERMS},
    # Creator / Specials
    {"name": "🎬 YouTuber",         "color": 0xFF0000, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎮 Twitch-Streamer",  "color": 0x6441A5, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎵 TikToker",         "color": 0x000000, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🖌️ Content-Creator",  "color": 0xC71585, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "✅ Verified",         "color": 0x57F287, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🤝 Bros",             "color": 0xFF69B4, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "💕 Friend",           "color": 0xFFB6C1, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🎶 DJ",               "color": 0x1DB954, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🎂 Geburtstagskind",  "color": 0xFF69B4, "hoist": False, "perms": MEMBER_PERMS},
    # Boosts
    {"name": "💖 Boost-King",       "color": 0xF47FFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💖 Booster",          "color": 0xF47FFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Nitro",            "color": 0xB9BBBE, "hoist": False, "perms": MEMBER_PERMS},
    # Sonder / Strafrollen
    {"name": "📝 Bewerber",         "color": 0x95A5A6, "hoist": True, "perms": BASIC_PERMS},
    {"name": "👋 Gast",             "color": 0xBDC3C7, "hoist": False, "perms": BASIC_PERMS},
    {"name": "😴 AFK",              "color": 0x4F545C, "hoist": False, "perms": BASIC_PERMS},
    {"name": "🔇 Muted",            "color": 0x36393F, "hoist": False, "perms": discord.Permissions.none()},
    {"name": "⚠️ Verwarnt",         "color": 0xE74C3C, "hoist": False, "perms": BASIC_PERMS},
    {"name": "❌ Unverified",       "color": 0x99AAB5, "hoist": False, "perms": discord.Permissions.none()},
]

# Schlüsselrollen für Permissions
KEY_ROLES = {
    "owner":      "👑 Owner",
    "admin":      "⚡ Admin",
    "mod":        "🔨 Moderator",
    "support":    "🎧 Supporter",
    "member":     "💠 Member",
    "verified":   "✅ Verified",
    "bewerber":   "📝 Bewerber",
    "muted":      "🔇 Muted",
    "unverified": "❌ Unverified",
}

# --------------------------------------------------------------------------- #
# KATEGORIEN & KANÄLE  (an Screenshots angelehnt)
# type: "text" | "voice" | "stage" | "forum"
# locked: True -> nur Staff/höhere Rollen
# --------------------------------------------------------------------------- #
STRUCTURE: list[dict] = [
    {
        "category": "📩 ✘ WILLKOMMEN",
        "visible_to": ["unverified", "verified", "member"],
        "channels": [
            {"name": "👋・willkommen",   "type": "text"},
            {"name": "📜・regelwerk",    "type": "text"},
            {"name": "✅・verify",       "type": "text"},
            {"name": "👋・tschüss",      "type": "text"},
        ],
    },
    {
        "category": "🌐 ✘ BEWERBUNG",
        "visible_to": ["verified", "member"],
        "channels": [
            {"name": "🎫・ticket",        "type": "text"},
            {"name": "👾・bewerbungschat","type": "text"},
            {"name": "📋・formular",      "type": "text"},
            {"name": "🎙️・warteraum",     "type": "voice"},
            {"name": "🚪・Einreise¹",     "type": "voice", "locked": True},
            {"name": "🚪・Einreise²",     "type": "voice", "locked": True},
        ],
    },
    {
        "category": "🎀 ✘ INFOS",
        "visible_to": ["member"],
        "channels": [
            {"name": "✅・activity-check","type": "text"},
            {"name": "🔔・ankündigung",   "type": "text"},
            {"name": "🎬・meeting-clips", "type": "text"},
            {"name": "🚀・boosts",        "type": "text"},
            {"name": "😂・hall-of-shame", "type": "text"},
            {"name": "🎥・free-tt-vid",   "type": "text"},
        ],
    },
    {
        "category": "💬 ✘ COMMUNITY",
        "visible_to": ["member"],
        "channels": [
            {"name": "💬・chat",          "type": "text"},
            {"name": "🎨・media",         "type": "text"},
            {"name": "🤣・memes",         "type": "text"},
            {"name": "🎮・gaming",        "type": "text"},
            {"name": "🤖・bot-commands",  "type": "text"},
            {"name": "💡・vorschläge",    "type": "text"},
        ],
    },
    {
        "category": "📱 ✘ SOCIALMEDIA",
        "visible_to": ["member"],
        "channels": [
            {"name": "💖・cani",          "type": "text"},
            {"name": "📱・socialmedia",   "type": "text"},
            {"name": "📸・instagram",     "type": "text"},
            {"name": "🎵・tiktok",        "type": "text"},
            {"name": "🎬・youtube",       "type": "text"},
        ],
    },
    {
        "category": "📞 ✘ TALKS",
        "visible_to": ["member"],
        "channels": [
            {"name": "🎤・Stage",         "type": "stage"},
            {"name": "🌐・FFA-VoiceChat", "type": "voice"},
            {"name": "🎮・Gaming-1",      "type": "voice"},
            {"name": "🎮・Gaming-2",      "type": "voice"},
            {"name": "🎵・Musik",         "type": "voice"},
            {"name": "😴・AFK",           "type": "voice"},
        ],
    },
    {
        "category": "🧱 ✘ BROS MERCH",
        "visible_to": ["member"],
        "channels": [
            {"name": "🦺・weste",         "type": "text"},
            {"name": "📿・armband",       "type": "text"},
            {"name": "👕・merch",         "type": "text"},
            {"name": "👕・trikot",        "type": "text"},
            {"name": "👕・polo",          "type": "text"},
        ],
    },
    {
        "category": "📓 ✘ GANG INFOS",
        "visible_to": ["member"],
        "channels": [
            {"name": "💗・farbe",            "type": "text"},
            {"name": "🎨・rollensystem",     "type": "text"},
            {"name": "🎮・roblox-gruppe",    "type": "text"},
            {"name": "🏠・anwesen",          "type": "text"},
            {"name": "🛡️・partnerschaft",    "type": "text"},
        ],
    },
    {
        "category": "🔒 LOUNGES",
        "visible_to": ["member"],
        "channels": [
            {"name": "🎀・LOUNGE-400-RBX",   "type": "voice", "locked": True},
            {"name": "♟️・Nils-Luke",         "type": "voice", "locked": True},
            {"name": "💎・M-J-S-F",           "type": "voice", "locked": True},
            {"name": "💬・lounge-chat",       "type": "text",  "locked": True},
            {"name": "🍺・Bier-Keller",       "type": "voice", "locked": True},
        ],
    },
    {
        "category": "🏢 ✘ BÜROS",
        "visible_to": ["staff"],
        "channels": [
            {"name": "👑・Owner-Büro",       "type": "voice", "staff_only": True},
            {"name": "⚡・Admin-Büro",        "type": "voice", "staff_only": True},
            {"name": "🔨・Mod-Büro",          "type": "voice", "staff_only": True},
            {"name": "🎧・Support-Büro",      "type": "voice", "staff_only": True},
            {"name": "📊・Meeting-Raum",      "type": "voice", "staff_only": True},
        ],
    },
    {
        "category": "🛡️ ✘ ADMIN",
        "visible_to": ["staff"],
        "channels": [
            {"name": "👑・owner-chat",        "type": "text", "owner_only": True},
            {"name": "⚡・admin-chat",         "type": "text", "staff_only": True},
            {"name": "🔨・mod-chat",           "type": "text", "staff_only": True},
            {"name": "🎧・support-chat",       "type": "text", "staff_only": True},
            {"name": "📋・team-ankündigung",   "type": "text", "staff_only": True},
            {"name": "📝・team-todo",          "type": "text", "staff_only": True},
            {"name": "🚨・report-eingang",     "type": "text", "staff_only": True},
        ],
    },
    {
        "category": "📋 ✘ LOGS",
        "visible_to": ["staff"],
        "channels": [
            {"name": "📥・join-logs",          "type": "text", "staff_only": True, "log": "join"},
            {"name": "📤・leave-logs",         "type": "text", "staff_only": True, "log": "leave"},
            {"name": "✅・verify-logs",        "type": "text", "staff_only": True, "log": "verify"},
            {"name": "💬・message-logs",       "type": "text", "staff_only": True, "log": "message"},
            {"name": "🎙️・voice-logs",         "type": "text", "staff_only": True, "log": "voice"},
            {"name": "🎭・role-logs",          "type": "text", "staff_only": True, "log": "role"},
            {"name": "📁・channel-logs",       "type": "text", "staff_only": True, "log": "channel"},
            {"name": "🌐・server-logs",        "type": "text", "staff_only": True, "log": "server"},
            {"name": "🎫・ticket-logs",        "type": "text", "staff_only": True, "log": "ticket"},
            {"name": "⚖️・moderation-logs",    "type": "text", "staff_only": True, "log": "moderation"},
            {"name": "🤖・bot-logs",           "type": "text", "staff_only": True, "log": "bot"},
        ],
    },
]

STAFF_ROLE_NAMES = [
    "👑 Owner", "👑 Co-Owner", "🛡️ Server-Manager",
    "⚡ Head-Admin", "⚡ Admin", "⚡ Vize-Admin",
    "🔨 Head-Moderator", "🔨 Senior-Moderator", "🔨 Moderator", "🔨 Trial-Moderator",
    "🎧 Support-Lead", "🎧 Supporter", "🎧 Trial-Supporter",
    "💻 Developer", "🤖 Bot-Manager",
]

# --------------------------------------------------------------------------- #
# HILFSFUNKTIONEN
# --------------------------------------------------------------------------- #
def find_role(guild: discord.Guild, name: str) -> Optional[discord.Role]:
    return discord.utils.get(guild.roles, name=name)

def find_category(guild: discord.Guild, name: str) -> Optional[discord.CategoryChannel]:
    return discord.utils.get(guild.categories, name=name)

def find_channel(guild: discord.Guild, name: str) -> Optional[discord.abc.GuildChannel]:
    return discord.utils.get(guild.channels, name=name)

def get_log_channel(guild: discord.Guild, log_type: str) -> Optional[discord.TextChannel]:
    """Findet einen Log-Kanal anhand des log-Keys."""
    mapping = {
        "join": "join-logs", "leave": "leave-logs", "verify": "verify-logs",
        "message": "message-logs", "voice": "voice-logs", "role": "role-logs",
        "channel": "channel-logs", "server": "server-logs", "ticket": "ticket-logs",
        "moderation": "moderation-logs", "bot": "bot-logs",
    }
    suffix = mapping.get(log_type)
    if not suffix:
        return None
    for ch in guild.text_channels:
        if ch.name.endswith(suffix):
            return ch
    return None

def build_overwrites(guild: discord.Guild, visible_to: list[str],
                     locked: bool = False, staff_only: bool = False,
                     owner_only: bool = False) -> dict:
    """
    Erstellt Permission-Overwrites für eine Kategorie/einen Kanal.
    visible_to gibt an, welche Stufe den Kanal sehen darf:
       - "unverified": jeder (auch Unverified)
       - "verified":   ab Verified
       - "member":     ab Member
       - "staff":      nur Team
    """
    everyone   = guild.default_role
    unverified = find_role(guild, KEY_ROLES["unverified"])
    verified   = find_role(guild, KEY_ROLES["verified"])
    member     = find_role(guild, KEY_ROLES["member"])
    bewerber   = find_role(guild, KEY_ROLES["bewerber"])
    muted      = find_role(guild, KEY_ROLES["muted"])

    ow: dict = {}

    # Standard: @everyone darf nichts sehen
    ow[everyone] = discord.PermissionOverwrite(view_channel=False, send_messages=False, connect=False)

    if "unverified" in visible_to:
        ow[everyone] = discord.PermissionOverwrite(view_channel=True, read_message_history=True,
                                                   send_messages=False, add_reactions=False, connect=False)
        if unverified:
            ow[unverified] = discord.PermissionOverwrite(view_channel=True, send_messages=False, connect=False)
    if "verified" in visible_to and verified:
        ow[verified] = discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True, speak=True)
        if bewerber:
            ow[bewerber] = discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True, speak=True)
    if "member" in visible_to and member:
        ow[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                 connect=True, speak=True, stream=True)

    # Staff sieht immer alles
    for rn in STAFF_ROLE_NAMES:
        r = find_role(guild, rn)
        if r:
            ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                connect=True, speak=True, read_message_history=True,
                                                manage_messages=True)

    if visible_to == ["staff"]:
        # Nur Team
        ow[everyone] = discord.PermissionOverwrite(view_channel=False, send_messages=False, connect=False)
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=False)
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=False)

    if staff_only:
        ow[everyone] = discord.PermissionOverwrite(view_channel=False, send_messages=False, connect=False)
        if member:   ow[member]   = discord.PermissionOverwrite(view_channel=False)
        if verified: ow[verified] = discord.PermissionOverwrite(view_channel=False)

    if owner_only:
        ow = {everyone: discord.PermissionOverwrite(view_channel=False, send_messages=False, connect=False)}
        for rn in ("👑 Owner", "👑 Co-Owner"):
            r = find_role(guild, rn)
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True, speak=True)

    if locked:
        # Lounges etc. - nur eingeladene/höhere Stufen
        ow[everyone] = discord.PermissionOverwrite(view_channel=True, send_messages=False, connect=False)
        if member:
            ow[member] = discord.PermissionOverwrite(view_channel=True, send_messages=False, connect=False)
        # Staff darf trotzdem rein - bereits oben gesetzt
        booster = find_role(guild, "💖 Booster")
        if booster:
            ow[booster] = discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True, speak=True)

    # Muted-Rolle: nichts schreiben/sprechen
    if muted:
        ow[muted] = discord.PermissionOverwrite(send_messages=False, speak=False, add_reactions=False,
                                                stream=False, send_messages_in_threads=False)

    return ow


# --------------------------------------------------------------------------- #
# SETUP-LOGIK
# --------------------------------------------------------------------------- #
async def create_roles(guild: discord.Guild, status_msg: discord.Message) -> None:
    """Erstellt alle Rollen, falls noch nicht vorhanden."""
    created = 0
    # Wir gehen UMGEKEHRT durch die Liste (unten zuerst), damit die zuletzt
    # erstellte Rolle (Owner) am höchsten ist.
    for role_def in reversed(ROLES):
        if find_role(guild, role_def["name"]):
            continue
        try:
            await guild.create_role(
                name=role_def["name"],
                color=discord.Color(role_def["color"]),
                hoist=role_def["hoist"],
                permissions=role_def["perms"],
                mentionable=False,
                reason="FUSE Setup",
            )
            created += 1
            await asyncio.sleep(0.4)  # Rate-Limit Schutz
        except Exception as e:
            log.warning("Rolle '%s' konnte nicht erstellt werden: %s", role_def["name"], e)
    log.info("Rollen erstellt: %s", created)

    # Reihenfolge korrigieren (Bot-Rolle muss höher sein als unsere höchste!)
    try:
        positions = {}
        # Bot eigene Rolle bleibt ganz oben
        bot_top = guild.me.top_role
        base = bot_top.position - 1
        for i, role_def in enumerate(ROLES):
            r = find_role(guild, role_def["name"])
            if r and r < bot_top:
                positions[r] = max(1, base - i)
        if positions:
            await guild.edit_role_positions(positions=positions, reason="FUSE Setup Order")
    except Exception as e:
        log.warning("Rollen-Positionen konnten nicht gesetzt werden: %s", e)


async def create_structure(guild: discord.Guild) -> None:
    """Erstellt alle Kategorien und Kanäle gemäß STRUCTURE."""
    for cat_def in STRUCTURE:
        cat_name = cat_def["category"]
        category = find_category(guild, cat_name)
        ow = build_overwrites(guild, cat_def["visible_to"])
        if not category:
            try:
                category = await guild.create_category(cat_name, overwrites=ow, reason="FUSE Setup")
                await asyncio.sleep(0.3)
            except Exception as e:
                log.warning("Kategorie '%s' fehlgeschlagen: %s", cat_name, e)
                continue
        else:
            try:
                await category.edit(overwrites=ow)
            except Exception:
                pass

        for ch_def in cat_def["channels"]:
            ch_name = ch_def["name"]
            ctype = ch_def.get("type", "text")
            locked = ch_def.get("locked", False)
            staff_only = ch_def.get("staff_only", False)
            owner_only = ch_def.get("owner_only", False)

            if find_channel(guild, ch_name):
                continue

            chan_ow = build_overwrites(
                guild, cat_def["visible_to"],
                locked=locked, staff_only=staff_only, owner_only=owner_only
            )

            try:
                if ctype == "text":
                    await guild.create_text_channel(ch_name, category=category, overwrites=chan_ow, reason="FUSE Setup")
                elif ctype == "voice":
                    await guild.create_voice_channel(ch_name, category=category, overwrites=chan_ow, reason="FUSE Setup")
                elif ctype == "stage":
                    if "COMMUNITY" in guild.features:
                        await guild.create_stage_channel(ch_name, category=category, overwrites=chan_ow, reason="FUSE Setup")
                    else:
                        await guild.create_voice_channel(ch_name, category=category, overwrites=chan_ow, reason="FUSE Setup")
                await asyncio.sleep(0.3)
            except Exception as e:
                log.warning("Kanal '%s' fehlgeschlagen: %s", ch_name, e)


async def wipe_server(guild: discord.Guild) -> None:
    """Löscht ALLE Kanäle und (vom Bot löschbare) Rollen."""
    for ch in list(guild.channels):
        try:
            await ch.delete(reason="FUSE Reset")
            await asyncio.sleep(0.25)
        except Exception:
            pass
    for r in list(guild.roles):
        if r.is_default() or r.managed or r >= guild.me.top_role:
            continue
        try:
            await r.delete(reason="FUSE Reset")
            await asyncio.sleep(0.25)
        except Exception:
            pass


async def fill_channels(guild: discord.Guild) -> None:
    """Füllt wichtige Kanäle mit Inhalten (Regeln, Verify-Button etc.)."""
    # --- Regelwerk ---
    rules_ch = discord.utils.get(guild.text_channels, name="📜・regelwerk")
    if rules_ch and not [m async for m in rules_ch.history(limit=1)]:
        emb = discord.Embed(
            title="📜 Regelwerk – FUSE | FS",
            description=(
                "Willkommen auf **FUSE | FS** – einer Roblox Roleplay / Crime-Gang Community.\n"
                "Damit hier alles entspannt bleibt, halte dich bitte an die folgenden Regeln.\n"
                "*Dieser Server ist ausschließlich für Roblox-Roleplay gedacht – nichts davon hat einen Real-Life-Bezug.*"
            ),
            color=BRAND_COLOR,
        )
        emb.add_field(name="§1 Respekt", value="Behandle jedes Mitglied freundlich. Keine Beleidigungen, kein Mobbing, kein Rassismus.", inline=False)
        emb.add_field(name="§2 Kein Spam", value="Kein Spammen von Nachrichten, Pings, Emojis oder Reaktionen.", inline=False)
        emb.add_field(name="§3 Keine Werbung", value="Werbung jeglicher Art ist ohne Erlaubnis verboten.", inline=False)
        emb.add_field(name="§4 NSFW", value="NSFW-Inhalte sind strengstens untersagt.", inline=False)
        emb.add_field(name="§5 Discord-Richtlinien", value="Die [Discord ToS](https://discord.com/terms) gelten zu jeder Zeit.", inline=False)
        emb.add_field(name="§6 Channel-Themen", value="Halte dich an die Themen der jeweiligen Kanäle.", inline=False)
        emb.add_field(name="§7 Roleplay", value="In RP-Kanälen wird im Charakter geschrieben. Keine OOC-Diskussionen.", inline=False)
        emb.add_field(name="§8 Team-Anweisungen", value="Anweisungen des Teams sind zu befolgen.", inline=False)
        emb.add_field(name="§9 Bugs / Glitches", value="Bekannte Bugs oder Exploits dem Team melden – nicht ausnutzen.", inline=False)
        emb.add_field(name="§10 Account-Sicherheit", value="Teile keine Accountdaten. Phishing = Bann.", inline=False)
        emb.set_footer(text="Mit dem Verify akzeptierst du diese Regeln.")
        await rules_ch.send(embed=emb)

    # --- Verify ---
    verify_ch = discord.utils.get(guild.text_channels, name="✅・verify")
    if verify_ch and not [m async for m in verify_ch.history(limit=1)]:
        emb = discord.Embed(
            title="✅ Verifizierung",
            description=(
                "Klicke auf den Button unten, um dich zu verifizieren.\n\n"
                "Damit bestätigst du, dass du das **Regelwerk** gelesen hast und "
                "Zugriff auf den Bewerbungs-Bereich erhältst.\n\n"
                "Nach erfolgreicher Bewerbung wirst du zum **Member** befördert "
                "und siehst alle Kanäle."
            ),
            color=SUCCESS_COLOR,
        )
        emb.set_footer(text="FUSE | FS – Verifizierungssystem")
        await verify_ch.send(embed=emb, view=VerifyView())

    # --- Willkommen-Info ---
    welcome_ch = discord.utils.get(guild.text_channels, name="👋・willkommen")
    if welcome_ch and not [m async for m in welcome_ch.history(limit=1)]:
        emb = discord.Embed(
            title=f"🎉 Willkommen auf {SERVER_NAME}!",
            description=(
                "Schön dass du da bist!\n\n"
                "➡️ Lies dir das **<#regelwerk>** durch.\n"
                "➡️ Anschließend kannst du dich im Kanal **<#verify>** verifizieren.\n"
                "➡️ Danach geht's weiter in den **Bewerbungs-Bereich**.\n\n"
                "Viel Spaß auf unserem Server! 💎"
            ),
            color=BRAND_COLOR,
        )
        await welcome_ch.send(embed=emb)

    # --- Bewerbung Formular ---
    form_ch = discord.utils.get(guild.text_channels, name="📋・formular")
    if form_ch and not [m async for m in form_ch.history(limit=1)]:
        emb = discord.Embed(
            title="📋 Bewerbungs-Formular",
            description=(
                "Möchtest du Member werden? Dann fülle bitte folgendes Formular aus "
                "und poste es im Kanal **#bewerbungschat**.\n\n"
                "```\n"
                "1. Wie heißt du im Roblox?\n"
                "2. Wie alt bist du?\n"
                "3. Wie lange spielst du schon Notruf Hamburg / Roblox-RP?\n"
                "4. Warum möchtest du zu FUSE?\n"
                "5. Was kannst du der Gang bieten?\n"
                "6. Hast du ein Mikrofon?\n"
                "7. Bist du aktiv (Std/Woche)?\n"
                "```\n"
                "Das Team meldet sich anschließend bei dir!"
            ),
            color=INFO_COLOR,
        )
        await form_ch.send(embed=emb)

    # --- Ticket ---
    ticket_ch = discord.utils.get(guild.text_channels, name="🎫・ticket")
    if ticket_ch and not [m async for m in ticket_ch.history(limit=1)]:
        emb = discord.Embed(
            title="🎫 Support-Tickets",
            description=(
                "Du brauchst Hilfe oder möchtest etwas dem Team melden?\n"
                "Klicke unten auf den Button, um ein **Ticket** zu öffnen.\n\n"
                "Ein Team-Mitglied wird sich schnellstmöglich melden."
            ),
            color=GOLD,
        )
        await ticket_ch.send(embed=emb, view=TicketView())

    # --- Ankündigung ---
    ann_ch = discord.utils.get(guild.text_channels, name="🔔・ankündigung")
    if ann_ch and not [m async for m in ann_ch.history(limit=1)]:
        emb = discord.Embed(
            title="🔔 Ankündigungen",
            description="Hier postet das Team alle wichtigen Ankündigungen rund um **FUSE | FS**.",
            color=BRAND_COLOR,
        )
        await ann_ch.send(embed=emb)

    # --- Boosts ---
    boost_ch = discord.utils.get(guild.text_channels, name="🚀・boosts")
    if boost_ch and not [m async for m in boost_ch.history(limit=1)]:
        emb = discord.Embed(
            title="🚀 Server Boosts",
            description=(
                "Danke an alle Booster! 💖\n"
                "Mit einem Boost unterstützt du die Community und erhältst die "
                "**💖 Booster** Rolle plus Zugang zu exklusiven Lounges."
            ),
            color=0xF47FFF,
        )
        await boost_ch.send(embed=emb)

    # --- Owner-Chat Hinweis ---
    owner_ch = discord.utils.get(guild.text_channels, name="👑・owner-chat")
    if owner_ch and not [m async for m in owner_ch.history(limit=1)]:
        emb = discord.Embed(
            title="👑 Owner-Chat",
            description="Privater Channel nur für Owner & Co-Owner.",
            color=0xFF0000,
        )
        await owner_ch.send(embed=emb)


# --------------------------------------------------------------------------- #
# VIEWS / BUTTONS
# --------------------------------------------------------------------------- #
class SetupView(discord.ui.View):
    """3-Button-Auswahl beim !start Befehl."""
    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Nur der Befehls-Autor darf das benutzen.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Abbruch", style=discord.ButtonStyle.danger, emoji="🛑")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb = discord.Embed(title="🛑 Setup abgebrochen", description="Es wurden keine Änderungen vorgenommen.", color=ERROR_COLOR)
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="Nur Hinzufügen", style=discord.ButtonStyle.primary, emoji="➕")
    async def only_add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(title="⏳ Setup läuft…",
                                description="Fehlende Rollen/Kanäle werden hinzugefügt.\nDas kann ein paar Minuten dauern.",
                                color=INFO_COLOR),
            view=None,
        )
        msg = await interaction.original_response()
        await run_setup(interaction.guild, msg, wipe=False)

    @discord.ui.button(label="Komplett neu aufsetzen", style=discord.ButtonStyle.success, emoji="♻️")
    async def fresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        confirm_view = ConfirmWipeView(self.author_id)
        emb = discord.Embed(
            title="⚠️ Wirklich KOMPLETT neu aufsetzen?",
            description="**ALLE Kanäle und Rollen werden gelöscht!**\nDas kann NICHT rückgängig gemacht werden.",
            color=ERROR_COLOR,
        )
        await interaction.response.edit_message(embed=emb, view=confirm_view)


class ConfirmWipeView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id

    @discord.ui.button(label="Ja, alles löschen & neu", style=discord.ButtonStyle.danger, emoji="♻️")
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(title="⏳ Server wird zurückgesetzt…",
                                description="Alle Kanäle & Rollen werden gelöscht und neu aufgebaut.",
                                color=INFO_COLOR),
            view=None,
        )
        msg = await interaction.original_response()
        await run_setup(interaction.guild, msg, wipe=True)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(title="🛑 Abgebrochen", color=ERROR_COLOR), view=None
        )


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verifizieren", style=discord.ButtonStyle.success, emoji="✅", custom_id="fuse_verify_btn")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        unv = find_role(guild, KEY_ROLES["unverified"])
        ver = find_role(guild, KEY_ROLES["verified"])
        bew = find_role(guild, KEY_ROLES["bewerber"])
        if ver and ver in member.roles:
            return await interaction.response.send_message("✅ Du bist bereits verifiziert!", ephemeral=True)
        try:
            if unv and unv in member.roles:
                await member.remove_roles(unv, reason="Verify")
            if ver:
                await member.add_roles(ver, reason="Verify")
            if bew:
                await member.add_roles(bew, reason="Verify -> Bewerber")
            await interaction.response.send_message(
                "✅ **Du wurdest verifiziert!** Du hast nun Zugriff auf den Bewerbungs-Bereich. Viel Glück!",
                ephemeral=True,
            )
            # Log
            log_ch = get_log_channel(guild, "verify")
            if log_ch:
                emb = discord.Embed(title="✅ User verifiziert", color=SUCCESS_COLOR, timestamp=datetime.utcnow())
                emb.add_field(name="User", value=f"{member.mention} (`{member.id}`)")
                emb.set_thumbnail(url=member.display_avatar.url)
                await log_ch.send(embed=emb)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Mir fehlen die Rechte. Schiebe meine Bot-Rolle ganz nach oben!", ephemeral=True)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket öffnen", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="fuse_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing:
            return await interaction.response.send_message(f"❗ Du hast bereits ein Ticket: {existing.mention}", ephemeral=True)

        category = find_category(guild, "🌐 ✘ BEWERBUNG")
        ow = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member:             discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, read_message_history=True),
            guild.me:           discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        for rn in STAFF_ROLE_NAMES:
            r = find_role(guild, rn)
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)

        ticket = await guild.create_text_channel(
            f"ticket-{member.name.lower()}",
            category=category, overwrites=ow, reason="Ticket geöffnet",
        )
        emb = discord.Embed(
            title="🎫 Ticket geöffnet",
            description=f"Hallo {member.mention}, ein Team-Mitglied meldet sich gleich bei dir.\nBeschreibe in der Zwischenzeit dein Anliegen.",
            color=GOLD,
        )
        await ticket.send(content=member.mention, embed=emb, view=TicketCloseView())
        await interaction.response.send_message(f"✅ Ticket erstellt: {ticket.mention}", ephemeral=True)
        log_ch = get_log_channel(guild, "ticket")
        if log_ch:
            await log_ch.send(embed=discord.Embed(title="🎫 Ticket geöffnet",
                                                  description=f"{member.mention} → {ticket.mention}",
                                                  color=GOLD, timestamp=datetime.utcnow()))


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="fuse_ticket_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Ticket wird in 5 Sekunden geschlossen…")
        await asyncio.sleep(5)
        try:
            log_ch = get_log_channel(interaction.guild, "ticket")
            if log_ch:
                await log_ch.send(embed=discord.Embed(title="🔒 Ticket geschlossen",
                                                      description=f"Channel: `{interaction.channel.name}` von {interaction.user.mention}",
                                                      color=ERROR_COLOR, timestamp=datetime.utcnow()))
            await interaction.channel.delete(reason="Ticket geschlossen")
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# SETUP RUNNER
# --------------------------------------------------------------------------- #
async def run_setup(guild: discord.Guild, status_msg: discord.Message, wipe: bool) -> None:
    try:
        if wipe:
            await status_msg.edit(embed=discord.Embed(title="🧹 Lösche alte Struktur…", color=INFO_COLOR))
            await wipe_server(guild)

        await status_msg.edit(embed=discord.Embed(title="🎭 Erstelle Rollen…", color=INFO_COLOR)) if status_msg else None
        await create_roles(guild, status_msg)

        await status_msg.edit(embed=discord.Embed(title="📁 Erstelle Kategorien & Kanäle…", color=INFO_COLOR)) if status_msg else None
        await create_structure(guild)

        await status_msg.edit(embed=discord.Embed(title="💬 Befülle wichtige Kanäle…", color=INFO_COLOR)) if status_msg else None
        await fill_channels(guild)

        done = discord.Embed(
            title="✅ Setup abgeschlossen!",
            description=(
                f"**{SERVER_NAME}** wurde komplett eingerichtet.\n\n"
                f"• 🎭 Rollen: **{len(ROLES)}**\n"
                f"• 📁 Kategorien: **{len(STRUCTURE)}**\n"
                f"• 💬 Kanäle: **{sum(len(c['channels']) for c in STRUCTURE)}**\n\n"
                "Vergiss nicht, die **Bot-Rolle** ganz oben in der Rollen-Liste zu lassen!"
            ),
            color=SUCCESS_COLOR,
        )
        try:
            if status_msg:
                await status_msg.edit(embed=done)
        except Exception:
            pass
    except Exception as e:
        log.exception("Setup-Fehler")
        try:
            if status_msg:
                await status_msg.edit(embed=discord.Embed(title="❌ Fehler beim Setup", description=f"```{e}```", color=ERROR_COLOR))
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# COMMANDS
# --------------------------------------------------------------------------- #
@bot.event
async def on_ready():
    log.info("Eingeloggt als %s (ID: %s)", bot.user, bot.user.id)
    # Persistent Views registrieren
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(TicketCloseView())
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}start | {SERVER_NAME}"))


@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start_cmd(ctx: commands.Context):
    """Setup-Wizard."""
    emb = discord.Embed(
        title=f"⚙️ {SERVER_NAME} – Setup Wizard",
        description=(
            "Wähle eine Option, um den Server einzurichten:\n\n"
            "🛑 **Abbruch** – nichts tun.\n"
            "➕ **Nur Hinzufügen** – fehlende Rollen & Kanäle ergänzen, bestehendes bleibt.\n"
            "♻️ **Komplett neu aufsetzen** – **ALLES** löschen und neu erstellen.\n\n"
            "*Stelle sicher, dass die Bot-Rolle ganz oben in der Hierarchie steht "
            "und der Bot Administrator-Rechte hat.*"
        ),
        color=BRAND_COLOR,
    )
    emb.set_footer(text="FUSE | FS Setup • nur Admins")
    await ctx.send(embed=emb, view=SetupView(ctx.author.id))


@start_cmd.error
async def start_err(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=discord.Embed(title="❌ Keine Berechtigung",
                                            description="Du brauchst **Administrator** für diesen Befehl.",
                                            color=ERROR_COLOR))


@bot.command(name="resend-verify")
@commands.has_permissions(administrator=True)
async def resend_verify(ctx):
    """Sendet den Verify-Button erneut im aktuellen Kanal."""
    emb = discord.Embed(
        title="✅ Verifizierung",
        description="Klicke auf den Button, um dich zu verifizieren.",
        color=SUCCESS_COLOR,
    )
    await ctx.send(embed=emb, view=VerifyView())


# --------------------------------------------------------------------------- #
# EVENTS – WELCOME / LEAVE / LOGS
# --------------------------------------------------------------------------- #
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    # Unverified Rolle
    unv = find_role(guild, KEY_ROLES["unverified"])
    if unv:
        try: await member.add_roles(unv, reason="Auto: Unverified")
        except Exception: pass

    # Welcome-Nachricht
    wc = discord.utils.get(guild.text_channels, name="👋・willkommen")
    if wc:
        emb = discord.Embed(
            title=f"**WILLKOMMEN IN {SERVER_NAME} !**",
            description=(
                f"Hey {member.mention}! Willkommen bei **Fuse**!\n"
                f"Du bist unser **{guild.member_count}.** Member.\n\n"
                f"Bitte halte dich an die <#{discord.utils.get(guild.text_channels, name='📜・regelwerk').id if discord.utils.get(guild.text_channels, name='📜・regelwerk') else 0}> "
                f"und geh freundlich mit allen Mitgliedern um.\n\n"
                f"➡️ Verifiziere dich im Kanal **#verify** um loszulegen!"
            ),
            color=BRAND_COLOR,
            timestamp=datetime.utcnow(),
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_footer(text=f"User-ID: {member.id}")
        await wc.send(content=member.mention, embed=emb)

    # Log
    log_ch = get_log_channel(guild, "join")
    if log_ch:
        emb = discord.Embed(title="📥 Member Joined", color=SUCCESS_COLOR, timestamp=datetime.utcnow())
        emb.add_field(name="User", value=f"{member.mention} (`{member.id}`)")
        emb.add_field(name="Account erstellt", value=f"<t:{int(member.created_at.timestamp())}:R>")
        emb.add_field(name="Member-Count", value=f"**{guild.member_count}**")
        emb.set_thumbnail(url=member.display_avatar.url)
        await log_ch.send(embed=emb)


@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild
    bye = discord.utils.get(guild.text_channels, name="👋・tschüss")
    if bye:
        emb = discord.Embed(
            title="👋 Tschüss!",
            description=f"**{member}** hat den Server verlassen.\nWir sind jetzt **{guild.member_count}** Member.",
            color=ERROR_COLOR, timestamp=datetime.utcnow(),
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        await bye.send(embed=emb)
    log_ch = get_log_channel(guild, "leave")
    if log_ch:
        emb = discord.Embed(title="📤 Member Left", color=ERROR_COLOR, timestamp=datetime.utcnow())
        emb.add_field(name="User", value=f"{member} (`{member.id}`)")
        emb.set_thumbnail(url=member.display_avatar.url)
        await log_ch.send(embed=emb)


@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot or not message.guild: return
    log_ch = get_log_channel(message.guild, "message")
    if not log_ch: return
    emb = discord.Embed(title="🗑️ Nachricht gelöscht", color=ERROR_COLOR, timestamp=datetime.utcnow())
    emb.add_field(name="Autor", value=message.author.mention, inline=True)
    emb.add_field(name="Kanal", value=message.channel.mention, inline=True)
    emb.add_field(name="Inhalt", value=(message.content[:1000] or "*kein Text*"), inline=False)
    await log_ch.send(embed=emb)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot or not before.guild or before.content == after.content: return
    log_ch = get_log_channel(before.guild, "message")
    if not log_ch: return
    emb = discord.Embed(title="✏️ Nachricht bearbeitet", color=GOLD, timestamp=datetime.utcnow(),
                        url=after.jump_url)
    emb.add_field(name="Autor", value=before.author.mention, inline=True)
    emb.add_field(name="Kanal", value=before.channel.mention, inline=True)
    emb.add_field(name="Vorher", value=(before.content[:500] or "*leer*"), inline=False)
    emb.add_field(name="Nachher", value=(after.content[:500] or "*leer*"), inline=False)
    await log_ch.send(embed=emb)


@bot.event
async def on_voice_state_update(member: discord.Member, before, after):
    log_ch = get_log_channel(member.guild, "voice")
    if not log_ch: return
    if before.channel != after.channel:
        if after.channel and not before.channel:
            txt, col = f"🎙️ **{member}** ist **{after.channel.name}** beigetreten.", SUCCESS_COLOR
        elif before.channel and not after.channel:
            txt, col = f"🔇 **{member}** hat **{before.channel.name}** verlassen.", ERROR_COLOR
        else:
            txt, col = f"🔄 **{member}**: `{before.channel.name}` → `{after.channel.name}`", INFO_COLOR
        await log_ch.send(embed=discord.Embed(description=txt, color=col, timestamp=datetime.utcnow()))


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.roles == after.roles: return
    log_ch = get_log_channel(before.guild, "role")
    if not log_ch: return
    added   = [r for r in after.roles if r not in before.roles]
    removed = [r for r in before.roles if r not in after.roles]
    emb = discord.Embed(title="🎭 Rollen geändert", color=INFO_COLOR, timestamp=datetime.utcnow())
    emb.add_field(name="User", value=after.mention, inline=False)
    if added:   emb.add_field(name="➕ Hinzugefügt", value=", ".join(r.mention for r in added), inline=False)
    if removed: emb.add_field(name="➖ Entfernt",    value=", ".join(r.mention for r in removed), inline=False)
    await log_ch.send(embed=emb)


@bot.event
async def on_guild_channel_create(channel):
    log_ch = get_log_channel(channel.guild, "channel")
    if log_ch:
        await log_ch.send(embed=discord.Embed(title="📁 Kanal erstellt",
                                              description=f"{channel.mention} (`{channel.name}`)",
                                              color=SUCCESS_COLOR, timestamp=datetime.utcnow()))


@bot.event
async def on_guild_channel_delete(channel):
    log_ch = get_log_channel(channel.guild, "channel")
    if log_ch:
        await log_ch.send(embed=discord.Embed(title="📁 Kanal gelöscht",
                                              description=f"`{channel.name}`",
                                              color=ERROR_COLOR, timestamp=datetime.utcnow()))


@bot.event
async def on_guild_role_create(role):
    log_ch = get_log_channel(role.guild, "server")
    if log_ch:
        await log_ch.send(embed=discord.Embed(title="🎭 Rolle erstellt",
                                              description=f"{role.mention} (`{role.name}`)",
                                              color=SUCCESS_COLOR, timestamp=datetime.utcnow()))


@bot.event
async def on_guild_role_delete(role):
    log_ch = get_log_channel(role.guild, "server")
    if log_ch:
        await log_ch.send(embed=discord.Embed(title="🎭 Rolle gelöscht",
                                              description=f"`{role.name}`",
                                              color=ERROR_COLOR, timestamp=datetime.utcnow()))


@bot.event
async def on_member_ban(guild, user):
    log_ch = get_log_channel(guild, "moderation")
    if log_ch:
        await log_ch.send(embed=discord.Embed(title="🔨 Member gebannt",
                                              description=f"**{user}** (`{user.id}`)",
                                              color=ERROR_COLOR, timestamp=datetime.utcnow()))


@bot.event
async def on_member_unban(guild, user):
    log_ch = get_log_channel(guild, "moderation")
    if log_ch:
        await log_ch.send(embed=discord.Embed(title="🕊️ Member entbannt",
                                              description=f"**{user}** (`{user.id}`)",
                                              color=SUCCESS_COLOR, timestamp=datetime.utcnow()))


# --------------------------------------------------------------------------- #
# START
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("❌ DISCORD_TOKEN fehlt! Lege ihn in den Railway-Variablen an.")
    bot.run(TOKEN)
