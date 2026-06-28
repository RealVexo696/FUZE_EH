"""
📈 SERVER-STATISTIK DASHBOARD
Erstellt Voice-Channels mit Live-Zahlen (Member, Online, In Voice, Bots).
Aktualisiert alle 10 Min.
"""
import asyncio

import discord
from discord.ext import commands, tasks

import db


CATEGORY_NAME = "📊 ✘ SERVER STATS"


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @commands.command(name="stats-setup")
    @commands.has_permissions(administrator=True)
    async def setup_stats(self, ctx):
        """Erstellt die Stats-Kategorie + Voice-Channels."""
        g = ctx.guild
        # Kategorie
        cat = discord.utils.get(g.categories, name=CATEGORY_NAME)
        if not cat:
            ow = {g.default_role: discord.PermissionOverwrite(connect=False)}
            cat = await g.create_category(CATEGORY_NAME, overwrites=ow, reason="Stats")
            try:
                await cat.move(beginning=True)
            except Exception:
                pass

        stats = db.DATA["stats_channels"]
        defaults = {
            "members": "📊 Member: {count}",
            "online":  "🟢 Online: {count}",
            "voice":   "🎮 In Voice: {count}",
            "bots":    "🤖 Bots: {count}",
        }
        for key, template in defaults.items():
            ch_id = stats.get(key)
            ch = g.get_channel(ch_id) if ch_id else None
            if not ch:
                ow = {g.default_role: discord.PermissionOverwrite(connect=False, view_channel=True)}
                ch = await g.create_voice_channel(template.format(count="…"), category=cat, overwrites=ow)
                stats[key] = ch.id
        db.save()
        await ctx.send("✅  Stats-Channels erstellt! Aktualisierung läuft alle 10 Minuten.")
        await self._update_for_guild(g)

    async def _update_for_guild(self, guild: discord.Guild):
        stats = db.DATA["stats_channels"]
        if not stats:
            return
        try:
            members = sum(1 for m in guild.members if not m.bot)
            online  = sum(1 for m in guild.members if not m.bot and m.status != discord.Status.offline)
            voice   = sum(1 for m in guild.members if m.voice and m.voice.channel and not m.bot)
            bots    = sum(1 for m in guild.members if m.bot)

            mapping = {
                "members": f"📊 Member: {members}",
                "online":  f"🟢 Online: {online}",
                "voice":   f"🎮 In Voice: {voice}",
                "bots":    f"🤖 Bots: {bots}",
            }
            for key, new_name in mapping.items():
                ch = guild.get_channel(stats.get(key, 0))
                if ch and ch.name != new_name:
                    try:
                        await ch.edit(name=new_name)
                    except Exception:
                        pass
        except Exception as e:
            print(f"[Stats] update fail: {e}")

    @tasks.loop(minutes=10)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        for g in self.bot.guilds:
            await self._update_for_guild(g)


async def setup(bot):
    await bot.add_cog(Stats(bot))
