"""
🤖 AUTO-MOD COG
- Beleidigungs-Filter
- Discord-Invite Filter
- Werbung / Scam-Links
- Caps-Lock-Spam
- Message-Spam (5 Nachrichten in 5s)
- Anti-Raid (10+ Joins in 60s -> Lockdown)
"""
import re
import time
import asyncio
from datetime import datetime, timedelta, timezone
from collections import defaultdict, deque

import discord
from discord.ext import commands

import db

# ─────────────────────────────────────────────────────────────────── #
# CONFIG
# ─────────────────────────────────────────────────────────────────── #
BAD_WORDS = {
    "hure", "huren", "nutte", "nutten", "fotze", "fotzen",
    "nigger", "n1gger", "nazi", "hitler",
    "kanake", "kanaken", "spast", "spasti", "spasten",
    "behindert", "mongo", "mongoloid",
    "kys", "killyourself",
    "missgeburt", "wichser", "wixxer", "wixer",
}

INVITE_RE = re.compile(r"(?:discord\.gg|discord\.com/invite|discordapp\.com/invite)/[a-zA-Z0-9-]+", re.IGNORECASE)
SCAM_RE   = re.compile(r"(free\s*nitro|steam\s*gift|free\s*robux|nitro\s*generator)", re.IGNORECASE)
URL_RE    = re.compile(r"https?://[^\s]+", re.IGNORECASE)

CAPS_THRESHOLD = 0.75          # 75% Großbuchstaben
CAPS_MIN_LEN   = 12            # erst ab 12 Zeichen relevant
SPAM_WINDOW    = 5             # 5 Sekunden
SPAM_LIMIT     = 5             # max 5 Nachrichten in 5s
RAID_WINDOW    = 60            # 60 Sekunden
RAID_LIMIT     = 10            # 10 Joins in 60s

WHITELIST_DOMAINS = {
    "youtube.com", "youtu.be", "twitch.tv", "tiktok.com",
    "instagram.com", "twitter.com", "x.com", "roblox.com",
    "discord.com", "media.discordapp.net", "cdn.discordapp.com",
    "tenor.com", "giphy.com", "imgur.com",
    "github.com", "spotify.com", "open.spotify.com",
}


def is_staff(member: discord.Member) -> bool:
    if member.guild_permissions.manage_messages: return True
    return any(r.name.startswith(("👑", "⚡", "🔨", "🎧", "💻")) for r in member.roles)


def domain_allowed(url: str) -> bool:
    try:
        host = url.split("//", 1)[1].split("/", 1)[0].lower()
        return any(host == d or host.endswith("." + d) for d in WHITELIST_DOMAINS)
    except Exception:
        return False


class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msg_history: dict[int, deque] = defaultdict(lambda: deque(maxlen=10))
        self.join_history: deque = deque(maxlen=50)
        self.raid_lockdown = False

    # ── Helpers ─────────────────────────────────────────────────
    async def punish(self, message: discord.Message, reason: str, mute_minutes: int = 0):
        """Löscht Nachricht, schreibt Log, ggf. Mute."""
        try: await message.delete()
        except Exception: pass

        try:
            warn = discord.Embed(
                title="⚠️  AutoMod-Verstoß",
                description=f"{message.author.mention}, deine Nachricht wurde gelöscht.\n**Grund:** {reason}",
                color=0xE74C3C,
            )
            await message.channel.send(embed=warn, delete_after=8)
        except Exception:
            pass

        # Mute
        if mute_minutes > 0:
            try:
                until = datetime.now(timezone.utc) + timedelta(minutes=mute_minutes)
                await message.author.timeout(until, reason=f"AutoMod: {reason}")
            except Exception:
                pass

        # Tracking
        viols = db.DATA["automod_violations"].setdefault(str(message.author.id), [])
        viols.append({"type": reason, "ts": time.time()})
        # Auto-Eskalation: 3 Verstöße in 24h → 10min Mute
        recent = [v for v in viols if time.time() - v["ts"] < 86400]
        if len(recent) >= 3 and mute_minutes == 0:
            try:
                until = datetime.now(timezone.utc) + timedelta(minutes=10)
                await message.author.timeout(until, reason="AutoMod-Eskalation (3 Verstöße in 24h)")
            except Exception:
                pass
        db.save()

        # Log
        from utils import get_log_channel, fuse_embed
        log_ch = get_log_channel(message.guild, "moderation")
        if log_ch:
            emb = fuse_embed(
                "🤖  AutoMod Aktion",
                f"**User:** {message.author.mention} (`{message.author.id}`)\n"
                f"**Grund:** {reason}\n"
                f"**Kanal:** {message.channel.mention}\n"
                f"**Inhalt:** ```{message.content[:300]}```",
                0xE74C3C, guild=message.guild, author=message.author,
            )
            await log_ch.send(embed=emb)

    # ── Message Listener ────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        if is_staff(message.author):
            return

        content_lower = message.content.lower()

        # 1) Bad-Words
        words = re.findall(r"\w+", content_lower)
        if any(w in BAD_WORDS for w in words):
            return await self.punish(message, "Beleidigung / unangemessene Sprache")

        # 2) Discord-Invites
        if INVITE_RE.search(message.content):
            return await self.punish(message, "Discord-Invite gepostet")

        # 3) Scam
        if SCAM_RE.search(message.content):
            return await self.punish(message, "Scam-Link / Free-Nitro-Spam", mute_minutes=30)

        # 4) Verbotene Domains
        urls = URL_RE.findall(message.content)
        for u in urls:
            if not domain_allowed(u):
                return await self.punish(message, "Nicht erlaubter Link")

        # 5) Caps-Lock-Spam
        if len(message.content) >= CAPS_MIN_LEN:
            letters = [c for c in message.content if c.isalpha()]
            if letters:
                caps_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
                if caps_ratio >= CAPS_THRESHOLD:
                    return await self.punish(message, "Caps-Lock-Spam")

        # 6) Message-Spam
        now = time.time()
        history = self.msg_history[message.author.id]
        history.append(now)
        recent = [t for t in history if now - t < SPAM_WINDOW]
        if len(recent) >= SPAM_LIMIT:
            history.clear()
            return await self.punish(message, "Nachrichten-Spam", mute_minutes=5)

    # ── Anti-Raid ───────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        now = time.time()
        self.join_history.append(now)
        recent = [t for t in self.join_history if now - t < RAID_WINDOW]
        if len(recent) >= RAID_LIMIT and not self.raid_lockdown:
            await self.trigger_raid_lockdown(member.guild)

    async def trigger_raid_lockdown(self, guild: discord.Guild):
        self.raid_lockdown = True
        from utils import get_log_channel, fuse_embed
        log_ch = get_log_channel(guild, "moderation")
        if log_ch:
            await log_ch.send(content="@here",
                              embed=fuse_embed(
                                  "🚨  RAID DETECTED",
                                  f"**{RAID_LIMIT}+ Joins in {RAID_WINDOW}s erkannt!**\n"
                                  "Auto-Lockdown aktiv: neue Joins werden in Quarantäne verschoben.\n"
                                  "Benutze `!raid-off` um den Lockdown aufzuheben.",
                                  0xFF0000, guild=guild))

    @commands.command(name="raid-off")
    @commands.has_permissions(administrator=True)
    async def raid_off(self, ctx):
        self.raid_lockdown = False
        await ctx.send("✅  Raid-Lockdown deaktiviert.")


async def setup(bot):
    await bot.add_cog(AutoMod(bot))
