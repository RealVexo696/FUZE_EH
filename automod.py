"""
🕵️ ALT-ACCOUNT DETECTION
Bei Join: Account zu jung / verdächtig → Quarantäne-Rolle, Staff-Ping.
"""
from datetime import datetime, timezone

import discord
from discord.ext import commands

MIN_ACCOUNT_AGE_DAYS = 7


class AltDetection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        from utils import get_log_channel, fuse_embed, find_role

        age_days = (datetime.now(timezone.utc) - member.created_at).days
        suspicious = []
        if age_days < MIN_ACCOUNT_AGE_DAYS:
            suspicious.append(f"Account ist nur **{age_days} Tage** alt")
        if member.avatar is None:
            suspicious.append("Kein Profilbild")
        if member.public_flags.value == 0 and age_days < 30:
            suspicious.append("Keine Discord-Badges")

        if not suspicious:
            return

        # Verwarnt-Rolle als Quarantäne nutzen
        quarantine = find_role(member.guild, "⚠️ Verwarnt")
        if quarantine:
            try: await member.add_roles(quarantine, reason="Alt-Detection")
            except Exception: pass

        log_ch = get_log_channel(member.guild, "moderation")
        if log_ch:
            emb = fuse_embed(
                "🕵️  Verdächtiger Account erkannt",
                f"**User:** {member.mention} (`{member.id}`)\n"
                f"**Erstellt:** <t:{int(member.created_at.timestamp())}:R>\n\n"
                f"**Auffälligkeiten:**\n" + "\n".join(f"• {s}" for s in suspicious) + "\n\n"
                f"*User wurde in Quarantäne gesetzt. Bitte prüfen!*",
                0xE67E22, guild=member.guild, author=member,
            )
            await log_ch.send(content="🕵️  Staff-Check erforderlich", embed=emb)


async def setup(bot):
    await bot.add_cog(AltDetection(bot))
