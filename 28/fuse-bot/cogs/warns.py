"""
⚖️ WARN-SYSTEM COG
- /warn @user reason
- /warnings @user
- /clearwarn @user index
- Auto-Mute bei 3 Warns (1h), Auto-Ban bei 5
"""
import time
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands
from discord import app_commands

import db


AUTO_MUTE_AT = 3
AUTO_BAN_AT  = 5
MUTE_DURATION_HOURS = 1


class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _warns(self, user_id: int) -> list:
        return db.DATA["warns"].get(str(user_id), [])

    def _set_warns(self, user_id: int, warns: list):
        db.DATA["warns"][str(user_id)] = warns
        db.save()

    @app_commands.command(name="warn", description="Verwarnt einen User.")
    @app_commands.describe(user="Zu verwarnender User", reason="Grund der Verwarnung")
    @app_commands.default_permissions(manage_messages=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌  Keine Berechtigung.", ephemeral=True)
        if user.bot:
            return await interaction.response.send_message("❌  Bots können nicht verwarnt werden.", ephemeral=True)
        if user.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌  Du kannst diesen User nicht verwarnen.", ephemeral=True)

        warns = self._warns(user.id)
        warns.append({"reason": reason, "mod_id": interaction.user.id, "ts": time.time()})
        self._set_warns(user.id, warns)

        from utils import fuse_embed, get_log_channel, find_role

        # Verwarnt-Rolle vergeben
        verwarnt = find_role(interaction.guild, "⚠️ Verwarnt")
        if verwarnt and verwarnt not in user.roles:
            try: await user.add_roles(verwarnt, reason="Warn-System")
            except Exception: pass

        emb = fuse_embed(
            "⚠️  Verwarnung erteilt",
            f"**User:** {user.mention}\n"
            f"**Grund:** {reason}\n"
            f"**Verwarnungen gesamt:** `{len(warns)}/{AUTO_BAN_AT}`\n"
            f"**Mod:** {interaction.user.mention}",
            0xE74C3C, guild=interaction.guild, author=user,
        )
        await interaction.response.send_message(embed=emb)

        # DM
        try:
            dm = fuse_embed(
                "⚠️  Du wurdest verwarnt",
                f"Auf **{interaction.guild.name}** wurdest du verwarnt.\n\n"
                f"**Grund:** {reason}\n"
                f"**Verwarnungen:** `{len(warns)}/{AUTO_BAN_AT}`",
                0xE74C3C, guild=interaction.guild,
            )
            await user.send(embed=dm)
        except Exception:
            pass

        # Log
        log_ch = get_log_channel(interaction.guild, "moderation")
        if log_ch:
            await log_ch.send(embed=emb)

        # Auto-Eskalation
        if len(warns) >= AUTO_BAN_AT:
            try:
                await user.ban(reason=f"Auto-Ban: {AUTO_BAN_AT} Verwarnungen")
                await interaction.followup.send(f"🔨  **{user}** wurde wegen {AUTO_BAN_AT} Verwarnungen automatisch gebannt.")
            except Exception:
                pass
        elif len(warns) >= AUTO_MUTE_AT:
            try:
                until = datetime.now(timezone.utc) + timedelta(hours=MUTE_DURATION_HOURS)
                await user.timeout(until, reason=f"Auto-Mute: {AUTO_MUTE_AT}+ Verwarnungen")
                await interaction.followup.send(f"🔇  **{user}** wurde für {MUTE_DURATION_HOURS}h gemutet ({len(warns)} Verwarnungen).")
            except Exception:
                pass

    @app_commands.command(name="warnings", description="Zeigt alle Verwarnungen eines Users.")
    @app_commands.describe(user="Ziel-User")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        warns = self._warns(user.id)
        from utils import fuse_embed
        if not warns:
            emb = fuse_embed("✅  Saubere Weste",
                             f"{user.mention} hat **keine** Verwarnungen.",
                             0x2ECC71, guild=interaction.guild, author=user)
            return await interaction.response.send_message(embed=emb, ephemeral=True)

        emb = fuse_embed(
            f"⚠️  Verwarnungen von {user.display_name}",
            f"Gesamt: **{len(warns)}/{AUTO_BAN_AT}**",
            0xE74C3C, guild=interaction.guild, author=user,
        )
        for i, w in enumerate(warns[-10:], start=1):
            mod = interaction.guild.get_member(w["mod_id"])
            mod_name = mod.mention if mod else f"`{w['mod_id']}`"
            emb.add_field(
                name=f"#{i}  •  <t:{int(w['ts'])}:f>",
                value=f"**Grund:** {w['reason']}\n**Mod:** {mod_name}",
                inline=False,
            )
        await interaction.response.send_message(embed=emb, ephemeral=True)

    @app_commands.command(name="clearwarn", description="Löscht eine Verwarnung.")
    @app_commands.describe(user="Ziel-User", index="Verwarnungs-Nummer (1 = neueste). Lass leer für alle.")
    @app_commands.default_permissions(manage_messages=True)
    async def clearwarn(self, interaction: discord.Interaction, user: discord.Member, index: int = 0):
        if not interaction.user.guild_permissions.manage_messages:
            return await interaction.response.send_message("❌  Keine Berechtigung.", ephemeral=True)
        warns = self._warns(user.id)
        from utils import fuse_embed
        if not warns:
            return await interaction.response.send_message("ℹ️  Keine Verwarnungen vorhanden.", ephemeral=True)
        if index == 0:
            self._set_warns(user.id, [])
            return await interaction.response.send_message(
                embed=fuse_embed("✅  Alle Verwarnungen gelöscht",
                                 f"{user.mention} hat jetzt 0 Verwarnungen.",
                                 0x2ECC71, guild=interaction.guild, author=user))
        if 1 <= index <= len(warns):
            warns.pop(-index)
            self._set_warns(user.id, warns)
            return await interaction.response.send_message(
                embed=fuse_embed("✅  Verwarnung gelöscht",
                                 f"Verbleibend: {len(warns)}",
                                 0x2ECC71, guild=interaction.guild, author=user))
        await interaction.response.send_message("❌  Ungültiger Index.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Warns(bot))
