"""
FUSE | FS - Discord Setup & Management Bot
==========================================
Roblox-RP / Notruf-Hamburg Crime-Gang Discord
- 52 Rollen in fester Hierarchie (Owner immer ganz oben)
- Saubere Sichtbarkeit:
    * Unverified  -> nur willkommen / regelwerk / verify
    * Verified    -> + Bewerbungs-Bereich (kein verify mehr)
    * Member      -> alles außer Verify & Bewerbung (das hat er schon)
    * Staff       -> alles
- Verify-System (Button), Tickets, Welcome, Logs, Büros, Lounges
- Setup-Wizard via !start (3 Buttons im Embed)
"""

import os
import asyncio
import logging
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
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
# BRANDING
# --------------------------------------------------------------------------- #
BRAND_COLOR   = 0xE91E63   # FUSE Pink
SUCCESS_COLOR = 0x2ECC71
ERROR_COLOR   = 0xE74C3C
INFO_COLOR    = 0x3498DB
GOLD          = 0xF1C40F
PURPLE        = 0x9B59B6
DARK          = 0x2B2D31

LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SOFT = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

# Banner / Logos
FUSE_BANNER = "https://i.imgur.com/8WqFbgM.png"   # generic dark banner fallback
FUSE_ICON   = "https://cdn.discordapp.com/embed/avatars/0.png"

# --------------------------------------------------------------------------- #
# PERMISSIONS-PROFILE
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
BASIC_PERMS = discord.Permissions(
    read_message_history=True, send_messages=True, connect=True, speak=True,
)

# --------------------------------------------------------------------------- #
# ROLLEN  (Index 0 = ganz oben in der Hierarchie -> Owner)
# --------------------------------------------------------------------------- #
ROLES: list[dict] = [
    # ── Leitung ─────────────────────────────────────
    {"name": "👑 Owner",            "color": 0xFF0000, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "👑 Co-Owner",         "color": 0xFF1A1A, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "🛡️ Server-Manager",   "color": 0xFF4500, "hoist": True, "perms": ADMIN_PERMS},
    # ── Admin ───────────────────────────────────────
    {"name": "⚡ Head-Admin",        "color": 0xFF6600, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "⚡ Admin",             "color": 0xFF8000, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "⚡ Vize-Admin",        "color": 0xFF9933, "hoist": True, "perms": MOD_PERMS},
    # ── Moderation ──────────────────────────────────
    {"name": "🔨 Head-Moderator",   "color": 0xFFAA00, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Senior-Moderator", "color": 0xFFC04D, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Moderator",        "color": 0xFFD580, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Trial-Moderator",  "color": 0xFFE0B3, "hoist": True, "perms": TRIAL_MOD_PERMS},
    # ── Support ─────────────────────────────────────
    {"name": "🎧 Support-Lead",     "color": 0x00CED1, "hoist": True, "perms": TRIAL_MOD_PERMS},
    {"name": "🎧 Supporter",        "color": 0x40E0D0, "hoist": True, "perms": TRIAL_MOD_PERMS},
    {"name": "🎧 Trial-Supporter",  "color": 0x7FFFD4, "hoist": True, "perms": MEMBER_PERMS},
    # ── Spezial-Team ────────────────────────────────
    {"name": "💻 Developer",        "color": 0x9B59B6, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "🤖 Bot-Manager",      "color": 0x8E44AD, "hoist": True, "perms": MOD_PERMS},
    {"name": "🎨 Designer",         "color": 0xE67E22, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎉 Event-Manager",    "color": 0xD35400, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "📝 Recruiter",        "color": 0x16A085, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🤝 Partner-Manager",  "color": 0x1ABC9C, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "📱 SocialMedia-Team", "color": 0xE91E63, "hoist": True, "perms": MEMBER_PERMS},
    # ── Gang-Ränge ──────────────────────────────────
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
    # ── Member-Stufen ───────────────────────────────
    {"name": "🏆 Veteran",          "color": 0xFFD700, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "⭐ Elite",             "color": 0xFFC125, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💠 Member+",          "color": 0x00BFFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💠 Member",           "color": 0x1E90FF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🧪 Trial-Member",     "color": 0x87CEEB, "hoist": True, "perms": MEMBER_PERMS},
    # ── Creator / Specials ──────────────────────────
    {"name": "🎬 YouTuber",         "color": 0xFF0000, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎮 Twitch-Streamer",  "color": 0x6441A5, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎵 TikToker",         "color": 0x010101, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🖌️ Content-Creator",  "color": 0xC71585, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "✅ Verified",         "color": 0x57F287, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🤝 Fuse",             "color": 0xFF69B4, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "💕 Friend",           "color": 0xFFB6C1, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🎶 DJ",               "color": 0x1DB954, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🎂 Geburtstagskind",  "color": 0xFF69B4, "hoist": False, "perms": MEMBER_PERMS},
    # ── Boosts ──────────────────────────────────────
    {"name": "💖 Boost-King",       "color": 0xF47FFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💖 Booster",          "color": 0xF47FFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Nitro",            "color": 0xB9BBBE, "hoist": False, "perms": MEMBER_PERMS},
    # ── Sonderrollen ────────────────────────────────
    {"name": "📝 Bewerber",         "color": 0x95A5A6, "hoist": True, "perms": BASIC_PERMS},
    {"name": "👋 Gast",             "color": 0xBDC3C7, "hoist": False, "perms": BASIC_PERMS},
    {"name": "😴 AFK",              "color": 0x4F545C, "hoist": False, "perms": BASIC_PERMS},
    {"name": "🔇 Muted",            "color": 0x36393F, "hoist": False, "perms": discord.Permissions.none()},
    {"name": "⚠️ Verwarnt",         "color": 0xE74C3C, "hoist": False, "perms": BASIC_PERMS},
    {"name": "❌ Unverified",       "color": 0x99AAB5, "hoist": False, "perms": discord.Permissions.none()},
]

KEY_ROLES = {
    "owner":      "👑 Owner",
    "member":     "💠 Member",
    "verified":   "✅ Verified",
    "bewerber":   "📝 Bewerber",
    "muted":      "🔇 Muted",
    "unverified": "❌ Unverified",
}

STAFF_ROLE_NAMES = [
    "👑 Owner", "👑 Co-Owner", "🛡️ Server-Manager",
    "⚡ Head-Admin", "⚡ Admin", "⚡ Vize-Admin",
    "🔨 Head-Moderator", "🔨 Senior-Moderator", "🔨 Moderator", "🔨 Trial-Moderator",
    "🎧 Support-Lead", "🎧 Supporter", "🎧 Trial-Supporter",
    "💻 Developer", "🤖 Bot-Manager",
]

# --------------------------------------------------------------------------- #
# SICHTBARKEITS-KEYS
# --------------------------------------------------------------------------- #
# "lobby"          → Unverified, Verified, Member sehen (willkommen, regelwerk, tschüss)
# "verify_only"    → NUR Unverified (Verify-Kanal verschwindet nach Verify)
# "bewerbung"      → NUR Verified + Bewerber (Member sieht das nicht mehr!)
# "member"         → NUR Member (+ Staff)
# "staff"          → NUR Staff
# Locked-Channel zusätzlich -> nur Booster / spezifische Rollen können rein

STRUCTURE: list[dict] = [
    {
        "category": "📩 ✘ WILLKOMMEN",
        "visibility": "lobby",
        "channels": [
            {"name": "👋・willkommen",   "type": "text",  "visibility": "lobby"},
            {"name": "📜・regelwerk",    "type": "text",  "visibility": "lobby"},
            {"name": "✅・verify",       "type": "text",  "visibility": "verify_only"},
            {"name": "👋・tschüss",      "type": "text",  "visibility": "lobby"},
        ],
    },
    {
        "category": "🌐 ✘ BEWERBUNG",
        "visibility": "bewerbung",
        "channels": [
            {"name": "🎫・ticket",         "type": "text",  "visibility": "bewerbung"},
            {"name": "👾・bewerbungschat", "type": "text",  "visibility": "bewerbung"},
            {"name": "📋・formular",       "type": "text",  "visibility": "bewerbung"},
            {"name": "🎙️・warteraum",      "type": "voice", "visibility": "bewerbung"},
            {"name": "🚪・Einreise-1",     "type": "voice", "visibility": "bewerbung", "locked": True},
            {"name": "🚪・Einreise-2",     "type": "voice", "visibility": "bewerbung", "locked": True},
        ],
    },
    {
        "category": "🎀 ✘ INFOS",
        "visibility": "member",
        "channels": [
            {"name": "✅・activity-check", "type": "text"},
            {"name": "🔔・ankündigung",    "type": "text"},
            {"name": "🎬・meeting-clips",  "type": "text"},
            {"name": "🚀・boosts",         "type": "text"},
            {"name": "😂・hall-of-shame",  "type": "text"},
            {"name": "🎥・free-tt-vid",    "type": "text"},
        ],
    },
    {
        "category": "💬 ✘ COMMUNITY",
        "visibility": "member",
        "channels": [
            {"name": "💬・chat",         "type": "text"},
            {"name": "🎨・media",        "type": "text"},
            {"name": "🤣・memes",        "type": "text"},
            {"name": "🎮・gaming",       "type": "text"},
            {"name": "🤖・bot-commands", "type": "text"},
            {"name": "💡・vorschläge",   "type": "text"},
        ],
    },
    {
        "category": "📱 ✘ SOCIALMEDIA",
        "visibility": "member",
        "channels": [
            {"name": "💖・cani",        "type": "text"},
            {"name": "📱・socialmedia", "type": "text"},
            {"name": "📸・instagram",   "type": "text"},
            {"name": "🎵・tiktok",      "type": "text"},
            {"name": "🎬・youtube",     "type": "text"},
        ],
    },
    {
        "category": "📞 ✘ TALKS",
        "visibility": "member",
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
        "category": "🧱 ✘ FUSE MERCH",
        "visibility": "member",
        "channels": [
            {"name": "🦺・weste",   "type": "text"},
            {"name": "📿・armband", "type": "text"},
            {"name": "👕・merch",   "type": "text"},
            {"name": "👕・trikot",  "type": "text"},
            {"name": "👕・polo",    "type": "text"},
        ],
    },
    {
        "category": "📓 ✘ GANG INFOS",
        "visibility": "member",
        "channels": [
            {"name": "💗・farbe",         "type": "text"},
            {"name": "🎨・rollensystem",  "type": "text"},
            {"name": "🎮・roblox-gruppe", "type": "text"},
            {"name": "🏠・anwesen",       "type": "text"},
            {"name": "🛡️・partnerschaft", "type": "text"},
        ],
    },
    {
        "category": "🔒 ✘ LOUNGES",
        "visibility": "member",
        "channels": [
            {"name": "🎀・LOUNGE-400-RBX", "type": "voice", "locked": True},
            {"name": "♟️・Nils-Luke",       "type": "voice", "locked": True},
            {"name": "💎・M-J-S-F",         "type": "voice", "locked": True},
            {"name": "💬・lounge-chat",     "type": "text",  "locked": True},
            {"name": "🍺・Bier-Keller",     "type": "voice", "locked": True},
        ],
    },
    {
        "category": "🏢 ✘ BÜROS",
        "visibility": "staff",
        "channels": [
            {"name": "👑・Owner-Büro",   "type": "voice", "visibility": "owner_only"},
            {"name": "⚡・Admin-Büro",    "type": "voice", "visibility": "staff"},
            {"name": "🔨・Mod-Büro",      "type": "voice", "visibility": "staff"},
            {"name": "🎧・Support-Büro",  "type": "voice", "visibility": "staff"},
            {"name": "📊・Meeting-Raum",  "type": "voice", "visibility": "staff"},
        ],
    },
    {
        "category": "🛡️ ✘ ADMIN",
        "visibility": "staff",
        "channels": [
            {"name": "👑・owner-chat",      "type": "text", "visibility": "owner_only"},
            {"name": "⚡・admin-chat",       "type": "text", "visibility": "staff"},
            {"name": "🔨・mod-chat",         "type": "text", "visibility": "staff"},
            {"name": "🎧・support-chat",     "type": "text", "visibility": "staff"},
            {"name": "📋・team-ankündigung", "type": "text", "visibility": "staff"},
            {"name": "📝・team-todo",        "type": "text", "visibility": "staff"},
            {"name": "🚨・report-eingang",   "type": "text", "visibility": "staff"},
        ],
    },
    {
        "category": "📋 ✘ LOGS",
        "visibility": "staff",
        "channels": [
            {"name": "📥・join-logs",       "type": "text", "log": "join"},
            {"name": "📤・leave-logs",      "type": "text", "log": "leave"},
            {"name": "✅・verify-logs",     "type": "text", "log": "verify"},
            {"name": "💬・message-logs",    "type": "text", "log": "message"},
            {"name": "🎙️・voice-logs",      "type": "text", "log": "voice"},
            {"name": "🎭・role-logs",       "type": "text", "log": "role"},
            {"name": "📁・channel-logs",    "type": "text", "log": "channel"},
            {"name": "🌐・server-logs",     "type": "text", "log": "server"},
            {"name": "🎫・ticket-logs",     "type": "text", "log": "ticket"},
            {"name": "⚖️・moderation-logs", "type": "text", "log": "moderation"},
            {"name": "🤖・bot-logs",        "type": "text", "log": "bot"},
        ],
    },
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
    suffix_map = {
        "join": "join-logs", "leave": "leave-logs", "verify": "verify-logs",
        "message": "message-logs", "voice": "voice-logs", "role": "role-logs",
        "channel": "channel-logs", "server": "server-logs", "ticket": "ticket-logs",
        "moderation": "moderation-logs", "bot": "bot-logs",
    }
    suffix = suffix_map.get(log_type)
    if not suffix: return None
    for ch in guild.text_channels:
        if ch.name.endswith(suffix):
            return ch
    return None


def build_overwrites(guild: discord.Guild, visibility: str, locked: bool = False) -> dict:
    """
    Erstellt Permission-Overwrites basierend auf einer Visibility-Stufe.

    Stufen:
      lobby        -> alle (Unverified/Verified/Member) dürfen sehen, nur Verified+Member schreiben
      verify_only  -> NUR Unverified (sehen + reagieren) - Verified/Member NICHT mehr
      bewerbung    -> NUR Verified + Bewerber - Member NICHT, Unverified NICHT
      member       -> NUR Member (+ Trial-Member, Veteran...) - Unverified/Verified NICHT
      staff        -> NUR Team
      owner_only   -> NUR Owner + Co-Owner
    """
    everyone   = guild.default_role
    unverified = find_role(guild, KEY_ROLES["unverified"])
    verified   = find_role(guild, KEY_ROLES["verified"])
    member     = find_role(guild, KEY_ROLES["member"])
    bewerber   = find_role(guild, KEY_ROLES["bewerber"])
    muted      = find_role(guild, KEY_ROLES["muted"])

    ow: dict = {}

    # Default: nichts sehen
    ow[everyone] = discord.PermissionOverwrite(view_channel=False, send_messages=False, connect=False)

    if visibility == "lobby":
        # Jeder (auch ohne Rolle) sieht die Lobby
        ow[everyone] = discord.PermissionOverwrite(
            view_channel=True, read_message_history=True,
            send_messages=False, add_reactions=False, connect=False,
        )
        if unverified:
            ow[unverified] = discord.PermissionOverwrite(view_channel=True, send_messages=False)
        if verified:
            ow[verified]   = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        if member:
            ow[member]     = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    elif visibility == "verify_only":
        # Nur Unverified sieht und kann mit dem Verify-Button interagieren
        if unverified:
            ow[unverified] = discord.PermissionOverwrite(
                view_channel=True, read_message_history=True,
                send_messages=False, add_reactions=True,
            )
        # Verified & Member explizit ausblenden!
        if verified: ow[verified] = discord.PermissionOverwrite(view_channel=False)
        if member:   ow[member]   = discord.PermissionOverwrite(view_channel=False)

    elif visibility == "bewerbung":
        # Nur Verified + Bewerber - NICHT Member, NICHT Unverified
        if verified:
            ow[verified] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, connect=True, speak=True,
                read_message_history=True,
            )
        if bewerber:
            ow[bewerber] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, connect=True, speak=True,
            )
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=False)

    elif visibility == "member":
        if member:
            ow[member] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, connect=True, speak=True, stream=True,
                read_message_history=True, add_reactions=True, embed_links=True, attach_files=True,
            )
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=False)

    elif visibility == "staff":
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=False)
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=False)

    elif visibility == "owner_only":
        # Nur Owner / Co-Owner sehen (zusätzlich zu Staff-Overrides unten wird wieder
        # hier am Ende „Team sieht alles" eingeschränkt)
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=False)
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=False)

    # ── Staff sieht IMMER alles (außer owner_only)
    if visibility != "owner_only":
        for rn in STAFF_ROLE_NAMES:
            r = find_role(guild, rn)
            if r:
                ow[r] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True,
                    connect=True, speak=True, read_message_history=True,
                    manage_messages=True,
                )
    else:
        for rn in ("👑 Owner", "👑 Co-Owner"):
            r = find_role(guild, rn)
            if r:
                ow[r] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True,
                    connect=True, speak=True, read_message_history=True,
                    manage_messages=True,
                )

    # ── Locked Channels: nur Booster + Staff
    if locked:
        # alle Standardrollen wieder aussperren
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=False)
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        booster = find_role(guild, "💖 Booster")
        if booster:
            ow[booster] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, connect=True, speak=True,
            )
        boost_king = find_role(guild, "💖 Boost-King")
        if boost_king:
            ow[boost_king] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, connect=True, speak=True,
            )

    # ── Muted: darf nie schreiben/sprechen
    if muted:
        ow[muted] = discord.PermissionOverwrite(
            send_messages=False, speak=False, add_reactions=False,
            stream=False, send_messages_in_threads=False,
        )

    return ow


# --------------------------------------------------------------------------- #
# SETUP-LOGIK
# --------------------------------------------------------------------------- #
async def create_roles(guild: discord.Guild) -> None:
    """Erstellt alle fehlenden Rollen."""
    created = 0
    # Umgekehrt (unten -> oben), damit zuletzt erstellte = Owner ganz oben
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
            await asyncio.sleep(0.35)
        except Exception as e:
            log.warning("Rolle '%s' fehlgeschlagen: %s", role_def["name"], e)
    log.info("Rollen erstellt: %s", created)
    await enforce_role_hierarchy(guild)


async def enforce_role_hierarchy(guild: discord.Guild) -> None:
    """
    Erzwingt: Owner steht IMMER ganz oben, danach Co-Owner, dann der Rest
    in der Reihenfolge der ROLES-Liste. Bot-Rolle bleibt technisch darüber.
    """
    try:
        bot_top = guild.me.top_role
        positions = {}
        # base = höchste freie Position direkt unter der Bot-Rolle
        base = bot_top.position - 1
        for i, role_def in enumerate(ROLES):
            r = find_role(guild, role_def["name"])
            if r and r < bot_top and not r.managed:
                positions[r] = max(1, base - i)
        if positions:
            await guild.edit_role_positions(positions=positions, reason="FUSE Hierarchie")
            log.info("Rollen-Hierarchie gesetzt (Owner ganz oben).")
    except Exception as e:
        log.warning("Rollen-Reihenfolge nicht setzbar: %s", e)


async def create_structure(guild: discord.Guild) -> None:
    """Erstellt alle Kategorien und Kanäle."""
    for cat_def in STRUCTURE:
        cat_name   = cat_def["category"]
        cat_vis    = cat_def["visibility"]
        cat_ow     = build_overwrites(guild, cat_vis)
        category   = find_category(guild, cat_name)
        if not category:
            try:
                category = await guild.create_category(cat_name, overwrites=cat_ow, reason="FUSE Setup")
                await asyncio.sleep(0.3)
            except Exception as e:
                log.warning("Kategorie '%s' fehlgeschlagen: %s", cat_name, e)
                continue
        else:
            try:
                await category.edit(overwrites=cat_ow)
            except Exception:
                pass

        for ch_def in cat_def["channels"]:
            ch_name = ch_def["name"]
            ctype   = ch_def.get("type", "text")
            ch_vis  = ch_def.get("visibility", cat_vis)
            locked  = ch_def.get("locked", False)

            if find_channel(guild, ch_name):
                # Bestehender Kanal -> Permissions neu setzen
                ch = find_channel(guild, ch_name)
                try:
                    await ch.edit(overwrites=build_overwrites(guild, ch_vis, locked=locked))
                except Exception:
                    pass
                continue

            chan_ow = build_overwrites(guild, ch_vis, locked=locked)
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
    """Löscht ALLE Kanäle und alle löschbaren Rollen."""
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


# --------------------------------------------------------------------------- #
# SCHÖNE EMBEDS
# --------------------------------------------------------------------------- #
def banner_embed(title: str, description: str, color: int = BRAND_COLOR) -> discord.Embed:
    """Großes Banner-Embed im FUSE-Style."""
    emb = discord.Embed(
        title=title,
        description=f"{LINE}\n{description}\n{LINE}",
        color=color,
        timestamp=datetime.utcnow(),
    )
    emb.set_footer(text=f"{SERVER_NAME}  •  Roblox Roleplay Community")
    return emb


async def fill_channels(guild: discord.Guild) -> None:
    """Füllt wichtige Kanäle mit hübschen Embeds."""

    # ════════════════════════════════════════════════════════════
    # 1) REGELWERK
    # ════════════════════════════════════════════════════════════
    rules_ch = discord.utils.get(guild.text_channels, name="📜・regelwerk")
    if rules_ch and not [m async for m in rules_ch.history(limit=1)]:
        # Header
        header = discord.Embed(
            description=(
                f"# 📜 {SERVER_NAME} — REGELWERK\n"
                f"{LINE}\n"
                f"> *Willkommen in unserer Familie.*\n"
                f"> *Bitte lies dir die Regeln sorgfältig durch — sie gelten für **jeden**.*\n"
                f"> *Mit dem Verify akzeptierst du diese Regeln automatisch.*\n"
                f"{LINE}"
            ),
            color=BRAND_COLOR,
        )
        header.set_image(url="https://singlecolorimage.com/get/E91E63/800x4.png")
        await rules_ch.send(embed=header)

        # Regelblöcke
        rules = [
            ("🤝", "§1  Respekt",        "Behandle jedes Mitglied freundlich. **Keine** Beleidigungen, kein Mobbing, kein Rassismus, kein Sexismus."),
            ("🔇", "§2  Kein Spam",      "Kein Spammen von Nachrichten, Pings, Emojis oder Reaktionen. Halte den Chat sauber."),
            ("📢", "§3  Keine Werbung",  "Werbung jeglicher Art (DM oder Channel) ist **ohne Erlaubnis verboten**."),
            ("🔞", "§4  NSFW",           "NSFW-, Gore- oder anstößige Inhalte sind **strikt untersagt**."),
            ("📜", "§5  Discord-ToS",    "Die [Discord Richtlinien](https://discord.com/terms) gelten zu jeder Zeit."),
            ("💬", "§6  Channel-Themen", "Halte dich an die Themen der jeweiligen Kanäle. Off-Topic gehört in <#💬・chat>."),
            ("🎭", "§7  Roleplay",       "In RP-Kanälen wird **im Charakter** geschrieben. Keine OOC-Diskussionen."),
            ("🛡️", "§8  Team-Anweisung", "Anweisungen des Teams sind ohne Diskussion zu befolgen."),
            ("🐛", "§9  Bugs / Exploits","Bekannte Bugs melden — **niemals** ausnutzen."),
            ("🔐", "§10 Account",        "Teile keine Account-Daten. Phishing-Links = **sofortiger Bann**."),
            ("🎮", "§11 Roblox-Only",    "Dieser Server ist **ausschließlich** Roblox-Roleplay. Kein Real-Life-Bezug."),
            ("⚖️", "§12 Strafen",        "Verstöße werden mit Verwarnung, Mute, Kick oder Bann sanktioniert."),
        ]
        body = discord.Embed(color=BRAND_COLOR)
        for emoji, name, desc in rules:
            body.add_field(name=f"{emoji}  **{name}**", value=f"> {desc}", inline=False)
        body.set_footer(text=f"{SERVER_NAME}  •  Stand: heute  •  Verstöße = Konsequenzen")
        await rules_ch.send(embed=body)

    # ════════════════════════════════════════════════════════════
    # 2) VERIFY
    # ════════════════════════════════════════════════════════════
    verify_ch = discord.utils.get(guild.text_channels, name="✅・verify")
    if verify_ch and not [m async for m in verify_ch.history(limit=1)]:
        emb = discord.Embed(
            title="🔐  VERIFIZIERUNG  •  FUSE | FS",
            description=(
                f"{LINE}\n"
                f"### 👋  Willkommen bei **{SERVER_NAME}**!\n\n"
                f"Bevor du den vollen Server erkunden kannst, musst du dich **kurz verifizieren**.\n"
                f"Damit bestätigst du, dass du das <#📜・regelwerk> gelesen hast.\n\n"
                f"**🔽 So geht's:**\n"
                f"`1.` Klicke unten auf den grünen Button **✅ Verifizieren**\n"
                f"`2.` Du erhältst sofort Zugriff auf den **Bewerbungs-Bereich**\n"
                f"`3.` Bewirb dich → werde **Member** → sieh alle Kanäle\n"
                f"{LINE}\n"
                f"*Probleme? Öffne im Anschluss ein Ticket unter <#🎫・ticket>.*"
            ),
            color=SUCCESS_COLOR,
        )
        emb.set_thumbnail(url=guild.icon.url if guild.icon else FUSE_ICON)
        emb.set_image(url="https://singlecolorimage.com/get/2ECC71/800x4.png")
        emb.set_footer(text=f"{SERVER_NAME}  •  Verifizierungs-System")
        await verify_ch.send(embed=emb, view=VerifyView())

    # ════════════════════════════════════════════════════════════
    # 3) WILLKOMMEN-INFO
    # ════════════════════════════════════════════════════════════
    welcome_ch = discord.utils.get(guild.text_channels, name="👋・willkommen")
    if welcome_ch and not [m async for m in welcome_ch.history(limit=1)]:
        rg = discord.utils.get(guild.text_channels, name="📜・regelwerk")
        vy = discord.utils.get(guild.text_channels, name="✅・verify")
        emb = discord.Embed(
            title=f"🎉  WILLKOMMEN AUF {SERVER_NAME.upper()}",
            description=(
                f"{LINE}\n"
                f"### 💎  Roblox  ✘  Roleplay  ✘  Crime-Gang\n\n"
                f"Schön dass du den Weg zu uns gefunden hast!\n"
                f"Wir sind eine **aktive Community** rund um Roblox-Roleplay & **Notruf Hamburg**.\n\n"
                f"**📌  Was du tun musst:**\n"
                f"➤  Lies dir das {rg.mention if rg else '#regelwerk'} durch\n"
                f"➤  Verifiziere dich im {vy.mention if vy else '#verify'}\n"
                f"➤  Bewirb dich im **Bewerbungs-Bereich**\n"
                f"➤  Werde **Member** & erlebe die volle Community 🎮\n"
                f"{LINE}\n"
                f"*Viel Spaß auf **{SERVER_NAME}**! 💎*"
            ),
            color=BRAND_COLOR,
        )
        emb.set_thumbnail(url=guild.icon.url if guild.icon else FUSE_ICON)
        emb.set_image(url="https://singlecolorimage.com/get/E91E63/800x4.png")
        emb.set_footer(text=f"{SERVER_NAME}  •  Welcome Center")
        await welcome_ch.send(embed=emb)

    # ════════════════════════════════════════════════════════════
    # 4) BEWERBUNGS-FORMULAR
    # ════════════════════════════════════════════════════════════
    form_ch = discord.utils.get(guild.text_channels, name="📋・formular")
    if form_ch and not [m async for m in form_ch.history(limit=1)]:
        emb = discord.Embed(
            title="📋  BEWERBUNG  •  FUSE | FS",
            description=(
                f"{LINE}\n"
                f"### 🎯  Du möchtest **Member** werden?\n"
                f"Dann fülle das untenstehende Formular **vollständig** aus und poste es im "
                f"<#👾・bewerbungschat>.\n\n"
                f"```yaml\n"
                f"━━━━━ BEWERBUNG ━━━━━\n"
                f"1. Roblox-Name:         \n"
                f"2. Alter:               \n"
                f"3. RP-Erfahrung:        \n"
                f"4. Warum FUSE?:         \n"
                f"5. Was bietest du uns?: \n"
                f"6. Mikrofon (Ja/Nein):  \n"
                f"7. Aktivität (Std/Wo):  \n"
                f"8. Discord-Erfahrung:   \n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"```\n"
                f"⏱️  **Bearbeitungszeit:** in der Regel **24 – 48 Std.**\n"
                f"🎤  **Voice-Interview:** möglich (Einreise¹ / Einreise²)\n"
                f"{LINE}"
            ),
            color=INFO_COLOR,
        )
        emb.set_image(url="https://singlecolorimage.com/get/3498DB/800x4.png")
        emb.set_footer(text=f"{SERVER_NAME}  •  Bewerbungs-System")
        await form_ch.send(embed=emb)

    # ════════════════════════════════════════════════════════════
    # 5) TICKET
    # ════════════════════════════════════════════════════════════
    ticket_ch = discord.utils.get(guild.text_channels, name="🎫・ticket")
    if ticket_ch and not [m async for m in ticket_ch.history(limit=1)]:
        emb = discord.Embed(
            title="🎫  SUPPORT-TICKETS  •  FUSE | FS",
            description=(
                f"{LINE}\n"
                f"### 💬  Brauchst du Hilfe?\n\n"
                f"Klicke unten auf **🎫 Ticket öffnen**, um privat mit dem Team zu schreiben.\n\n"
                f"**🛠️  Wofür?**\n"
                f"➤  Bewerbung & Fragen\n"
                f"➤  Beschwerden / Reports\n"
                f"➤  Partnerschaften\n"
                f"➤  Sonstige Anliegen\n\n"
                f"**⚠️  Hinweis:** Missbrauch von Tickets wird sanktioniert.\n"
                f"{LINE}"
            ),
            color=GOLD,
        )
        emb.set_image(url="https://singlecolorimage.com/get/F1C40F/800x4.png")
        emb.set_footer(text=f"{SERVER_NAME}  •  Ticket-System")
        await ticket_ch.send(embed=emb, view=TicketView())

    # ════════════════════════════════════════════════════════════
    # 6) ANKÜNDIGUNG
    # ════════════════════════════════════════════════════════════
    ann_ch = discord.utils.get(guild.text_channels, name="🔔・ankündigung")
    if ann_ch and not [m async for m in ann_ch.history(limit=1)]:
        emb = banner_embed(
            "🔔  ANKÜNDIGUNGEN",
            (
                f"### 📣  Hier postet das Team alle wichtigen News.\n\n"
                f"➤  Updates & Patches\n"
                f"➤  Events & Meetings\n"
                f"➤  Regel-Änderungen\n"
                f"➤  Server-News\n\n"
                f"*Schalte die Glocke 🔔 ein, um nichts zu verpassen!*"
            ),
            BRAND_COLOR,
        )
        await ann_ch.send(embed=emb)

    # ════════════════════════════════════════════════════════════
    # 7) BOOSTS
    # ════════════════════════════════════════════════════════════
    boost_ch = discord.utils.get(guild.text_channels, name="🚀・boosts")
    if boost_ch and not [m async for m in boost_ch.history(limit=1)]:
        emb = banner_embed(
            "🚀  SERVER BOOSTS  •  THANK YOU 💖",
            (
                f"### 💎  Danke an alle Booster!\n\n"
                f"Mit einem Boost unterstützt du **{SERVER_NAME}** und bekommst:\n"
                f"➤  💖 **Booster-Rolle**\n"
                f"➤  🔒 Zugang zu **Locked-Lounges**\n"
                f"➤  🎨 Eigene Farbe\n"
                f"➤  📌 Bevorzugter Support\n\n"
                f"*Aktuelle Boosts: **{boost_ch.guild.premium_subscription_count or 0}** 🚀*"
            ),
            0xF47FFF,
        )
        await boost_ch.send(embed=emb)

    # ════════════════════════════════════════════════════════════
    # 8) CHAT (Community)
    # ════════════════════════════════════════════════════════════
    chat_ch = discord.utils.get(guild.text_channels, name="💬・chat")
    if chat_ch and not [m async for m in chat_ch.history(limit=1)]:
        emb = banner_embed(
            "💬  COMMUNITY-CHAT",
            "Hier kannst du **frei mit anderen Membern quatschen**.\nHalte dich an die Regeln und hab Spaß! 🎉",
            BRAND_COLOR,
        )
        await chat_ch.send(embed=emb)

    # ════════════════════════════════════════════════════════════
    # 9) PARTNERSCHAFT
    # ════════════════════════════════════════════════════════════
    pn_ch = discord.utils.get(guild.text_channels, name="🛡️・partnerschaft")
    if pn_ch and not [m async for m in pn_ch.history(limit=1)]:
        emb = banner_embed(
            "🤝  PARTNERSCHAFT  •  FUSE | FS",
            (
                "### 📑 Anforderungen\n"
                "➤  **min. 50 Member**\n"
                "➤  aktive Community\n"
                "➤  keine NSFW / Toxic Server\n\n"
                "### 📨 Interesse?\n"
                "Öffne ein **Ticket** und wähle 'Partnerschaft'."
            ),
            0x1ABC9C,
        )
        await pn_ch.send(embed=emb)

    # ════════════════════════════════════════════════════════════
    # 10) OWNER-CHAT
    # ════════════════════════════════════════════════════════════
    owner_ch = discord.utils.get(guild.text_channels, name="👑・owner-chat")
    if owner_ch and not [m async for m in owner_ch.history(limit=1)]:
        emb = banner_embed(
            "👑  OWNER-CHAT",
            "Privater Kanal **ausschließlich** für Owner & Co-Owner.\nHier werden die wichtigsten Entscheidungen besprochen.",
            0xFF0000,
        )
        await owner_ch.send(embed=emb)

    # ════════════════════════════════════════════════════════════
    # 11) ADMIN-CHAT
    # ════════════════════════════════════════════════════════════
    admin_ch = discord.utils.get(guild.text_channels, name="⚡・admin-chat")
    if admin_ch and not [m async for m in admin_ch.history(limit=1)]:
        emb = banner_embed(
            "⚡  ADMIN-CHAT",
            "Privater Kanal für das **Admin-Team**.\nBitte alles Wichtige hier oder im Meeting-Raum besprechen.",
            0xFF8000,
        )
        await admin_ch.send(embed=emb)


# --------------------------------------------------------------------------- #
# VIEWS / BUTTONS
# --------------------------------------------------------------------------- #
class SetupView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=180)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌ Nur der Befehls-Autor darf das benutzen.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Abbruch", style=discord.ButtonStyle.danger, emoji="🛑")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb = discord.Embed(
            title="🛑  Setup abgebrochen",
            description=f"{LINE}\n*Es wurden keine Änderungen vorgenommen.*\n{LINE}",
            color=ERROR_COLOR,
        )
        await interaction.response.edit_message(embed=emb, view=None)

    @discord.ui.button(label="Nur Hinzufügen", style=discord.ButtonStyle.primary, emoji="➕")
    async def only_add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="⏳  Setup läuft…",
                description=f"{LINE}\nFehlende Rollen & Kanäle werden hinzugefügt.\nDas kann ein paar Minuten dauern.\n{LINE}",
                color=INFO_COLOR,
            ),
            view=None,
        )
        msg = await interaction.original_response()
        await run_setup(interaction.guild, msg, wipe=False)

    @discord.ui.button(label="Komplett neu aufsetzen", style=discord.ButtonStyle.success, emoji="♻️")
    async def fresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        emb = discord.Embed(
            title="⚠️  KOMPLETT neu aufsetzen?",
            description=(
                f"{LINE}\n"
                f"**ALLE Kanäle und Rollen werden gelöscht!**\n"
                f"Dieser Vorgang kann **NICHT** rückgängig gemacht werden.\n"
                f"{LINE}"
            ),
            color=ERROR_COLOR,
        )
        await interaction.response.edit_message(embed=emb, view=ConfirmWipeView(self.author_id))


class ConfirmWipeView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.author_id

    @discord.ui.button(label="Ja, alles löschen & neu", style=discord.ButtonStyle.danger, emoji="♻️")
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(
                title="⏳  Server wird zurückgesetzt…",
                description=f"{LINE}\nAlle Kanäle & Rollen werden gelöscht und neu aufgebaut.\n{LINE}",
                color=INFO_COLOR,
            ),
            view=None,
        )
        msg = await interaction.original_response()
        await run_setup(interaction.guild, msg, wipe=True)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            embed=discord.Embed(title="🛑  Abgebrochen", color=ERROR_COLOR), view=None,
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
            return await interaction.response.send_message("✅  Du bist bereits verifiziert!", ephemeral=True)
        try:
            if unv and unv in member.roles:
                await member.remove_roles(unv, reason="Verify")
            if ver:
                await member.add_roles(ver, reason="Verify")
            if bew:
                await member.add_roles(bew, reason="Verify -> Bewerber")
            emb = discord.Embed(
                title="🎉  Verifizierung erfolgreich!",
                description=(
                    f"{LINE}\n"
                    f"Willkommen, {member.mention}!\n\n"
                    f"Du hast nun Zugriff auf den **Bewerbungs-Bereich**.\n"
                    f"➤  Fülle das **Formular** aus\n"
                    f"➤  Poste es im **#bewerbungschat**\n"
                    f"➤  Warte auf die Rückmeldung des Teams\n"
                    f"{LINE}\n"
                    f"*Viel Erfolg! 🍀*"
                ),
                color=SUCCESS_COLOR,
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)

            log_ch = get_log_channel(guild, "verify")
            if log_ch:
                logemb = discord.Embed(title="✅ User verifiziert", color=SUCCESS_COLOR, timestamp=datetime.utcnow())
                logemb.add_field(name="User", value=f"{member.mention} (`{member.id}`)")
                logemb.set_thumbnail(url=member.display_avatar.url)
                await log_ch.send(embed=logemb)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌  Mir fehlen die Rechte! Schiebe die **Bot-Rolle** ganz nach oben.", ephemeral=True,
            )


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket öffnen", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="fuse_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
        if existing:
            return await interaction.response.send_message(
                f"❗  Du hast bereits ein Ticket: {existing.mention}", ephemeral=True
            )

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
            title="🎫  Ticket geöffnet",
            description=(
                f"{LINE}\n"
                f"Hallo {member.mention},\n"
                f"ein Team-Mitglied meldet sich gleich bei dir.\n\n"
                f"**📝  In der Zwischenzeit:**\n"
                f"➤  Beschreibe dein Anliegen so genau wie möglich\n"
                f"➤  Füge Screenshots / Beweise an\n"
                f"➤  Bleibe geduldig & freundlich\n"
                f"{LINE}"
            ),
            color=GOLD,
        )
        await ticket.send(content=member.mention, embed=emb, view=TicketCloseView())
        await interaction.response.send_message(f"✅  Ticket erstellt: {ticket.mention}", ephemeral=True)

        log_ch = get_log_channel(guild, "ticket")
        if log_ch:
            await log_ch.send(embed=discord.Embed(
                title="🎫 Ticket geöffnet",
                description=f"{member.mention} → {ticket.mention}",
                color=GOLD, timestamp=datetime.utcnow(),
            ))


class TicketCloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="fuse_ticket_close")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒  Ticket wird in 5 Sekunden geschlossen…")
        await asyncio.sleep(5)
        try:
            log_ch = get_log_channel(interaction.guild, "ticket")
            if log_ch:
                await log_ch.send(embed=discord.Embed(
                    title="🔒 Ticket geschlossen",
                    description=f"Channel: `{interaction.channel.name}` von {interaction.user.mention}",
                    color=ERROR_COLOR, timestamp=datetime.utcnow(),
                ))
            await interaction.channel.delete(reason="Ticket geschlossen")
        except Exception:
            pass


# --------------------------------------------------------------------------- #
# SETUP RUNNER (mit safe-edit)
# --------------------------------------------------------------------------- #
async def safe_edit(status_msg: Optional[discord.Message], **kwargs) -> Optional[discord.Message]:
    if status_msg is None: return None
    try:
        await status_msg.edit(**kwargs)
        return status_msg
    except (discord.NotFound, discord.Forbidden, discord.HTTPException) as e:
        log.warning("Status-Edit fehlgeschlagen: %s", e)
        return None
    except Exception as e:
        log.warning("Unerwarteter Status-Edit Fehler: %s", e)
        return None


async def post_status(guild: discord.Guild, embed: discord.Embed) -> Optional[discord.Message]:
    candidates = []
    if guild.system_channel:
        candidates.append(guild.system_channel)
    candidates.extend(guild.text_channels)
    for ch in candidates:
        try:
            perms = ch.permissions_for(guild.me)
            if perms.send_messages and perms.embed_links:
                return await ch.send(embed=embed)
        except Exception:
            continue
    return None


async def run_setup(guild: discord.Guild, status_msg: Optional[discord.Message], wipe: bool) -> None:
    try:
        if wipe:
            await safe_edit(status_msg, embed=discord.Embed(title="🧹  Lösche alte Struktur…", color=INFO_COLOR))
            await wipe_server(guild)
            status_msg = None  # alles weg

        status_msg = await safe_edit(
            status_msg, embed=discord.Embed(title="🎭  Erstelle Rollen…", color=INFO_COLOR)
        ) or status_msg
        await create_roles(guild)

        if status_msg is None:
            status_msg = await post_status(
                guild, discord.Embed(title="📁  Erstelle Kategorien & Kanäle…", color=INFO_COLOR),
            )
        else:
            status_msg = await safe_edit(
                status_msg, embed=discord.Embed(title="📁  Erstelle Kategorien & Kanäle…", color=INFO_COLOR),
            ) or status_msg

        await create_structure(guild)

        # Hierarchie nochmal erzwingen (falls neue Rollen entstanden sind)
        await enforce_role_hierarchy(guild)

        status_msg = await safe_edit(
            status_msg, embed=discord.Embed(title="💬  Befülle wichtige Kanäle…", color=INFO_COLOR),
        ) or status_msg
        await fill_channels(guild)

        done = discord.Embed(
            title="✅  Setup abgeschlossen!",
            description=(
                f"{LINE}\n"
                f"**{SERVER_NAME}** wurde komplett eingerichtet.\n\n"
                f"➤  🎭  Rollen:      **{len(ROLES)}**\n"
                f"➤  📁  Kategorien:  **{len(STRUCTURE)}**\n"
                f"➤  💬  Kanäle:      **{sum(len(c['channels']) for c in STRUCTURE)}**\n\n"
                f"⚠️  *Vergiss nicht, die **Bot-Rolle** ganz oben in der Rollen-Liste zu lassen!*\n"
                f"{LINE}"
            ),
            color=SUCCESS_COLOR,
        )
        if (await safe_edit(status_msg, embed=done)) is None:
            await post_status(guild, done)
    except Exception as e:
        log.exception("Setup-Fehler")
        err = discord.Embed(
            title="❌  Fehler beim Setup",
            description=f"```{type(e).__name__}: {e}```",
            color=ERROR_COLOR,
        )
        if (await safe_edit(status_msg, embed=err)) is None:
            await post_status(guild, err)


# --------------------------------------------------------------------------- #
# COMMANDS
# --------------------------------------------------------------------------- #
@bot.event
async def on_ready():
    log.info("Eingeloggt als %s (ID: %s)", bot.user, bot.user.id)
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(TicketCloseView())
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}start  •  {SERVER_NAME}"))


@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start_cmd(ctx: commands.Context):
    emb = discord.Embed(
        title=f"⚙️  {SERVER_NAME}  •  SETUP WIZARD",
        description=(
            f"{LINE}\n"
            f"### 💎  Willkommen zum Server-Setup!\n\n"
            f"Wähle eine der folgenden Optionen:\n\n"
            f"🛑  **Abbruch**\n"
            f"> Nichts tun, Wizard schließen.\n\n"
            f"➕  **Nur Hinzufügen**\n"
            f"> Fehlende Rollen & Kanäle ergänzen — Bestehendes bleibt.\n\n"
            f"♻️  **Komplett neu aufsetzen**\n"
            f"> **ALLES** löschen & sauber neu erstellen *(mit Sicherheitsfrage)*.\n"
            f"{LINE}\n"
            f"⚠️  *Stelle sicher: **Bot-Rolle ganz oben** + **Admin-Rechte**.*"
        ),
        color=BRAND_COLOR,
    )
    emb.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else FUSE_ICON)
    emb.set_image(url="https://singlecolorimage.com/get/E91E63/800x4.png")
    emb.set_footer(text=f"{SERVER_NAME}  •  Setup  •  nur Admins")
    await ctx.send(embed=emb, view=SetupView(ctx.author.id))


@start_cmd.error
async def start_err(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=discord.Embed(
            title="❌  Keine Berechtigung",
            description="Du brauchst **Administrator** für diesen Befehl.",
            color=ERROR_COLOR,
        ))


@bot.command(name="fix-hierarchie")
@commands.has_permissions(administrator=True)
async def fix_hierarchy(ctx):
    """Erzwingt die Rollen-Reihenfolge (Owner ganz oben)."""
    await enforce_role_hierarchy(ctx.guild)
    await ctx.send(embed=discord.Embed(
        title="✅  Hierarchie aktualisiert",
        description=f"{LINE}\nDie Rollen wurden in die richtige Reihenfolge gebracht.\n{LINE}",
        color=SUCCESS_COLOR,
    ))


@bot.command(name="resend-verify")
@commands.has_permissions(administrator=True)
async def resend_verify(ctx):
    emb = discord.Embed(
        title="🔐  VERIFIZIERUNG  •  FUSE | FS",
        description=f"{LINE}\nKlicke unten, um dich zu verifizieren.\n{LINE}",
        color=SUCCESS_COLOR,
    )
    await ctx.send(embed=emb, view=VerifyView())


# --------------------------------------------------------------------------- #
# EVENTS – WELCOME / LEAVE / LOGS
# --------------------------------------------------------------------------- #
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    unv = find_role(guild, KEY_ROLES["unverified"])
    if unv:
        try: await member.add_roles(unv, reason="Auto: Unverified")
        except Exception: pass

    wc = discord.utils.get(guild.text_channels, name="👋・willkommen")
    rules = discord.utils.get(guild.text_channels, name="📜・regelwerk")
    verify = discord.utils.get(guild.text_channels, name="✅・verify")
    if wc:
        emb = discord.Embed(
            title=f"🎉  WILLKOMMEN IN {SERVER_NAME.upper()}!",
            description=(
                f"{LINE}\n"
                f"Hey {member.mention}!  Willkommen bei **{SERVER_NAME}**! 💎\n"
                f"Du bist unser **{guild.member_count}. Member**.\n\n"
                f"📜  Lies dir die {rules.mention if rules else '#regelwerk'} durch.\n"
                f"✅  Verifiziere dich im {verify.mention if verify else '#verify'}.\n"
                f"🎮  Anschließend kannst du dich bewerben.\n\n"
                f"*Bitte halte dich an die Regeln und geh freundlich mit allen Mitgliedern um.*\n"
                f"{LINE}"
            ),
            color=BRAND_COLOR,
            timestamp=datetime.utcnow(),
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        emb.set_image(url="https://singlecolorimage.com/get/E91E63/800x4.png")
        emb.set_footer(text=f"User-ID: {member.id}  •  Account erstellt", icon_url=guild.icon.url if guild.icon else FUSE_ICON)
        await wc.send(content=member.mention, embed=emb)

    log_ch = get_log_channel(guild, "join")
    if log_ch:
        emb = discord.Embed(title="📥  Member Joined", color=SUCCESS_COLOR, timestamp=datetime.utcnow())
        emb.add_field(name="User", value=f"{member.mention} (`{member.id}`)", inline=False)
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
            title="👋  TSCHÜSS!",
            description=(
                f"{LINE}\n"
                f"**{member}** hat den Server verlassen.\n"
                f"Wir sind jetzt **{guild.member_count}** Member.\n"
                f"{LINE}"
            ),
            color=ERROR_COLOR, timestamp=datetime.utcnow(),
        )
        emb.set_thumbnail(url=member.display_avatar.url)
        await bye.send(embed=emb)
    log_ch = get_log_channel(guild, "leave")
    if log_ch:
        emb = discord.Embed(title="📤  Member Left", color=ERROR_COLOR, timestamp=datetime.utcnow())
        emb.add_field(name="User", value=f"{member} (`{member.id}`)")
        emb.set_thumbnail(url=member.display_avatar.url)
        await log_ch.send(embed=emb)


@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot or not message.guild: return
    log_ch = get_log_channel(message.guild, "message")
    if not log_ch: return
    emb = discord.Embed(title="🗑️  Nachricht gelöscht", color=ERROR_COLOR, timestamp=datetime.utcnow())
    emb.add_field(name="Autor", value=message.author.mention, inline=True)
    emb.add_field(name="Kanal", value=message.channel.mention, inline=True)
    emb.add_field(name="Inhalt", value=(message.content[:1000] or "*kein Text*"), inline=False)
    await log_ch.send(embed=emb)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot or not before.guild or before.content == after.content: return
    log_ch = get_log_channel(before.guild, "message")
    if not log_ch: return
    emb = discord.Embed(title="✏️  Nachricht bearbeitet", color=GOLD, timestamp=datetime.utcnow(), url=after.jump_url)
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
            txt, col = f"🎙️  **{member}** → **{after.channel.name}**", SUCCESS_COLOR
        elif before.channel and not after.channel:
            txt, col = f"🔇  **{member}** verließ **{before.channel.name}**", ERROR_COLOR
        else:
            txt, col = f"🔄  **{member}**: `{before.channel.name}` → `{after.channel.name}`", INFO_COLOR
        await log_ch.send(embed=discord.Embed(description=txt, color=col, timestamp=datetime.utcnow()))


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.roles == after.roles: return
    log_ch = get_log_channel(before.guild, "role")
    if not log_ch: return
    added   = [r for r in after.roles  if r not in before.roles]
    removed = [r for r in before.roles if r not in after.roles]
    emb = discord.Embed(title="🎭  Rollen geändert", color=INFO_COLOR, timestamp=datetime.utcnow())
    emb.add_field(name="User", value=after.mention, inline=False)
    if added:   emb.add_field(name="➕ Hinzugefügt", value=", ".join(r.mention for r in added), inline=False)
    if removed: emb.add_field(name="➖ Entfernt",    value=", ".join(r.mention for r in removed), inline=False)
    await log_ch.send(embed=emb)


@bot.event
async def on_guild_channel_create(channel):
    log_ch = get_log_channel(channel.guild, "channel")
    if log_ch:
        await log_ch.send(embed=discord.Embed(
            title="📁  Kanal erstellt",
            description=f"{channel.mention} (`{channel.name}`)",
            color=SUCCESS_COLOR, timestamp=datetime.utcnow(),
        ))


@bot.event
async def on_guild_channel_delete(channel):
    log_ch = get_log_channel(channel.guild, "channel")
    if log_ch:
        await log_ch.send(embed=discord.Embed(
            title="📁  Kanal gelöscht",
            description=f"`{channel.name}`",
            color=ERROR_COLOR, timestamp=datetime.utcnow(),
        ))


@bot.event
async def on_guild_role_create(role):
    log_ch = get_log_channel(role.guild, "server")
    if log_ch:
        await log_ch.send(embed=discord.Embed(
            title="🎭  Rolle erstellt",
            description=f"{role.mention} (`{role.name}`)",
            color=SUCCESS_COLOR, timestamp=datetime.utcnow(),
        ))


@bot.event
async def on_guild_role_delete(role):
    log_ch = get_log_channel(role.guild, "server")
    if log_ch:
        await log_ch.send(embed=discord.Embed(
            title="🎭  Rolle gelöscht",
            description=f"`{role.name}`",
            color=ERROR_COLOR, timestamp=datetime.utcnow(),
        ))


@bot.event
async def on_member_ban(guild, user):
    log_ch = get_log_channel(guild, "moderation")
    if log_ch:
        await log_ch.send(embed=discord.Embed(
            title="🔨  Member gebannt",
            description=f"**{user}** (`{user.id}`)",
            color=ERROR_COLOR, timestamp=datetime.utcnow(),
        ))


@bot.event
async def on_member_unban(guild, user):
    log_ch = get_log_channel(guild, "moderation")
    if log_ch:
        await log_ch.send(embed=discord.Embed(
            title="🕊️  Member entbannt",
            description=f"**{user}** (`{user.id}`)",
            color=SUCCESS_COLOR, timestamp=datetime.utcnow(),
        ))


# --------------------------------------------------------------------------- #
# START
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("❌  DISCORD_TOKEN fehlt! Setze ihn in den Railway-Variablen.")
    bot.run(TOKEN)
