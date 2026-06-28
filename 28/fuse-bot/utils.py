"""
Geteilte Helper-Funktionen — Premium Embed-Engine v2
"""
from datetime import datetime
from typing import Optional

import discord

# ─── Brand ────────────────────────────────────────────────────────
BRAND_COLOR   = 0xE91E63
SUCCESS_COLOR = 0x2ECC71
ERROR_COLOR   = 0xE74C3C
INFO_COLOR    = 0x3498DB
GOLD          = 0xF1C40F
PURPLE        = 0x9B59B6
DARK          = 0x2B2D31

# ─── Decorative Strings ────────────────────────────────────────────
DIVIDER       = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
SOFT_DIVIDER  = "▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱▱"
DOTS          = "✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦ ✧ ✦"
SECTION       = "◆━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━◆"
INVISIBLE     = "\u200b"

# Bullets
BULLET_DIAMOND = "◆"
BULLET_ARROW   = "➤"
BULLET_STAR    = "✦"
BULLET_DOT     = "•"
BULLET_GEM     = "❖"


# ─── Helpers ──────────────────────────────────────────────────────
def find_role(g: discord.Guild, name: str) -> Optional[discord.Role]:
    return discord.utils.get(g.roles, name=name)


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


def color_bar(hex_color: int) -> str:
    """800x4 px farbiger Strich für unten im Embed."""
    return f"https://singlecolorimage.com/get/{hex_color:06X}/800x4.png"


def color_banner(hex_color: int) -> str:
    """800x80 px Banner für ganz oben."""
    return f"https://singlecolorimage.com/get/{hex_color:06X}/800x80.png"


# ─── Quote Helpers ────────────────────────────────────────────────
def quote(text: str) -> str:
    """Wandelt jede Zeile in ein '> '-Blockquote um."""
    return "\n".join(f"> {line}" if line.strip() else ">" for line in text.split("\n"))


def big_quote(text: str) -> str:
    """Discord '>>>' Multiline-Blockquote."""
    return f">>> {text}"


def section(title: str, body: str, emoji: str = "◆") -> str:
    """
    Rendert einen 'Section'-Block:
        ◆ TITEL
        ▱▱▱▱▱▱▱▱▱▱
        > body text
    """
    return f"### {emoji}  {title}\n{quote(body)}"


def kv(rows: list[tuple[str, str]], inline_sep: str = "  •  ") -> str:
    """Key-Value Liste:  ➤  Label:  Wert"""
    return "\n".join(f"{BULLET_ARROW}  **{k}:**  {v}" for k, v in rows)


# ─── Embed Engine ─────────────────────────────────────────────────
def fuse_embed(
    title: str = "",
    description: str = "",
    color: int = BRAND_COLOR,
    *,
    author=None,
    author_name: Optional[str] = None,
    guild: Optional[discord.Guild] = None,
    footer: Optional[str] = None,
    thumbnail: Optional[str] = None,
    show_thumbnail: bool = True,
    show_color_bar: bool = True,
    show_color_banner: bool = False,
    timestamp: bool = True,
    fields: Optional[list[dict]] = None,
) -> discord.Embed:
    """
    Premium Embed-Engine v2

    Args:
        title:           Großer Titel
        description:     Body-Text (Markdown unterstützt)
        color:           Akzent-Farbe
        author:          discord.Member/User → Avatar+Name im Author-Slot
        author_name:     Falls kein User, manueller Name
        guild:           für Server-Icon
        footer:          eigener Footer-Text (sonst Default)
        thumbnail:       URL für Thumbnail rechts oben
        show_thumbnail:  Server-Icon als Thumb wenn kein expliziter angegeben
        show_color_bar:  4px Color-Bar unten
        show_color_banner: 80px Color-Banner oben (statt color_bar)
        fields:          Liste von {name, value, inline}
    """
    SERVER_NAME = guild.name if guild else "FUSE | FS"

    emb = discord.Embed(
        title=title or None,
        description=description or None,
        color=color,
        timestamp=datetime.utcnow() if timestamp else None,
    )

    # Author
    if author:
        emb.set_author(name=str(author), icon_url=author.display_avatar.url)
    elif author_name:
        emb.set_author(name=author_name,
                       icon_url=guild.icon.url if (guild and guild.icon) else None)
    else:
        emb.set_author(name=f"{SERVER_NAME}  ❖  Premium",
                       icon_url=guild.icon.url if (guild and guild.icon) else None)

    # Thumbnail
    if thumbnail:
        emb.set_thumbnail(url=thumbnail)
    elif show_thumbnail and guild and guild.icon:
        emb.set_thumbnail(url=guild.icon.url)

    # Felder
    if fields:
        for f in fields:
            emb.add_field(
                name=f.get("name", INVISIBLE),
                value=f.get("value", INVISIBLE),
                inline=f.get("inline", False),
            )

    # Banner / Bar
    if show_color_banner:
        emb.set_image(url=color_banner(color))
    elif show_color_bar:
        emb.set_image(url=color_bar(color))

    # Footer
    emb.set_footer(
        text=footer or f"{SERVER_NAME}  ❖  Roblox Roleplay Community  ❖  Premium Edition",
        icon_url=(guild.icon.url if (guild and guild.icon) else None),
    )
    return emb


# ─── Specialty Embeds ─────────────────────────────────────────────
def banner_embed(
    headline: str,
    subline: str,
    sections: list[tuple[str, str, str]],   # (emoji, title, body)
    color: int = BRAND_COLOR,
    guild: Optional[discord.Guild] = None,
    footer: Optional[str] = None,
    author=None,
    accent: str = "💎",
) -> discord.Embed:
    """
    Großes Premium-Embed:

        # 💎  HEADLINE
        ▱▱▱▱▱▱▱▱▱▱▱▱
        > subline

        ### ◆  SECTION 1
        > body text
        > more text

        ### ◆  SECTION 2
        > body text
    """
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
        title="",
        description="\n".join(parts).strip(),
        color=color, guild=guild, footer=footer, author=author,
    )


def success_embed(title: str, body: str, guild=None, author=None) -> discord.Embed:
    return fuse_embed(
        f"✅  {title}",
        f"{SOFT_DIVIDER}\n{big_quote(body)}\n{SOFT_DIVIDER}",
        SUCCESS_COLOR, guild=guild, author=author,
    )


def error_embed(title: str, body: str, guild=None, author=None) -> discord.Embed:
    return fuse_embed(
        f"❌  {title}",
        f"{SOFT_DIVIDER}\n{big_quote(body)}\n{SOFT_DIVIDER}",
        ERROR_COLOR, guild=guild, author=author,
    )


def info_embed(title: str, body: str, guild=None, author=None) -> discord.Embed:
    return fuse_embed(
        f"ℹ️  {title}",
        f"{SOFT_DIVIDER}\n{big_quote(body)}\n{SOFT_DIVIDER}",
        INFO_COLOR, guild=guild, author=author,
    )
