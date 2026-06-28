"""
🏅 XP / LEVEL / LEADERBOARD COG
- Messages = +15-25 XP (mit 60s Cooldown pro User)
- Voice = +5 XP / Minute
- /top messages / voice / xp
- /profile @user
- Monatlicher Spieler-des-Monats
"""
import time
import random
import asyncio
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks
from discord import app_commands

import db


XP_PER_MSG_MIN = 15
XP_PER_MSG_MAX = 25
XP_COOLDOWN    = 60  # Sekunden
XP_PER_VOICE_MIN = 5


def xp_for_level(lvl: int) -> int:
    return 5 * (lvl ** 2) + 50 * lvl + 100


def get_user_data(user_id: int) -> dict:
    d = db.DATA["xp"].setdefault(str(user_id), {
        "xp": 0, "level": 0, "msgs": 0, "voice_minutes": 0, "last_msg_ts": 0,
        "msgs_month": 0, "voice_month": 0,
    })
    # Migration für alte Einträge
    d.setdefault("msgs_month", 0)
    d.setdefault("voice_month", 0)
    return d


class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_loop.start()
        self.monthly_reset.start()

    def cog_unload(self):
        self.voice_loop.cancel()
        self.monthly_reset.cancel()

    # ── Message XP ──────────────────────────────────────────────
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        if message.content.startswith(self.bot.command_prefix):
            return

        d = get_user_data(message.author.id)
        now = time.time()
        d["msgs"] += 1
        d["msgs_month"] += 1
        if now - d.get("last_msg_ts", 0) < XP_COOLDOWN:
            db.save()
            return

        d["last_msg_ts"] = now
        gain = random.randint(XP_PER_MSG_MIN, XP_PER_MSG_MAX)
        d["xp"] += gain
        await self._check_level_up(message.author, message.channel, d)
        db.save()

    # ── Voice XP ────────────────────────────────────────────────
    @tasks.loop(minutes=1)
    async def voice_loop(self):
        await self.bot.wait_until_ready()
        for g in self.bot.guilds:
            for vc in g.voice_channels:
                humans = [m for m in vc.members if not m.bot and not (m.voice.self_deaf or m.voice.deaf)]
                if len(humans) < 2:
                    continue
                for m in humans:
                    d = get_user_data(m.id)
                    d["voice_minutes"] += 1
                    d["voice_month"] += 1
                    d["xp"] += XP_PER_VOICE_MIN
                    await self._check_level_up(m, None, d)
        db.save()

    async def _check_level_up(self, member, channel, d):
        new_lvl = d["level"]
        while d["xp"] >= xp_for_level(new_lvl):
            new_lvl += 1
        if new_lvl > d["level"]:
            d["level"] = new_lvl
            from utils import fuse_embed, find_role
            if channel:
                try:
                    await channel.send(
                        embed=fuse_embed(
                            "🎉  Level-Up!",
                            f"{member.mention} hat **Level {new_lvl}** erreicht!",
                            0xFFD700, guild=member.guild, author=member,
                        ),
                        delete_after=10,
                    )
                except Exception: pass
            # Auto-Rollen
            mapping = {5: "🧪 Trial-Member", 25: "💠 Member", 50: "💠 Member+", 100: "🏆 Veteran", 200: "⭐ Elite"}
            for lvl, role_name in mapping.items():
                if new_lvl >= lvl:
                    r = find_role(member.guild, role_name)
                    if r and r not in member.roles:
                        try: await member.add_roles(r, reason=f"Level {lvl}")
                        except Exception: pass

    # ── /profile ────────────────────────────────────────────────
    @app_commands.command(name="profile", description="Zeigt das Profil eines Users.")
    @app_commands.describe(user="(optional) anderer User")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        target = user or interaction.user
        d = get_user_data(target.id)
        warns = db.DATA["warns"].get(str(target.id), [])
        bday = db.DATA["birthdays"].get(str(target.id))
        cooldown_until = db.DATA["cooldowns"].get(str(target.id))

        from utils import fuse_embed
        next_xp = xp_for_level(d["level"])
        bar_filled = int((d["xp"] / next_xp) * 20) if next_xp else 0
        bar = "█" * bar_filled + "░" * (20 - bar_filled)

        emb = fuse_embed(
            f"📊  Profil von {target.display_name}",
            f"`{bar}` **{d['xp']}/{next_xp} XP**",
            0x3498DB, guild=interaction.guild, author=target,
        )
        emb.add_field(name="🏆  Level",     value=f"`{d['level']}`",         inline=True)
        emb.add_field(name="💬  Messages",  value=f"`{d['msgs']:,}`",        inline=True)
        emb.add_field(name="🎙️  Voice (min)", value=f"`{d['voice_minutes']:,}`", inline=True)
        emb.add_field(name="⚠️  Warns",      value=f"`{len(warns)}/5`",      inline=True)
        emb.add_field(name="📅  Joined",     value=f"<t:{int(target.joined_at.timestamp())}:R>" if target.joined_at else "—", inline=True)
        emb.add_field(name="🎂  Geburtstag", value=f"{bday['day']}.{bday['month']}." if bday else "—", inline=True)
        if cooldown_until:
            emb.add_field(name="📋  Bewerbungs-Sperre", value=f"bis {cooldown_until}", inline=False)
        top_role = next((r for r in reversed(target.roles) if not r.is_default() and r.name[0] not in "▰"), None)
        if top_role:
            emb.add_field(name="🎭  Top-Rolle", value=top_role.mention, inline=False)
        await interaction.response.send_message(embed=emb)

    # ── /top ────────────────────────────────────────────────────
    @app_commands.command(name="top", description="Leaderboard")
    @app_commands.describe(kategorie="Kategorie")
    @app_commands.choices(kategorie=[
        app_commands.Choice(name="XP",       value="xp"),
        app_commands.Choice(name="Messages", value="msgs"),
        app_commands.Choice(name="Voice",    value="voice_minutes"),
        app_commands.Choice(name="Monatlich (Messages)", value="msgs_month"),
        app_commands.Choice(name="Monatlich (Voice)",    value="voice_month"),
    ])
    async def top(self, interaction: discord.Interaction, kategorie: app_commands.Choice[str]):
        sorted_users = sorted(
            db.DATA["xp"].items(),
            key=lambda x: x[1].get(kategorie.value, 0),
            reverse=True,
        )[:10]
        from utils import fuse_embed
        emb = fuse_embed(
            f"🏆  Top 10 — {kategorie.name}",
            "", 0xFFD700, guild=interaction.guild,
        )
        medals = ["🥇", "🥈", "🥉"] + ["▫️"] * 7
        lines = []
        for i, (uid, data) in enumerate(sorted_users):
            member = interaction.guild.get_member(int(uid))
            if not member: continue
            val = data.get(kategorie.value, 0)
            if kategorie.value == "voice_minutes" or kategorie.value == "voice_month":
                val = f"{val:,} min ({val // 60}h)"
            else:
                val = f"{val:,}"
            lines.append(f"{medals[i]}  **{member.display_name}**  •  `{val}`")
        emb.description = "\n".join(lines) or "Noch keine Daten."
        await interaction.response.send_message(embed=emb)

    # ── Monatlicher Reset + Spieler des Monats ──────────────────
    @tasks.loop(hours=1)
    async def monthly_reset(self):
        """Am 1. des Monats: Spieler-des-Monats vergeben, Counter resetten."""
        await self.bot.wait_until_ready()
        now = datetime.now(timezone.utc)
        if now.day != 1 or now.hour != 3:  # 3 Uhr morgens am 1.
            return

        last_key = f"{(now.year if now.month > 1 else now.year - 1)}-{(now.month - 1) if now.month > 1 else 12:02d}"
        if last_key in db.DATA["monthly_winners"]:
            return

        # Top 3 nach msgs_month + voice_month/10
        for g in self.bot.guilds:
            scored = []
            for uid, d in db.DATA["xp"].items():
                score = d.get("msgs_month", 0) + d.get("voice_month", 0) // 10
                if score > 0:
                    scored.append((uid, score))
            scored.sort(key=lambda x: x[1], reverse=True)
            top3 = scored[:3]

            from utils import find_role, fuse_embed
            role = find_role(g, "⭐ Elite")
            winners = []
            for uid, _ in top3:
                m = g.get_member(int(uid))
                if m:
                    winners.append(m.id)
                    if role:
                        try: await m.add_roles(role, reason="Spieler des Monats")
                        except Exception: pass

            # Announce
            ann = discord.utils.get(g.text_channels, name="🔔・ankündigungen") or discord.utils.get(g.text_channels, name="💬・chat")
            if ann and top3:
                lines = []
                medals = ["🥇", "🥈", "🥉"]
                for i, (uid, sc) in enumerate(top3):
                    m = g.get_member(int(uid))
                    if m: lines.append(f"{medals[i]}  {m.mention} — `{sc}` Punkte")
                await ann.send(embed=fuse_embed(
                    f"🏆  Spieler des Monats — {last_key}",
                    "Glückwunsch an unsere aktivsten Member!\n\n" + "\n".join(lines),
                    0xFFD700, guild=g,
                ))

            db.DATA["monthly_winners"][last_key] = winners

        # Reset monthly counters
        for uid in db.DATA["xp"]:
            db.DATA["xp"][uid]["msgs_month"] = 0
            db.DATA["xp"][uid]["voice_month"] = 0
        db.save()


async def setup(bot):
    await bot.add_cog(XP(bot))
