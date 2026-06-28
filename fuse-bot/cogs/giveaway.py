"""
🎁 GIVEAWAY SYSTEM
- /giveaway create
- 🎉 Button zum Mitmachen
- Auto-Ziehung nach Ablauf
- Re-Roll Button
"""
import time
import random
import asyncio
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands, tasks
from discord import app_commands

import db


def parse_duration(s: str) -> int:
    """'1d' / '2h' / '30m' / '90' -> Sekunden"""
    s = s.strip().lower()
    try:
        if s.endswith("d"): return int(s[:-1]) * 86400
        if s.endswith("h"): return int(s[:-1]) * 3600
        if s.endswith("m"): return int(s[:-1]) * 60
        if s.endswith("s"): return int(s[:-1])
        return int(s) * 60  # default: Minuten
    except Exception:
        return 0


class GiveawayJoinView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Teilnehmen", style=discord.ButtonStyle.success, emoji="🎉", custom_id="ga_join")
    async def join(self, interaction: discord.Interaction, button):
        ga = db.DATA["giveaways"].get(str(interaction.message.id))
        if not ga:
            return await interaction.response.send_message("❌  Giveaway nicht gefunden.", ephemeral=True)
        if ga.get("ended"):
            return await interaction.response.send_message("❌  Giveaway bereits beendet.", ephemeral=True)
        # Required Role?
        req_id = ga.get("role_required")
        if req_id:
            role = interaction.guild.get_role(req_id)
            if role and role not in interaction.user.roles:
                return await interaction.response.send_message(
                    f"❌  Du brauchst die Rolle {role.mention} um teilzunehmen.", ephemeral=True,
                )
        entries = ga.setdefault("entries", [])
        uid = interaction.user.id
        if uid in entries:
            entries.remove(uid)
            db.save()
            return await interaction.response.send_message("⛔  Du hast deine Teilnahme zurückgezogen.", ephemeral=True)
        entries.append(uid)
        db.save()
        await interaction.response.send_message(f"🎉  Du bist im Giveaway! Aktuelle Teilnehmer: **{len(entries)}**", ephemeral=True)


class GiveawayRerollView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Re-Roll", style=discord.ButtonStyle.primary, emoji="🔄", custom_id="ga_reroll")
    async def reroll(self, interaction, button):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌  Keine Berechtigung.", ephemeral=True)
        ga = db.DATA["giveaways"].get(str(interaction.message.id))
        if not ga:
            return await interaction.response.send_message("❌  Daten nicht gefunden.", ephemeral=True)
        entries = ga.get("entries", [])
        if not entries:
            return await interaction.response.send_message("❌  Keine Teilnehmer.", ephemeral=True)
        winners = random.sample(entries, min(ga.get("winners_count", 1), len(entries)))
        mentions = ", ".join(f"<@{u}>" for u in winners)
        await interaction.response.send_message(f"🔄  **Re-Roll Gewinner:** {mentions}  •  Preis: **{ga['prize']}**")


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checker.start()

    def cog_unload(self):
        self.checker.cancel()

    @app_commands.command(name="giveaway", description="Erstellt ein Giveaway.")
    @app_commands.describe(prize="Preis", duration="Dauer (z.B. 1d, 2h, 30m)", winners="Anzahl Gewinner", role="(optional) benötigte Rolle")
    @app_commands.default_permissions(manage_messages=True)
    async def create(self, interaction: discord.Interaction, prize: str, duration: str, winners: int = 1, role: discord.Role = None):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌  Keine Berechtigung.", ephemeral=True)
        seconds = parse_duration(duration)
        if seconds <= 0:
            return await interaction.response.send_message("❌  Ungültige Dauer. Beispiel: `1d`, `2h`, `30m`.", ephemeral=True)
        end_ts = time.time() + seconds

        from utils import fuse_embed
        emb = fuse_embed(
            f"🎁  GIVEAWAY  •  {prize}",
            f"### Klicke unten auf **🎉 Teilnehmen**!\n\n"
            f"➤  **Gewinner:** {winners}\n"
            f"➤  **Endet:** <t:{int(end_ts)}:R>  (<t:{int(end_ts)}:F>)\n"
            f"➤  **Host:** {interaction.user.mention}\n"
            + (f"➤  **Benötigte Rolle:** {role.mention}\n" if role else ""),
            0xF1C40F, guild=interaction.guild, author=interaction.user,
        )
        await interaction.response.send_message(embed=emb, view=GiveawayJoinView())
        msg = await interaction.original_response()

        db.DATA["giveaways"][str(msg.id)] = {
            "prize": prize,
            "end_ts": end_ts,
            "winners_count": winners,
            "host_id": interaction.user.id,
            "channel_id": interaction.channel.id,
            "role_required": role.id if role else None,
            "entries": [],
            "ended": False,
        }
        db.save()

    @tasks.loop(seconds=30)
    async def checker(self):
        await self.bot.wait_until_ready()
        now = time.time()
        for mid, ga in list(db.DATA["giveaways"].items()):
            if ga.get("ended"): continue
            if now < ga["end_ts"]: continue
            await self._end_giveaway(int(mid), ga)

    async def _end_giveaway(self, message_id: int, ga: dict):
        ga["ended"] = True
        db.save()
        ch = self.bot.get_channel(ga["channel_id"])
        if not ch: return
        try:
            msg = await ch.fetch_message(message_id)
        except Exception:
            return

        from utils import fuse_embed
        entries = ga.get("entries", [])
        if not entries:
            emb = fuse_embed(
                f"🎁  GIVEAWAY BEENDET  •  {ga['prize']}",
                "😢  **Keine Teilnehmer** — kein Gewinner.",
                0xE74C3C, guild=ch.guild,
            )
            try: await msg.edit(embed=emb, view=None)
            except: pass
            return

        winners = random.sample(entries, min(ga["winners_count"], len(entries)))
        mentions = ", ".join(f"<@{u}>" for u in winners)
        emb = fuse_embed(
            f"🎉  GIVEAWAY BEENDET  •  {ga['prize']}",
            f"### 🏆  Gewinner: {mentions}\n\n"
            f"Teilnehmer: **{len(entries)}**\n"
            f"Host: <@{ga['host_id']}>",
            0xFFD700, guild=ch.guild,
        )
        try: await msg.edit(embed=emb, view=GiveawayRerollView())
        except: pass
        try:
            await ch.send(f"🎉  Glückwunsch {mentions}! Du hast **{ga['prize']}** gewonnen!")
        except: pass


async def setup(bot):
    await bot.add_cog(Giveaway(bot))
