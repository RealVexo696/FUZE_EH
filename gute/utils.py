"""
Geteilte Helper-Funktionen (von Cogs benutzt).
"""
from datetime import datetime
from typing import Optional

import discord

BRAND_COLOR = 0xE91E63


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
    return f"https://singlecolorimage.com/get/{hex_color:06X}/800x4.png"


def fuse_embed(title: str = "", description: str = "", color: int = BRAND_COLOR, *,
               author=None, guild: Optional[discord.Guild] = None,
               footer: Optional[str] = None) -> discord.Embed:
    SERVER_NAME = guild.name if guild else "FUSE | FS"
    emb = discord.Embed(
        title=title or None,
        description=description or None,
        color=color,
        timestamp=datetime.utcnow(),
    )
    if author:
        emb.set_author(name=str(author), icon_url=author.display_avatar.url)
    else:
        emb.set_author(name=SERVER_NAME, icon_url=guild.icon.url if (guild and guild.icon) else None)
    if guild and guild.icon:
        emb.set_thumbnail(url=guild.icon.url)
    emb.set_image(url=color_bar(color))
    emb.set_footer(
        text=footer or f"{SERVER_NAME}  •  Roblox Roleplay Community",
        icon_url=(guild.icon.url if (guild and guild.icon) else None),
    )
    return emb
