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
import time
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
# DATEN-PERSISTENZ — jetzt aus db.py
# ─────────────────────────────────────────────────────────────────── #
import db

def get_cooldown(user_id: int) -> Optional[datetime]:
    raw = db.DATA["cooldowns"].get(str(user_id))
    if not raw: return None
    try:
        return datetime.fromisoformat(raw)
    except Exception:
        return None

def set_cooldown(user_id: int, minutes: int) -> datetime:
    until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    db.DATA["cooldowns"][str(user_id)] = until.isoformat()
    db.save()
    return until

def clear_cooldown(user_id: int) -> None:
    db.DATA["cooldowns"].pop(str(user_id), None)
    db.save()


# ─────────────────────────────────────────────────────────────────── #
# EINHEITLICHE EMBEDS — aus utils.py (Premium Engine v2)
# Mit Fallback falls utils.py veraltet ist
# ─────────────────────────────────────────────────────────────────── #
try:
    from utils import (
        fuse_embed, banner_embed, success_embed, error_embed, info_embed,
        quote, big_quote, section, kv,
        DIVIDER, SOFT_DIVIDER, DOTS, SECTION, INVISIBLE,
        BULLET_ARROW, BULLET_DIAMOND, BULLET_STAR, BULLET_DOT, BULLET_GEM,
        color_bar, color_banner,
    )
except ImportError as _e:
    # Fallback: alles inline definieren wenn utils.py veraltet/fehlt
    print(f"[WARN] utils.py incomplete ({_e}) — using inline fallback")

    DIVIDER       = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    SOFT_DIVIDER  = "▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱"
    DOTS          = "✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦"
    SECTION       = "◆━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◆"
    INVISIBLE     = "\u200b"
    BULLET_DIAMOND = "◆"
    BULLET_ARROW   = "➤"
    BULLET_STAR    = "✦"
    BULLET_DOT     = "•"
    BULLET_GEM     = "❖"

    def color_bar(hex_color: int) -> str:
        return f"https://singlecolorimage.com/get/{hex_color:06X}/800x4.png"

    def color_banner(hex_color: int) -> str:
        return f"https://singlecolorimage.com/get/{hex_color:06X}/800x80.png"

    def quote(text: str) -> str:
        return "\n".join(f"> {line}" if line.strip() else ">" for line in text.split("\n"))

    def big_quote(text: str) -> str:
        return f">>> {text}"

    def section(title: str, body: str, emoji: str = "◆") -> str:
        return f"### {emoji}  {title}\n{quote(body)}"

    def kv(rows, inline_sep: str = "  •  ") -> str:
        return "\n".join(f"{BULLET_ARROW}  **{k}:**  {v}" for k, v in rows)

    def fuse_embed(title="", description="", color=0xE91E63, *,
                   author=None, author_name=None, guild=None, footer=None,
                   thumbnail=None, show_thumbnail=True, show_color_bar=True,
                   show_color_banner=False, timestamp=True, fields=None, **kwargs):
        srv = guild.name if guild else "FUSE | FS"
        emb = discord.Embed(
            title=title or None, description=description or None,
            color=color, timestamp=datetime.utcnow() if timestamp else None,
        )
        if author:
            emb.set_author(name=str(author), icon_url=author.display_avatar.url)
        elif author_name:
            emb.set_author(name=author_name, icon_url=guild.icon.url if (guild and guild.icon) else None)
        else:
            emb.set_author(name=f"{srv}  ❖  Premium",
                           icon_url=guild.icon.url if (guild and guild.icon) else None)
        if thumbnail:
            emb.set_thumbnail(url=thumbnail)
        elif show_thumbnail and guild and guild.icon:
            emb.set_thumbnail(url=guild.icon.url)
        if fields:
            for f in fields:
                emb.add_field(name=f.get("name", INVISIBLE),
                              value=f.get("value", INVISIBLE),
                              inline=f.get("inline", False))
        if show_color_banner:
            emb.set_image(url=color_banner(color))
        elif show_color_bar:
            emb.set_image(url=color_bar(color))
        emb.set_footer(
            text=footer or f"{srv}  ❖  Roblox Roleplay Community  ❖  Premium Edition",
            icon_url=guild.icon.url if (guild and guild.icon) else None,
        )
        return emb

    def banner_embed(headline, subline, sections, color=0xE91E63,
                     guild=None, footer=None, author=None, accent="💎"):
        parts = [
            f"# {accent}  {headline.upper()}",
            SOFT_DIVIDER,
            big_quote(subline),
            "",
        ]
        for emoji, t, body in sections:
            parts.append(f"### {emoji}  __{t}__")
            parts.append(quote(body))
            parts.append("")
        return fuse_embed(
            title="", description="\n".join(parts).strip(),
            color=color, guild=guild, footer=footer, author=author,
        )

    def success_embed(title, body, guild=None, author=None):
        return fuse_embed(f"✅  {title}",
                          f"{SOFT_DIVIDER}\n{big_quote(body)}\n{SOFT_DIVIDER}",
                          0x2ECC71, guild=guild, author=author)

    def error_embed(title, body, guild=None, author=None):
        return fuse_embed(f"❌  {title}",
                          f"{SOFT_DIVIDER}\n{big_quote(body)}\n{SOFT_DIVIDER}",
                          0xE74C3C, guild=guild, author=author)

    def info_embed(title, body, guild=None, author=None):
        return fuse_embed(f"ℹ️  {title}",
                          f"{SOFT_DIVIDER}\n{big_quote(body)}\n{SOFT_DIVIDER}",
                          0x3498DB, guild=guild, author=author)

LINE = DIVIDER  # Backwards-Compat


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
    # ═══════════════════════════════════════════════════════════════
    # 📩  WILLKOMMEN  (alles read-only außer „tschüss" wird vom Bot bedient)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "📩 ✘ WILLKOMMEN", "visibility": "lobby",
        "channels": [
            {"name": "👋・willkommen",   "type": "text", "visibility": "lobby",       "readonly": True},
            {"name": "📜・regelwerk",    "type": "text", "visibility": "lobby",       "readonly": True},
            {"name": "✅・verify",       "type": "text", "visibility": "verify_only", "readonly": True},
            {"name": "👋・tschüss",      "type": "text", "visibility": "lobby",       "readonly": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 📋  BEWERBUNG  (Info-Channels readonly, Chat & Bewerbung schreibbar)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "📋 ✘ BEWERBUNG", "visibility": "bewerbung",
        "channels": [
            {"name": "❓・bewerbungs-info", "type": "text",  "visibility": "bewerbung", "readonly": True},
            {"name": "📋・bewerbung",       "type": "text",  "visibility": "bewerbung", "readonly": True},
            {"name": "👾・bewerbungs-chat", "type": "text",  "visibility": "bewerbung"},
            {"name": "🎙️・warteraum",       "type": "voice", "visibility": "bewerbung"},
            {"name": "🚪・einreise-1",      "type": "voice", "visibility": "bewerbung", "locked": True},
            {"name": "🚪・einreise-2",      "type": "voice", "visibility": "bewerbung", "locked": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 🎫  SUPPORT  (beide Info-Channels readonly)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "🎫 ✘ SUPPORT", "visibility": "member",
        "channels": [
            {"name": "📖・ticket-info",   "type": "text", "visibility": "member", "readonly": True},
            {"name": "🎫・ticket-öffnen", "type": "text", "visibility": "member", "readonly": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 🔔  INFOS  (alle Info-Channels readonly — nur Team postet hier)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "🔔 ✘ INFOS", "visibility": "member",
        "channels": [
            {"name": "🔔・ankündigungen",  "type": "text", "readonly": True},
            {"name": "📰・server-news",    "type": "text", "readonly": True},
            {"name": "🎉・events",         "type": "text", "readonly": True},
            {"name": "🚀・boosts",         "type": "text", "readonly": True},
            {"name": "🤝・partner",        "type": "text", "readonly": True},
            {"name": "✅・activity-check", "type": "text", "readonly": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 💬  COMMUNITY  (alles schreibbar — das ist der Hauptbereich)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "💬 ✘ COMMUNITY", "visibility": "member",
        "channels": [
            {"name": "💬・chat",          "type": "text"},
            {"name": "🎨・media",         "type": "text"},
            {"name": "🤣・memes",         "type": "text"},
            {"name": "🎮・gaming-talk",   "type": "text"},
            {"name": "💡・vorschläge",    "type": "text"},
            {"name": "🎂・geburtstage",   "type": "text"},
            {"name": "🤖・bot-commands",  "type": "text"},
            {"name": "😂・hall-of-shame", "type": "text", "readonly": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 📱  SOCIALMEDIA  (alle Showcase-Channels readonly — nur Team postet)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "📱 ✘ SOCIALMEDIA", "visibility": "member",
        "channels": [
            {"name": "📱・socialmedia",   "type": "text", "readonly": True},
            {"name": "📸・instagram",     "type": "text", "readonly": True},
            {"name": "🎵・tiktok",        "type": "text", "readonly": True},
            {"name": "🎬・youtube",       "type": "text", "readonly": True},
            {"name": "🎮・twitch",        "type": "text", "readonly": True},
            {"name": "🎥・meeting-clips", "type": "text", "readonly": True},
            {"name": "🎞️・free-tt-vids",  "type": "text", "readonly": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 🔊  TALKS
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "🔊 ✘ TALKS", "visibility": "member",
        "channels": [
            {"name": "🎤・Stage",          "type": "stage"},
            {"name": "🌐・FFA-VoiceChat",  "type": "voice"},
            {"name": "💬・Talk-1",         "type": "voice"},
            {"name": "💬・Talk-2",         "type": "voice"},
            {"name": "🎮・Gaming-1",       "type": "voice"},
            {"name": "🎮・Gaming-2",       "type": "voice"},
            {"name": "🎵・Musik",          "type": "voice"},
            {"name": "🎬・Streaming",      "type": "voice"},
            {"name": "😴・AFK",            "type": "voice"},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 🧱  FUSE MERCH  (alle Showcase-Channels readonly)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "🧱 ✘ FUSE MERCH", "visibility": "member",
        "channels": [
            {"name": "🦺・weste",   "type": "text", "readonly": True},
            {"name": "📿・armband", "type": "text", "readonly": True},
            {"name": "👕・merch",   "type": "text", "readonly": True},
            {"name": "👕・trikot",  "type": "text", "readonly": True},
            {"name": "👕・polo",    "type": "text", "readonly": True},
            {"name": "🧢・cap",     "type": "text", "readonly": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 📓  GANG INFOS  (alles readonly — nur Team postet Infos)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "📓 ✘ GANG INFOS", "visibility": "member",
        "channels": [
            {"name": "💗・farbe",         "type": "text", "readonly": True},
            {"name": "🎨・rollensystem",  "type": "text", "readonly": True},
            {"name": "🎮・roblox-gruppe", "type": "text", "readonly": True},
            {"name": "🏠・anwesen",       "type": "text", "readonly": True},
            {"name": "🚗・fuhrpark",      "type": "text", "readonly": True},
            {"name": "💰・kasse",         "type": "text", "readonly": True},
            {"name": "🛡️・partnerschaft", "type": "text", "readonly": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 🔒  LOUNGES — Booster & Premium
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "🔒 ✘ LOUNGES", "visibility": "member",
        "channels": [
            {"name": "🎀・premium-lounge",  "type": "voice", "locked": True},
            {"name": "💎・diamond-lounge",  "type": "voice", "locked": True},
            {"name": "♟️・schach-lounge",   "type": "voice", "locked": True},
            {"name": "🍺・bier-keller",     "type": "voice", "locked": True},
            {"name": "🎮・gaming-lounge",   "type": "voice", "locked": True},
            {"name": "💬・lounge-chat",     "type": "text",  "locked": True},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 🏢  BÜROS — Team Voice
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "🏢 ✘ BÜROS", "visibility": "staff",
        "channels": [
            {"name": "👑・Owner-Büro",   "type": "voice", "visibility": "owner_only"},
            {"name": "⚡・Admin-Büro",    "type": "voice", "visibility": "staff"},
            {"name": "🔨・Mod-Büro",      "type": "voice", "visibility": "staff"},
            {"name": "🎧・Support-Büro",  "type": "voice", "visibility": "staff"},
            {"name": "💻・Dev-Büro",      "type": "voice", "visibility": "staff"},
            {"name": "📊・Meeting-Raum",  "type": "voice", "visibility": "staff"},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 🛡️  ADMIN — Team Chats
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "🛡️ ✘ ADMIN", "visibility": "staff",
        "channels": [
            {"name": "📋・team-ankündigung", "type": "text", "visibility": "staff"},
            {"name": "👑・owner-chat",       "type": "text", "visibility": "owner_only"},
            {"name": "⚡・admin-chat",        "type": "text", "visibility": "staff"},
            {"name": "🔨・mod-chat",          "type": "text", "visibility": "staff"},
            {"name": "🎧・support-chat",      "type": "text", "visibility": "staff"},
            {"name": "💻・dev-chat",          "type": "text", "visibility": "staff"},
            {"name": "📝・team-todo",         "type": "text", "visibility": "staff"},
            {"name": "🚨・report-eingang",    "type": "text", "visibility": "staff"},
        ],
    },

    # ═══════════════════════════════════════════════════════════════
    # 📋  LOGS — nur Bot postet hier (NICHT readonly — sonst kann Bot nicht schreiben)
    # ═══════════════════════════════════════════════════════════════
    {
        "category": "📋 ✘ LOGS", "visibility": "staff",
        "channels": [
            {"name": "📨・bewerbung-logs",  "type": "text", "log": "application"},
            {"name": "🎫・ticket-logs",     "type": "text", "log": "ticket"},
            {"name": "✅・verify-logs",     "type": "text", "log": "verify"},
            {"name": "📥・join-logs",       "type": "text", "log": "join"},
            {"name": "📤・leave-logs",      "type": "text", "log": "leave"},
            {"name": "💬・message-logs",    "type": "text", "log": "message"},
            {"name": "🎙️・voice-logs",      "type": "text", "log": "voice"},
            {"name": "🎭・role-logs",       "type": "text", "log": "role"},
            {"name": "📁・channel-logs",    "type": "text", "log": "channel"},
            {"name": "🌐・server-logs",     "type": "text", "log": "server"},
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


def build_overwrites(g: discord.Guild, visibility: str, locked: bool = False,
                     readonly: bool = False) -> dict:
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

    # Staff sieht alles (außer owner_only) — DARF immer schreiben (auch in readonly!)
    if visibility != "owner_only":
        for rn in STAFF_ROLE_NAMES:
            r = find_role(g, rn)
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                    connect=True, speak=True, read_message_history=True,
                                                    manage_messages=True, add_reactions=True,
                                                    embed_links=True, attach_files=True)
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

    # READONLY: niemand außer Staff darf schreiben/reagieren
    # (Staff-Overwrites bleiben oben drüber → können trotzdem posten)
    if readonly:
        readonly_perm = discord.PermissionOverwrite(
            send_messages=False, send_messages_in_threads=False,
            create_public_threads=False, create_private_threads=False,
            add_reactions=False,
        )
        # @everyone als Basis
        base_eo = ow.get(everyone, discord.PermissionOverwrite())
        base_eo.update(
            send_messages=False, send_messages_in_threads=False,
            create_public_threads=False, create_private_threads=False,
            add_reactions=False,
        )
        ow[everyone] = base_eo
        # Alle bekannten Member-Rollen schreibverbot
        for role_name in (KEY_ROLES["member"], KEY_ROLES["verified"],
                          KEY_ROLES["unverified"], KEY_ROLES["bewerber"],
                          "🤝 Fuse", "💕 Friend", "🧪 Trial-Member",
                          "💠 Member+", "🏆 Veteran", "⭐ Elite",
                          "💖 Booster", "💖 Boost-King", "💎 Nitro",
                          "🎬 YouTuber", "🎮 Twitch-Streamer", "🎵 TikToker",
                          "🖌️ Content-Creator", "🎶 DJ",
                          "💎 Boss", "💎 Underboss", "💎 Consigliere",
                          "💎 Capo", "💎 Soldato", "🔫 Hitman", "🔫 Enforcer",
                          "💊 Dealer", "🚚 Smuggler", "🏎️ Driver",
                          "🔧 Mechanic", "🛡️ Bodyguard"):
            r = find_role(g, role_name)
            if r:
                existing = ow.get(r, discord.PermissionOverwrite())
                existing.update(
                    send_messages=False, send_messages_in_threads=False,
                    create_public_threads=False, create_private_threads=False,
                    add_reactions=False,
                )
                ow[r] = existing

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
            readonly = ch_def.get("readonly", False)

            existing = find_channel(g, ch_name)
            if existing:
                await _safe(
                    lambda: existing.edit(overwrites=build_overwrites(g, ch_vis, locked=locked, readonly=readonly)),
                    label=f"edit ch {ch_name}",
                )
                continue

            chan_ow = build_overwrites(g, ch_vis, locked=locked, readonly=readonly)
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
    # Stats-IDs in DB resetten (Channels wurden ja gelöscht)
    db.DATA["stats_channels"] = {}
    db.save()
    log.info("Wipe abgeschlossen.")


# ─────────────────────────────────────────────────────────────────── #
# KANAL-INHALTE
# ═══════════════════════════════════════════════════════════════════ #
# CHANNEL-INHALTE — Components V2 Panels
# ═══════════════════════════════════════════════════════════════════ #
import panels


async def fill_channels(g: discord.Guild) -> None:
    """Befüllt wichtige Kanäle mit Components V2 Layouts (statt Embeds)."""

    async def _send_if_empty(ch_name: str, view_factory):
        ch = discord.utils.get(g.text_channels, name=ch_name)
        if ch and not [m async for m in ch.history(limit=1)]:
            try:
                await ch.send(view=view_factory())
            except Exception as e:
                log.warning("send %s: %s", ch_name, e)

    await _send_if_empty("📜・regelwerk",        lambda: panels.rules_panel(g))
    await _send_if_empty("✅・verify",           lambda: panels.VerifyLayoutView(g))
    await _send_if_empty("👋・willkommen",       lambda: panels.welcome_panel(g))
    await _send_if_empty("❓・bewerbungs-info",  lambda: panels.bewerbungs_info_panel(g))
    await _send_if_empty("📋・bewerbung",        lambda: panels.ApplyLayoutView(g))
    await _send_if_empty("📖・ticket-info",      lambda: panels.ticket_info_panel(g))
    await _send_if_empty("🎫・ticket-öffnen",    lambda: panels.TicketCategoryLayoutView(g))
    await _send_if_empty("🔔・ankündigungen",    lambda: panels.announcement_panel(g))
    await _send_if_empty("🚀・boosts",           lambda: panels.boost_panel(g))
    await _send_if_empty("💬・chat",             lambda: panels.chat_panel(g))
    await _send_if_empty("🛡️・partnerschaft",    lambda: panels.partner_panel(g))
    await _send_if_empty("👑・owner-chat",       lambda: panels.owner_chat_panel(g))
    await _send_if_empty("⚡・admin-chat",        lambda: panels.admin_chat_panel(g))


# ═══════════════════════════════════════════════════════════════════ #
# SETUP-RUNNER — sendet jetzt LayoutViews als Status
# ═══════════════════════════════════════════════════════════════════ #
async def safe_edit_view(msg: Optional[discord.Message], view) -> Optional[discord.Message]:
    """Edit-Helper für LayoutViews (keine embed=, kein content=)."""
    if msg is None: return None
    try:
        # Bei LayoutView musst du content/embeds explizit nullen
        await msg.edit(content=None, embeds=[], view=view)
        return msg
    except (discord.NotFound, discord.Forbidden, discord.HTTPException):
        return None
    except Exception:
        return None


async def post_status_view(g: discord.Guild, view) -> Optional[discord.Message]:
    candidates = []
    if g.system_channel: candidates.append(g.system_channel)
    candidates.extend(g.text_channels)
    for ch in candidates:
        try:
            perms = ch.permissions_for(g.me)
            if perms.send_messages and perms.embed_links:
                return await ch.send(view=view)
        except Exception: continue
    return None


async def run_setup(g: discord.Guild, status_msg: Optional[discord.Message], wipe: bool) -> None:
    try:
        if wipe:
            await safe_edit_view(status_msg, panels.status_panel(
                "🧹", "Lösche alte Struktur…",
                "Alle alten Kanäle und Rollen werden entfernt.",
                color=panels.INFO_COLOR, guild=g,
            ))
            await wipe_server(g)
            status_msg = None

        new_status = panels.status_panel(
            "🎭", "Erstelle Rollen…",
            "52+ Rollen werden in korrekter Hierarchie angelegt.",
            color=panels.INFO_COLOR, guild=g,
        )
        status_msg = await safe_edit_view(status_msg, new_status) or status_msg
        await create_roles(g)

        new_status = panels.status_panel(
            "📁", "Erstelle Kategorien & Kanäle…",
            "Die komplette Server-Struktur wird aufgebaut.",
            color=panels.INFO_COLOR, guild=g,
        )
        if status_msg is None:
            status_msg = await post_status_view(g, new_status)
        else:
            status_msg = await safe_edit_view(status_msg, new_status) or status_msg

        await create_structure(g)
        await enforce_role_hierarchy(g)

        new_status = panels.status_panel(
            "💬", "Befülle wichtige Kanäle…",
            "Regelwerk, Verify, Bewerbung & Co. werden mit Premium-Layouts ausgestattet.",
            color=panels.INFO_COLOR, guild=g,
        )
        status_msg = await safe_edit_view(status_msg, new_status) or status_msg
        await fill_channels(g)

        # 📊 Stats-Channels (ganz oben, für alle sichtbar) automatisch einrichten
        try:
            stats_cog = bot.get_cog("Stats")
            if stats_cog:
                await stats_cog.ensure_setup(g)
        except Exception as e:
            log.warning("Stats-Auto-Setup fehlgeschlagen: %s", e)

        done = panels.setup_done_panel(
            g,
            n_roles=len(ROLES),
            n_cats=len(STRUCTURE),
            n_chans=sum(len(c['channels']) for c in STRUCTURE),
        )
        if (await safe_edit_view(status_msg, done)) is None:
            await post_status_view(g, done)
    except Exception as e:
        log.exception("Setup-Fehler")
        err = panels.status_panel(
            "❌", "Fehler beim Setup",
            f"```{type(e).__name__}: {e}```",
            color=panels.ERROR_COLOR, guild=g,
        )
        if (await safe_edit_view(status_msg, err)) is None:
            await post_status_view(g, err)


# ─────────────────────────────────────────────────────────────────── #
COGS = [
    "cogs.automod",
    "cogs.warns",
    "cogs.alt_detection",
    "cogs.stats",
    "cogs.xp",
    "cogs.giveaway",
    "cogs.birthday",
    "cogs.application_tasks",
]


async def load_cogs():
    for c in COGS:
        try:
            await bot.load_extension(c)
            log.info("✓ Cog geladen: %s", c)
        except Exception as e:
            log.warning("✗ Cog '%s' fehlgeschlagen: %s", c, e)


@bot.event
async def setup_hook():
    """Wird VOR on_ready aufgerufen — perfekt zum Cogs laden."""
    await load_cogs()
    # Persistente Giveaway-Views
    try:
        from cogs.giveaway import GiveawayJoinView, GiveawayRerollView
        bot.add_view(GiveawayJoinView())
        bot.add_view(GiveawayRerollView())
    except Exception as e:
        log.warning("Giveaway views: %s", e)


@bot.event
async def on_ready():
    log.info("Eingeloggt als %s (ID: %s)", bot.user, bot.user.id)
    # Persistente V2 Layout-Views
    bot.add_view(panels.VerifyLayoutView())
    bot.add_view(panels.ApplyLayoutView())
    bot.add_view(panels.TicketCategoryLayoutView())
    bot.add_view(panels.ApplicationDecisionLayoutView())
    # Persistente Ticket-Control-Buttons (in einer leeren LayoutView registrieren)
    _ticket_ctrl = discord.ui.LayoutView(timeout=None)
    _ticket_ctrl.add_item(discord.ui.ActionRow(panels.TicketCloseButton(), panels.TicketClaimButton()))
    bot.add_view(_ticket_ctrl)
    _ticket_close_confirm = discord.ui.LayoutView(timeout=None)
    _ticket_close_confirm.add_item(discord.ui.ActionRow(panels.TicketCloseConfirmYes(), panels.TicketCloseConfirmNo()))
    bot.add_view(_ticket_close_confirm)
    # Slash-Commands syncen
    try:
        synced = await bot.tree.sync()
        log.info("Slash-Commands gesynct: %d", len(synced))
    except Exception as e:
        log.warning("Sync failed: %s", e)
    await bot.change_presence(activity=discord.Game(name=f"{PREFIX}start  •  {SERVER_NAME}"))


@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start_cmd(ctx):
    await ctx.send(view=panels.setup_wizard_panel(ctx.guild, ctx.author.id))


@start_cmd.error
async def start_err(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(view=panels.status_panel(
            "❌", "Keine Berechtigung",
            "Du brauchst **Administrator**.",
            color=panels.ERROR_COLOR, guild=ctx.guild,
        ))


@bot.command(name="fix-hierarchie")
@commands.has_permissions(administrator=True)
async def fix_hierarchy(ctx):
    await enforce_role_hierarchy(ctx.guild)
    await ctx.send(view=panels.status_panel(
        "✅", "Hierarchie aktualisiert",
        "Rollen sind jetzt in der richtigen Reihenfolge.",
        color=panels.SUCCESS_COLOR, guild=ctx.guild,
    ))


@bot.command(name="resend-verify")
@commands.has_permissions(administrator=True)
async def resend_verify(ctx):
    await ctx.send(view=panels.VerifyLayoutView(ctx.guild))


@bot.command(name="resend-apply")
@commands.has_permissions(administrator=True)
async def resend_apply(ctx):
    await ctx.send(view=panels.ApplyLayoutView(ctx.guild))


@bot.command(name="resend-ticket")
@commands.has_permissions(administrator=True)
async def resend_ticket(ctx):
    await ctx.send(view=panels.TicketCategoryLayoutView(ctx.guild))


@bot.command(name="clear-cooldown")
@commands.has_permissions(administrator=True)
async def clear_cd(ctx, user: discord.Member):
    clear_cooldown(user.id)
    await ctx.send(view=panels.status_panel(
        "✅", "Cooldown entfernt",
        f"{user.mention} kann sich wieder bewerben.",
        color=panels.SUCCESS_COLOR, guild=ctx.guild,
    ))


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
        # Ping zuerst (separate Message), dann V2-Panel
        try:
            await wc.send(content=member.mention, allowed_mentions=discord.AllowedMentions(users=True))
        except Exception: pass
        await wc.send(view=panels.welcome_join_panel(member))

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
        await bye.send(view=panels.goodbye_panel(member))
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

    # Dashboard parallel starten (wenn nicht deaktiviert)
    if os.getenv("ENABLE_DASHBOARD", "1") == "1":
        try:
            import dashboard
            dashboard.start_in_thread()
        except Exception as e:
            log.warning("Dashboard konnte nicht starten: %s", e)

    bot.run(TOKEN)
