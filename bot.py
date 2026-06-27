import os
import asyncio
from typing import Optional, Dict, List, Tuple

import discord
from discord.ext import commands
from discord import app_commands

# =========================
# FUSE | FS Setup Bot
# Railway/GitHub ready
# =========================
# ENV:
#   DISCORD_TOKEN=dein_bot_token
# Optional:
#   COMMAND_PREFIX=!
#
# Wichtig:
# - Aktiviere im Discord Developer Portal unter Bot: SERVER MEMBERS INTENT und MESSAGE CONTENT INTENT.
# - Gib dem Bot auf deinem Server Administrator-Rechte.
# - Die Bot-Rolle muss über allen Rollen stehen, die der Bot erstellen/verwalten soll.

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("COMMAND_PREFIX", "!")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True
intents.messages = True
intents.reactions = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

BRAND = "FUSE | FS"
THEME_COLOR = discord.Color.from_rgb(255, 60, 90)

# ---------- Rollen: low -> high, damit Owner am Ende/oben landet ----------
ROLE_DEFS: List[Tuple[str, discord.Color, discord.Permissions, bool]] = [
    ("❌ Unverified", discord.Color.dark_grey(), discord.Permissions.none(), False),
    ("✅ Verified", discord.Color.green(), discord.Permissions.none(), False),
    ("👤 Member", discord.Color.light_grey(), discord.Permissions.none(), False),
    ("🌱 Newcomer", discord.Color.from_rgb(130, 200, 130), discord.Permissions.none(), False),
    ("💬 Aktiv", discord.Color.from_rgb(70, 180, 255), discord.Permissions.none(), False),
    ("🔥 Stammgast", discord.Color.orange(), discord.Permissions.none(), False),
    ("⭐ Elite Member", discord.Color.gold(), discord.Permissions.none(), False),
    ("💎 VIP", discord.Color.teal(), discord.Permissions.none(), False),
    ("👑 Premium", discord.Color.purple(), discord.Permissions.none(), False),
    ("🎁 Booster", discord.Color.magenta(), discord.Permissions.none(), True),
    ("🎮 Gamer", discord.Color.blurple(), discord.Permissions.none(), False),
    ("🎨 Designer", discord.Color.from_rgb(255, 120, 200), discord.Permissions.none(), False),
    ("🎬 Cutter", discord.Color.from_rgb(160, 90, 255), discord.Permissions.none(), False),
    ("📸 Media", discord.Color.from_rgb(255, 180, 60), discord.Permissions.none(), False),
    ("🤝 Partner", discord.Color.from_rgb(30, 200, 200), discord.Permissions.none(), False),
    ("🏢 Firma", discord.Color.from_rgb(80, 160, 255), discord.Permissions.none(), False),
    ("🚨 NH Crime", discord.Color.from_rgb(210, 50, 50), discord.Permissions.none(), False),
    ("🕵️ Informant", discord.Color.dark_teal(), discord.Permissions.none(), False),
    ("🔫 Gang Member", discord.Color.dark_red(), discord.Permissions.none(), False),
    ("🧢 Runner", discord.Color.from_rgb(90, 90, 160), discord.Permissions.none(), False),
    ("💼 Dealer", discord.Color.from_rgb(120, 70, 40), discord.Permissions.none(), False),
    ("🛡️ Security", discord.Color.from_rgb(80, 80, 80), discord.Permissions.none(), False),
    ("🏦 Buchhaltung", discord.Color.from_rgb(100, 160, 100), discord.Permissions.none(), False),
    ("🎫 Ticket Support", discord.Color.from_rgb(90, 200, 255), discord.Permissions(manage_channels=True, read_message_history=True, send_messages=True), False),
    ("📝 Bewerbungsteam", discord.Color.from_rgb(120, 170, 255), discord.Permissions(read_message_history=True, send_messages=True), False),
    ("🎤 Event Team", discord.Color.from_rgb(240, 160, 60), discord.Permissions(manage_events=True), False),
    ("📢 Social Media", discord.Color.from_rgb(255, 90, 160), discord.Permissions(send_messages=True), False),
    ("🧪 Probe Support", discord.Color.from_rgb(120, 220, 220), discord.Permissions(kick_members=True), False),
    ("🟢 Supporter", discord.Color.from_rgb(60, 220, 120), discord.Permissions(kick_members=True, manage_messages=True), False),
    ("🔵 Senior Supporter", discord.Color.blue(), discord.Permissions(kick_members=True, manage_messages=True, move_members=True), False),
    ("🟣 Moderator", discord.Color.purple(), discord.Permissions(kick_members=True, moderate_members=True, manage_messages=True, move_members=True), False),
    ("🟠 Senior Moderator", discord.Color.orange(), discord.Permissions(kick_members=True, ban_members=True, moderate_members=True, manage_messages=True, move_members=True), False),
    ("🔴 Admin", discord.Color.red(), discord.Permissions(administrator=True), False),
    ("⚡ Senior Admin", discord.Color.dark_red(), discord.Permissions(administrator=True), False),
    ("🧠 Management", discord.Color.from_rgb(255, 210, 80), discord.Permissions(administrator=True), False),
    ("💼 Teamleitung", discord.Color.from_rgb(255, 190, 50), discord.Permissions(administrator=True), False),
    ("🛠️ Technik", discord.Color.from_rgb(40, 210, 255), discord.Permissions(administrator=True), False),
    ("📌 Projektleitung", discord.Color.from_rgb(255, 140, 40), discord.Permissions(administrator=True), False),
    ("🧬 Developer", discord.Color.from_rgb(80, 255, 200), discord.Permissions(administrator=True), False),
    ("🤖 Bot", discord.Color.from_rgb(110, 180, 255), discord.Permissions.none(), False),
    ("🎖️ High Team", discord.Color.from_rgb(255, 100, 100), discord.Permissions(administrator=True), False),
    ("👮 Stv. Leitung", discord.Color.from_rgb(180, 60, 255), discord.Permissions(administrator=True), False),
    ("👑 Leitung", discord.Color.from_rgb(255, 70, 180), discord.Permissions(administrator=True), False),
    ("💠 Co Owner", discord.Color.from_rgb(120, 255, 255), discord.Permissions(administrator=True), False),
    ("🔥 Owner", discord.Color.from_rgb(255, 0, 70), discord.Permissions(administrator=True), False),
]

SETUP_ROLE_NAMES = {r[0] for r in ROLE_DEFS}

# ---------- Server Struktur ----------
# channel tuple: (type, name, topic/bitrate-note)
STRUCTURE = [
    ("🔰 X WILLKOMMEN", [
        ("text", "👋・willkommen", "Hier werden neue Mitglieder begrüßt."),
        ("text", "📜・regelwerk", "Regeln von FUSE | FS."),
        ("text", "✅・verify", "Verifiziere dich hier per Button."),
        ("text", "👋・tschüss", "Leave-Nachrichten."),
    ]),
    ("🌐 X COMMUNITY", [
        ("text", "💬・chat", "Allgemeiner Chat."),
        ("text", "📸・socialmedia", "TikTok, YouTube, Clips und Social Media."),
        ("text", "🤖・bot-commands", "Bot Befehle."),
        ("text", "🎮・gaming", "Gaming Talk."),
        ("text", "📷・bilder", "Bilder und Screenshots."),
    ]),
    ("🌎 X BEWERBUNG", [
        ("text", "🎫・ticket", "Support- und Bewerbungstickets."),
        ("text", "👾・bewerbungschat", "Bewerbungsfragen und Infos."),
        ("text", "📋・formular", "Bewerbungsformular."),
        ("voice", "🛋️・warteraum", "Warteraum"),
        ("voice", "💼・Einreise ¹", "Einreise"),
        ("voice", "💼・Einreise ²", "Einreise"),
    ]),
    ("📣 X INFOS", [
        ("text", "✅・activity-check", "Aktivitätschecks."),
        ("text", "🔔・ankündigung", "Ankündigungen."),
        ("text", "🎬・meeting-clips", "Meetings und Clips."),
        ("text", "🔮・boosts", "Boost Infos."),
        ("text", "😂・hall-of-shame", "Hall of Shame."),
        ("text", "🎥・free-tt-vid", "Freie TikTok Videos."),
    ]),
    ("🛒 X BROS MERCH", [
        ("text", "🦺・weste", "Merch Weste."),
        ("text", "🧪・armband", "Merch Armband."),
        ("text", "👕・merch", "Allgemeiner Merch."),
        ("text", "👕・trikot", "Trikot."),
        ("text", "👕・polo", "Polo."),
    ]),
    ("💜 X GANG INFOS", [
        ("text", "💗・farbe", "Gang Farbe."),
        ("text", "🎉・rollensystem", "Rollensystem."),
        ("text", "🎮・roblox-gruppe", "Roblox Gruppe."),
        ("text", "🏠・anwesen", "Anwesen."),
        ("text", "🛡️・partnerschaft", "Partnerschaften."),
    ]),
    ("📞 X TALKS", [
        ("voice", "🌎・FFA VoiceChat", "FFA"),
        ("voice", "🔊・Talk 1", "Talk"),
        ("voice", "🔊・Talk 2", "Talk"),
        ("voice", "🎮・Gaming 1", "Gaming"),
        ("voice", "🎮・Gaming 2", "Gaming"),
        ("voice", "🎵・Musik", "Musik"),
        ("stage", "🎙️・Stage", "Stage"),
    ]),
    ("🔒 TEAM BEREICH", [
        ("text", "💬・team-chat", "Interner Teamchat."),
        ("text", "🛡️・admin-chat", "Admin Chat."),
        ("text", "📌・team-infos", "Team Infos."),
        ("text", "📋・team-todo", "Team ToDos."),
        ("voice", "👑・Owner Büro", "Büro"),
        ("voice", "💠・Co Owner Büro", "Büro"),
        ("voice", "🧠・Management Büro", "Büro"),
        ("voice", "🛡️・Admin Büro", "Büro"),
        ("voice", "🟣・Mod Büro", "Büro"),
    ]),
    ("📁 LOGS", [
        ("text", "👋・welcome-logs", "Join Logs."),
        ("text", "✅・verify-logs", "Verify Logs."),
        ("text", "👋・leave-logs", "Leave Logs."),
        ("text", "📝・message-logs", "Message Logs."),
        ("text", "🎤・voice-logs", "Voice Logs."),
        ("text", "🎫・ticket-logs", "Ticket Logs."),
        ("text", "🛡️・mod-logs", "Moderation Logs."),
        ("text", "👥・member-logs", "Member Update Logs."),
        ("text", "⚙️・server-logs", "Server Logs."),
        ("text", "🚪・join-leave-logs", "Join/Leave Logs."),
    ]),
]

TEXTS = {
    "📜・regelwerk": """# 📜 REGELWERK — FUSE | FS\n\n**1. Respekt** — Beleidigungen, Rassismus, Sexismus und Hate sind verboten.\n**2. Kein Spam** — Keine Werbung, kein Caps-Spam, keine Mass-Pings.\n**3. Datenschutz** — Keine privaten Daten veröffentlichen.\n**4. Voice Regeln** — Kein Soundboard-Spam, kein Trolling.\n**5. Team-Anweisungen** — Folge den Anweisungen vom Team.\n**6. Crime RP Vibe** — Bleibt clean, fair und respektvoll.\n\nMit der Verifizierung akzeptierst du diese Regeln.""",
    "📋・formular": """# 📋 Bewerbungsformular\n\nKopiere das Formular in ein Ticket:\n\n**Name:**\n**Alter:**\n**Warum willst du zu FUSE | FS?**\n**Erfahrung in Notruf Hamburg / Crime RP:**\n**Stärken:**\n**Onlinezeiten:**\n\nEin Teammitglied meldet sich bei dir.""",
    "👾・bewerbungschat": "Willkommen im Bewerbungschat. Bei Fragen öffne bitte ein Ticket in <#TICKET_CHANNEL#>.",
    "🔔・ankündigung": "# 🔔 Ankündigungen\nHier posten Owner/Leitung wichtige News.",
    "🎉・rollensystem": "# 🎉 Rollensystem\nRollen werden vom Team vergeben. Booster/VIP/Spezialrollen können extra freigeschaltet werden.",
}


def role_name(guild: discord.Guild, name: str) -> Optional[discord.Role]:
    return discord.utils.get(guild.roles, name=name)


def channel_name(guild: discord.Guild, name: str):
    return discord.utils.get(guild.channels, name=name)


async def send_log(guild: discord.Guild, channel_name_: str, embed: discord.Embed):
    ch = discord.utils.get(guild.text_channels, name=channel_name_)
    if ch:
        try:
            await ch.send(embed=embed)
        except discord.Forbidden:
            pass


class SetupView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Nur die Person, die `!start` ausgeführt hat, kann diese Buttons nutzen.", ephemeral=True)
            return False
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Du brauchst Administrator-Rechte.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Abbruch", style=discord.ButtonStyle.danger, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="❌ Setup abgebrochen.", embed=None, view=None)

    @discord.ui.button(label="Nur hinzufügen", style=discord.ButtonStyle.primary, emoji="➕")
    async def add_only(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="⏳ Setup läuft: Es werden nur fehlende Rollen/Kanäle hinzugefügt...", embed=None, view=None)
        await run_setup(interaction.guild, reset=False, status_channel=interaction.channel)
        await interaction.channel.send("✅ Setup fertig: Fehlende Rollen/Kanäle wurden hinzugefügt.")

    @discord.ui.button(label="Komplett neu aufsetzen", style=discord.ButtonStyle.success, emoji="🔄")
    async def full_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content="⚠️ Komplett-Reset startet. Kanäle und erstellbare Rollen werden gelöscht und neu erstellt...", embed=None, view=None)
        await run_setup(interaction.guild, reset=True, status_channel=interaction.channel)
        # channel may be deleted; find new log/general channel
        ch = discord.utils.get(interaction.guild.text_channels, name="⚙️・server-logs") or discord.utils.get(interaction.guild.text_channels, name="💬・chat")
        if ch:
            await ch.send("✅ Komplett neu aufgesetzt. Willkommen bei **FUSE | FS**!")


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verifizieren", style=discord.ButtonStyle.success, custom_id="fuse_verify_button", emoji="✅")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        verified = role_name(guild, "✅ Verified")
        unverified = role_name(guild, "❌ Unverified")
        if verified and verified in member.roles:
            await interaction.response.send_message("Du bist bereits verifiziert ✅", ephemeral=True)
            return
        try:
            roles_to_add = [r for r in [verified] if r]
            if roles_to_add:
                await member.add_roles(*roles_to_add, reason="Verify Button")
            if unverified and unverified in member.roles:
                await member.remove_roles(unverified, reason="Verifiziert")
            emb = discord.Embed(title="✅ Verify erfolgreich", description=f"{member.mention} wurde verifiziert und sieht jetzt die Bewerbungskanäle.", color=discord.Color.green())
            await send_log(guild, "✅・verify-logs", emb)
            await interaction.response.send_message("✅ Du bist jetzt verifiziert! Bitte lies die Bewerbungsinfos und öffne bei Bedarf ein Ticket.", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Ich kann dir die Rolle nicht geben. Bitte prüfe meine Rollenposition/Rechte.", ephemeral=True)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket öffnen", style=discord.ButtonStyle.primary, custom_id="fuse_ticket_button", emoji="🎫")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{member.name}".lower().replace(" ", "-"))
        if existing:
            await interaction.response.send_message(f"Du hast bereits ein Ticket: {existing.mention}", ephemeral=True)
            return

        category = discord.utils.get(guild.categories, name="🎫 TICKETS")
        if not category:
            category = await guild.create_category("🎫 TICKETS")

        support_roles = [r for r in [role_name(guild, "🎫 Ticket Support"), role_name(guild, "🟣 Moderator"), role_name(guild, "🔴 Admin"), role_name(guild, "🔥 Owner")] if r]
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, read_message_history=True),
        }
        for r in support_roles:
            overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)

        channel = await guild.create_text_channel(
            name=f"ticket-{member.name}"[:95],
            category=category,
            overwrites=overwrites,
            topic=f"Ticket von {member} ({member.id})",
        )
        emb = discord.Embed(
            title="🎫 Ticket geöffnet",
            description=f"Hey {member.mention}, beschreibe bitte dein Anliegen oder deine Bewerbung.\nEin Teammitglied meldet sich gleich.",
            color=THEME_COLOR,
        )
        await channel.send(content=f"{member.mention} {' '.join(r.mention for r in support_roles[:2])}", embed=emb, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Dein Ticket wurde erstellt: {channel.mention}", ephemeral=True)
        log = discord.Embed(title="🎫 Ticket erstellt", description=f"{member.mention} hat {channel.mention} erstellt.", color=THEME_COLOR)
        await send_log(guild, "🎫・ticket-logs", log)


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.danger, custom_id="fuse_close_ticket", emoji="🔒")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("Dafür brauchst du `Kanäle verwalten`.", ephemeral=True)
            return
        channel = interaction.channel
        await interaction.response.send_message("🔒 Ticket wird in 5 Sekunden geschlossen...", ephemeral=False)
        log = discord.Embed(title="🔒 Ticket geschlossen", description=f"{channel.name} wurde von {interaction.user.mention} geschlossen.", color=discord.Color.red())
        await send_log(interaction.guild, "🎫・ticket-logs", log)
        await asyncio.sleep(5)
        await channel.delete(reason=f"Ticket geschlossen von {interaction.user}")


async def create_roles(guild: discord.Guild):
    created_roles = []
    for name, color, perms, hoist in ROLE_DEFS:
        r = role_name(guild, name)
        if not r:
            try:
                r = await guild.create_role(name=name, colour=color, permissions=perms, hoist=hoist, mentionable=False, reason="FUSE Setup")
                created_roles.append(r)
                await asyncio.sleep(0.15)
            except discord.Forbidden:
                raise RuntimeError("Ich kann Rollen nicht erstellen. Gib mir Administrator und setze meine Bot-Rolle ganz nach oben.")
        else:
            try:
                await r.edit(colour=color, permissions=perms, hoist=hoist, reason="FUSE Setup Rollenupdate")
            except discord.Forbidden:
                pass

    # Positionen setzen: Owner oben, Unverified unten. Bot muss darüber stehen.
    positions: Dict[discord.Role, int] = {}
    for idx, (name, _, __, ___) in enumerate(ROLE_DEFS, start=1):
        r = role_name(guild, name)
        if r and not r.managed:
            positions[r] = idx
    try:
        await guild.edit_role_positions(positions=positions, reason="FUSE Rollenreihenfolge")
    except Exception:
        # Wenn die Bot-Rolle nicht hoch genug ist, bleiben Rollen trotzdem erstellt.
        pass


async def delete_setup(guild: discord.Guild):
    # Kanäle/Kategorien löschen (vorsichtig: nur bekannte Setup-Kategorien + Tickets)
    setup_categories = {cat for cat, _ in STRUCTURE} | {"🎫 TICKETS"}
    for ch in list(guild.channels):
        if isinstance(ch, discord.CategoryChannel) and ch.name in setup_categories:
            try:
                await ch.delete(reason="FUSE Komplett Reset")
                await asyncio.sleep(0.2)
            except discord.Forbidden:
                pass
    # Falls einzelne bekannte Kanäle außerhalb Kategorien existieren
    known_channel_names = {c[1] for _, chans in STRUCTURE for c in chans}
    for ch in list(guild.channels):
        if ch.name in known_channel_names or ch.name.startswith("ticket-"):
            try:
                await ch.delete(reason="FUSE Komplett Reset")
                await asyncio.sleep(0.15)
            except discord.Forbidden:
                pass
    # Rollen löschen, nur wenn Bot sie verwalten kann und nicht managed
    for r in list(guild.roles):
        if r.name in SETUP_ROLE_NAMES and not r.managed:
            try:
                await r.delete(reason="FUSE Komplett Reset")
                await asyncio.sleep(0.15)
            except discord.Forbidden:
                pass


async def setup_permissions(guild: discord.Guild, category_name: str):
    everyone = guild.default_role
    unverified = role_name(guild, "❌ Unverified")
    verified = role_name(guild, "✅ Verified")
    member = role_name(guild, "👤 Member")
    admin = role_name(guild, "🔴 Admin")
    mod = role_name(guild, "🟣 Moderator")
    support = role_name(guild, "🎫 Ticket Support")
    owner = role_name(guild, "🔥 Owner")
    co_owner = role_name(guild, "💠 Co Owner")
    management = role_name(guild, "🧠 Management")

    base_hidden = {
        everyone: discord.PermissionOverwrite(view_channel=False),
        guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True, read_message_history=True),
    }

    if category_name == "🔰 X WILLKOMMEN":
        ow = base_hidden.copy()
        if unverified:
            ow[unverified] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
        if verified:
            ow[verified] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
        if member:
            ow[member] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
        for r in [admin, mod, owner, co_owner, management]:
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        return ow

    if category_name == "🌎 X BEWERBUNG":
        ow = base_hidden.copy()
        if verified:
            ow[verified] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        if member:
            ow[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        for r in [support, admin, mod, owner, co_owner, management]:
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_channels=True)
        return ow

    if category_name in ["🔒 TEAM BEREICH", "📁 LOGS"]:
        ow = base_hidden.copy()
        for r in [support, admin, mod, owner, co_owner, management]:
            if r:
                ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        return ow

    # Community/Infos/Merch/Gang/Talks: erst ab Member sichtbar
    ow = base_hidden.copy()
    if member:
        ow[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
    for r in [support, admin, mod, owner, co_owner, management]:
        if r:
            ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True, connect=True, speak=True)
    return ow


async def create_structure(guild: discord.Guild):
    created_text_channels: Dict[str, discord.TextChannel] = {}

    for cat_name, channels in STRUCTURE:
        category = discord.utils.get(guild.categories, name=cat_name)
        overwrites = await setup_permissions(guild, cat_name)
        if not category:
            category = await guild.create_category(cat_name, overwrites=overwrites, reason="FUSE Setup")
            await asyncio.sleep(0.25)
        else:
            try:
                await category.edit(overwrites=overwrites, reason="FUSE Setup Permissions")
            except discord.Forbidden:
                pass

        for ch_type, ch_name, topic in channels:
            existing = discord.utils.get(guild.channels, name=ch_name)
            if existing:
                try:
                    await existing.edit(category=category, overwrites=None, reason="FUSE Setup Channel Update")
                except Exception:
                    pass
                if isinstance(existing, discord.TextChannel):
                    created_text_channels[ch_name] = existing
                continue

            if ch_type == "text":
                ch = await guild.create_text_channel(name=ch_name, category=category, topic=topic, reason="FUSE Setup")
                created_text_channels[ch_name] = ch
            elif ch_type == "voice":
                await guild.create_voice_channel(name=ch_name, category=category, bitrate=min(guild.bitrate_limit, 64000), user_limit=0, reason="FUSE Setup")
            elif ch_type == "stage":
                try:
                    await guild.create_stage_channel(name=ch_name, category=category, reason="FUSE Setup")
                except Exception:
                    await guild.create_voice_channel(name=ch_name, category=category, reason="FUSE Setup")
            await asyncio.sleep(0.15)

    # Ticket Kategorie vorbereiten
    if not discord.utils.get(guild.categories, name="🎫 TICKETS"):
        await guild.create_category("🎫 TICKETS", reason="FUSE Tickets")

    await seed_messages(guild)


async def seed_messages(guild: discord.Guild):
    # Verify Embed
    verify_channel = discord.utils.get(guild.text_channels, name="✅・verify")
    if verify_channel:
        emb = discord.Embed(
            title="✅ Verifizierung — FUSE | FS",
            description="Klicke auf den Button, um dich zu verifizieren.\nDanach siehst du die Bewerbungskanäle.",
            color=discord.Color.green(),
        )
        emb.set_footer(text="FUSE | FS • Notruf Hamburg Crime Gang")
        await verify_channel.purge(limit=10)
        await verify_channel.send(embed=emb, view=VerifyView())

    # Ticket Embed
    ticket_channel = discord.utils.get(guild.text_channels, name="🎫・ticket")
    if ticket_channel:
        emb = discord.Embed(
            title="🎫 Support / Bewerbung Ticket",
            description="Öffne ein Ticket für Bewerbung, Support, Partnerschaft oder wichtige Fragen.",
            color=THEME_COLOR,
        )
        await ticket_channel.purge(limit=10)
        await ticket_channel.send(embed=emb, view=TicketView())

    # Standardtexte
    ticket_mention = ticket_channel.mention if ticket_channel else "#ticket"
    for name, text in TEXTS.items():
        ch = discord.utils.get(guild.text_channels, name=name)
        if ch:
            try:
                await ch.purge(limit=5)
            except Exception:
                pass
            await ch.send(text.replace("<#TICKET_CHANNEL#>", ticket_mention))


async def run_setup(guild: discord.Guild, reset: bool, status_channel: Optional[discord.abc.Messageable] = None):
    if reset:
        await delete_setup(guild)
    await create_roles(guild)
    await create_structure(guild)
    log = discord.Embed(title="⚙️ Setup abgeschlossen", description=f"Reset: `{reset}`\nServer: **{guild.name}**", color=THEME_COLOR)
    await send_log(guild, "⚙️・server-logs", log)


@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    print(f"✅ Eingeloggt als {bot.user} | Prefix: {PREFIX}")


@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start_setup(ctx: commands.Context):
    embed = discord.Embed(
        title="⚙️ FUSE | FS Server Setup",
        description=(
            "Wähle aus, was der Bot machen soll:\n\n"
            "❌ **Abbruch** — Setup wird nicht gestartet.\n"
            "➕ **Nur hinzufügen** — fehlende Rollen/Kanäle werden ergänzt, nichts wird gelöscht.\n"
            "🔄 **Komplett neu aufsetzen** — bekannte FUSE-Kanäle/Rollen werden gelöscht und neu erstellt.\n\n"
            "⚠️ Stelle sicher, dass meine Bot-Rolle ganz oben steht."
        ),
        color=THEME_COLOR,
    )
    embed.set_footer(text="Nur Administratoren können dieses Menü verwenden.")
    await ctx.send(embed=embed, view=SetupView(ctx.author.id))


@bot.command(name="member")
@commands.has_permissions(manage_roles=True)
async def give_member(ctx: commands.Context, member: discord.Member):
    """Gibt einem verifizierten User die Member-Rolle nach bestandener Bewerbung."""
    member_role = role_name(ctx.guild, "👤 Member")
    verified_role = role_name(ctx.guild, "✅ Verified")
    if not member_role:
        await ctx.reply("❌ Member-Rolle existiert nicht. Führe `!start` aus.")
        return
    try:
        await member.add_roles(member_role, reason=f"Member bestanden durch {ctx.author}")
        if verified_role and verified_role in member.roles:
            await member.remove_roles(verified_role, reason="Zu Member hochgestuft")
        await ctx.reply(f"✅ {member.mention} ist jetzt **Member**.")
        emb = discord.Embed(title="👤 Member vergeben", description=f"{member.mention} wurde von {ctx.author.mention} zu Member gemacht.", color=discord.Color.green())
        await send_log(ctx.guild, "👥・member-logs", emb)
    except discord.Forbidden:
        await ctx.reply("❌ Ich kann diese Rolle nicht vergeben. Prüfe meine Rollenposition.")


@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    emb = discord.Embed(title="🤖 FUSE Bot Hilfe", color=THEME_COLOR)
    emb.add_field(name="!start", value="Startet das Setup-Menü mit Buttons.", inline=False)
    emb.add_field(name="!member @User", value="Gibt einem Bewerber nach Annahme die Member-Rolle.", inline=False)
    await ctx.send(embed=emb)


@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    unverified = role_name(guild, "❌ Unverified")
    if unverified:
        try:
            await member.add_roles(unverified, reason="Neuer User - Unverified")
        except discord.Forbidden:
            pass

    ch = discord.utils.get(guild.text_channels, name="👋・willkommen")
    count = guild.member_count or 0
    embed = discord.Embed(
        title=f"**WILLKOMMEN IN {BRAND} !**",
        description=(
            f"Hey **{member.mention}**! Willkommen bei **Fuse**!\n"
            f"Du bist unser **{count}. Member**. Bitte halte dich an die Regeln und geh freundlich mit allen Mitgliedern um.\n\n"
            "✅ Verifiziere dich in **✅・verify** und lies das Regelwerk."
        ),
        color=THEME_COLOR,
    )
    embed.set_thumbnail(url=member.display_avatar.url)
    if ch:
        await ch.send(embed=embed)

    log = discord.Embed(title="👋 Member joined", description=f"{member.mention} (`{member.id}`) ist beigetreten.", color=discord.Color.green())
    await send_log(guild, "👋・welcome-logs", log)
    await send_log(guild, "🚪・join-leave-logs", log)


@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild
    ch = discord.utils.get(guild.text_channels, name="👋・tschüss")
    if ch:
        await ch.send(f"👋 **{member}** hat den Server verlassen. Wir wünschen dir alles Gute!")
    log = discord.Embed(title="👋 Member left", description=f"{member} (`{member.id}`) hat den Server verlassen.", color=discord.Color.red())
    await send_log(guild, "👋・leave-logs", log)
    await send_log(guild, "🚪・join-leave-logs", log)


@bot.event
async def on_message_delete(message: discord.Message):
    if not message.guild or message.author.bot:
        return
    emb = discord.Embed(title="🗑️ Nachricht gelöscht", color=discord.Color.orange())
    emb.add_field(name="Autor", value=f"{message.author.mention} (`{message.author.id}`)", inline=False)
    emb.add_field(name="Kanal", value=message.channel.mention, inline=False)
    if message.content:
        emb.add_field(name="Inhalt", value=message.content[:1000], inline=False)
    await send_log(message.guild, "📝・message-logs", emb)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if not before.guild or before.author.bot or before.content == after.content:
        return
    emb = discord.Embed(title="✏️ Nachricht bearbeitet", color=discord.Color.gold())
    emb.add_field(name="Autor", value=before.author.mention, inline=False)
    emb.add_field(name="Kanal", value=before.channel.mention, inline=False)
    emb.add_field(name="Vorher", value=(before.content or "-")[:800], inline=False)
    emb.add_field(name="Nachher", value=(after.content or "-")[:800], inline=False)
    await send_log(before.guild, "📝・message-logs", emb)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel == after.channel:
        return
    if before.channel is None and after.channel is not None:
        desc = f"{member.mention} ist **{after.channel.name}** beigetreten."
        color = discord.Color.green()
    elif before.channel is not None and after.channel is None:
        desc = f"{member.mention} hat **{before.channel.name}** verlassen."
        color = discord.Color.red()
    else:
        desc = f"{member.mention} wechselte von **{before.channel.name}** zu **{after.channel.name}**."
        color = discord.Color.blue()
    emb = discord.Embed(title="🎤 Voice Log", description=desc, color=color)
    await send_log(member.guild, "🎤・voice-logs", emb)


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.roles != after.roles:
        before_set = set(before.roles)
        after_set = set(after.roles)
        added = after_set - before_set
        removed = before_set - after_set
        desc = []
        if added:
            desc.append("**Hinzugefügt:** " + ", ".join(r.mention for r in added if r.name != "@everyone"))
        if removed:
            desc.append("**Entfernt:** " + ", ".join(r.name for r in removed if r.name != "@everyone"))
        emb = discord.Embed(title="👥 Rollen geändert", description=f"{after.mention}\n" + "\n".join(desc), color=THEME_COLOR)
        await send_log(after.guild, "👥・member-logs", emb)


if not TOKEN:
    raise SystemExit("❌ DISCORD_TOKEN fehlt. Lege die Variable in Railway an.")

bot.run(TOKEN)
