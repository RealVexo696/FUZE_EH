import os
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------
# CONFIG
# -----------------------------
CATEGORY_ORDER = [
    "👋 START",
    "📝 BEWERBUNG",
    "📢 INFOS",
    "💬 COMMUNITY",
    "🎙 TALKS",
    "🛡 ADMIN",
    "📂 LOGS",
]

TEXT_CHANNELS = {
    "👋 START": [
        "👋・willkommen",
        "✅・verify",
        "📜・regeln",
        "👋・tschuss",
    ],
    "📝 BEWERBUNG": [
        "🎫・ticket",
        "💬・bewerbungschat",
        "📋・formular",
        "🔊・warteraum",
    ],
    "📢 INFOS": [
        "✅・activity-check",
        "🔔・ankundigung",
        "🎁・meeting-clips",
        "🚀・boosts",
        "😂・hall-of-shame",
        "🎥・free-tt-vid",
    ],
    "💬 COMMUNITY": [
        "📱・socialmedia",
        "💬・chat",
        "🍻・bier-keller",
        "💎・lounge-400-rbx",
        "❤️・farbe",
        "🎉・rollensystem",
        "🎮・roblox-gruppe",
        "🏠・anwesen",
        "🛡️・partnerschaft",
        "👕・trikot",
        "👕・polo",
        "🦺・weste",
        "💊・armband",
        "🛍️・merch",
    ],
    "🛡 ADMIN": [
        "🔒・admin-chat",
        "📋・admin-notizen",
        "🚨・team-logs",
        "🏢・leitung-buro",
        "🏢・management-buro",
        "🏢・owner-buro",
    ],
    "📂 LOGS": [
        "📥・join-logs",
        "📤・leave-logs",
        "✅・verify-logs",
        "🎫・ticket-logs",
        "📝・bewerbung-logs",
        "💬・chat-logs",
        "🛡️・mod-logs",
        "⚙️・setup-logs",
    ]
}

VOICE_CHANNELS = {
    "🎙 TALKS": [
        "🌍・ffa-voicechat",
        "🎧・talk-1",
        "🎧・talk-2",
        "🎧・talk-3",
        "🏢・leitung-buro",
        "🏢・management-buro",
        "👑・owner-buro",
    ]
}

ROLES = [
    "Owner",
    "Co-Owner",
    "Projektleitung",
    "Serverleitung",
    "Management",
    "Head Admin",
    "Admin",
    "Moderator",
    "Support-Leitung",
    "Support",
    "Developer",
    "Designer",
    "Eventleitung",
    "Event-Team",
    "Media-Leitung",
    "Media-Team",
    "Ticket-Team",
    "Bewerbungs-Team",
    "Roblox-Leitung",
    "Roblox-Team",
    "Gang-Leitung",
    "Gang-Rat",
    "High Command",
    "Commander",
    "Captain",
    "Lieutenant",
    "Sergeant",
    "Corporal",
    "Elite",
    "Veteran",
    "Trusted",
    "Partner",
    "Booster",
    "VIP",
    "Lounge 400 RBX",
    "Buro Zugang",
    "Social Media",
    "Clan Friend",
    "TikTok Creator",
    "YouTube Creator",
    "Bewerber",
    "Member",
    "Verified",
    "Unverified",
    "Muted",
    "Warn 1",
    "Warn 2",
    "Warn 3",
    "AFK",
    "Bot"
]

RULES_TEXT = """# 📜 Fuse | FS Regeln\n\n1. Sei respektvoll zu allen Mitgliedern.\n2. Kein Spam, kein unnötiges Pingen.\n3. Keine Beleidigungen, kein Drama.\n4. Roblox/Crime-Gang Roleplay nur im passenden Rahmen.\n5. Folge den Anweisungen des Teams.\n6. Werbung nur mit Erlaubnis.\n7. Tickets und Bewerbungen sauber ausfüllen.\n8. Verstöße können zu Mute, Kick oder Bann führen.\n"""

WELCOME_TEXT = "# 👋 Willkommen bei Fuse | FS\nBitte lies zuerst die Regeln und verifiziere dich im Verify-Kanal, damit du den Server vollständig sehen kannst."

APPLICATION_TEXT = "# 📝 Bewerbung\nSobald du verifiziert bist, kannst du dich hier bewerben. Nach Annahme bekommst du die Member-Rolle."

class StartSetupView(View):
    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Nur der Nutzer, der !start benutzt hat, kann diese Buttons verwenden.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Abbruch", style=discord.ButtonStyle.danger, emoji="✖️")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=discord.Embed(title="Setup abgebrochen", description="Es wurden keine Änderungen vorgenommen.", color=discord.Color.red()), view=None)

    @discord.ui.button(label="Nur hinzufügen", style=discord.ButtonStyle.secondary, emoji="➕")
    async def add_only(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True, ephemeral=True)
        await run_setup(interaction.guild, interaction.user, mode="add")
        await interaction.followup.send("Setup abgeschlossen: Fehlende Elemente wurden hinzugefügt.", ephemeral=True)

    @discord.ui.button(label="Komplett neu aufsetzen", style=discord.ButtonStyle.success, emoji="🛠️")
    async def full_reset(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=True, ephemeral=True)
        await run_setup(interaction.guild, interaction.user, mode="reset")
        await interaction.followup.send("Setup abgeschlossen: Server wurde neu strukturiert.", ephemeral=True)

class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Jetzt verifizieren", style=discord.ButtonStyle.success, emoji="✅", custom_id="verify_button")
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        verified_role = discord.utils.get(guild.roles, name="Verified")
        unverified_role = discord.utils.get(guild.roles, name="Unverified")
        bewerber_role = discord.utils.get(guild.roles, name="Bewerber")

        if verified_role and verified_role not in member.roles:
            await member.add_roles(verified_role, reason="User verified via button")
        if bewerber_role and bewerber_role not in member.roles:
            await member.add_roles(bewerber_role, reason="User unlocked application area")
        if unverified_role and unverified_role in member.roles:
            await member.remove_roles(unverified_role, reason="User verified")

        log_channel = discord.utils.get(guild.text_channels, name="✅・verify-logs")
        if log_channel:
            embed = discord.Embed(title="Verify Log", description=f"{member.mention} hat sich verifiziert.", color=discord.Color.green())
            await log_channel.send(embed=embed)

        await interaction.response.send_message("Du wurdest erfolgreich verifiziert und kannst jetzt die Bewerbungsbereiche sehen.", ephemeral=True)

async def ensure_role(guild: discord.Guild, role_name: str):
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        role = await guild.create_role(name=role_name, reason="Fuse Setup")
    return role

async def create_roles(guild: discord.Guild):
    created = []
    for role_name in reversed(ROLES):
        role = discord.utils.get(guild.roles, name=role_name)
        if role is None:
            role = await guild.create_role(name=role_name, mentionable=False, hoist=False, reason="Fuse role setup")
            created.append(role)
    role_map = {r.name: r for r in guild.roles}
    ordered_roles = [role_map[name] for name in ROLES if name in role_map]
    try:
        await guild.edit_role_positions(positions={role: len(ordered_roles)-i for i, role in enumerate(ordered_roles)})
    except Exception:
        pass
    return created

async def get_or_create_category(guild: discord.Guild, name: str):
    category = discord.utils.get(guild.categories, name=name)
    if not category:
        category = await guild.create_category(name)
    return category

async def create_channels(guild: discord.Guild):
    default_role = guild.default_role
    unverified = discord.utils.get(guild.roles, name="Unverified")
    verified = discord.utils.get(guild.roles, name="Verified")
    bewerber = discord.utils.get(guild.roles, name="Bewerber")
    member = discord.utils.get(guild.roles, name="Member")
    admin = discord.utils.get(guild.roles, name="Admin")
    head_admin = discord.utils.get(guild.roles, name="Head Admin")
    management = discord.utils.get(guild.roles, name="Management")
    owner = discord.utils.get(guild.roles, name="Owner")

    for category_name in CATEGORY_ORDER:
        category = await get_or_create_category(guild, category_name)

        if category_name in TEXT_CHANNELS:
            for ch_name in TEXT_CHANNELS[category_name]:
                if discord.utils.get(guild.text_channels, name=ch_name):
                    continue
                overwrites = {default_role: discord.PermissionOverwrite(read_messages=False)}

                if category_name == "👋 START":
                    overwrites[default_role] = discord.PermissionOverwrite(read_messages=True)
                    if verified:
                        overwrites[verified] = discord.PermissionOverwrite(read_messages=True)
                    if unverified:
                        overwrites[unverified] = discord.PermissionOverwrite(read_messages=True)
                elif category_name == "📝 BEWERBUNG":
                    if bewerber:
                        overwrites[bewerber] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    if member:
                        overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                elif category_name == "🛡 ADMIN":
                    if admin:
                        overwrites[admin] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    if head_admin:
                        overwrites[head_admin] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    if management:
                        overwrites[management] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    if owner:
                        overwrites[owner] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                elif category_name == "📂 LOGS":
                    if admin:
                        overwrites[admin] = discord.PermissionOverwrite(read_messages=True)
                    if head_admin:
                        overwrites[head_admin] = discord.PermissionOverwrite(read_messages=True)
                    if management:
                        overwrites[management] = discord.PermissionOverwrite(read_messages=True)
                    if owner:
                        overwrites[owner] = discord.PermissionOverwrite(read_messages=True)
                else:
                    if member:
                        overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                    if verified:
                        overwrites[verified] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

                await guild.create_text_channel(ch_name, category=category, overwrites=overwrites, reason="Fuse channel setup")

        if category_name in VOICE_CHANNELS:
            for ch_name in VOICE_CHANNELS[category_name]:
                if discord.utils.get(guild.voice_channels, name=ch_name):
                    continue
                overwrites = {default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
                if member:
                    overwrites[member] = discord.PermissionOverwrite(connect=True, view_channel=True)
                if "buro" in ch_name.lower() or "owner" in ch_name.lower():
                    overwrites = {default_role: discord.PermissionOverwrite(connect=False, view_channel=False)}
                    if admin:
                        overwrites[admin] = discord.PermissionOverwrite(connect=True, view_channel=True)
                    if management:
                        overwrites[management] = discord.PermissionOverwrite(connect=True, view_channel=True)
                    if owner:
                        overwrites[owner] = discord.PermissionOverwrite(connect=True, view_channel=True)
                await guild.create_voice_channel(ch_name, category=category, overwrites=overwrites, reason="Fuse voice setup")

async def send_start_messages(guild: discord.Guild):
    regeln = discord.utils.get(guild.text_channels, name="📜・regeln")
    verify = discord.utils.get(guild.text_channels, name="✅・verify")
    willkommen = discord.utils.get(guild.text_channels, name="👋・willkommen")
    formular = discord.utils.get(guild.text_channels, name="📋・formular")
    ticket = discord.utils.get(guild.text_channels, name="🎫・ticket")
    ankuendigung = discord.utils.get(guild.text_channels, name="🔔・ankundigung")

    if willkommen:
        await willkommen.send(WELCOME_TEXT)
    if regeln:
        await regeln.send(RULES_TEXT)
    if verify:
        embed = discord.Embed(title="✅ Verify", description="Klicke auf den Button, um dich zu verifizieren und die nächsten Bereiche freizuschalten.", color=discord.Color.green())
        await verify.send(embed=embed, view=VerifyView())
    if formular:
        await formular.send(APPLICATION_TEXT)
    if ticket:
        await ticket.send("# 🎫 Ticket\nErstelle hier deine Support-Anfrage oder Roblox-Gang Anfrage.")
    if ankuendigung:
        await ankuendigung.send("# 🔔 Ankündigungen\nWichtige Server-News werden hier gepostet.")

async def cleanup_created_structure(guild: discord.Guild):
    for channel in list(guild.channels):
        try:
            await channel.delete(reason="Fuse full reset")
        except Exception:
            pass
    protected_roles = {guild.default_role.name, bot.user.name if bot.user else ""}
    for role in list(guild.roles):
        if role.name in protected_roles or role.managed:
            continue
        try:
            await role.delete(reason="Fuse full reset")
        except Exception:
            pass

async def run_setup(guild: discord.Guild, actor: discord.Member, mode: str = "add"):
    if mode == "reset":
        await cleanup_created_structure(guild)

    await create_roles(guild)

    verified = discord.utils.get(guild.roles, name="Verified")
    unverified = discord.utils.get(guild.roles, name="Unverified")
    member = discord.utils.get(guild.roles, name="Member")

    if unverified and verified:
        try:
            await verified.edit(permissions=discord.Permissions.none())
            await unverified.edit(permissions=discord.Permissions.none())
            await member.edit(permissions=discord.Permissions.none())
        except Exception:
            pass

    await create_channels(guild)
    await send_start_messages(guild)

    setup_log = discord.utils.get(guild.text_channels, name="⚙️・setup-logs")
    if setup_log:
        embed = discord.Embed(title="Setup Log", description=f"Setup wurde von {actor.mention} ausgeführt. Modus: **{mode}**", color=discord.Color.blurple())
        await setup_log.send(embed=embed)

@bot.event
async def on_ready():
    bot.add_view(VerifyView())
    print(f"Eingeloggt als {bot.user}")

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    willkommen = discord.utils.get(guild.text_channels, name="👋・willkommen")
    join_logs = discord.utils.get(guild.text_channels, name="📥・join-logs")
    unverified = discord.utils.get(guild.roles, name="Unverified")

    if unverified:
        try:
            await member.add_roles(unverified, reason="Auto unverified on join")
        except Exception:
            pass

    if willkommen:
        embed = discord.Embed(
            title="WILLKOMMEN IN FUSE | FS !",
            description=f"Hey {member.mention}! Willkommen bei Fuse! Du bist unser **{guild.member_count}.** Member. Bitte halte dich an die Regeln und geh freundlich mit allen Mitgliedern um.",
            color=discord.Color.gold()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await willkommen.send(embed=embed)

    if join_logs:
        await join_logs.send(embed=discord.Embed(title="Join Log", description=f"{member.mention} ist dem Server beigetreten.", color=discord.Color.green()))

@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild
    tschuss = discord.utils.get(guild.text_channels, name="👋・tschuss")
    leave_logs = discord.utils.get(guild.text_channels, name="📤・leave-logs")

    if tschuss:
        await tschuss.send(f"😢 {member} hat den Server verlassen.")
    if leave_logs:
        await leave_logs.send(embed=discord.Embed(title="Leave Log", description=f"{member} hat den Server verlassen.", color=discord.Color.red()))

@bot.command(name="start")
@commands.has_permissions(administrator=True)
async def start(ctx: commands.Context):
    embed = discord.Embed(
        title="Fuse Setup starten",
        description=(
            "Wähle unten eine Option aus:\n\n"
            "**Abbruch** → Nichts machen\n"
            "**Nur hinzufügen** → Fehlende Rollen/Kanäle/Nachrichten erstellen\n"
            "**Komplett neu aufsetzen** → Bestehende Struktur löschen und komplett neu bauen"
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Achtung: Komplett neu aufsetzen löscht vorhandene Kanäle und Rollen, soweit möglich.")
    await ctx.send(embed=embed, view=StartSetupView(ctx.author.id))

@start.error
async def start_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("Dafür brauchst du Administrator-Rechte.")

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN Umgebungsvariable fehlt.")

bot.run(TOKEN)
