"""
FUSE | FS — Discord Bot  •  v3 (Pro Edition)
============================================
Features
--------
• 52 Rollen, feste Hierarchie (Owner immer oben)  +  Auto-Enforcement
• Saubere Visibility-Stufen (Unverified / Verified / Member / Staff)
• Setup-Wizard mit 3 Buttons (!start)
• Welcome / Goodbye System mit Member-Counter
• Verify-System per Button
• 📋 BEWERBUNGS-SYSTEM
    - Modal mit 5 Fragen
    - Posting in #bewerbung-logs mit ✅ Annehmen / ❌ Ablehnen
    - Annehmen → Member-Rolle automatisch
    - Ablehnen → Ticket schließt + 30-Minuten-Cooldown (persistent JSON)
• 🎫 TICKET-SYSTEM (Multi-Kategorie via Select)
    - Allgemeine Frage
    - Problem / Bug
    - Player-Meldung (Modal: Wer / Was / Beweis)
    - Partnerschaft
    - Sonstiges
• 11 Log-Kanäle (alles wird mitgeschrieben)
• Einheitliche Embeds (Author, Footer, Color-Bar)
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import discord
from discord.ext import commands
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────────── #
# CONFIG
# ─────────────────────────────────────────────────────────────────── #
load_dotenv()
TOKEN       = os.getenv("DISCORD_TOKEN")
PREFIX      = os.getenv("PREFIX", "!")
SERVER_NAME = os.getenv("SERVER_NAME", "FUSE | FS")
DATA_FILE   = "data.json"
APPLY_COOLDOWN_MIN = 30  # Minuten Sperre nach Ablehnung

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("fuse")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ─────────────────────────────────────────────────────────────────── #
# BRANDING
# ─────────────────────────────────────────────────────────────────── #
BRAND_COLOR   = 0xE91E63
SUCCESS_COLOR = 0x2ECC71
ERROR_COLOR   = 0xE74C3C
INFO_COLOR    = 0x3498DB
GOLD          = 0xF1C40F
PURPLE        = 0x9B59B6

LINE = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

def color_bar(hex_color: int) -> str:
    """Generiert eine 800x4 px Color-Bar als Image-URL für Embeds."""
    return f"https://singlecolorimage.com/get/{hex_color:06X}/800x4.png"


# ─────────────────────────────────────────────────────────────────── #
# DATEN-PERSISTENZ (JSON)
# ─────────────────────────────────────────────────────────────────── #
def load_data() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"cooldowns": {}, "applications": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"cooldowns": {}, "applications": {}}

def save_data(d: dict) -> None:
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(d, f, indent=2)
    except Exception as e:
        log.warning("Save failed: %s", e)

DATA = load_data()

def get_cooldown(user_id: int) -> Optional[datetime]:
    raw = DATA.get("cooldowns", {}).get(str(user_id))
    if not raw: return None
    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return None

def set_cooldown(user_id: int, minutes: int) -> datetime:
    until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    DATA.setdefault("cooldowns", {})[str(user_id)] = until.isoformat()
    save_data(DATA)
    return until

def clear_cooldown(user_id: int) -> None:
    DATA.get("cooldowns", {}).pop(str(user_id), None)
    save_data(DATA)


# ─────────────────────────────────────────────────────────────────── #
# EINHEITLICHE EMBEDS
# ─────────────────────────────────────────────────────────────────── #
def fuse_embed(
    title: str = "",
    description: str = "",
    color: int = BRAND_COLOR,
    *,
    author: Optional[discord.abc.User] = None,
    author_name: Optional[str] = None,
    author_icon: Optional[str] = None,
    thumbnail: Optional[str] = None,
    footer: Optional[str] = None,
    footer_icon: Optional[str] = None,
    guild: Optional[discord.Guild] = None,
    color_strip: bool = True,
    timestamp: bool = True,
) -> discord.Embed:
    """
    Erstellt ein einheitliches FUSE-Embed:
    - Author (Server-Name oder User)
    - Optionales Thumbnail
    - Color-Bar als Image (unten)
    - Footer mit Brand
    """
    emb = discord.Embed(
        title=title or None,
        description=description or None,
        color=color,
        timestamp=datetime.utcnow() if timestamp else None,
    )

    # Author
    if author:
        emb.set_author(
            name=str(author),
            icon_url=author.display_avatar.url,
        )
    else:
        icon = author_icon or (guild.icon.url if (guild and guild.icon) else None)
        emb.set_author(name=author_name or SERVER_NAME, icon_url=icon)

    if thumbnail:
        emb.set_thumbnail(url=thumbnail)
    elif guild and guild.icon:
        emb.set_thumbnail(url=guild.icon.url)

    if color_strip:
        emb.set_image(url=color_bar(color))

    emb.set_footer(
        text=footer or f"{SERVER_NAME}  •  Roblox Roleplay Community",
        icon_url=footer_icon or (guild.icon.url if (guild and guild.icon) else None),
    )
    return emb


# ─────────────────────────────────────────────────────────────────── #
# ROLLEN
# ─────────────────────────────────────────────────────────────────── #
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

ROLES: list[dict] = [
    # ═══════════════════════════════════════════════
    # ▰▰▰▰▰▰▰▰▰▰  DIVIDER  ▰▰▰▰▰▰▰▰▰▰
    # ═══════════════════════════════════════════════
    {"name": "▰▰▰▰▰  LEITUNG  ▰▰▰▰▰",   "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "👑 Owner",                  "color": 0xFF0000, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "👑 Co-Owner",               "color": 0xFF1A1A, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "🛡️ Server-Manager",         "color": 0xFF4500, "hoist": True, "perms": ADMIN_PERMS},

    {"name": "▰▰▰▰▰  ADMIN-TEAM  ▰▰▰▰▰", "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "⚡ Head-Admin",              "color": 0xFF6600, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "⚡ Admin",                   "color": 0xFF8000, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "⚡ Vize-Admin",              "color": 0xFF9933, "hoist": True, "perms": MOD_PERMS},

    {"name": "▰▰▰▰▰  MODERATION  ▰▰▰▰▰", "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "🔨 Head-Moderator",         "color": 0xFFAA00, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Senior-Moderator",       "color": 0xFFC04D, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Moderator",              "color": 0xFFD580, "hoist": True, "perms": MOD_PERMS},
    {"name": "🔨 Trial-Moderator",        "color": 0xFFE0B3, "hoist": True, "perms": TRIAL_MOD_PERMS},

    {"name": "▰▰▰▰▰  SUPPORT  ▰▰▰▰▰",    "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "🎧 Support-Lead",           "color": 0x00CED1, "hoist": True, "perms": TRIAL_MOD_PERMS},
    {"name": "🎧 Supporter",              "color": 0x40E0D0, "hoist": True, "perms": TRIAL_MOD_PERMS},
    {"name": "🎧 Trial-Supporter",        "color": 0x7FFFD4, "hoist": True, "perms": MEMBER_PERMS},

    {"name": "▰▰▰▰▰  TEAM  ▰▰▰▰▰",       "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "💻 Developer",              "color": 0x9B59B6, "hoist": True, "perms": ADMIN_PERMS},
    {"name": "🤖 Bot-Manager",            "color": 0x8E44AD, "hoist": True, "perms": MOD_PERMS},
    {"name": "🎨 Designer",               "color": 0xE67E22, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎉 Event-Manager",          "color": 0xD35400, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "📝 Recruiter",              "color": 0x16A085, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🤝 Partner-Manager",        "color": 0x1ABC9C, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "📱 SocialMedia-Team",       "color": 0xE91E63, "hoist": True, "perms": MEMBER_PERMS},

    {"name": "▰▰▰▰▰  GANG-RÄNGE  ▰▰▰▰▰", "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "💎 Boss",                   "color": 0x800080, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Underboss",              "color": 0x8B008B, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Consigliere",            "color": 0x9932CC, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Capo",                   "color": 0xA020F0, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Soldato",                "color": 0xBA55D3, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🔫 Hitman",                 "color": 0x4B0082, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🔫 Enforcer",               "color": 0x483D8B, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💊 Dealer",                 "color": 0x2F4F4F, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🚚 Smuggler",               "color": 0x556B2F, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🏎️ Driver",                 "color": 0x6B8E23, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🔧 Mechanic",               "color": 0x808000, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🛡️ Bodyguard",              "color": 0x708090, "hoist": True, "perms": MEMBER_PERMS},

    {"name": "▰▰▰▰▰  MEMBER  ▰▰▰▰▰",     "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "🏆 Veteran",                "color": 0xFFD700, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "⭐ Elite",                   "color": 0xFFC125, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💠 Member+",                "color": 0x00BFFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💠 Member",                 "color": 0x1E90FF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🧪 Trial-Member",           "color": 0x87CEEB, "hoist": True, "perms": MEMBER_PERMS},

    {"name": "▰▰▰▰▰  CREATOR  ▰▰▰▰▰",    "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "🎬 YouTuber",               "color": 0xFF0000, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎮 Twitch-Streamer",        "color": 0x6441A5, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🎵 TikToker",               "color": 0x010101, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "🖌️ Content-Creator",        "color": 0xC71585, "hoist": True, "perms": MEMBER_PERMS},

    {"name": "▰▰▰▰▰  BOOSTS  ▰▰▰▰▰",     "color": 0x000001, "hoist": True, "perms": discord.Permissions.none(), "divider": True},
    {"name": "💖 Boost-King",             "color": 0xF47FFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💖 Booster",                "color": 0xF47FFF, "hoist": True, "perms": MEMBER_PERMS},
    {"name": "💎 Nitro",                  "color": 0xB9BBBE, "hoist": False, "perms": MEMBER_PERMS},

    {"name": "▰▰▰▰▰  SPEZIAL  ▰▰▰▰▰",    "color": 0x000001, "hoist": False, "perms": discord.Permissions.none(), "divider": True},
    {"name": "✅ Verified",               "color": 0x57F287, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🤝 Fuse",                   "color": 0xFF69B4, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "💕 Friend",                 "color": 0xFFB6C1, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🎶 DJ",                     "color": 0x1DB954, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "🎂 Geburtstagskind",        "color": 0xFF69B4, "hoist": False, "perms": MEMBER_PERMS},
    {"name": "📝 Bewerber",               "color": 0x95A5A6, "hoist": True, "perms": BASIC_PERMS},
    {"name": "👋 Gast",                   "color": 0xBDC3C7, "hoist": False, "perms": BASIC_PERMS},
    {"name": "😴 AFK",                    "color": 0x4F545C, "hoist": False, "perms": BASIC_PERMS},

    {"name": "▰▰▰▰▰  STRAFEN  ▰▰▰▰▰",    "color": 0x000001, "hoist": False, "perms": discord.Permissions.none(), "divider": True},
    {"name": "⚠️ Verwarnt",                "color": 0xE74C3C, "hoist": False, "perms": BASIC_PERMS},
    {"name": "🔇 Muted",                  "color": 0x36393F, "hoist": False, "perms": discord.Permissions.none()},
    {"name": "❌ Unverified",             "color": 0x99AAB5, "hoist": False, "perms": discord.Permissions.none()},
]

KEY_ROLES = {
    "owner": "👑 Owner", "member": "💠 Member", "verified": "✅ Verified",
    "bewerber": "📝 Bewerber", "muted": "🔇 Muted", "unverified": "❌ Unverified",
}

STAFF_ROLE_NAMES = [
    "👑 Owner", "👑 Co-Owner", "🛡️ Server-Manager",
    "⚡ Head-Admin", "⚡ Admin", "⚡ Vize-Admin",
    "🔨 Head-Moderator", "🔨 Senior-Moderator", "🔨 Moderator", "🔨 Trial-Moderator",
    "🎧 Support-Lead", "🎧 Supporter", "🎧 Trial-Supporter",
    "💻 Developer", "🤖 Bot-Manager",
]


# ─────────────────────────────────────────────────────────────────── #
# STRUKTUR
# ─────────────────────────────────────────────────────────────────── #
STRUCTURE: list[dict] = [
    {
        "category": "📩 ✘ WILLKOMMEN", "visibility": "lobby",
        "channels": [
            {"name": "👋・willkommen", "type": "text", "visibility": "lobby"},
            {"name": "📜・regelwerk",  "type": "text", "visibility": "lobby"},
            {"name": "✅・verify",     "type": "text", "visibility": "verify_only"},
            {"name": "👋・tschüss",    "type": "text", "visibility": "lobby"},
        ],
    },
    {
        "category": "🌐 ✘ BEWERBUNG", "visibility": "bewerbung",
        "channels": [
            {"name": "📋・bewerbung",      "type": "text", "visibility": "bewerbung"},
            {"name": "❓・bewerbungs-info", "type": "text", "visibility": "bewerbung"},
            {"name": "🎙️・warteraum",      "type": "voice", "visibility": "bewerbung"},
            {"name": "🚪・Einreise-1",     "type": "voice", "visibility": "bewerbung", "locked": True},
            {"name": "🚪・Einreise-2",     "type": "voice", "visibility": "bewerbung", "locked": True},
        ],
    },
    {
        "category": "🎫 ✘ SUPPORT", "visibility": "member",
        "channels": [
            {"name": "🎫・ticket-öffnen", "type": "text", "visibility": "member"},
            {"name": "📖・ticket-info",   "type": "text", "visibility": "member"},
        ],
    },
    {
        "category": "🎀 ✘ INFOS", "visibility": "member",
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
        "category": "💬 ✘ COMMUNITY", "visibility": "member",
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
        "category": "📱 ✘ SOCIALMEDIA", "visibility": "member",
        "channels": [
            {"name": "💖・cani",        "type": "text"},
            {"name": "📱・socialmedia", "type": "text"},
            {"name": "📸・instagram",   "type": "text"},
            {"name": "🎵・tiktok",      "type": "text"},
            {"name": "🎬・youtube",     "type": "text"},
        ],
    },
    {
        "category": "📞 ✘ TALKS", "visibility": "member",
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
        "category": "🧱 ✘ FUSE MERCH", "visibility": "member",
        "channels": [
            {"name": "🦺・weste",   "type": "text"},
            {"name": "📿・armband", "type": "text"},
            {"name": "👕・merch",   "type": "text"},
            {"name": "👕・trikot",  "type": "text"},
            {"name": "👕・polo",    "type": "text"},
        ],
    },
    {
        "category": "📓 ✘ GANG INFOS", "visibility": "member",
        "channels": [
            {"name": "💗・farbe",         "type": "text"},
            {"name": "🎨・rollensystem",  "type": "text"},
            {"name": "🎮・roblox-gruppe", "type": "text"},
            {"name": "🏠・anwesen",       "type": "text"},
            {"name": "🛡️・partnerschaft", "type": "text"},
        ],
    },
    {
        "category": "🔒 ✘ LOUNGES", "visibility": "member",
        "channels": [
            {"name": "🎀・LOUNGE-400-RBX", "type": "voice", "locked": True},
            {"name": "♟️・Nils-Luke",       "type": "voice", "locked": True},
            {"name": "💎・M-J-S-F",         "type": "voice", "locked": True},
            {"name": "💬・lounge-chat",     "type": "text",  "locked": True},
            {"name": "🍺・Bier-Keller",     "type": "voice", "locked": True},
        ],
    },
    {
        "category": "🏢 ✘ BÜROS", "visibility": "staff",
        "channels": [
            {"name": "👑・Owner-Büro",   "type": "voice", "visibility": "owner_only"},
            {"name": "⚡・Admin-Büro",    "type": "voice", "visibility": "staff"},
            {"name": "🔨・Mod-Büro",      "type": "voice", "visibility": "staff"},
            {"name": "🎧・Support-Büro",  "type": "voice", "visibility": "staff"},
            {"name": "📊・Meeting-Raum",  "type": "voice", "visibility": "staff"},
        ],
    },
    {
        "category": "🛡️ ✘ ADMIN", "visibility": "staff",
        "channels": [
            {"name": "👑・owner-chat",      "type": "text", "visibility": "owner_only"},
            {"name": "⚡・admin-chat",       "type": "text", "visibility": "staff"},
            {"name": "🔨・mod-chat",         "type": "text", "visibility": "staff"},
            {"name": "🎧・support-chat",     "type": "text", "visibility": "staff"},
            {"name": "📋・team-ankündigung", "type": "text", "visibility": "staff"},
            {"name": "📝・team-todo",        "type": "text", "visibility": "staff"},
            {"name": "🚨・report-eingang",   "type": "text", "visibility": "staff"},
            {"name": "📨・bewerbung-logs",   "type": "text", "visibility": "staff"},
        ],
    },
    {
        "category": "📋 ✘ LOGS", "visibility": "staff",
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


# ─────────────────────────────────────────────────────────────────── #
# UTILS
# ─────────────────────────────────────────────────────────────────── #
def find_role(g: discord.Guild, name: str) -> Optional[discord.Role]:
    return discord.utils.get(g.roles, name=name)

def find_category(g: discord.Guild, name: str) -> Optional[discord.CategoryChannel]:
    return discord.utils.get(g.categories, name=name)

def find_channel(g: discord.Guild, name: str) -> Optional[discord.abc.GuildChannel]:
    return discord.utils.get(g.channels, name=name)

def get_log_channel(g: discord.Guild, log_type: str) -> Optional[discord.TextChannel]:
    suffix_map = {
        "join": "join-logs", "leave": "leave-logs", "verify": "verify-logs",
        "message": "message-logs", "voice": "voice-logs", "role": "role-logs",
        "channel": "channel-logs", "server": "server-logs", "ticket": "ticket-logs",
        "moderation": "moderation-logs", "bot": "bot-logs",
        "application": "bewerbung-logs",
    }
    suffix = suffix_map.get(log_type)
    if not suffix: return None
    for ch in g.text_channels:
        if ch.name.endswith(suffix):
            return ch
    return None


def build_overwrites(g: discord.Guild, visibility: str, locked: bool = False) -> dict:
    everyone   = g.default_role
    unverified = find_role(g, KEY_ROLES["unverified"])
    verified   = find_role(g, KEY_ROLES["verified"])
    member     = find_role(g, KEY_ROLES["member"])
    bewerber   = find_role(g, KEY_ROLES["bewerber"])
    muted      = find_role(g, KEY_ROLES["muted"])

    ow: dict = {everyone: discord.PermissionOverwrite(view_channel=False, send_messages=False, connect=False)}

    if visibility == "lobby":
        ow[everyone] = discord.PermissionOverwrite(
            view_channel=True, read_message_history=True,
            send_messages=False, add_reactions=False, connect=False,
        )
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=True, send_messages=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=True, send_messages=True)

    elif visibility == "verify_only":
        if unverified:
            ow[unverified] = discord.PermissionOverwrite(view_channel=True, read_message_history=True,
                                                         send_messages=False, add_reactions=True)
        if verified: ow[verified] = discord.PermissionOverwrite(view_channel=False)
        if member:   ow[member]   = discord.PermissionOverwrite(view_channel=False)

    elif visibility == "bewerbung":
        if verified:
            ow[verified] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                       connect=True, speak=True, read_message_history=True)
        if bewerber:
            ow[bewerber] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                       connect=True, speak=True)
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=False)

    elif visibility == "member":
        if member:
            ow[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                     connect=True, speak=True, stream=True,
                                                     read_message_history=True, add_reactions=True,
                                                     embed_links=True, attach_files=True)
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=False)

    elif visibility in ("staff", "owner_only"):
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=False)
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=False)

    # Staff sieht alles (außer owner_only)
    if visibility != "owner_only":
        for rn in STAFF_ROLE_NAMES:
            r = find_role(g, rn)
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                    connect=True, speak=True, read_message_history=True,
                                                    manage_messages=True)
    else:
        for rn in ("👑 Owner", "👑 Co-Owner"):
            r = find_role(g, rn)
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                    connect=True, speak=True, read_message_history=True,
                                                    manage_messages=True)

    if locked:
        if member:     ow[member]     = discord.PermissionOverwrite(view_channel=False)
        if verified:   ow[verified]   = discord.PermissionOverwrite(view_channel=False)
        if unverified: ow[unverified] = discord.PermissionOverwrite(view_channel=False)
        for rn in ("💖 Booster", "💖 Boost-King"):
            r = find_role(g, rn)
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                    connect=True, speak=True)

    if muted:
        ow[muted] = discord.PermissionOverwrite(send_messages=False, speak=False, add_reactions=False,
                                                stream=False, send_messages_in_threads=False)
    return ow


# ─────────────────────────────────────────────────────────────────── #
# SETUP-FUNKTIONEN
# ─────────────────────────────────────────────────────────────────── #
def _sanitize_perms(g: discord.Guild, perms: discord.Permissions) -> discord.Permissions:
    """Beschneidet Permissions auf das, was der Bot selbst hat."""
    return discord.Permissions(perms.value & g.me.guild_permissions.value)


async def _safe(coro_factory, *, label: str = "", retries: int = 4):
    """
    Wrapper mit Retry. Discord.py hat schon einen internen Rate-Limiter,
    wir brauchen nur Retries für transient errors. KEINE manuellen Sleeps.
    """
    for attempt in range(1, retries + 1):
        try:
            return await coro_factory()
        except discord.HTTPException as e:
            if e.status == 429:
                wait = float(getattr(e, "retry_after", 0) or 3)
                log.warning("[%s] 429 – warte %.1fs", label, wait)
                await asyncio.sleep(min(wait + 0.3, 30))
                continue
            if e.code == 50013:
                log.warning("[%s] Missing Permissions", label)
                return None
            if 500 <= (e.status or 0) < 600 and attempt < retries:
                await asyncio.sleep(1)
                continue
            log.warning("[%s] HTTP %s: %s", label, e.status, e)
            return None
        except Exception as e:
            log.warning("[%s] %s", label, e)
            return None
    return None


async def create_roles(g: discord.Guild) -> None:
    """
    Erstellt Rollen SEQUENTIELL ohne manuelle Sleeps.
    discord.py's interner Rate-Limiter sorgt automatisch für korrekte Pausen.
    Sequentiell ist hier deutlich zuverlässiger als parallel — Discord
    bevorzugt einen Bucket-Strom statt 5 gleichzeitige Anfragen.
    """
    bot_has_admin = g.me.guild_permissions.administrator
    to_create = [r for r in reversed(ROLES) if not find_role(g, r["name"])]
    total = len(to_create)
    log.info("Erstelle %d Rollen (Bot-Admin: %s)", total, bot_has_admin)

    if not to_create:
        await enforce_role_hierarchy(g)
        return

    created = 0
    for idx, role_def in enumerate(to_create, start=1):
        name = role_def["name"]
        perms = role_def["perms"] if bot_has_admin else _sanitize_perms(g, role_def["perms"])
        r = await _safe(
            lambda: g.create_role(
                name=name,
                color=discord.Color(role_def["color"]),
                hoist=role_def["hoist"],
                permissions=perms,
                mentionable=False,
                reason="FUSE Setup",
            ),
            label=f"role {name}",
        )
        if r is not None:
            created += 1
            log.info("  ✓ (%d/%d) %s", idx, total, name)
        else:
            log.warning("  ✗ (%d/%d) %s", idx, total, name)

    log.info("Rollen fertig: %d/%d", created, total)
    await enforce_role_hierarchy(g)


async def enforce_role_hierarchy(g: discord.Guild) -> None:
    try:
        bot_top = g.me.top_role
        positions = {}
        base = bot_top.position - 1
        for i, role_def in enumerate(ROLES):
            r = find_role(g, role_def["name"])
            if r and r < bot_top and not r.managed:
                positions[r] = max(1, base - i)
        if positions:
            await _safe(
                lambda: g.edit_role_positions(positions=positions, reason="FUSE Hierarchie"),
                label="role_positions",
            )
            log.info("Hierarchie OK (%d)", len(positions))
    except Exception as e:
        log.warning("Hierarchie nicht setzbar: %s", e)


async def create_structure(g: discord.Guild) -> None:
    """Sequentiell — Kategorien zuerst, dann ihre Kanäle. Kein manuelles Sleep."""
    total_chs = sum(len(c["channels"]) for c in STRUCTURE)
    log.info("Erstelle %d Kategorien + %d Kanäle", len(STRUCTURE), total_chs)

    ch_done = 0
    for cat_def in STRUCTURE:
        cat_name = cat_def["category"]
        cat_vis  = cat_def["visibility"]
        cat_ow   = build_overwrites(g, cat_vis)
        category = find_category(g, cat_name)

        if not category:
            category = await _safe(
                lambda: g.create_category(cat_name, overwrites=cat_ow, reason="FUSE Setup"),
                label=f"cat {cat_name}",
            )
            if category is None:
                log.warning("Kategorie übersprungen: %s", cat_name)
                continue
        else:
            await _safe(lambda: category.edit(overwrites=cat_ow), label=f"edit_cat {cat_name}")

        for ch_def in cat_def["channels"]:
            ch_done += 1
            ch_name = ch_def["name"]
            ctype   = ch_def.get("type", "text")
            ch_vis  = ch_def.get("visibility", cat_vis)
            locked  = ch_def.get("locked", False)

            existing = find_channel(g, ch_name)
            if existing:
                await _safe(
                    lambda: existing.edit(overwrites=build_overwrites(g, ch_vis, locked=locked)),
                    label=f"edit ch {ch_name}",
                )
                continue

            chan_ow = build_overwrites(g, ch_vis, locked=locked)
            if ctype == "text":
                factory = lambda: g.create_text_channel(ch_name, category=category, overwrites=chan_ow, reason="FUSE Setup")
            elif ctype == "voice":
                factory = lambda: g.create_voice_channel(ch_name, category=category, overwrites=chan_ow, reason="FUSE Setup")
            elif ctype == "stage":
                if "COMMUNITY" in g.features:
                    factory = lambda: g.create_stage_channel(ch_name, category=category, overwrites=chan_ow, reason="FUSE Setup")
                else:
                    factory = lambda: g.create_voice_channel(ch_name, category=category, overwrites=chan_ow, reason="FUSE Setup")
            else:
                continue

            r = await _safe(factory, label=f"ch {ch_name}")
            if r is not None:
                log.info("  ✓ (%d/%d) %s", ch_done, total_chs, ch_name)

    log.info("Struktur fertig.")


async def wipe_server(g: discord.Guild) -> None:
    """Sequentiell. discord.py rate-limited automatisch."""
    log.info("Wipe: %d Kanäle, %d Rollen", len(g.channels), len(g.roles))
    for ch in list(g.channels):
        await _safe(lambda: ch.delete(reason="FUSE Reset"), label=f"del ch {ch.name}")
    for r in list(g.roles):
        if r.is_default() or r.managed or r >= g.me.top_role:
            continue
        await _safe(lambda: r.delete(reason="FUSE Reset"), label=f"del role {r.name}")
    log.info("Wipe abgeschlossen.")


# ─────────────────────────────────────────────────────────────────── #
# KANAL-INHALTE
# ─────────────────────────────────────────────────────────────────── #
async def fill_channels(g: discord.Guild) -> None:
    # ── Regelwerk ───────────────────────────────────────────────
    rules_ch = discord.utils.get(g.text_channels, name="📜・regelwerk")
    if rules_ch and not [m async for m in rules_ch.history(limit=1)]:
        emb = fuse_embed(
            title=f"📜  REGELWERK  •  {SERVER_NAME}",
            description=(
                f"### Willkommen in unserer Familie 💎\n"
                f"Bitte lies dir die folgenden Regeln **sorgfältig** durch.\n"
                f"Mit dem **Verify** akzeptierst du sie automatisch.\n\n"
                f"*Dieser Server ist ausschließlich für **Roblox-Roleplay** — "
                f"nichts davon hat einen Real-Life-Bezug.*"
            ),
            color=BRAND_COLOR, guild=g,
        )
        rules = [
            ("🤝", "§1  Respekt",        "Behandle jedes Mitglied freundlich. Keine Beleidigungen, kein Mobbing, kein Rassismus."),
            ("🔇", "§2  Kein Spam",      "Kein Spammen von Nachrichten, Pings, Emojis oder Reaktionen."),
            ("📢", "§3  Keine Werbung",  "Werbung jeglicher Art ist **ohne Erlaubnis verboten**."),
            ("🔞", "§4  NSFW",           "NSFW-, Gore- oder anstößige Inhalte sind **strikt untersagt**."),
            ("📜", "§5  Discord-ToS",    "Die [Discord Richtlinien](https://discord.com/terms) gelten jederzeit."),
            ("💬", "§6  Channel-Themen", "Halte dich an die Themen der Kanäle. Off-Topic gehört in den Chat."),
            ("🎭", "§7  Roleplay",       "In RP-Kanälen wird **im Charakter** geschrieben. Kein OOC."),
            ("🛡️", "§8  Team",            "Anweisungen des Teams sind ohne Diskussion zu befolgen."),
            ("🐛", "§9  Bugs",           "Bekannte Bugs melden — **niemals** ausnutzen."),
            ("🔐", "§10 Account",        "Teile keine Accountdaten. Phishing = sofortiger Bann."),
            ("🎮", "§11 Roblox-Only",    "Dieser Server ist ausschließlich Roblox-Roleplay."),
            ("⚖️", "§12 Strafen",         "Verstöße = Verwarnung, Mute, Kick oder Bann."),
        ]
        for emoji, name, desc in rules:
            emb.add_field(name=f"{emoji}  {name}", value=f"> {desc}", inline=False)
        await rules_ch.send(embed=emb)

    # ── Verify ──────────────────────────────────────────────────
    verify_ch = discord.utils.get(g.text_channels, name="✅・verify")
    if verify_ch and not [m async for m in verify_ch.history(limit=1)]:
        emb = fuse_embed(
            title="🔐  VERIFIZIERUNG",
            description=(
                f"### 👋  Willkommen bei **{SERVER_NAME}**!\n\n"
                f"Bevor du den vollen Server erkunden kannst, musst du dich kurz verifizieren.\n"
                f"Damit bestätigst du, dass du das <#📜・regelwerk> gelesen hast.\n\n"
                f"**🔽  So funktioniert's:**\n"
                f"`1.` Klicke unten auf **✅  Verifizieren**\n"
                f"`2.` Du erhältst sofort Zugriff auf den **Bewerbungs-Bereich**\n"
                f"`3.` Sende deine Bewerbung ab und warte auf das Team\n"
                f"`4.` Nach Annahme bist du **Member** und siehst alles 🎉"
            ),
            color=SUCCESS_COLOR, guild=g,
        )
        await verify_ch.send(embed=emb, view=VerifyView())

    # ── Willkommen-Info ────────────────────────────────────────
    welcome_ch = discord.utils.get(g.text_channels, name="👋・willkommen")
    if welcome_ch and not [m async for m in welcome_ch.history(limit=1)]:
        emb = fuse_embed(
            title=f"🎉  WILLKOMMEN AUF {SERVER_NAME.upper()}",
            description=(
                f"### 💎  Roblox  ✘  Roleplay  ✘  Crime-Gang\n\n"
                f"Schön dass du den Weg zu uns gefunden hast!\n"
                f"Wir sind eine **aktive Community** rund um Roblox-Roleplay & Notruf Hamburg.\n\n"
                f"**📌  Was du tun musst:**\n"
                f"➤  Lies dir das <#📜・regelwerk> durch\n"
                f"➤  Verifiziere dich im <#✅・verify>\n"
                f"➤  Sende deine Bewerbung im <#📋・bewerbung>\n"
                f"➤  Werde **Member** & erlebe die volle Community"
            ),
            color=BRAND_COLOR, guild=g,
        )
        await welcome_ch.send(embed=emb)

    # ── Bewerbungs-Info ────────────────────────────────────────
    binfo_ch = discord.utils.get(g.text_channels, name="❓・bewerbungs-info")
    if binfo_ch and not [m async for m in binfo_ch.history(limit=1)]:
        emb = fuse_embed(
            title="📖  BEWERBUNGS-INFOS",
            description="### So läuft deine Bewerbung ab:",
            color=INFO_COLOR, guild=g,
        )
        emb.add_field(
            name="📝  Schritt 1  —  Formular",
            value=("> Gehe in den Kanal <#📋・bewerbung> und klicke\n"
                   "> auf **📋  Bewerbung starten**."),
            inline=False,
        )
        emb.add_field(
            name="⏳  Schritt 2  —  Warten",
            value=("> Das Team prüft deine Bewerbung — meist innerhalb\n"
                   "> von **24 – 48 Stunden**."),
            inline=False,
        )
        emb.add_field(
            name="✅  Schritt 3  —  Annahme",
            value=("> Wirst du angenommen, bekommst du automatisch die\n"
                   "> **💠 Member**-Rolle und vollen Zugriff."),
            inline=False,
        )
        emb.add_field(
            name="❌  Schritt 4  —  Ablehnung",
            value=("> Bei Ablehnung gibt es eine **30 Min Sperre**\n"
                   f"> bevor du eine neue Bewerbung senden kannst."),
            inline=False,
        )
        await binfo_ch.send(embed=emb)

    # ── Bewerbung (Button) ─────────────────────────────────────
    bewerb_ch = discord.utils.get(g.text_channels, name="📋・bewerbung")
    if bewerb_ch and not [m async for m in bewerb_ch.history(limit=1)]:
        emb = fuse_embed(
            title="📋  BEWERBUNG  •  FUSE | FS",
            description=(
                f"### 🎯  Du möchtest **Member** werden?\n\n"
                f"Klicke unten auf **📋  Bewerbung starten** — es öffnet sich ein Formular.\n"
                f"Beantworte alle Fragen ehrlich und ausführlich.\n\n"
                f"**📌  Wichtig:**\n"
                f"➤  Pro Bewerbung **1 Versuch**\n"
                f"➤  Bei Ablehnung **30 Min** Sperre\n"
                f"➤  Bei Annahme: sofort **Member** 🎉"
            ),
            color=BRAND_COLOR, guild=g,
        )
        await bewerb_ch.send(embed=emb, view=ApplyView())

    # ── Ticket-Info ────────────────────────────────────────────
    tinfo_ch = discord.utils.get(g.text_channels, name="📖・ticket-info")
    if tinfo_ch and not [m async for m in tinfo_ch.history(limit=1)]:
        emb = fuse_embed(
            title="📖  TICKET-SYSTEM  •  INFOS",
            description="### Wofür kannst du ein Ticket öffnen?",
            color=GOLD, guild=g,
        )
        emb.add_field(name="❓  Allgemeine Frage", value="> Du hast eine Frage rund um den Server.", inline=False)
        emb.add_field(name="🐛  Problem / Bug",    value="> Etwas funktioniert nicht oder ist kaputt.", inline=False)
        emb.add_field(name="🚨  Player-Meldung",   value="> Ein anderer Spieler verstößt gegen Regeln.", inline=False)
        emb.add_field(name="🤝  Partnerschaft",    value="> Du möchtest eine Partnerschaft anfragen.", inline=False)
        emb.add_field(name="💎  Sonstiges",        value="> Anliegen, die nicht in andere Kategorien passen.", inline=False)
        await tinfo_ch.send(embed=emb)

    # ── Ticket öffnen (Select) ─────────────────────────────────
    ticket_ch = discord.utils.get(g.text_channels, name="🎫・ticket-öffnen")
    if ticket_ch and not [m async for m in ticket_ch.history(limit=1)]:
        emb = fuse_embed(
            title="🎫  TICKET ERÖFFNEN",
            description=(
                f"### 💬  Brauchst du Hilfe?\n\n"
                f"Wähle unten eine **Kategorie** aus dem Menü.\n"
                f"Es wird ein privater Kanal für dich und das Team erstellt.\n\n"
                f"⚠️  *Missbrauch des Ticket-Systems wird sanktioniert.*"
            ),
            color=GOLD, guild=g,
        )
        await ticket_ch.send(embed=emb, view=TicketCategoryView())

    # ── Ankündigung / Boosts / Chat / Partnerschaft / Owner / Admin
    for ch_name, title, desc, color in [
        ("🔔・ankündigung",
            "🔔  ANKÜNDIGUNGEN",
            "### 📣  Hier postet das Team alle wichtigen News.\n\n"
            "➤  Updates & Patches\n➤  Events & Meetings\n➤  Regel-Änderungen",
            BRAND_COLOR),
        ("🚀・boosts",
            "🚀  SERVER BOOSTS",
            f"### 💖  Danke an alle Booster!\n\n"
            f"Mit einem Boost unterstützt du **{SERVER_NAME}** und bekommst:\n"
            f"➤  💖  Booster-Rolle\n➤  🔒  Locked-Lounges\n➤  🎨  Eigene Farbe",
            0xF47FFF),
        ("💬・chat",
            "💬  COMMUNITY-CHAT",
            "Hier kannst du **frei mit anderen Membern quatschen**.\nHalte dich an die Regeln und hab Spaß!",
            BRAND_COLOR),
        ("🛡️・partnerschaft",
            "🤝  PARTNERSCHAFT",
            "### 📑  Anforderungen\n"
            "➤  **min. 50 Member**\n➤  aktive Community\n➤  keine NSFW / Toxic Server\n\n"
            "### 📨  Interesse?\nÖffne ein Ticket und wähle 'Partnerschaft'.",
            0x1ABC9C),
        ("👑・owner-chat",
            "👑  OWNER-CHAT",
            "Privater Kanal **ausschließlich** für Owner & Co-Owner.",
            0xFF0000),
        ("⚡・admin-chat",
            "⚡  ADMIN-CHAT",
            "Privater Kanal für das **Admin-Team**.",
            0xFF8000),
    ]:
        ch = discord.utils.get(g.text_channels, name=ch_name)
        if ch and not [m async for m in ch.history(limit=1)]:
            await ch.send(embed=fuse_embed(title=title, description=desc, color=color, guild=g))


# ─────────────────────────────────────────────────────────────────── #
# VIEWS — SETUP
# ─────────────────────────────────────────────────────────────────── #
class SetupView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=180)
        self.author_id = author_id

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌  Nur der Befehls-Autor.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Abbruch", style=discord.ButtonStyle.danger, emoji="🛑")
    async def cancel(self, interaction, button):
        await interaction.response.edit_message(
            embed=fuse_embed("🛑  Setup abgebrochen", "Keine Änderungen vorgenommen.", ERROR_COLOR, guild=interaction.guild),
            view=None,
        )

    @discord.ui.button(label="Nur Hinzufügen", style=discord.ButtonStyle.primary, emoji="➕")
    async def only_add(self, interaction, button):
        await interaction.response.edit_message(
            embed=fuse_embed("⏳  Setup läuft…", "Fehlende Rollen & Kanäle werden ergänzt.", INFO_COLOR, guild=interaction.guild),
            view=None,
        )
        msg = await interaction.original_response()
        await run_setup(interaction.guild, msg, wipe=False)

    @discord.ui.button(label="Komplett neu aufsetzen", style=discord.ButtonStyle.success, emoji="♻️")
    async def fresh(self, interaction, button):
        await interaction.response.edit_message(
            embed=fuse_embed(
                "⚠️  Wirklich KOMPLETT neu aufsetzen?",
                "**ALLE Kanäle und Rollen werden gelöscht!**\nDieser Vorgang ist **NICHT** rückgängig zu machen.",
                ERROR_COLOR, guild=interaction.guild,
            ),
            view=ConfirmWipeView(self.author_id),
        )


class ConfirmWipeView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id

    async def interaction_check(self, interaction):
        return interaction.user.id == self.author_id

    @discord.ui.button(label="Ja, alles löschen", style=discord.ButtonStyle.danger, emoji="♻️")
    async def yes(self, interaction, button):
        await interaction.response.edit_message(
            embed=fuse_embed("⏳  Server wird zurückgesetzt…",
                             "Alle Kanäle & Rollen werden gelöscht und neu aufgebaut.",
                             INFO_COLOR, guild=interaction.guild),
            view=None,
        )
        msg = await interaction.original_response()
        await run_setup(interaction.guild, msg, wipe=True)

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def no(self, interaction, button):
        await interaction.response.edit_message(
            embed=fuse_embed("🛑  Abgebrochen", "Es wurde nichts geändert.", ERROR_COLOR, guild=interaction.guild),
            view=None,
        )


# ─────────────────────────────────────────────────────────────────── #
# VIEWS — VERIFY
# ─────────────────────────────────────────────────────────────────── #
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verifizieren", style=discord.ButtonStyle.success, emoji="✅", custom_id="fuse_verify_btn")
    async def verify(self, interaction, button):
        g, m = interaction.guild, interaction.user
        unv = find_role(g, KEY_ROLES["unverified"])
        ver = find_role(g, KEY_ROLES["verified"])
        bew = find_role(g, KEY_ROLES["bewerber"])
        if ver and ver in m.roles:
            return await interaction.response.send_message("✅  Du bist bereits verifiziert!", ephemeral=True)
        try:
            if unv and unv in m.roles: await m.remove_roles(unv, reason="Verify")
            if ver:                    await m.add_roles(ver, reason="Verify")
            if bew:                    await m.add_roles(bew, reason="Verify -> Bewerber")
            emb = fuse_embed(
                "🎉  Verifizierung erfolgreich!",
                f"Willkommen, {m.mention}!\n\n"
                "Du hast nun Zugriff auf den **Bewerbungs-Bereich**.\n"
                "Gehe in <#📋・bewerbung> und klicke auf **📋  Bewerbung starten**.",
                SUCCESS_COLOR, guild=g, author=m,
            )
            await interaction.response.send_message(embed=emb, ephemeral=True)
            log_ch = get_log_channel(g, "verify")
            if log_ch:
                await log_ch.send(embed=fuse_embed(
                    "✅  User verifiziert",
                    f"{m.mention} (`{m.id}`)",
                    SUCCESS_COLOR, author=m, guild=g,
                ))
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌  Mir fehlen die Rechte! Schiebe die Bot-Rolle ganz nach oben.", ephemeral=True,
            )


# ─────────────────────────────────────────────────────────────────── #
# VIEWS / MODAL — BEWERBUNG
# ─────────────────────────────────────────────────────────────────── #
class ApplicationModal(discord.ui.Modal, title="📋 FUSE | FS — Bewerbung"):
    roblox_name = discord.ui.TextInput(
        label="Roblox-Name & Alter",
        placeholder="z.B. JustVexo • 15 Jahre",
        max_length=80, required=True,
    )
    experience = discord.ui.TextInput(
        label="Wie lange spielst du Roblox-RP?",
        placeholder="z.B. 2 Jahre Notruf Hamburg, ...",
        max_length=200, required=True,
    )
    why_fuse = discord.ui.TextInput(
        label="Warum möchtest du zu FUSE?",
        style=discord.TextStyle.paragraph,
        placeholder="Erkläre, warum gerade FUSE...",
        max_length=600, required=True,
    )
    offer = discord.ui.TextInput(
        label="Was bietest du der Gang?",
        style=discord.TextStyle.paragraph,
        placeholder="Skills, Aktivität, Persönlichkeit, ...",
        max_length=600, required=True,
    )
    activity = discord.ui.TextInput(
        label="Aktivität (Std./Woche) + Mikrofon?",
        placeholder="z.B. ~15 Std/Woche, Mikrofon: Ja",
        max_length=100, required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        g, m = interaction.guild, interaction.user
        log_ch = get_log_channel(g, "application")
        if not log_ch:
            return await interaction.response.send_message(
                "❌  Bewerbungs-Log-Kanal nicht gefunden. Bitte Admin informieren.", ephemeral=True,
            )

        emb = fuse_embed(
            title="📨  NEUE BEWERBUNG EINGEGANGEN",
            description=f"Eine neue Bewerbung von {m.mention} liegt zur Prüfung bereit.",
            color=INFO_COLOR, guild=g, author=m,
        )
        emb.add_field(name="👤  Roblox-Name & Alter",  value=f"```{self.roblox_name.value}```", inline=False)
        emb.add_field(name="🎮  RP-Erfahrung",          value=f"```{self.experience.value}```", inline=False)
        emb.add_field(name="💡  Warum FUSE?",            value=f"```{self.why_fuse.value}```", inline=False)
        emb.add_field(name="🎯  Was bietest du uns?",   value=f"```{self.offer.value}```", inline=False)
        emb.add_field(name="⏱️  Aktivität & Mikrofon",   value=f"```{self.activity.value}```", inline=False)
        emb.add_field(name="🆔  User-ID",                value=f"`{m.id}`", inline=True)
        emb.add_field(name="📅  Account erstellt",       value=f"<t:{int(m.created_at.timestamp())}:R>", inline=True)
        # ID auch im Footer speichern (für persistente Buttons nach Bot-Restart)
        emb.set_footer(text=f"Bewerber-ID: {m.id}  •  {SERVER_NAME}",
                       icon_url=g.icon.url if g.icon else None)

        view = ApplicationDecisionView()
        await log_ch.send(content=f"📨  Neue Bewerbung von {m.mention}", embed=emb, view=view)

        # Bestätigung an User
        await interaction.response.send_message(
            embed=fuse_embed(
                title="✅  Bewerbung erfolgreich abgeschickt!",
                description=(
                    "Deine Bewerbung wurde an das Team weitergeleitet.\n\n"
                    "**⏱️  Bearbeitungszeit:** in der Regel **24 – 48 Stunden**.\n"
                    "Du bekommst hier eine Benachrichtigung sobald entschieden wurde."
                ),
                color=SUCCESS_COLOR, guild=g, author=m,
            ),
            ephemeral=True,
        )


class ApplyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Bewerbung starten", style=discord.ButtonStyle.success, emoji="📋", custom_id="fuse_apply_btn")
    async def apply(self, interaction, button):
        g, m = interaction.guild, interaction.user
        # Check: schon Member?
        member_role = find_role(g, KEY_ROLES["member"])
        if member_role and member_role in m.roles:
            return await interaction.response.send_message("✅  Du bist bereits Member!", ephemeral=True)
        # Check: verifiziert?
        ver = find_role(g, KEY_ROLES["verified"])
        if ver and ver not in m.roles:
            return await interaction.response.send_message(
                "❌  Du musst dich zuerst verifizieren (<#✅・verify>).", ephemeral=True,
            )
        # Check: Cooldown?
        cd = get_cooldown(m.id)
        if cd and cd > datetime.now(timezone.utc):
            return await interaction.response.send_message(
                embed=fuse_embed(
                    title="⏳  Du bist gesperrt",
                    description=(
                        f"Deine letzte Bewerbung wurde abgelehnt.\n\n"
                        f"**Du kannst dich erneut bewerben:** <t:{int(cd.timestamp())}:R>\n"
                        f"(<t:{int(cd.timestamp())}:F>)"
                    ),
                    color=ERROR_COLOR, guild=g, author=m,
                ),
                ephemeral=True,
            )
        await interaction.response.send_modal(ApplicationModal())


class ApplicationDecisionView(discord.ui.View):
    """Buttons für Admins um eine Bewerbung anzunehmen / abzulehnen.
    Persistent: applicant_id wird aus dem Embed-Footer extrahiert."""

    def __init__(self):
        super().__init__(timeout=None)

    @staticmethod
    def _extract_applicant_id(message: discord.Message) -> Optional[int]:
        """Extrahiert die Bewerber-ID aus dem Footer des Embeds."""
        if not message.embeds:
            return None
        footer = message.embeds[0].footer.text or ""
        # Format: "Bewerber-ID: 1234567890..."
        import re
        m = re.search(r"Bewerber-ID:\s*(\d+)", footer)
        return int(m.group(1)) if m else None

    @discord.ui.button(label="Annehmen", style=discord.ButtonStyle.success, emoji="✅", custom_id="apply_accept")
    async def accept(self, interaction, button):
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌  Du brauchst **Rollen verwalten**.", ephemeral=True)
        applicant_id = self._extract_applicant_id(interaction.message)
        if applicant_id is None:
            return await interaction.response.send_message("❌  Bewerber-ID nicht ermittelbar.", ephemeral=True)

        g = interaction.guild
        applicant = g.get_member(applicant_id)
        if applicant is None:
            return await interaction.response.send_message("❌  Der Bewerber ist nicht mehr auf dem Server.", ephemeral=True)

        member_role  = find_role(g, KEY_ROLES["member"])
        bewerber_role = find_role(g, KEY_ROLES["bewerber"])
        try:
            if member_role:   await applicant.add_roles(member_role, reason=f"Bewerbung angenommen von {interaction.user}")
            if bewerber_role and bewerber_role in applicant.roles:
                await applicant.remove_roles(bewerber_role, reason="Bewerbung angenommen")
            clear_cooldown(applicant.id)
        except discord.Forbidden:
            return await interaction.response.send_message("❌  Rechte fehlen (Bot-Rolle zu niedrig?).", ephemeral=True)

        # Embed aktualisieren
        old = interaction.message.embeds[0] if interaction.message.embeds else None
        emb = fuse_embed(
            title="✅  BEWERBUNG ANGENOMMEN",
            description=f"Bewerbung von {applicant.mention} wurde **angenommen**.",
            color=SUCCESS_COLOR, guild=g, author=applicant,
        )
        emb.add_field(name="✅  Entschieden von", value=interaction.user.mention, inline=True)
        emb.add_field(name="🕒  Zeitpunkt",       value=f"<t:{int(datetime.now(timezone.utc).timestamp())}:F>", inline=True)
        if old:
            for f in old.fields:
                if f.name not in ("✅  Entschieden von", "🕒  Zeitpunkt"):
                    emb.add_field(name=f.name, value=f.value, inline=f.inline)
        emb.set_footer(text=f"Bewerber-ID: {applicant.id}  •  {SERVER_NAME}",
                       icon_url=g.icon.url if g.icon else None)
        for c in self.children: c.disabled = True
        await interaction.response.edit_message(embed=emb, view=self)

        # User benachrichtigen
        try:
            dm = fuse_embed(
                title="🎉  Deine Bewerbung wurde angenommen!",
                description=(
                    f"Glückwunsch! Du bist jetzt **Member** auf **{SERVER_NAME}**.\n"
                    f"Du hast jetzt vollen Zugriff auf die Community.\n\n"
                    f"Viel Spaß! 💎"
                ),
                color=SUCCESS_COLOR, guild=g, author=applicant,
            )
            await applicant.send(embed=dm)
        except Exception:
            pass

    @discord.ui.button(label="Ablehnen", style=discord.ButtonStyle.danger, emoji="❌", custom_id="apply_deny")
    async def deny(self, interaction, button):
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌  Du brauchst **Rollen verwalten**.", ephemeral=True)
        applicant_id = self._extract_applicant_id(interaction.message)
        if applicant_id is None:
            return await interaction.response.send_message("❌  Bewerber-ID nicht ermittelbar.", ephemeral=True)
        await interaction.response.send_modal(DenyReasonModal(applicant_id=applicant_id, decision_view=self))


class DenyReasonModal(discord.ui.Modal, title="❌ Bewerbung ablehnen"):
    reason = discord.ui.TextInput(
        label="Begründung für Ablehnung",
        style=discord.TextStyle.paragraph,
        placeholder="z.B. zu wenig RP-Erfahrung, unvollständige Antworten ...",
        max_length=500, required=True,
    )

    def __init__(self, applicant_id: int, decision_view: discord.ui.View):
        super().__init__()
        self.applicant_id = applicant_id
        self.decision_view = decision_view

    async def on_submit(self, interaction: discord.Interaction):
        g = interaction.guild
        applicant = g.get_member(self.applicant_id)

        # Cooldown setzen
        until = set_cooldown(self.applicant_id, APPLY_COOLDOWN_MIN)

        # Bewerber-Rolle behalten (oder nicht — wir lassen sie drauf damit User Bewerbungsbereich behält)

        # Embed updaten
        old = interaction.message.embeds[0] if interaction.message.embeds else None
        emb = fuse_embed(
            title="❌  BEWERBUNG ABGELEHNT",
            description=(
                f"Bewerbung von {applicant.mention if applicant else f'`{self.applicant_id}`'} wurde **abgelehnt**.\n\n"
                f"**📝  Begründung:**\n```{self.reason.value}```\n"
                f"**⏳  Sperre:** {APPLY_COOLDOWN_MIN} Minuten — wieder möglich <t:{int(until.timestamp())}:R>"
            ),
            color=ERROR_COLOR, guild=g, author=applicant if applicant else None,
        )
        emb.add_field(name="❌  Entschieden von", value=interaction.user.mention, inline=True)
        emb.add_field(name="🕒  Zeitpunkt",        value=f"<t:{int(datetime.now(timezone.utc).timestamp())}:F>", inline=True)
        if old:
            for f in old.fields:
                if f.name not in ("❌  Entschieden von", "🕒  Zeitpunkt"):
                    emb.add_field(name=f.name, value=f.value, inline=f.inline)

        for c in self.decision_view.children: c.disabled = True
        await interaction.response.edit_message(embed=emb, view=self.decision_view)

        # User benachrichtigen
        if applicant:
            try:
                dm = fuse_embed(
                    title="❌  Deine Bewerbung wurde abgelehnt",
                    description=(
                        f"Leider wurde deine Bewerbung bei **{SERVER_NAME}** abgelehnt.\n\n"
                        f"**📝  Begründung:**\n```{self.reason.value}```\n"
                        f"**⏳  Sperre:** Du kannst dich in **{APPLY_COOLDOWN_MIN} Minuten** erneut bewerben.\n"
                        f"Wieder möglich: <t:{int(until.timestamp())}:R>"
                    ),
                    color=ERROR_COLOR, guild=g, author=applicant,
                )
                await applicant.send(embed=dm)
            except Exception:
                pass


# ─────────────────────────────────────────────────────────────────── #
# VIEWS / MODAL — TICKETS
# ─────────────────────────────────────────────────────────────────── #
TICKET_CATEGORIES = {
    "general":     {"label": "Allgemeine Frage", "emoji": "❓", "color": INFO_COLOR,
                    "desc": "Allgemeine Fragen zum Server."},
    "problem":     {"label": "Problem / Bug",    "emoji": "🐛", "color": ERROR_COLOR,
                    "desc": "Etwas funktioniert nicht oder ist kaputt."},
    "report":      {"label": "Player-Meldung",   "emoji": "🚨", "color": 0xFF4500,
                    "desc": "Ein Spieler verstößt gegen Regeln."},
    "partner":     {"label": "Partnerschaft",    "emoji": "🤝", "color": 0x1ABC9C,
                    "desc": "Partner-Anfrage."},
    "other":       {"label": "Sonstiges",        "emoji": "💎", "color": PURPLE,
                    "desc": "Alles andere."},
}


class TicketCategoryView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        placeholder="🎫  Wähle eine Ticket-Kategorie…",
        custom_id="fuse_ticket_select",
        min_values=1, max_values=1,
        options=[
            discord.SelectOption(label=c["label"], emoji=c["emoji"], description=c["desc"], value=key)
            for key, c in TICKET_CATEGORIES.items()
        ],
    )
    async def select(self, interaction: discord.Interaction, sel: discord.ui.Select):
        cat_key = sel.values[0]
        if cat_key == "report":
            # Player-Meldung → Modal mit Details
            await interaction.response.send_modal(ReportModal())
        else:
            await create_ticket(interaction, cat_key)


class ReportModal(discord.ui.Modal, title="🚨 Player-Meldung"):
    reported_user = discord.ui.TextInput(
        label="Wen meldest du? (Discord-Name / ID)",
        placeholder="z.B. @JustVexo  oder  123456789012345678",
        max_length=100, required=True,
    )
    what_happened = discord.ui.TextInput(
        label="Was ist passiert?",
        style=discord.TextStyle.paragraph,
        placeholder="Beschreibe genau was passiert ist...",
        max_length=800, required=True,
    )
    proof = discord.ui.TextInput(
        label="Beweise (Links zu Bildern/Clips)",
        style=discord.TextStyle.paragraph,
        placeholder="https://...   (Discord-Anhänge danach im Ticket möglich)",
        max_length=400, required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await create_ticket(
            interaction, "report",
            extra_fields={
                "🎯  Gemeldeter User": f"```{self.reported_user.value}```",
                "📝  Was passierte":   f"```{self.what_happened.value}```",
                "📎  Beweise":         f"```{self.proof.value or '— keine —'}```",
            },
        )


async def create_ticket(interaction: discord.Interaction, cat_key: str,
                        extra_fields: Optional[dict] = None):
    g, m = interaction.guild, interaction.user
    cat = TICKET_CATEGORIES[cat_key]

    existing = discord.utils.get(g.text_channels, name=f"ticket-{cat_key}-{m.name.lower()}")
    if existing:
        return await interaction.response.send_message(
            f"❗  Du hast bereits ein offenes Ticket: {existing.mention}", ephemeral=True,
        )

    parent = find_category(g, "🎫 ✘ SUPPORT")
    ow = {
        g.default_role: discord.PermissionOverwrite(view_channel=False),
        m:              discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                    attach_files=True, read_message_history=True,
                                                    embed_links=True),
        g.me:           discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
    }
    for rn in STAFF_ROLE_NAMES:
        r = find_role(g, rn)
        if r:
            ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)

    ticket = await g.create_text_channel(
        f"ticket-{cat_key}-{m.name.lower()}"[:90],
        category=parent, overwrites=ow,
        topic=f"{cat['label']} • Ersteller: {m.id}",
        reason=f"Ticket: {cat['label']}",
    )

    emb = fuse_embed(
        title=f"{cat['emoji']}  TICKET  •  {cat['label']}",
        description=(
            f"Hallo {m.mention},\n"
            f"vielen Dank für dein Anliegen — ein Team-Mitglied meldet sich gleich.\n\n"
            f"**📝  Bitte beschreibe dein Anliegen so genau wie möglich.**\n"
            f"Füge Screenshots, Beweise oder Links bei wenn relevant."
        ),
        color=cat["color"], guild=g, author=m,
    )
    if extra_fields:
        for k, v in extra_fields.items():
            emb.add_field(name=k, value=v, inline=False)

    await ticket.send(content=f"{m.mention}  •  {' '.join(find_role(g, r).mention for r in ('🔨 Moderator',) if find_role(g, r))}",
                      embed=emb, view=TicketControlView())

    # Response
    if not interaction.response.is_done():
        await interaction.response.send_message(f"✅  Ticket erstellt: {ticket.mention}", ephemeral=True)
    else:
        await interaction.followup.send(f"✅  Ticket erstellt: {ticket.mention}", ephemeral=True)

    log_ch = get_log_channel(g, "ticket")
    if log_ch:
        await log_ch.send(embed=fuse_embed(
            f"{cat['emoji']}  Ticket geöffnet",
            f"**Kategorie:** {cat['label']}\n**User:** {m.mention}\n**Kanal:** {ticket.mention}",
            cat["color"], author=m, guild=g,
        ))


class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Schließen", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="ticket_close")
    async def close_btn(self, interaction, button):
        await interaction.response.send_message(
            embed=fuse_embed("🔒  Ticket schließen?",
                             "Möchtest du dieses Ticket wirklich schließen?",
                             ERROR_COLOR, guild=interaction.guild),
            view=TicketCloseConfirmView(), ephemeral=False,
        )

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary, emoji="🙋", custom_id="ticket_claim")
    async def claim(self, interaction, button):
        if not any(find_role(interaction.guild, rn) in interaction.user.roles for rn in STAFF_ROLE_NAMES if find_role(interaction.guild, rn)):
            return await interaction.response.send_message("❌  Nur Staff kann Tickets claimen.", ephemeral=True)
        await interaction.response.send_message(
            embed=fuse_embed("🙋  Ticket übernommen",
                             f"{interaction.user.mention} kümmert sich um dieses Ticket.",
                             SUCCESS_COLOR, guild=interaction.guild, author=interaction.user),
        )


class TicketCloseConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Ja, schließen", style=discord.ButtonStyle.danger, emoji="🔒")
    async def yes(self, interaction, button):
        await interaction.response.edit_message(
            embed=fuse_embed("🔒  Ticket wird in 5s geschlossen…", "", ERROR_COLOR, guild=interaction.guild),
            view=None,
        )
        await asyncio.sleep(5)
        try:
            log_ch = get_log_channel(interaction.guild, "ticket")
            if log_ch:
                await log_ch.send(embed=fuse_embed(
                    "🔒  Ticket geschlossen",
                    f"**Channel:** `{interaction.channel.name}`\n**Geschlossen von:** {interaction.user.mention}",
                    ERROR_COLOR, guild=interaction.guild, author=interaction.user,
                ))
            await interaction.channel.delete(reason="Ticket geschlossen")
        except Exception:
            pass

    @discord.ui.button(label="Abbrechen", style=discord.ButtonStyle.secondary, emoji="✖️")
    async def no(self, interaction, button):
        await interaction.response.edit_message(
            embed=fuse_embed("✖️  Abgebrochen", "Ticket bleibt offen.", INFO_COLOR, guild=interaction.guild),
            view=None,
        )


# ─────────────────────────────────────────────────────────────────── #
# SETUP-RUNNER
# ─────────────────────────────────────────────────────────────────── #
async def safe_edit(msg: Optional[discord.Message], **kw) -> Optional[discord.Message]:
    if msg is None: return None
    try:
        await msg.edit(**kw)
        return msg
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None
    except Exception:
        return None

async def post_status(g: discord.Guild, embed: discord.Embed) -> Optional[discord.Message]:
    candidates = []
    if g.system_channel: candidates.append(g.system_channel)
    candidates.extend(g.text_channels)
    for ch in candidates:
        try:
            perms = ch.permissions_for(g.me)
            if perms.send_messages and perms.embed_links:
                return await ch.send(embed=embed)
        except Exception: continue
    return None

async def run_setup(g: discord.Guild, status_msg: Optional[discord.Message], wipe: bool) -> None:
    try:
        if wipe:
            await safe_edit(status_msg, embed=fuse_embed("🧹  Lösche alte Struktur…", "", INFO_COLOR, guild=g))
            await wipe_server(g)
            status_msg = None

        status_msg = await safe_edit(status_msg, embed=fuse_embed("🎭  Erstelle Rollen…", "", INFO_COLOR, guild=g)) or status_msg
        await create_roles(g)

        if status_msg is None:
            status_msg = await post_status(g, fuse_embed("📁  Erstelle Kategorien & Kanäle…", "", INFO_COLOR, guild=g))
        else:
            status_msg = await safe_edit(status_msg, embed=fuse_embed("📁  Erstelle Kategorien & Kanäle…", "", INFO_COLOR, guild=g)) or status_msg

        await create_structure(g)
        await enforce_role_hierarchy(g)

        status_msg = await safe_edit(status_msg, embed=fuse_embed("💬  Befülle wichtige Kanäle…", "", INFO_COLOR, guild=g)) or status_msg
        await fill_channels(g)

        done = fuse_embed(
            "✅  Setup abgeschlossen!",
            f"**{SERVER_NAME}** ist komplett eingerichtet.\n\n"
            f"➤  🎭  Rollen:      **{len(ROLES)}**\n"
            f"➤  📁  Kategorien:  **{len(STRUCTURE)}**\n"
            f"➤  💬  Kanäle:      **{sum(len(c['channels']) for c in STRUCTURE)}**\n\n"
            "⚠️  *Lasse die **Bot-Rolle** ganz oben.*",
            SUCCESS_COLOR, guild=g,
        )
        if (await safe_edit(status_msg, embed=done)) is None:
            await post_status(g, done)
    except Exception as e:
        log.exception("Setup-Fehler")
        err = fuse_embed("❌  Fehler beim Setup", f"```{type(e).__name__}: {e}```", ERROR_COLOR, guild=g)
        if (await safe_edit(status_msg, embed=err)) is None:
            await post_status(g, err)


# ─────────────────────────────────────────────────────────────────── #
# COMMANDS
# ─────────────────────────────────────────────────────────────────── #
@bot.event
async def on_ready():
    log.info("Eingeloggt als %s (ID: %s)", bot.user, bot.user.id)
    # Persistente Views
    bot.add_view(VerifyView())
    bot.add_view(ApplyView())
    bot.add_view(TicketCategoryView())
    bot.add_view(TicketControlView())
    bot.add_view(ApplicationDecisionView())
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}start  •  {SERVER_NAME}"))


@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start_cmd(ctx):
    emb = fuse_embed(
        title=f"⚙️  {SERVER_NAME}  •  SETUP WIZARD",
        description=(
            "### 💎  Willkommen zum Server-Setup!\n\n"
            "Wähle eine Option:\n\n"
            "🛑  **Abbruch** — Nichts tun.\n\n"
            "➕  **Nur Hinzufügen** — Fehlendes ergänzen, Bestehendes bleibt.\n\n"
            "♻️  **Komplett neu aufsetzen** — Alles löschen & neu erstellen.\n\n"
            "⚠️  *Bot-Rolle ganz oben + Admin-Rechte erforderlich.*"
        ),
        color=BRAND_COLOR, guild=ctx.guild,
    )
    await ctx.send(embed=emb, view=SetupView(ctx.author.id))


@start_cmd.error
async def start_err(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=fuse_embed("❌  Keine Berechtigung",
                                        "Du brauchst **Administrator**.", ERROR_COLOR, guild=ctx.guild))


@bot.command(name="fix-hierarchie")
@commands.has_permissions(administrator=True)
async def fix_hierarchy(ctx):
    await enforce_role_hierarchy(ctx.guild)
    await ctx.send(embed=fuse_embed("✅  Hierarchie aktualisiert",
                                    "Rollen sind jetzt in der richtigen Reihenfolge.",
                                    SUCCESS_COLOR, guild=ctx.guild))


@bot.command(name="resend-verify")
@commands.has_permissions(administrator=True)
async def resend_verify(ctx):
    emb = fuse_embed("🔐  VERIFIZIERUNG", "Klicke auf den Button, um dich zu verifizieren.",
                     SUCCESS_COLOR, guild=ctx.guild)
    await ctx.send(embed=emb, view=VerifyView())


@bot.command(name="resend-apply")
@commands.has_permissions(administrator=True)
async def resend_apply(ctx):
    emb = fuse_embed("📋  BEWERBUNG", "Klicke unten auf **Bewerbung starten**.",
                     BRAND_COLOR, guild=ctx.guild)
    await ctx.send(embed=emb, view=ApplyView())


@bot.command(name="resend-ticket")
@commands.has_permissions(administrator=True)
async def resend_ticket(ctx):
    emb = fuse_embed("🎫  TICKET ERÖFFNEN",
                     "Wähle unten eine Kategorie aus.", GOLD, guild=ctx.guild)
    await ctx.send(embed=emb, view=TicketCategoryView())


@bot.command(name="clear-cooldown")
@commands.has_permissions(administrator=True)
async def clear_cd(ctx, user: discord.Member):
    clear_cooldown(user.id)
    await ctx.send(embed=fuse_embed("✅  Cooldown entfernt",
                                    f"{user.mention} kann sich wieder bewerben.",
                                    SUCCESS_COLOR, guild=ctx.guild))


# ─────────────────────────────────────────────────────────────────── #
# EVENTS
# ─────────────────────────────────────────────────────────────────── #
@bot.event
async def on_member_join(member: discord.Member):
    g = member.guild
    unv = find_role(g, KEY_ROLES["unverified"])
    if unv:
        try: await member.add_roles(unv, reason="Auto: Unverified")
        except Exception: pass

    wc = discord.utils.get(g.text_channels, name="👋・willkommen")
    if wc:
        emb = fuse_embed(
            title=f"🎉  WILLKOMMEN IN {SERVER_NAME.upper()}!",
            description=(
                f"Hey {member.mention}!  Willkommen bei **{SERVER_NAME}** 💎\n"
                f"Du bist unser **{g.member_count}. Member**.\n\n"
                f"📜  Lies dir das <#📜・regelwerk> durch.\n"
                f"✅  Verifiziere dich im <#✅・verify>.\n"
                f"📋  Sende deine Bewerbung im <#📋・bewerbung>.\n\n"
                f"*Bitte halte dich an die Regeln und geh freundlich mit allen um.*"
            ),
            color=BRAND_COLOR, guild=g, author=member,
        )
        await wc.send(content=member.mention, embed=emb)

    log_ch = get_log_channel(g, "join")
    if log_ch:
        emb = fuse_embed("📥  Member Joined", "", SUCCESS_COLOR, guild=g, author=member)
        emb.add_field(name="User",              value=f"{member.mention} (`{member.id}`)", inline=False)
        emb.add_field(name="Account erstellt",  value=f"<t:{int(member.created_at.timestamp())}:R>")
        emb.add_field(name="Member-Count",      value=f"**{g.member_count}**")
        await log_ch.send(embed=emb)


@bot.event
async def on_member_remove(member: discord.Member):
    g = member.guild
    bye = discord.utils.get(g.text_channels, name="👋・tschüss")
    if bye:
        emb = fuse_embed(
            "👋  TSCHÜSS!",
            f"**{member}** hat den Server verlassen.\nWir sind jetzt **{g.member_count}** Member.",
            ERROR_COLOR, guild=g, author=member,
        )
        await bye.send(embed=emb)
    log_ch = get_log_channel(g, "leave")
    if log_ch:
        emb = fuse_embed("📤  Member Left", f"**{member}** (`{member.id}`)", ERROR_COLOR, guild=g, author=member)
        await log_ch.send(embed=emb)


@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot or not message.guild: return
    log_ch = get_log_channel(message.guild, "message")
    if not log_ch: return
    emb = fuse_embed("🗑️  Nachricht gelöscht", "", ERROR_COLOR, guild=message.guild, author=message.author)
    emb.add_field(name="Kanal",   value=message.channel.mention, inline=True)
    emb.add_field(name="Autor",   value=message.author.mention, inline=True)
    emb.add_field(name="Inhalt",  value=(message.content[:1000] or "*kein Text*"), inline=False)
    await log_ch.send(embed=emb)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot or not before.guild or before.content == after.content: return
    log_ch = get_log_channel(before.guild, "message")
    if not log_ch: return
    emb = fuse_embed("✏️  Nachricht bearbeitet", "", GOLD, guild=before.guild, author=before.author)
    emb.add_field(name="Kanal",   value=before.channel.mention, inline=True)
    emb.add_field(name="Vorher",  value=(before.content[:500] or "*leer*"), inline=False)
    emb.add_field(name="Nachher", value=(after.content[:500]  or "*leer*"), inline=False)
    await log_ch.send(embed=emb)


@bot.event
async def on_voice_state_update(member, before, after):
    log_ch = get_log_channel(member.guild, "voice")
    if not log_ch: return
    if before.channel != after.channel:
        if after.channel and not before.channel:
            txt, col = f"🎙️  **{member}** → **{after.channel.name}**", SUCCESS_COLOR
        elif before.channel and not after.channel:
            txt, col = f"🔇  **{member}** verließ **{before.channel.name}**", ERROR_COLOR
        else:
            txt, col = f"🔄  **{member}**: `{before.channel.name}` → `{after.channel.name}`", INFO_COLOR
        emb = fuse_embed("🎙️  Voice", txt, col, guild=member.guild, author=member)
        await log_ch.send(embed=emb)


@bot.event
async def on_member_update(before, after):
    if before.roles == after.roles: return
    log_ch = get_log_channel(before.guild, "role")
    if not log_ch: return
    added   = [r for r in after.roles  if r not in before.roles]
    removed = [r for r in before.roles if r not in after.roles]
    emb = fuse_embed("🎭  Rollen geändert", f"User: {after.mention}", INFO_COLOR, guild=before.guild, author=after)
    if added:   emb.add_field(name="➕ Hinzugefügt", value=", ".join(r.mention for r in added), inline=False)
    if removed: emb.add_field(name="➖ Entfernt",    value=", ".join(r.mention for r in removed), inline=False)
    await log_ch.send(embed=emb)


@bot.event
async def on_guild_channel_create(channel):
    log_ch = get_log_channel(channel.guild, "channel")
    if log_ch:
        await log_ch.send(embed=fuse_embed("📁  Kanal erstellt",
                                           f"{channel.mention} (`{channel.name}`)",
                                           SUCCESS_COLOR, guild=channel.guild))

@bot.event
async def on_guild_channel_delete(channel):
    log_ch = get_log_channel(channel.guild, "channel")
    if log_ch:
        await log_ch.send(embed=fuse_embed("📁  Kanal gelöscht",
                                           f"`{channel.name}`", ERROR_COLOR, guild=channel.guild))

@bot.event
async def on_guild_role_create(role):
    log_ch = get_log_channel(role.guild, "server")
    if log_ch:
        await log_ch.send(embed=fuse_embed("🎭  Rolle erstellt",
                                           f"{role.mention} (`{role.name}`)",
                                           SUCCESS_COLOR, guild=role.guild))

@bot.event
async def on_guild_role_delete(role):
    log_ch = get_log_channel(role.guild, "server")
    if log_ch:
        await log_ch.send(embed=fuse_embed("🎭  Rolle gelöscht",
                                           f"`{role.name}`", ERROR_COLOR, guild=role.guild))

@bot.event
async def on_member_ban(guild, user):
    log_ch = get_log_channel(guild, "moderation")
    if log_ch:
        await log_ch.send(embed=fuse_embed("🔨  Member gebannt",
                                           f"**{user}** (`{user.id}`)",
                                           ERROR_COLOR, guild=guild))

@bot.event
async def on_member_unban(guild, user):
    log_ch = get_log_channel(guild, "moderation")
    if log_ch:
        await log_ch.send(embed=fuse_embed("🕊️  Member entbannt",
                                           f"**{user}** (`{user.id}`)",
                                           SUCCESS_COLOR, guild=guild))


# ─────────────────────────────────────────────────────────────────── #
# START
# ─────────────────────────────────────────────────────────────────── #
if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("❌  DISCORD_TOKEN fehlt! Setze ihn in Railway-Variablen.")
    bot.run(TOKEN)
