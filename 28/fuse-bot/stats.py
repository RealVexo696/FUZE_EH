"""
📊 SERVER-STATISTIK DASHBOARD
=============================
Voice-Channels mit Live-Zahlen — ganz oben im Server,
sichtbar für JEDEN (auch Unverified) aber niemand kann reinjoinen.

Stats:
  👥 Member  •  🟢 Online  •  🎙️ In Voice  •  🤖 Bots  •  🚀 Boosts

Updates:
  - Beim Start
  - Bei Member-Join / Leave
  - Bei Boost-Änderungen
  - Alle 10 Minuten als Fallback
"""
import asyncio

import discord
from discord.ext import commands, tasks

import db


CATEGORY_NAME = "📊 ✘ SERVER STATS"

# Templates für die Voice-Channels (Reihenfolge = Anzeige-Reihenfolge)
STATS_TEMPLATES = [
    ("members", "👥 Member: {count}"),
    ("online",  "🟢 Online: {count}"),
    ("voice",   "🎙️ In Voice: {count}"),
    ("bots",    "🤖 Bots: {count}"),
    ("boosts",  "🚀 Boosts: {count}"),
]


class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._setup_lock = asyncio.Lock()
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    # ─────────────────────────────────────────────────────────────
    # SETUP — Kategorie + Channels erstellen
    # ─────────────────────────────────────────────────────────────
    async def ensure_setup(self, guild: discord.Guild):
        """Erstellt Stats-Kategorie + Channels falls noch nicht da. Idempotent."""
        async with self._setup_lock:
            stats = db.DATA["stats_channels"]

            # Kategorie suchen oder erstellen
            cat = discord.utils.get(guild.categories, name=CATEGORY_NAME)
            if not cat:
                # Sichtbar für ALLE, aber niemand darf connecten
                cat_ow = {
                    guild.default_role: discord.PermissionOverwrite(
                        view_channel=True, connect=False, send_messages=False,
                    ),
                }
                try:
                    cat = await guild.create_category(
                        CATEGORY_NAME, overwrites=cat_ow,
                        reason="FUSE Stats Setup",
                    )
                except Exception as e:
                    print(f"[Stats] Kategorie-Erstellung fail: {e}")
                    return

            # Ganz nach oben verschieben
            try:
                if cat.position != 0:
                    await cat.edit(position=0)
            except Exception:
                pass

            # Channels erstellen / fixen
            for key, template in STATS_TEMPLATES:
                ch_id = stats.get(key)
                ch = guild.get_channel(ch_id) if ch_id else None
                # falls Channel gelöscht wurde -> neu anlegen
                if not ch:
                    try:
                        ch_ow = {
                            guild.default_role: discord.PermissionOverwrite(
                                view_channel=True, connect=False, send_messages=False,
                            ),
                        }
                        ch = await guild.create_voice_channel(
                            template.format(count="…"),
                            category=cat, overwrites=ch_ow,
                            reason="FUSE Stats Channel",
                        )
                        stats[key] = ch.id
                    except Exception as e:
                        print(f"[Stats] Channel '{key}' fail: {e}")
                        continue
                else:
                    # Stelle sicher, dass er in der richtigen Kategorie ist
                    if ch.category_id != cat.id:
                        try: await ch.edit(category=cat)
                        except Exception: pass
                    # Permissions fixen (auch Unverified darf sehen)
                    try:
                        await ch.edit(overwrites={
                            guild.default_role: discord.PermissionOverwrite(
                                view_channel=True, connect=False, send_messages=False,
                            ),
                        })
                    except Exception: pass

            db.save()
            await self.update_one(guild)

    # ─────────────────────────────────────────────────────────────
    # COMMANDS
    # ─────────────────────────────────────────────────────────────
    @commands.command(name="stats-setup")
    @commands.has_permissions(administrator=True)
    async def setup_cmd(self, ctx):
        """Manuelles Setup / Reset der Stats-Channels."""
        await ctx.send("⏳  Stats-Channels werden eingerichtet…")
        await self.ensure_setup(ctx.guild)
        await ctx.send("✅  Stats-Channels erstellt & aktualisiert!\n"
                       f"➤  `{CATEGORY_NAME}` ist jetzt ganz oben sichtbar für alle.")

    @commands.command(name="stats-update")
    @commands.has_permissions(administrator=True)
    async def manual_update(self, ctx):
        """Sofort-Update aller Stats-Channels (für Tests)."""
        await self.update_one(ctx.guild)
        await ctx.send("✅  Stats aktualisiert.")

    # ─────────────────────────────────────────────────────────────
    # UPDATER
    # ─────────────────────────────────────────────────────────────
    async def update_one(self, guild: discord.Guild):
        stats = db.DATA["stats_channels"]
        if not stats:
            return
        try:
            members = sum(1 for m in guild.members if not m.bot)
            online  = sum(1 for m in guild.members
                          if not m.bot and m.status != discord.Status.offline)
            voice   = sum(1 for m in guild.members
                          if m.voice and m.voice.channel and not m.bot)
            bots    = sum(1 for m in guild.members if m.bot)
            boosts  = guild.premium_subscription_count or 0

            counts = {
                "members": members,
                "online":  online,
                "voice":   voice,
                "bots":    bots,
                "boosts":  boosts,
            }

            for key, template in STATS_TEMPLATES:
                ch = guild.get_channel(stats.get(key, 0))
                if not ch:
                    continue
                new_name = template.format(count=counts[key])
                if ch.name != new_name:
                    try:
                        await ch.edit(name=new_name)
                    except discord.HTTPException as e:
                        # Rate-Limit bei Channel-Renames: 2 pro 10min
                        if e.status == 429:
                            print(f"[Stats] Rate-limited bei '{key}' — skip")
                        else:
                            print(f"[Stats] edit '{key}' fail: {e}")
                    except Exception as e:
                        print(f"[Stats] edit '{key}' unexpected: {e}")
        except Exception as e:
            print(f"[Stats] update fail: {e}")

    # ─────────────────────────────────────────────────────────────
    # AUTO-UPDATE-TRIGGER
    # ─────────────────────────────────────────────────────────────
    @tasks.loop(minutes=10)
    async def update_stats(self):
        await self.bot.wait_until_ready()
        for g in self.bot.guilds:
            await self.update_one(g)

    @commands.Cog.listener()
    async def on_ready(self):
        """Beim ersten Start: Stats automatisch einrichten falls noch nicht da."""
        await asyncio.sleep(3)  # kurz warten bis cache full ist
        for g in self.bot.guilds:
            # Auto-Setup nur wenn Kategorie noch nicht existiert
            if not discord.utils.get(g.categories, name=CATEGORY_NAME):
                try:
                    await self.ensure_setup(g)
                except Exception as e:
                    print(f"[Stats] Auto-Setup fail für {g.name}: {e}")
            else:
                # Existiert schon -> nur Counts updaten
                await self.update_one(g)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.update_one(member.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.update_one(member.guild)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        # Nur updaten wenn Boost-Status sich änderte
        if before.premium_since != after.premium_since:
            await self.update_one(after.guild)


async def setup(bot):
    await bot.add_cog(Stats(bot))
