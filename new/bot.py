import os
import asyncio
import discord
from discord.ext import commands

# ==========================================================
# Fuse | FS - Discord Setup Bot (Railway/GitHub ready)
# Python 3.11+ | discord.py 2.x
# ==========================================================
# WICHTIG:
# 1) In Discord Developer Portal aktivieren:
#    - SERVER MEMBERS INTENT
#    - MESSAGE CONTENT INTENT
# 2) Bot-Rolle im Server ganz nach oben ziehen, sonst kann er
#    Rollen/Permissions nicht korrekt setzen.
# 3) Railway Variable setzen: DISCORD_TOKEN=dein_token
# ==========================================================

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "!"
BRAND = "Fuse | FS"
ACCENT = discord.Color.from_rgb(235, 55, 90)
SUCCESS = discord.Color.from_rgb(72, 214, 116)
WARNING = discord.Color.orange()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.voice_states = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None)

# ---------- Rollen: unten -> oben erstellen, danach Positionen setzen ----------
# Farben sind bewusst dunkler/Crime-Style.
ROLE_SPECS = [
    ("❌ Unverified", 0x3A3A3A),
    ("✅ Verified", 0x57F287),
    ("👤 Member", 0x99AAB5),
    ("📝 Bewerber", 0xFEE75C),
    ("🎟️ Ticket Offen", 0xE67E22),
    ("🎮 Roblox Verknüpft", 0x5865F2),
    ("🔔 Ping: Ankündigung", 0xF1C40F),
    ("🎉 Ping: Events", 0xE91E63),
    ("💬 Aktiv", 0x1ABC9C),
    ("🔥 Stammgast", 0xE74C3C),
    ("💎 VIP", 0x3498DB),
    ("💠 Booster", 0xF47FFF),
    ("🤝 Partner", 0x00B0F4),
    ("🧾 Support Wartet", 0x9B59B6),
    ("🚨 Blacklist", 0x111111),
    ("🕒 Timeout Watch", 0x7F8C8D),
    ("🚔 Probe-Mitglied", 0x95A5A6),
    ("🚔 Gang Mitglied", 0x2ECC71),
    ("⚔️ Kämpfer", 0x16A085),
    ("🛡️ Schutz", 0x2980B9),
    ("📡 Funker", 0x8E44AD),
    ("🚗 Fahrer", 0xD35400),
    ("🎯 Schütze", 0xC0392B),
    ("🕵️ Späher", 0x34495E),
    ("💼 Händler", 0xF39C12),
    ("🏦 Finanzen", 0x27AE60),
    ("🧠 Taktiker", 0x9B59B6),
    ("👑 Elite", 0xF1C40F),
    ("🧪 Test-Team", 0x00A8FF),
    ("🎨 Designer", 0xE84393),
    ("🎬 Content", 0xFD79A8),
    ("📢 Social Media", 0x55EFC4),
    ("🎫 Ticket Support", 0xA29BFE),
    ("📋 Bewerbungs-Team", 0xFAB1A0),
    ("🧰 Supporter", 0x74B9FF),
    ("🔨 Moderator", 0x0984E3),
    ("🛡️ Senior Moderator", 0x6C5CE7),
    ("⚙️ Administrator", 0xD63031),
    ("🧩 Manager", 0xE17055),
    ("📌 Teamleitung", 0xE84393),
    ("💻 Developer", 0x00CEC9),
    ("🔐 Sicherheitsleitung", 0x2D3436),
    ("🚨 Einsatzleitung", 0xB71540),
    ("🏛️ Fraktionsleitung", 0x6D214F),
    ("👔 Co-Leitung", 0xF8C291),
    ("👑 Leitung", 0xF6B93B),
    ("💎 Co-Owner", 0xB8E994),
    ("👑 Owner", 0xFFD700),
    ("🤖 Bot", 0x5865F2),
    ("🎖️ Ehrenmitglied", 0xFAD390),
]

ADMIN_ROLES = [
    "🧰 Supporter", "🔨 Moderator", "🛡️ Senior Moderator", "⚙️ Administrator",
    "🧩 Manager", "📌 Teamleitung", "💻 Developer", "🔐 Sicherheitsleitung",
    "🚨 Einsatzleitung", "🏛️ Fraktionsleitung", "👔 Co-Leitung", "👑 Leitung",
    "💎 Co-Owner", "👑 Owner"
]
HIGH_ROLES = ["⚙️ Administrator", "🧩 Manager", "📌 Teamleitung", "👑 Leitung", "💎 Co-Owner", "👑 Owner"]
MEMBER_ROLE = "👤 Member"
VERIFIED_ROLE = "✅ Verified"
UNVERIFIED_ROLE = "❌ Unverified"
BEWERBER_ROLE = "📝 Bewerber"
TICKET_ROLE = "🎟️ Ticket Offen"

# ---------- Layout ----------
LAYOUT = [
    {
        "name": "🧾 FUSE X WILLKOMMEN",
        "type": "public_limited",
        "channels": [
            ("text", "👋・willkommen", "welcome"),
            ("text", "📜・regelwerk", "rules"),
            ("text", "✅・verify", "verify"),
            ("text", "👋・tschüss", "goodbye"),
        ],
    },
    {
        "name": "🌐 X COMMUNITY",
        "type": "member",
        "channels": [
            ("text", "💬・chat", "chat"),
            ("text", "📸・socialmedia", "social"),
            ("text", "🤖・roblox-gruppe", "roblox"),
            ("text", "🎨・farbe", "farbe"),
            ("text", "📌・rollen", "roles"),
        ],
    },
    {
        "name": "📝 X BEWERBUNG",
        "type": "verified",
        "channels": [
            ("text", "🎫・ticket", "ticket"),
            ("text", "👾・bewerbungschat", "bewerbungschat"),
            ("text", "📋・formular", "formular"),
            ("voice", "🛬・warteraum", "warteraum"),
            ("voice", "💼・einreise-1", "einreise1"),
            ("voice", "💼・einreise-2", "einreise2"),
        ],
    },
    {
        "name": "📢 X INFOS",
        "type": "member",
        "channels": [
            ("text", "✅・activity-check", "activity"),
            ("text", "🔔・ankündigung", "announcements"),
            ("text", "🎬・meeting-clips", "clips"),
            ("text", "🚀・boosts", "boosts"),
            ("text", "😂・hall-of-shame", "shame"),
        ],
    },
    {
        "name": "📞 X TALKS",
        "type": "member",
        "channels": [
            ("stage", "🎙️・stage", "stage"),
            ("voice", "🌍・FFA VoiceChat", "ffa"),
            ("voice", "🍺・Bier Keller", "bier"),
            ("voice", "💬・Talk 1", "talk1"),
            ("voice", "💬・Talk 2", "talk2"),
            ("voice", "🎮・Gaming", "gaming"),
        ],
    },
    {
        "name": "👕 X BROS MERCH",
        "type": "member",
        "channels": [
            ("text", "🦺・weste", "weste"),
            ("text", "🧪・armband", "armband"),
            ("text", "👕・merch", "merch"),
            ("text", "👕・trikot", "trikot"),
            ("text", "👕・polo", "polo"),
        ],
    },
    {
        "name": "📓 X GANG INFOS",
        "type": "member",
        "channels": [
            ("text", "💖・farbe", "gangfarbe"),
            ("text", "🗺️・rollensystem", "rollensystem"),
            ("text", "🎮・roblox-gruppe", "gangroblox"),
            ("text", "🏠・anwesen", "anwesen"),
            ("text", "🛡️・partnerschaft", "partnerschaft"),
        ],
    },
    {
        "name": "🔒 LOUNGES",
        "type": "member",
        "channels": [
            ("voice", "🎀・LOUNGE 400 RBX", "lounge400"),
            ("voice", "♟️・Nils x Luke", "nils-luke"),
            ("voice", "💎・M J S F", "mjsf"),
            ("voice", "☁️・privat-chat", "privat"),
        ],
    },
    {
        "name": "🔐 X TEAM",
        "type": "admin",
        "channels": [
            ("text", "💬・admin-chat", "adminchat"),
            ("text", "📌・team-infos", "teaminfos"),
            ("text", "🧾・team-todo", "todo"),
            ("text", "⚠️・warnungen", "warnungen"),
            ("voice", "🔊・Team Talk", "teamtalk"),
        ],
    },
    {
        "name": "🏢 X BÜROS",
        "type": "high",
        "channels": [
            ("voice", "👑・Owner Büro", "ownerbuero"),
            ("voice", "💎・Co-Owner Büro", "coownerbuero"),
            ("voice", "🧩・Manager Büro", "managerbuero"),
            ("voice", "⚙️・Admin Büro", "adminbuero"),
        ],
    },
    {
        "name": "📁 X LOGS",
        "type": "admin",
        "channels": [
            ("text", "👋・welcome-logs", "welcome_logs"),
            ("text", "✅・verify-logs", "verify_logs"),
            ("text", "👋・leave-logs", "leave_logs"),
            ("text", "🎫・ticket-logs", "ticket_logs"),
            ("text", "📝・bewerbung-logs", "application_logs"),
            ("text", "🛡️・mod-logs", "mod_logs"),
            ("text", "🧾・message-logs", "message_logs"),
            ("text", "🔊・voice-logs", "voice_logs"),
            ("text", "👤・member-logs", "member_logs"),
            ("text", "🔧・server-logs", "server_logs"),
            ("text", "🎭・role-logs", "role_logs"),
        ],
    },
]

# Channel keys -> actual IDs, stored in memory after setup. On restart we find by name.
CHANNEL_ALIASES = {
    "welcome": "👋・willkommen",
    "rules": "📜・regelwerk",
    "verify": "✅・verify",
    "goodbye": "👋・tschüss",
    "ticket": "🎫・ticket",
    "formular": "📋・formular",
    "welcome_logs": "👋・welcome-logs",
    "verify_logs": "✅・verify-logs",
    "leave_logs": "👋・leave-logs",
    "ticket_logs": "🎫・ticket-logs",
    "application_logs": "📝・bewerbung-logs",
    "message_logs": "🧾・message-logs",
    "voice_logs": "🔊・voice-logs",
    "member_logs": "👤・member-logs",
    "role_logs": "🎭・role-logs",
    "server_logs": "🔧・server-logs",
}


def role(guild: discord.Guild, name: str):
    return discord.utils.get(guild.roles, name=name)


def channel_by_name(guild: discord.Guild, name: str):
    return discord.utils.get(guild.channels, name=name)


def text_channel(guild: discord.Guild, key: str):
    name = CHANNEL_ALIASES.get(key, key)
    ch = channel_by_name(guild, name)
    return ch if isinstance(ch, discord.TextChannel) else None


def basic_embed(title: str, description: str, color: discord.Color = ACCENT):
    return discord.Embed(title=title, description=description, color=color)


async def send_log(guild: discord.Guild, key: str, embed: discord.Embed):
    ch = text_channel(guild, key)
    if ch:
        try:
            await ch.send(embed=embed)
        except discord.Forbidden:
            pass


def overwrites_for(guild: discord.Guild, kind: str):
    everyone = guild.default_role
    unverified = role(guild, UNVERIFIED_ROLE)
    verified = role(guild, VERIFIED_ROLE)
    member = role(guild, MEMBER_ROLE)
    bewerber = role(guild, BEWERBER_ROLE)

    overwrites = {
        everyone: discord.PermissionOverwrite(view_channel=False),
    }

    # Admins sehen immer Team/Logs/alles.
    for r_name in ADMIN_ROLES:
        r = role(guild, r_name)
        if r:
            overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)

    if kind == "public_limited":
        if unverified:
            overwrites[unverified] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
        if verified:
            overwrites[verified] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
        if member:
            overwrites[member] = discord.PermissionOverwrite(view_channel=True, send_messages=False, read_message_history=True)
    elif kind == "verified":
        if verified:
            overwrites[verified] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
        if bewerber:
            overwrites[bewerber] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
        if member:
            overwrites[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
    elif kind == "member":
        if member:
            overwrites[member] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
    elif kind == "admin":
        pass
    elif kind == "high":
        for r_name in HIGH_ROLES:
            r = role(guild, r_name)
            if r:
                overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, connect=True, speak=True)
    return overwrites


async def create_roles(guild: discord.Guild):
    created = 0
    existing = {r.name for r in guild.roles}
    # Unverified standardmäßig grau, Adminrollen mit Rechten.
    for name, color in ROLE_SPECS:
        if name not in existing:
            perms = discord.Permissions.none()
            if name in ["⚙️ Administrator", "🧩 Manager", "📌 Teamleitung", "💻 Developer", "👑 Owner", "💎 Co-Owner", "👑 Leitung"]:
                perms = discord.Permissions(administrator=True)
            elif name in ADMIN_ROLES:
                perms = discord.Permissions(manage_messages=True, kick_members=True, mute_members=True, deafen_members=True, move_members=True)
            await guild.create_role(name=name, color=discord.Color(color), permissions=perms, reason="Fuse Setup Rollen")
            created += 1
            await asyncio.sleep(0.2)

    # Rollenreihenfolge: Owner oben. Bot kann nur unter seiner höchsten Rolle sortieren.
    try:
        position = len(guild.roles) - 1
        # ROLE_SPECS ist unten -> oben, also reversed setzen.
        for name, _ in reversed(ROLE_SPECS):
            r = role(guild, name)
            if r and r < guild.me.top_role:
                await r.edit(position=max(1, position), reason="Fuse Setup Rollenreihenfolge")
                position -= 1
                await asyncio.sleep(0.15)
    except discord.Forbidden:
        pass
    return created


async def create_layout(guild: discord.Guild):
    made = {"categories": 0, "channels": 0}
    for cat_spec in LAYOUT:
        cat = discord.utils.get(guild.categories, name=cat_spec["name"])
        if not cat:
            cat = await guild.create_category(
                name=cat_spec["name"],
                overwrites=overwrites_for(guild, cat_spec["type"]),
                reason="Fuse Setup Kategorie",
            )
            made["categories"] += 1
            await asyncio.sleep(0.3)
        else:
            try:
                await cat.edit(overwrites=overwrites_for(guild, cat_spec["type"]), reason="Fuse Setup Kategorie Update")
            except discord.Forbidden:
                pass

        for ch_type, ch_name, _key in cat_spec["channels"]:
            existing = discord.utils.get(guild.channels, name=ch_name)
            if existing:
                continue
            if ch_type == "text":
                await guild.create_text_channel(ch_name, category=cat, reason="Fuse Setup Channel")
            elif ch_type == "voice":
                await guild.create_voice_channel(ch_name, category=cat, reason="Fuse Setup Voice")
            elif ch_type == "stage":
                await guild.create_stage_channel(ch_name, category=cat, reason="Fuse Setup Stage")
            made["channels"] += 1
            await asyncio.sleep(0.25)
    return made


async def setup_messages(guild: discord.Guild):
    # Regeln
    rules = text_channel(guild, "rules")
    if rules:
        embed = basic_embed(
            "📜 Regelwerk | Fuse | FS",
            "**1.** Respektvoll bleiben.\n"
            "**2.** Kein Spam, keine Werbung ohne Erlaubnis.\n"
            "**3.** Kein Rassismus, Hate oder Provokation.\n"
            "**4.** Roblox bleibt Roblox: Keine Real-Life Gewaltandrohungen.\n"
            "**5.** Team-Anweisungen befolgen.\n"
            "**6.** Tickets/Bewerbungen ernst benutzen.\n\n"
            "Mit dem Verifizieren akzeptierst du diese Regeln.",
        )
        await rules.send(embed=embed)

    verify = text_channel(guild, "verify")
    if verify:
        embed = basic_embed(
            "✅ Verifizierung",
            "Klicke auf **Verifizieren**, damit du die Bewerbungs-Kanäle sehen kannst.\n"
            "Nach der Bewerbung bekommst du den Member-Rang und siehst fast alles.",
            SUCCESS,
        )
        await verify.send(embed=embed, view=VerifyView())

    ticket = text_channel(guild, "ticket")
    if ticket:
        embed = basic_embed(
            "🎫 Ticket System",
            "Brauchst du Hilfe, möchtest du eine Bewerbung starten oder ein Problem melden?\n"
            "Klicke auf **Ticket erstellen**.",
        )
        await ticket.send(embed=embed, view=TicketView())

    formular = text_channel(guild, "formular")
    if formular:
        embed = basic_embed(
            "📋 Bewerbungsformular",
            "Klicke auf **Bewerbung starten**. Danach erhältst du den Bewerber-Rang.\n\n"
            "**Roblox Name:**\n"
            "**Alter:**\n"
            "**Warum Fuse | FS?:**\n"
            "**Stärken:**\n"
            "**Schwächen:**\n"
            "**Erfahrung in Notruf Hamburg Crime/Gang RP:**",
        )
        await formular.send(embed=embed, view=ApplicationView())


async def reset_created_setup(guild: discord.Guild):
    # Löscht nur Kategorien aus LAYOUT und die Channels darin + Rollen aus ROLE_SPECS.
    deleted_channels = 0
    deleted_roles = 0
    layout_category_names = {c["name"] for c in LAYOUT}

    for cat in list(guild.categories):
        if cat.name in layout_category_names:
            for ch in list(cat.channels):
                try:
                    await ch.delete(reason="Fuse Komplett neu aufsetzen")
                    deleted_channels += 1
                    await asyncio.sleep(0.2)
                except discord.Forbidden:
                    pass
            try:
                await cat.delete(reason="Fuse Komplett neu aufsetzen")
                await asyncio.sleep(0.2)
            except discord.Forbidden:
                pass

    spec_names = {name for name, _ in ROLE_SPECS}
    for r in list(guild.roles):
        if r.name in spec_names and not r.managed and r < guild.me.top_role:
            try:
                await r.delete(reason="Fuse Komplett neu aufsetzen")
                deleted_roles += 1
                await asyncio.sleep(0.15)
            except discord.Forbidden:
                pass
    return deleted_channels, deleted_roles


async def run_setup(interaction_or_ctx, mode: str):
    guild = interaction_or_ctx.guild
    if not guild:
        return

    if isinstance(interaction_or_ctx, discord.Interaction):
        sender = interaction_or_ctx.followup
        await interaction_or_ctx.response.defer(ephemeral=True, thinking=True)
    else:
        sender = interaction_or_ctx

    try:
        if mode == "reset":
            dc, dr = await reset_created_setup(guild)
            msg = f"🧹 Gelöscht: **{dc} Channels**, **{dr} Rollen**.\n"
        else:
            msg = ""

        roles_created = await create_roles(guild)
        made = await create_layout(guild)
        await setup_messages(guild)

        done = basic_embed(
            "✅ Setup fertig",
            msg
            + f"Rollen erstellt: **{roles_created}**\n"
            + f"Kategorien erstellt: **{made['categories']}**\n"
            + f"Channels erstellt: **{made['channels']}**\n\n"
            + "Hinweis: Ziehe die Bot-Rolle ganz nach oben, falls Rollen/Permissions nicht vollständig gesetzt wurden.",
            SUCCESS,
        )
        if isinstance(interaction_or_ctx, discord.Interaction):
            await sender.send(embed=done, ephemeral=True)
        else:
            await sender.send(embed=done)
        await send_log(guild, "server_logs", done)
    except discord.Forbidden:
        err = basic_embed("❌ Keine Rechte", "Der Bot braucht **Administrator** und seine Rolle muss weit oben sein.", discord.Color.red())
        if isinstance(interaction_or_ctx, discord.Interaction):
            await sender.send(embed=err, ephemeral=True)
        else:
            await sender.send(embed=err)
    except Exception as e:
        err = basic_embed("❌ Fehler", f"```{type(e).__name__}: {e}```", discord.Color.red())
        if isinstance(interaction_or_ctx, discord.Interaction):
            await sender.send(embed=err, ephemeral=True)
        else:
            await sender.send(embed=err)


class StartSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="Abbruch", style=discord.ButtonStyle.danger, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=basic_embed("❌ Abgebrochen", "Setup wurde abgebrochen.", WARNING), view=None)

    @discord.ui.button(label="Nur hinzufügen", style=discord.ButtonStyle.primary, emoji="➕")
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        await run_setup(interaction, "add")

    @discord.ui.button(label="Komplett neu aufsetzen", style=discord.ButtonStyle.success, emoji="🧹")
    async def reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        await run_setup(interaction, "reset")


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verifizieren", style=discord.ButtonStyle.success, emoji="✅", custom_id="fuse_verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        if not isinstance(member, discord.Member) or not guild:
            return
        verified = role(guild, VERIFIED_ROLE)
        unverified = role(guild, UNVERIFIED_ROLE)
        if verified:
            await member.add_roles(verified, reason="User verifiziert")
        if unverified and unverified in member.roles:
            await member.remove_roles(unverified, reason="User verifiziert")
        await interaction.response.send_message("✅ Du bist verifiziert! Du kannst jetzt die Bewerbungs-Kanäle sehen.", ephemeral=True)
        embed = basic_embed("✅ Verify Log", f"{member.mention} hat sich verifiziert.", SUCCESS)
        await send_log(guild, "verify_logs", embed)


class ApplicationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Bewerbung starten", style=discord.ButtonStyle.primary, emoji="📋", custom_id="fuse_application_button")
    async def apply(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        if not isinstance(member, discord.Member) or not guild:
            return
        bewerber = role(guild, BEWERBER_ROLE)
        if bewerber:
            await member.add_roles(bewerber, reason="Bewerbung gestartet")
        await interaction.response.send_message(
            "📋 Du hast den Bewerber-Rang bekommen. Schreibe deine Bewerbung in den Bewerbungschat oder erstelle ein Ticket.",
            ephemeral=True,
        )
        embed = basic_embed("📝 Bewerbung Log", f"{member.mention} hat eine Bewerbung gestartet.", ACCENT)
        await send_log(guild, "application_logs", embed)


class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket erstellen", style=discord.ButtonStyle.primary, emoji="🎫", custom_id="fuse_ticket_button")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        if not isinstance(member, discord.Member) or not guild:
            return

        category = discord.utils.get(guild.categories, name="📝 X BEWERBUNG") or guild.categories[0]
        safe_name = member.name.lower().replace(" ", "-")[:20]
        existing = discord.utils.get(guild.text_channels, name=f"ticket-{safe_name}")
        if existing:
            await interaction.response.send_message(f"Du hast bereits ein Ticket: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        for r_name in ADMIN_ROLES:
            r = role(guild, r_name)
            if r:
                overwrites[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        ch = await guild.create_text_channel(f"ticket-{safe_name}", category=category, overwrites=overwrites, reason="Ticket erstellt")
        ticket_role = role(guild, TICKET_ROLE)
        if ticket_role:
            await member.add_roles(ticket_role, reason="Ticket offen")
        await ch.send(embed=basic_embed("🎫 Ticket", f"Hey {member.mention}, beschreibe dein Anliegen. Ein Teammitglied meldet sich gleich."), view=CloseTicketView())
        await interaction.response.send_message(f"🎫 Ticket erstellt: {ch.mention}", ephemeral=True)
        await send_log(guild, "ticket_logs", basic_embed("🎫 Ticket Log", f"{member.mention} hat {ch.mention} erstellt."))


class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Ticket schließen", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="fuse_close_ticket_button")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        ch = interaction.channel
        if not guild or not isinstance(ch, discord.TextChannel):
            return
        await interaction.response.send_message("🔒 Ticket wird in 5 Sekunden geschlossen...", ephemeral=True)
        await send_log(guild, "ticket_logs", basic_embed("🔒 Ticket geschlossen", f"{ch.name} wurde von {interaction.user.mention} geschlossen.", WARNING))
        await asyncio.sleep(5)
        try:
            await ch.delete(reason="Ticket geschlossen")
        except discord.Forbidden:
            pass


@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    bot.add_view(TicketView())
    bot.add_view(ApplicationView())
    bot.add_view(CloseTicketView())
    print(f"✅ Eingeloggt als {bot.user} | Server: {len(bot.guilds)}")


@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    unverified = role(guild, UNVERIFIED_ROLE)
    if unverified:
        try:
            await member.add_roles(unverified, reason="Neuer User - Unverified")
        except discord.Forbidden:
            pass

    welcome = text_channel(guild, "welcome")
    count = guild.member_count or 0
    msg = (
        f"**WILLKOMMEN IN FUSE | FS !**\n\n"
        f"Hey **{member.mention}**! Willkommen bei **Fuse**! "
        f"Du bist unser **{count}. Member**. Bitte halte dich an die Regeln und geh freundlich mit allen Mitgliedern um.\n\n"
        f"➡️ Geh zu <#{text_channel(guild, 'verify').id}> und verifiziere dich, um loszulegen."
        if text_channel(guild, "verify") else
        f"**WILLKOMMEN IN FUSE | FS !**\n\nHey **{member.mention}**! Willkommen bei **Fuse**! Du bist unser **{count}. Member**."
    )
    embed = basic_embed("👋 Neuer Member", msg, SUCCESS)
    if welcome:
        await welcome.send(content=member.mention, embed=embed)
    await send_log(guild, "welcome_logs", basic_embed("👋 Welcome Log", f"{member.mention} ist beigetreten. Member: **{count}**", SUCCESS))


@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild
    goodbye = text_channel(guild, "goodbye")
    embed = basic_embed("👋 Tschüss", f"**{member}** hat Fuse | FS verlassen. Viel Erfolg weiterhin!", WARNING)
    if goodbye:
        await goodbye.send(embed=embed)
    await send_log(guild, "leave_logs", basic_embed("👋 Leave Log", f"{member} hat den Server verlassen.", WARNING))


@bot.event
async def on_message_delete(message: discord.Message):
    if not message.guild or message.author.bot:
        return
    embed = basic_embed("🗑️ Nachricht gelöscht", f"**Autor:** {message.author.mention}\n**Channel:** {message.channel.mention}\n**Inhalt:**\n{message.content[:1500] or '*Kein Text*'}", WARNING)
    await send_log(message.guild, "message_logs", embed)


@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if not before.guild or before.author.bot or before.content == after.content:
        return
    embed = basic_embed("✏️ Nachricht bearbeitet", f"**Autor:** {before.author.mention}\n**Channel:** {before.channel.mention}\n**Vorher:** {before.content[:800] or '*Leer*'}\n**Nachher:** {after.content[:800] or '*Leer*'}", ACCENT)
    await send_log(before.guild, "message_logs", embed)


@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel == after.channel:
        return
    if before.channel is None and after.channel is not None:
        desc = f"{member.mention} ist **{after.channel.name}** beigetreten."
    elif before.channel is not None and after.channel is None:
        desc = f"{member.mention} hat **{before.channel.name}** verlassen."
    else:
        desc = f"{member.mention} wechselte von **{before.channel.name}** zu **{after.channel.name}**."
    await send_log(member.guild, "voice_logs", basic_embed("🔊 Voice Log", desc))


@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    if before.roles != after.roles:
        added = [r.mention for r in after.roles if r not in before.roles]
        removed = [r.mention for r in before.roles if r not in after.roles]
        desc = f"**User:** {after.mention}\n"
        if added:
            desc += f"**Rolle hinzugefügt:** {', '.join(added)}\n"
        if removed:
            desc += f"**Rolle entfernt:** {', '.join(removed)}\n"
        await send_log(after.guild, "role_logs", basic_embed("🎭 Rollen Log", desc))


@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start(ctx: commands.Context):
    embed = basic_embed(
        "⚙️ Fuse | FS Server Setup",
        "Wähle aus, was der Bot machen soll:\n\n"
        "**✖️ Abbruch** - Nichts passiert.\n"
        "**➕ Nur hinzufügen** - Fehlende Rollen/Kanäle werden ergänzt.\n"
        "**🧹 Komplett neu aufsetzen** - Erstellt das Fuse-Layout neu und löscht vorher die vom Bot bekannten Setup-Kategorien/Rollen.\n\n"
        "⚠️ Der Bot braucht Administrator-Rechte und seine Rolle muss oben stehen.",
        ACCENT,
    )
    await ctx.reply(embed=embed, view=StartSetupView(), mention_author=False)


@start.error
async def start_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("❌ Nur Administratoren dürfen `!start` benutzen.", mention_author=False)
    else:
        await ctx.reply(f"❌ Fehler: `{error}`", mention_author=False)


@bot.command(name="member")
@commands.has_any_role("📋 Bewerbungs-Team", "🧰 Supporter", "🔨 Moderator", "⚙️ Administrator", "👑 Owner")
async def give_member(ctx: commands.Context, user: discord.Member):
    """Team-Befehl: !member @User -> Bewerber wird Member."""
    member_r = role(ctx.guild, MEMBER_ROLE)
    verified_r = role(ctx.guild, VERIFIED_ROLE)
    bewerber_r = role(ctx.guild, BEWERBER_ROLE)
    unverified_r = role(ctx.guild, UNVERIFIED_ROLE)
    add = [r for r in [member_r, verified_r] if r]
    remove = [r for r in [bewerber_r, unverified_r] if r and r in user.roles]
    if add:
        await user.add_roles(*add, reason=f"Member durch {ctx.author}")
    if remove:
        await user.remove_roles(*remove, reason=f"Member durch {ctx.author}")
    await ctx.reply(f"✅ {user.mention} ist jetzt Member.", mention_author=False)
    await send_log(ctx.guild, "member_logs", basic_embed("👤 Member vergeben", f"{ctx.author.mention} hat {user.mention} zum Member gemacht.", SUCCESS))


@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    embed = basic_embed(
        "🤖 Fuse Bot Hilfe",
        "`!start` - Setup-Menü öffnen.\n"
        "`!member @User` - Bewerber als Member freischalten.\n\n"
        "Buttons: Verify, Ticket, Bewerbung werden automatisch erstellt.",
    )
    await ctx.reply(embed=embed, mention_author=False)


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN fehlt. Setze die Variable in Railway oder lokal in deiner Umgebung.")

bot.run(TOKEN)
