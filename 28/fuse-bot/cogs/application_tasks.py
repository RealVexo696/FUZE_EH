"""
⏰ BEWERBUNGS-REMINDER & AUTO-CLOSE
- Check stündlich: alle offenen Bewerbungen
- > 48h offen -> Recruiter-Ping
- > 7 Tage offen -> Auto-Close + DM
"""
import time
import asyncio
from datetime import datetime, timezone

import discord
from discord.ext import commands, tasks

import db


REMIND_AFTER_HOURS = 48
AUTOCLOSE_AFTER_HOURS = 24 * 7


class ApplicationTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.checker.start()

    def cog_unload(self):
        self.checker.cancel()

    @tasks.loop(hours=1)
    async def checker(self):
        await self.bot.wait_until_ready()
        now = time.time()
        for mid, app in list(db.DATA.get("applications", {}).items()):
            if app.get("decided"): continue
            age_h = (now - app["posted_ts"]) / 3600
            ch = self.bot.get_channel(app["channel_id"])
            if not ch: continue

            # 48h Reminder
            if age_h >= REMIND_AFTER_HOURS and not app.get("reminded"):
                from utils import find_role
                rec = find_role(ch.guild, "📝 Recruiter")
                mention = rec.mention if rec else "@Staff"
                try:
                    await ch.send(f"⏰  {mention} — Bewerbung von <@{app['applicant_id']}> wartet seit **{int(age_h)}h** auf eine Antwort!")
                    app["reminded"] = True
                    db.save()
                except Exception: pass

            # 7d Auto-Close
            if age_h >= AUTOCLOSE_AFTER_HOURS:
                from utils import fuse_embed
                try:
                    msg = await ch.fetch_message(int(mid))
                    emb = fuse_embed(
                        "⏰  AUTO-CLOSE",
                        f"Diese Bewerbung wurde nach **7 Tagen** automatisch geschlossen.\n"
                        f"Bewerber: <@{app['applicant_id']}>",
                        0x95A5A6, guild=ch.guild,
                    )
                    await msg.reply(embed=emb)
                    app["decided"] = "auto_closed"
                    db.save()
                    # DM
                    member = ch.guild.get_member(app["applicant_id"])
                    if member:
                        try:
                            await member.send(embed=fuse_embed(
                                "⏰  Bewerbung automatisch geschlossen",
                                "Deine Bewerbung wurde nach 7 Tagen ohne Bearbeitung geschlossen.\n"
                                "Du kannst dich jederzeit neu bewerben.",
                                0x95A5A6,
                            ))
                        except: pass
                except Exception: pass


async def setup(bot):
    await bot.add_cog(ApplicationTasks(bot))
