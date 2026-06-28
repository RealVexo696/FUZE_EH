"""
🎂 GEBURTSTAGS-SYSTEM
- /birthday set / remove / list
- Täglicher Check (8 Uhr) -> Ping + Rolle 24h
"""
from datetime import datetime, timezone, timedelta

import discord
from discord.ext import commands, tasks
from discord import app_commands

import db


class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checker.start()

    def cog_unload(self):
        self.checker.cancel()

    @app_commands.command(name="birthday", description="Geburtstag verwalten.")
    @app_commands.describe(aktion="set / remove / list", tag="1-31", monat="1-12")
    @app_commands.choices(aktion=[
        app_commands.Choice(name="set",    value="set"),
        app_commands.Choice(name="remove", value="remove"),
        app_commands.Choice(name="list",   value="list"),
    ])
    async def birthday(self, interaction: discord.Interaction, aktion: app_commands.Choice[str],
                       tag: int = 0, monat: int = 0):
        uid = str(interaction.user.id)
        from utils import fuse_embed
        if aktion.value == "set":
            if not (1 <= tag <= 31) or not (1 <= monat <= 12):
                return await interaction.response.send_message("❌  Ungültiges Datum.", ephemeral=True)
            db.DATA["birthdays"][uid] = {"day": tag, "month": monat}
            db.save()
            await interaction.response.send_message(
                embed=fuse_embed("🎂  Geburtstag gespeichert",
                                 f"Wir gratulieren dir am **{tag}.{monat}.** 🎉",
                                 0xFF69B4, guild=interaction.guild, author=interaction.user),
                ephemeral=True,
            )
        elif aktion.value == "remove":
            db.DATA["birthdays"].pop(uid, None)
            db.save()
            await interaction.response.send_message("✅  Geburtstag gelöscht.", ephemeral=True)
        elif aktion.value == "list":
            bdays = db.DATA["birthdays"]
            if not bdays:
                return await interaction.response.send_message("ℹ️  Noch keine Geburtstage.", ephemeral=True)
            sorted_b = sorted(bdays.items(), key=lambda x: (x[1]["month"], x[1]["day"]))
            lines = []
            for uid, b in sorted_b:
                m = interaction.guild.get_member(int(uid))
                if m: lines.append(f"🎂  **{b['day']:02d}.{b['month']:02d}.**  —  {m.mention}")
            await interaction.response.send_message(
                embed=fuse_embed("🎂  Geburtstage", "\n".join(lines[:50]),
                                 0xFF69B4, guild=interaction.guild),
                ephemeral=True,
            )

    @tasks.loop(hours=1)
    async def checker(self):
        await self.bot.wait_until_ready()
        now = datetime.now(timezone.utc)
        if now.hour != 8:
            return
        today = (now.day, now.month)
        for g in self.bot.guilds:
            chat = discord.utils.get(g.text_channels, name="💬・chat") \
                or discord.utils.get(g.text_channels, name="👋・willkommen")
            if not chat: continue
            from utils import find_role, fuse_embed
            role = find_role(g, "🎂 Geburtstagskind")
            # Alte Geburtstagskinder de-rollen
            if role:
                for m in list(role.members):
                    try: await m.remove_roles(role, reason="Geburtstag vorbei")
                    except: pass

            for uid, b in db.DATA["birthdays"].items():
                if (b["day"], b["month"]) != today: continue
                member = g.get_member(int(uid))
                if not member: continue
                if role:
                    try: await member.add_roles(role, reason="Heute Geburtstag")
                    except: pass
                emb = fuse_embed(
                    "🎂🎉  HEUTE GEBURTSTAG! 🎉🎂",
                    f"### Alles Gute zum Geburtstag {member.mention}! 🥳\n\n"
                    f"Wir wünschen dir einen tollen Tag!\n"
                    f"Das gesamte **FUSE | FS** Team feiert mit dir!",
                    0xFF69B4, guild=g, author=member,
                )
                emb.set_image(url="https://media.tenor.com/x8v1oNUOmg4AAAAd/happy-birthday.gif")
                await chat.send(content=member.mention, embed=emb)


async def setup(bot):
    await bot.add_cog(Birthday(bot))
