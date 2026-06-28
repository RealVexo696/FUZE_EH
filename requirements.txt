"""
🎨 FUSE | FS — Components V2 Panel-Engine
==========================================
Premium-Layouts mit Container + Section + Separator + TextDisplay
statt klassischer Embeds. Voraussetzung: discord.py >= 2.5

Wichtig:
  - LayoutViews dürfen NICHT mit content= oder embed= zusammen verschickt werden
  - Erlaubt: nur `view=...` (+ `files=` falls Attachments referenziert werden)
  - Buttons müssen in ActionRows leben (oder als Section-Accessory)
  - Separator = die "komischen Striche" mit visible=True
"""
from __future__ import annotations
import asyncio
import time
import re
from datetime import datetime, timezone, timedelta
from typing import Optional

import discord
from discord import ui

import db


# ─── BRAND ────────────────────────────────────────────────────────
BRAND_COLOR   = discord.Color(0xE91E63)
SUCCESS_COLOR = discord.Color(0x2ECC71)
ERROR_COLOR   = discord.Color(0xE74C3C)
INFO_COLOR    = discord.Color(0x3498DB)
GOLD_COLOR    = discord.Color(0xF1C40F)
PURPLE_COLOR  = discord.Color(0x9B59B6)
DARK_COLOR    = discord.Color(0x2B2D31)

SERVER_TAG    = "FUSE | FS"
BRAND_DIAMOND = "❖"
ARROW         = "➤"
DOT           = "•"
STAR          = "✦"
DIAMOND       = "◆"

APPLY_COOLDOWN_MIN = 30


# ─── HELPERS ──────────────────────────────────────────────────────
def _sep(large: bool = False, visible: bool = True) -> ui.Separator:
    """Die 'komischen Striche' — visueller Trenner zwischen Sections."""
    return ui.Separator(
        spacing=discord.SeparatorSpacing.large if large else discord.SeparatorSpacing.small,
        visible=visible,
    )


def _header_text(emoji: str, headline: str) -> str:
    return f"# {emoji}  {headline.upper()}\n-# {BRAND_DIAMOND}  {SERVER_TAG}  {BRAND_DIAMOND}  Premium Edition"


def _footer_text(extra: str = "") -> str:
    base = f"{SERVER_TAG}  {BRAND_DIAMOND}  Roblox Roleplay Community"
    return f"-# {extra}  {BRAND_DIAMOND}  {base}" if extra else f"-# {base}"


def _quote(body: str) -> str:
    return "\n".join(f"> {l}" if l.strip() else ">" for l in body.split("\n"))


def _section_text(emoji: str, title: str, body: str) -> ui.TextDisplay:
    return ui.TextDisplay(f"### {emoji}  __{title}__\n{_quote(body)}")


def _find_role(g: discord.Guild, name: str) -> Optional[discord.Role]:
    return discord.utils.get(g.roles, name=name)


def _get_log_channel(g: discord.Guild, log_type: str) -> Optional[discord.TextChannel]:
    suffix_map = {
        "verify": "verify-logs", "ticket": "ticket-logs",
        "moderation": "moderation-logs", "application": "bewerbung-logs",
    }
    suffix = suffix_map.get(log_type)
    if not suffix: return None
    for ch in g.text_channels:
        if ch.name.endswith(suffix):
            return ch
    return None


# ─── BASIS-BUILDER ────────────────────────────────────────────────
def _build_container(
    accent: str,
    headline: str,
    subline: str,
    sections: list[tuple[str, str, str]],
    color: discord.Color = BRAND_COLOR,
    *,
    thumbnail_url: Optional[str] = None,
    footer_text: str = "",
    extra_components: Optional[list] = None,
) -> ui.Container:
    container = ui.Container(accent_color=color)

    # Header (optional mit Thumbnail)
    header = ui.TextDisplay(_header_text(accent, headline))
    if thumbnail_url:
        container.add_item(ui.Section(header, accessory=ui.Thumbnail(thumbnail_url)))
    else:
        container.add_item(header)

    container.add_item(_sep(large=True, visible=True))

    # Subline
    if subline:
        container.add_item(ui.TextDisplay(_quote(subline)))
        container.add_item(_sep(large=False, visible=False))

    # Sections
    for i, (e, t, b) in enumerate(sections):
        container.add_item(_section_text(e, t, b))
        if i < len(sections) - 1:
            container.add_item(_sep(large=False, visible=True))

    # Extra Components
    if extra_components:
        container.add_item(_sep(large=True, visible=True))
        for c in extra_components:
            container.add_item(c)

    # Footer
    container.add_item(_sep(large=False, visible=True))
    container.add_item(ui.TextDisplay(_footer_text(footer_text)))
    return container


# ────────────────────────────────────────────────────────────────── #
# PANELS  —  Channel-Inhalte
# ────────────────────────────────────────────────────────────────── #

# ─── REGELWERK ────────────────────────────────────────────────────
def rules_panel(guild: discord.Guild) -> ui.LayoutView:
    sections = [
        ("🤝", "§1  Respekt",
         "Behandle jedes Mitglied **freundlich**.\nKeine Beleidigungen, kein Mobbing, kein Rassismus."),
        ("🔇", "§2  Kein Spam",
         "Kein Spammen von Nachrichten, Pings, Emojis oder Reaktionen."),
        ("📢", "§3  Werbung",
         "Werbung jeglicher Art ist **ohne Erlaubnis verboten**."),
        ("🔞", "§4  NSFW",
         "NSFW-, Gore- oder anstößige Inhalte sind **strikt untersagt**."),
        ("📜", "§5  Discord-ToS",
         "Die [Discord Richtlinien](https://discord.com/terms) gelten **jederzeit**."),
        ("💬", "§6  Channel-Themen",
         "Halte dich an die Themen der jeweiligen Kanäle."),
        ("🎭", "§7  Roleplay",
         "In RP-Kanälen wird **im Charakter** geschrieben. Kein OOC."),
        ("🛡️", "§8  Team",
         "Anweisungen des Teams sind **ohne Diskussion** zu befolgen."),
        ("🐛", "§9  Bugs",
         "Bekannte Bugs melden — **niemals** ausnutzen."),
        ("🔐", "§10  Account",
         "Teile **keine** Accountdaten. Phishing = sofortiger Bann."),
        ("🎮", "§11  Roblox-Only",
         "Dieser Server ist ausschließlich Roblox-Roleplay."),
        ("⚖️", "§12  Strafen",
         "Verstöße = Verwarnung → Mute → Kick → Bann."),
    ]
    container = _build_container(
        "📜", "Regelwerk",
        f"**Willkommen in unserer Familie.** {BRAND_DIAMOND}\n"
        f"*Diese Regeln gelten für **jeden** auf {SERVER_TAG} — ohne Ausnahme.*\n"
        f"*Mit deinem Verify akzeptierst du sie automatisch.*",
        sections,
        color=BRAND_COLOR, guild=None,
        thumbnail_url=guild.icon.url if guild.icon else None,
        footer_text="Stand: aktuell",
    ) if False else _build_container(
        "📜", "Regelwerk",
        f"**Willkommen in unserer Familie.** {BRAND_DIAMOND}\n"
        f"*Diese Regeln gelten für **jeden** auf {SERVER_TAG} — ohne Ausnahme.*\n"
        f"*Mit deinem Verify akzeptierst du sie automatisch.*",
        sections,
        color=BRAND_COLOR,
        thumbnail_url=guild.icon.url if guild.icon else None,
        footer_text="Stand: aktuell",
    )
    v = ui.LayoutView(); v.add_item(container); return v


# ─── VERIFY ───────────────────────────────────────────────────────
class VerifyLayoutView(ui.LayoutView):
    def __init__(self, guild: Optional[discord.Guild] = None):
        super().__init__(timeout=None)
        thumb = guild.icon.url if (guild and guild.icon) else None
        btn = VerifyButton()
        action_row = ui.ActionRow(btn)
        self.add_item(_build_container(
            "🔐", "Verifizierung",
            f"**Willkommen bei {SERVER_TAG}!** 👋\n"
            f"*Bevor du den vollen Server erkunden kannst, verifiziere dich kurz.\n"
            f"Damit bestätigst du, das Regelwerk gelesen zu haben.*",
            [
                ("🔽", "So funktioniert's",
                 f"**1.**  Klicke unten auf **✅ Verifizieren**\n"
                 f"**2.**  Du erhältst Zugriff auf den **Bewerbungs-Bereich**\n"
                 f"**3.**  Sende deine Bewerbung ab\n"
                 f"**4.**  Nach Annahme bist du **Member** & siehst alles 🎉"),
                ("📜", "Hinweis",
                 "*Mit dem Klick akzeptierst du das* <#📜・regelwerk>*.*"),
            ],
            color=SUCCESS_COLOR,
            thumbnail_url=thumb,
            extra_components=[action_row],
            footer_text="Sicheres Verify-System",
        ))


class VerifyButton(ui.Button):
    def __init__(self):
        super().__init__(label="Verifizieren", style=discord.ButtonStyle.success,
                         emoji="✅", custom_id="fuse_verify_btn")

    async def callback(self, interaction: discord.Interaction):
        g, m = interaction.guild, interaction.user
        unv = _find_role(g, "❌ Unverified")
        ver = _find_role(g, "✅ Verified")
        bew = _find_role(g, "📝 Bewerber")
        if ver and ver in m.roles:
            return await interaction.response.send_message("✅  Du bist bereits verifiziert!", ephemeral=True)
        try:
            if unv and unv in m.roles: await m.remove_roles(unv, reason="Verify")
            if ver:                    await m.add_roles(ver, reason="Verify")
            if bew:                    await m.add_roles(bew, reason="Verify -> Bewerber")
            view = ui.LayoutView()
            view.add_item(_build_container(
                "🎉", "Verifizierung erfolgreich!",
                f"**Willkommen, {m.mention}!**",
                [
                    ("✅", "Du hast jetzt Zugriff auf",
                     f"{ARROW}  <#📋・bewerbung>\n"
                     f"{ARROW}  <#❓・bewerbungs-info>\n"
                     f"{ARROW}  <#🎙️・warteraum>"),
                    ("📋", "Dein nächster Schritt",
                     "Gehe in <#📋・bewerbung> und klicke auf **📋 Bewerbung starten**."),
                ],
                color=SUCCESS_COLOR,
                thumbnail_url=m.display_avatar.url,
            ))
            await interaction.response.send_message(view=view, ephemeral=True)
            log_ch = _get_log_channel(g, "verify")
            if log_ch:
                lv = ui.LayoutView()
                lv.add_item(_build_container(
                    "✅", "User verifiziert",
                    f"{m.mention} (`{m.id}`)",
                    [],
                    color=SUCCESS_COLOR,
                    thumbnail_url=m.display_avatar.url,
                ))
                await log_ch.send(view=lv)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌  Mir fehlen die Rechte! Schiebe die Bot-Rolle ganz nach oben.", ephemeral=True,
            )


# ─── BEWERBUNG (Modal + Layout) ───────────────────────────────────
class ApplicationModal(ui.Modal, title="📋 FUSE | FS — Bewerbung"):
    roblox_name = ui.TextInput(label="Roblox-Name & Alter",
                                placeholder="z.B. JustVexo • 15 Jahre",
                                max_length=80, required=True)
    experience  = ui.TextInput(label="Wie lange spielst du Roblox-RP?",
                                placeholder="z.B. 2 Jahre Notruf Hamburg...",
                                max_length=200, required=True)
    why_fuse    = ui.TextInput(label="Warum möchtest du zu FUSE?",
                                style=discord.TextStyle.paragraph,
                                placeholder="Erkläre warum gerade FUSE...",
                                max_length=600, required=True)
    offer       = ui.TextInput(label="Was bietest du der Gang?",
                                style=discord.TextStyle.paragraph,
                                placeholder="Skills, Aktivität, Persönlichkeit...",
                                max_length=600, required=True)
    activity    = ui.TextInput(label="Aktivität (Std/Woche) + Mikrofon?",
                                placeholder="z.B. ~15 Std/Woche, Mikrofon: Ja",
                                max_length=100, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        g, m = interaction.guild, interaction.user
        log_ch = _get_log_channel(g, "application")
        if not log_ch:
            return await interaction.response.send_message(
                "❌  Bewerbungs-Log-Kanal nicht gefunden. Bitte Admin informieren.", ephemeral=True,
            )

        # Layout-View mit allen Daten + Buttons
        decision_view = ApplicationDecisionLayoutView(
            applicant_id=m.id,
            applicant_avatar=m.display_avatar.url,
            applicant_tag=str(m),
            account_created=int(m.created_at.timestamp()),
            member_count=g.member_count,
            roblox_name=self.roblox_name.value,
            experience=self.experience.value,
            why_fuse=self.why_fuse.value,
            offer=self.offer.value,
            activity=self.activity.value,
        )
        sent = await log_ch.send(view=decision_view)

        db.DATA["applications"][str(sent.id)] = {
            "applicant_id": m.id,
            "posted_ts": time.time(),
            "decided": None,
            "reminded": False,
            "channel_id": log_ch.id,
        }
        db.save()

        # Bestätigung an User
        cv = ui.LayoutView()
        cv.add_item(_build_container(
            "✅", "Bewerbung abgeschickt!",
            "*Deine Bewerbung wurde an das Team weitergeleitet.*",
            [
                ("⏱️", "Bearbeitungszeit",
                 "In der Regel **24 – 48 Stunden**.\n"
                 "Du bekommst eine **DM** sobald entschieden wurde."),
                ("💡", "Tipp",
                 "Halte deine Discord-DMs für unseren Bot offen!"),
            ],
            color=SUCCESS_COLOR,
            thumbnail_url=m.display_avatar.url,
        ))
        await interaction.response.send_message(view=cv, ephemeral=True)


def _build_application_panel(
    *, applicant_id: int, applicant_tag: str, applicant_avatar: str,
    account_created: int, member_count: int,
    roblox_name: str, experience: str, why_fuse: str, offer: str, activity: str,
    decision: Optional[str] = None,
    decided_by: Optional[str] = None,
    decision_reason: Optional[str] = None,
    cooldown_until: Optional[int] = None,
) -> ui.Container:
    """Zentraler Container — vor & nach Entscheidung gleich, nur Status-Header ändert sich."""
    if decision == "accepted":
        accent, headline, color = "✅", "Bewerbung Angenommen", SUCCESS_COLOR
    elif decision == "denied":
        accent, headline, color = "❌", "Bewerbung Abgelehnt", ERROR_COLOR
    else:
        accent, headline, color = "📨", "Neue Bewerbung", INFO_COLOR

    sections = [
        ("👤", "Bewerber",
         f"**{applicant_tag}**  <@{applicant_id}>\n"
         f"{ARROW}  User-ID: `{applicant_id}`\n"
         f"{ARROW}  Account: <t:{account_created}:R>\n"
         f"{ARROW}  Member-Count beim Eingang: `{member_count}`"),
        ("🎮", "Roblox-Name & Alter",
         roblox_name),
        ("🕹️", "RP-Erfahrung",
         experience),
        ("💡", "Warum FUSE?",
         why_fuse),
        ("🎯", "Was bietest du uns?",
         offer),
        ("⏱️", "Aktivität & Mikrofon",
         activity),
    ]
    if decision == "accepted":
        sections.append(("🎉", "Status", f"Angenommen von {decided_by}\n*Member-Rolle vergeben.*"))
    elif decision == "denied":
        sections.append(("📝", "Begründung", decision_reason or "—"))
        if cooldown_until:
            sections.append(("⏳", "Sperre",
                             f"Wieder möglich:  <t:{cooldown_until}:R>  *(*<t:{cooldown_until}:F>*)*"))
        sections.append(("❌", "Status", f"Abgelehnt von {decided_by}"))

    return _build_container(
        accent, headline,
        f"**Bewerbung von** <@{applicant_id}>",
        sections, color=color,
        thumbnail_url=applicant_avatar,
        footer_text=f"Bewerber-ID: {applicant_id}",
    )


class ApplicationDecisionLayoutView(ui.LayoutView):
    """Persistent Layout-View für eine Bewerbung mit Accept/Deny Buttons."""

    def __init__(self,
                 applicant_id: int = 0,
                 applicant_avatar: str = "",
                 applicant_tag: str = "",
                 account_created: int = 0,
                 member_count: int = 0,
                 roblox_name: str = "",
                 experience: str = "",
                 why_fuse: str = "",
                 offer: str = "",
                 activity: str = "",
                 decision: Optional[str] = None,
                 decided_by: Optional[str] = None,
                 decision_reason: Optional[str] = None,
                 cooldown_until: Optional[int] = None):
        super().__init__(timeout=None)

        container = _build_application_panel(
            applicant_id=applicant_id, applicant_tag=applicant_tag,
            applicant_avatar=applicant_avatar, account_created=account_created,
            member_count=member_count, roblox_name=roblox_name,
            experience=experience, why_fuse=why_fuse, offer=offer,
            activity=activity, decision=decision, decided_by=decided_by,
            decision_reason=decision_reason, cooldown_until=cooldown_until,
        )

        if decision is None:
            # Buttons hinzufügen
            row = ui.ActionRow(
                ApplicationAcceptButton(),
                ApplicationDenyButton(),
            )
            container.add_item(_sep(large=True, visible=True))
            container.add_item(row)

        self.add_item(container)


def _extract_applicant_id(message: discord.Message) -> Optional[int]:
    """Extrahiert die Bewerber-ID aus dem Layout (Footer-TextDisplay)."""
    # Wir suchen einen TextDisplay-Inhalt der "Bewerber-ID: <number>" enthält
    if not message.components:
        return None

    def walk(components):
        for c in components:
            # API: c hat type+children
            if hasattr(c, "children"):
                yield from walk(c.children)
            yield c

    for c in walk(message.components):
        content = getattr(c, "content", None) or ""
        match = re.search(r"Bewerber-ID:\s*(\d+)", content)
        if match:
            return int(match.group(1))
    return None


def _extract_application_data(message: discord.Message) -> dict:
    """Liest alle Bewerbungs-Daten aus dem bestehenden Layout zurück."""
    data = {
        "applicant_id": 0, "applicant_tag": "", "applicant_avatar": "",
        "account_created": 0, "member_count": 0,
        "roblox_name": "", "experience": "", "why_fuse": "", "offer": "", "activity": "",
    }

    def walk(components):
        for c in components:
            if hasattr(c, "children"):
                yield from walk(c.children)
            yield c

    section_map = {
        "Roblox-Name & Alter": "roblox_name",
        "RP-Erfahrung":        "experience",
        "Warum FUSE?":         "why_fuse",
        "Was bietest du uns?": "offer",
        "Aktivität & Mikrofon":"activity",
    }

    for c in walk(message.components):
        content = getattr(c, "content", None) or ""

        # ID
        m = re.search(r"Bewerber-ID:\s*(\d+)", content)
        if m: data["applicant_id"] = int(m.group(1))

        # Avatar (aus Thumbnail)
        if hasattr(c, "media"):
            try:
                data["applicant_avatar"] = c.media.url
            except Exception: pass

        # Sections: matchen anhand des Section-Titles
        for title_key, data_key in section_map.items():
            if f"__{title_key}__" in content:
                # body steht in `> `-Zeilen direkt unter dem Header
                body_lines = []
                for line in content.split("\n")[1:]:
                    if line.startswith("> "):
                        body_lines.append(line[2:])
                    elif line.startswith(">"):
                        body_lines.append("")
                data[data_key] = "\n".join(body_lines).strip()

        if "👤  __Bewerber__" in content:
            tm = re.search(r"\*\*(.+?)\*\*", content)
            if tm: data["applicant_tag"] = tm.group(1)
            acm = re.search(r"<t:(\d+):R>", content)
            if acm: data["account_created"] = int(acm.group(1))
            mcm = re.search(r"Member-Count beim Eingang:\s*`?(\d+)", content)
            if mcm: data["member_count"] = int(mcm.group(1))

    return data


class ApplicationAcceptButton(ui.Button):
    def __init__(self):
        super().__init__(label="Annehmen", style=discord.ButtonStyle.success,
                         emoji="✅", custom_id="apply_accept")

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌  Du brauchst **Rollen verwalten**.", ephemeral=True)

        data = _extract_application_data(interaction.message)
        if not data["applicant_id"]:
            return await interaction.response.send_message("❌  Bewerber-ID nicht ermittelbar.", ephemeral=True)

        g = interaction.guild
        applicant = g.get_member(data["applicant_id"])
        if applicant is None:
            return await interaction.response.send_message("❌  Bewerber ist nicht mehr auf dem Server.", ephemeral=True)

        member_role  = _find_role(g, "💠 Member")
        bewerber     = _find_role(g, "📝 Bewerber")
        try:
            if member_role: await applicant.add_roles(member_role, reason=f"Bewerbung angenommen von {interaction.user}")
            if bewerber and bewerber in applicant.roles:
                await applicant.remove_roles(bewerber, reason="Bewerbung angenommen")
            db.DATA["cooldowns"].pop(str(applicant.id), None)
        except discord.Forbidden:
            return await interaction.response.send_message("❌  Rechte fehlen.", ephemeral=True)

        new_view = ApplicationDecisionLayoutView(
            applicant_id=data["applicant_id"], applicant_tag=data["applicant_tag"],
            applicant_avatar=data["applicant_avatar"], account_created=data["account_created"],
            member_count=data["member_count"],
            roblox_name=data["roblox_name"], experience=data["experience"],
            why_fuse=data["why_fuse"], offer=data["offer"], activity=data["activity"],
            decision="accepted", decided_by=interaction.user.mention,
        )
        await interaction.response.edit_message(view=new_view)

        # DB
        app_entry = db.DATA["applications"].get(str(interaction.message.id))
        if app_entry:
            app_entry["decided"] = "accepted"
            db.save()

        # DM
        try:
            dm = ui.LayoutView()
            dm.add_item(_build_container(
                "🎉", "Bewerbung angenommen!",
                f"**Glückwunsch, {applicant.mention}!**",
                [
                    ("💎", "Du bist jetzt Member",
                     f"Du hast jetzt **vollen Zugriff** auf {SERVER_TAG}.\n"
                     f"Erkunde die Community, lerne andere kennen, hab Spaß!"),
                    ("📌", "Empfohlene Kanäle",
                     f"{ARROW}  <#💬・chat>\n"
                     f"{ARROW}  <#🔔・ankündigungen>\n"
                     f"{ARROW}  <#🎫・ticket-öffnen>"),
                ],
                color=SUCCESS_COLOR,
                thumbnail_url=applicant.display_avatar.url,
            ))
            await applicant.send(view=dm)
        except Exception:
            pass


class ApplicationDenyButton(ui.Button):
    def __init__(self):
        super().__init__(label="Ablehnen", style=discord.ButtonStyle.danger,
                         emoji="❌", custom_id="apply_deny")

    async def callback(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_roles:
            return await interaction.response.send_message("❌  Du brauchst **Rollen verwalten**.", ephemeral=True)
        if not _extract_applicant_id(interaction.message):
            return await interaction.response.send_message("❌  Bewerber-ID nicht ermittelbar.", ephemeral=True)
        await interaction.response.send_modal(DenyReasonModal())


class DenyReasonModal(ui.Modal, title="❌ Bewerbung ablehnen"):
    reason = ui.TextInput(label="Begründung für Ablehnung",
                          style=discord.TextStyle.paragraph,
                          placeholder="z.B. zu wenig RP-Erfahrung, unvollständige Antworten...",
                          max_length=500, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        data = _extract_application_data(interaction.message)
        if not data["applicant_id"]:
            return await interaction.response.send_message("❌  Daten konnten nicht gelesen werden.", ephemeral=True)

        until = datetime.now(timezone.utc) + timedelta(minutes=APPLY_COOLDOWN_MIN)
        db.DATA["cooldowns"][str(data["applicant_id"])] = until.isoformat()
        db.save()

        new_view = ApplicationDecisionLayoutView(
            applicant_id=data["applicant_id"], applicant_tag=data["applicant_tag"],
            applicant_avatar=data["applicant_avatar"], account_created=data["account_created"],
            member_count=data["member_count"],
            roblox_name=data["roblox_name"], experience=data["experience"],
            why_fuse=data["why_fuse"], offer=data["offer"], activity=data["activity"],
            decision="denied", decided_by=interaction.user.mention,
            decision_reason=self.reason.value,
            cooldown_until=int(until.timestamp()),
        )
        await interaction.response.edit_message(view=new_view)

        # DB
        app_entry = db.DATA["applications"].get(str(interaction.message.id))
        if app_entry:
            app_entry["decided"] = "denied"
            db.save()

        # DM
        g = interaction.guild
        applicant = g.get_member(data["applicant_id"])
        if applicant:
            try:
                dm = ui.LayoutView()
                dm.add_item(_build_container(
                    "❌", "Bewerbung abgelehnt",
                    f"*Leider wurde deine Bewerbung bei {SERVER_TAG} abgelehnt.*",
                    [
                        ("📝", "Begründung", self.reason.value),
                        ("⏳", "Sperre",
                         f"Du kannst dich in **{APPLY_COOLDOWN_MIN} Minuten** erneut bewerben.\n"
                         f"Wieder möglich:  <t:{int(until.timestamp())}:R>"),
                        ("💡", "Tipp",
                         "Beantworte die Fragen beim nächsten Mal **ausführlicher**."),
                    ],
                    color=ERROR_COLOR,
                    thumbnail_url=applicant.display_avatar.url,
                ))
                await applicant.send(view=dm)
            except Exception: pass


# ─── APPLY (Channel Panel mit Button) ────────────────────────────
class ApplyButton(ui.Button):
    def __init__(self):
        super().__init__(label="Bewerbung starten", style=discord.ButtonStyle.success,
                         emoji="📋", custom_id="fuse_apply_btn")

    async def callback(self, interaction: discord.Interaction):
        g, m = interaction.guild, interaction.user
        member_role = _find_role(g, "💠 Member")
        if member_role and member_role in m.roles:
            return await interaction.response.send_message("✅  Du bist bereits Member!", ephemeral=True)
        ver = _find_role(g, "✅ Verified")
        if ver and ver not in m.roles:
            return await interaction.response.send_message(
                "❌  Du musst dich zuerst verifizieren (<#✅・verify>).", ephemeral=True,
            )
        raw = db.DATA["cooldowns"].get(str(m.id))
        if raw:
            try:
                cd = datetime.fromisoformat(raw)
                if cd > datetime.now(timezone.utc):
                    cv = ui.LayoutView()
                    cv.add_item(_build_container(
                        "⏳", "Du bist gesperrt",
                        "*Deine letzte Bewerbung wurde abgelehnt.*",
                        [
                            ("⏳", "Wieder möglich",
                             f"{ARROW}  <t:{int(cd.timestamp())}:R>\n"
                             f"{ARROW}  <t:{int(cd.timestamp())}:F>"),
                            ("💡", "Tipp",
                             "Nutze die Zeit um deine Antworten besser vorzubereiten!"),
                        ],
                        color=ERROR_COLOR,
                        thumbnail_url=m.display_avatar.url,
                    ))
                    return await interaction.response.send_message(view=cv, ephemeral=True)
            except Exception: pass
        await interaction.response.send_modal(ApplicationModal())


class ApplyLayoutView(ui.LayoutView):
    def __init__(self, guild: Optional[discord.Guild] = None):
        super().__init__(timeout=None)
        thumb = guild.icon.url if (guild and guild.icon) else None
        row = ui.ActionRow(ApplyButton())
        self.add_item(_build_container(
            "📋", "Bewerbung",
            f"**Du möchtest Member werden?** 🎯\n"
            f"*Klicke unten auf **📋 Bewerbung starten** — es öffnet sich ein Formular.\n"
            f"Beantworte alle Fragen ehrlich und ausführlich.*",
            [
                ("📌", "Wichtige Hinweise",
                 f"{ARROW}  Pro Versuch **1 Bewerbung**\n"
                 f"{ARROW}  Bei Ablehnung: **30 Min Sperre**\n"
                 f"{ARROW}  Bei Annahme: **sofort Member** 🎉"),
                ("⏱️", "Bearbeitungszeit",
                 "In der Regel **24 – 48 Stunden**.\n"
                 "Bei längerer Bearbeitung pingt der Bot das Recruiter-Team."),
            ],
            color=BRAND_COLOR,
            thumbnail_url=thumb,
            extra_components=[row],
        ))


# ─── BEWERBUNGS-INFO ──────────────────────────────────────────────
def bewerbungs_info_panel(guild: discord.Guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "📖", "Bewerbungs-Ablauf",
        "*So läuft deine Bewerbung ab — Schritt für Schritt.*",
        [
            ("📝", "Schritt 1  —  Formular",
             "Gehe in <#📋・bewerbung> und klicke auf **📋 Bewerbung starten**."),
            ("⏳", "Schritt 2  —  Warten",
             "Das Team prüft deine Bewerbung — meist in **24 – 48 Stunden**."),
            ("✅", "Schritt 3  —  Annahme",
             "Wirst du angenommen, bekommst du automatisch **💠 Member** und vollen Zugriff."),
            ("❌", "Schritt 4  —  Ablehnung",
             "Bei Ablehnung gibt es eine **30 Min Sperre**.\n"
             "Du bekommst eine **DM mit Begründung**."),
        ],
        color=INFO_COLOR,
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


# ─── WELCOME ──────────────────────────────────────────────────────
def welcome_panel(guild: discord.Guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "🎉", f"Willkommen auf {SERVER_TAG}",
        f"**Roblox  ✘  Roleplay  ✘  Crime-Gang** {BRAND_DIAMOND}\n"
        f"*Schön dass du den Weg zu uns gefunden hast.*",
        [
            ("📌", "Deine ersten Schritte",
             f"{ARROW}  Lies das <#📜・regelwerk>\n"
             f"{ARROW}  Verifiziere dich im <#✅・verify>\n"
             f"{ARROW}  Sende deine Bewerbung im <#📋・bewerbung>\n"
             f"{ARROW}  Werde **Member** & erlebe die volle Community"),
            ("💎", "Was dich erwartet",
             f"{STAR}  Aktive Voice- & Chat-Community\n"
             f"{STAR}  Events, Giveaways & Meetings\n"
             f"{STAR}  Eigenes Roleplay-System\n"
             f"{STAR}  Faires & freundliches Team"),
        ],
        color=BRAND_COLOR,
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


def welcome_join_panel(member: discord.Member) -> ui.LayoutView:
    g = member.guild
    v = ui.LayoutView()
    v.add_item(_build_container(
        "🎉", f"Willkommen in {SERVER_TAG}!",
        f"**Hey {member.mention}!** 👋\n"
        f"*Du bist unser **{g.member_count}. Member** — schön dass du da bist!*",
        [
            ("📌", "Deine ersten Schritte",
             f"{ARROW}  Lies das <#📜・regelwerk>\n"
             f"{ARROW}  Verifiziere dich im <#✅・verify>\n"
             f"{ARROW}  Bewirb dich im <#📋・bewerbung>"),
            ("💎", "Sei willkommen",
             "*Bitte halte dich an die Regeln und sei freundlich zu allen.*\n"
             "**Viel Spaß bei uns!** 🎉"),
        ],
        color=BRAND_COLOR,
        thumbnail_url=member.display_avatar.url,
        footer_text=f"User-ID: {member.id}",
    ))
    return v


def goodbye_panel(member: discord.Member) -> ui.LayoutView:
    g = member.guild
    v = ui.LayoutView()
    joined = f"{ARROW}  Beitritt: <t:{int(member.joined_at.timestamp())}:R>\n" if member.joined_at else ""
    v.add_item(_build_container(
        "👋", "Tschüss!",
        f"**{member}** *hat den Server verlassen.*",
        [
            ("📊", "Aktueller Stand",
             f"{DOT}  Wir sind jetzt **{g.member_count}** Member\n{joined}"),
        ],
        color=ERROR_COLOR,
        thumbnail_url=member.display_avatar.url,
    ))
    return v


# ─── TICKETS ──────────────────────────────────────────────────────
TICKET_CATEGORIES = {
    "general":  {"label": "Allgemeine Frage", "emoji": "❓", "color": INFO_COLOR,
                 "desc":  "Allgemeine Fragen zum Server."},
    "problem":  {"label": "Problem / Bug",    "emoji": "🐛", "color": ERROR_COLOR,
                 "desc":  "Etwas funktioniert nicht oder ist kaputt."},
    "report":   {"label": "Player-Meldung",   "emoji": "🚨", "color": discord.Color(0xFF4500),
                 "desc":  "Ein Spieler verstößt gegen Regeln."},
    "partner":  {"label": "Partnerschaft",    "emoji": "🤝", "color": discord.Color(0x1ABC9C),
                 "desc":  "Partner-Anfrage."},
    "other":    {"label": "Sonstiges",        "emoji": "💎", "color": PURPLE_COLOR,
                 "desc":  "Alles andere."},
}


STAFF_ROLE_NAMES = [
    "👑 Owner", "👑 Co-Owner", "🛡️ Server-Manager",
    "⚡ Head-Admin", "⚡ Admin", "⚡ Vize-Admin",
    "🔨 Head-Moderator", "🔨 Senior-Moderator", "🔨 Moderator", "🔨 Trial-Moderator",
    "🎧 Support-Lead", "🎧 Supporter", "🎧 Trial-Supporter",
    "💻 Developer", "🤖 Bot-Manager",
]


def ticket_info_panel(guild: discord.Guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "📖", "Ticket-System",
        "*Wofür kannst du ein Ticket öffnen?*",
        [(c["emoji"], c["label"], c["desc"]) for c in TICKET_CATEGORIES.values()],
        color=GOLD_COLOR,
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


class TicketCategorySelect(ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="🎫  Wähle eine Ticket-Kategorie…",
            custom_id="fuse_ticket_select",
            min_values=1, max_values=1,
            options=[
                discord.SelectOption(label=c["label"], emoji=c["emoji"],
                                     description=c["desc"], value=key)
                for key, c in TICKET_CATEGORIES.items()
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        cat_key = self.values[0]
        # Reset Select-Anzeige
        if cat_key == "report":
            await interaction.response.send_modal(ReportModal())
        else:
            await _create_ticket(interaction, cat_key)


class TicketCategoryLayoutView(ui.LayoutView):
    def __init__(self, guild: Optional[discord.Guild] = None):
        super().__init__(timeout=None)
        thumb = guild.icon.url if (guild and guild.icon) else None
        row = ui.ActionRow(TicketCategorySelect())
        self.add_item(_build_container(
            "🎫", "Ticket eröffnen",
            "**Brauchst du Hilfe?** 💬\n"
            "*Wähle unten eine Kategorie aus dem Menü.\n"
            "Es wird ein privater Kanal für dich und das Team erstellt.*",
            [
                ("⚡", "Was passiert",
                 f"{DOT}  Eigener privater Kanal für dich\n"
                 f"{DOT}  Nur du & das Team können ihn sehen\n"
                 f"{DOT}  Beim Schließen: HTML-Transcript per DM"),
                ("⚠️", "Hinweis",
                 "*Missbrauch des Ticket-Systems wird sanktioniert.*"),
            ],
            color=GOLD_COLOR,
            thumbnail_url=thumb,
            extra_components=[row],
        ))


class ReportModal(ui.Modal, title="🚨 Player-Meldung"):
    reported_user = ui.TextInput(label="Wen meldest du? (Name / ID)",
                                  placeholder="z.B. @JustVexo oder 123456789",
                                  max_length=100, required=True)
    what_happened = ui.TextInput(label="Was ist passiert?",
                                  style=discord.TextStyle.paragraph,
                                  placeholder="Beschreibe genau...",
                                  max_length=800, required=True)
    proof = ui.TextInput(label="Beweise (Links zu Bildern/Clips)",
                          style=discord.TextStyle.paragraph,
                          placeholder="https://...",
                          max_length=400, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await _create_ticket(interaction, "report", extra_sections=[
            ("🎯", "Gemeldeter User",  self.reported_user.value),
            ("📝", "Was passiert ist", self.what_happened.value),
            ("📎", "Beweise",          self.proof.value or "— keine —"),
        ])


async def _create_ticket(interaction: discord.Interaction, cat_key: str,
                         extra_sections: Optional[list] = None):
    g, m = interaction.guild, interaction.user
    cat = TICKET_CATEGORIES[cat_key]

    existing = discord.utils.get(g.text_channels, name=f"ticket-{cat_key}-{m.name.lower()}")
    if existing:
        if not interaction.response.is_done():
            return await interaction.response.send_message(
                f"❗  Du hast bereits ein offenes Ticket: {existing.mention}", ephemeral=True,
            )
        else:
            return await interaction.followup.send(
                f"❗  Du hast bereits ein offenes Ticket: {existing.mention}", ephemeral=True,
            )

    parent = discord.utils.get(g.categories, name="🎫 ✘ SUPPORT")
    ow = {
        g.default_role: discord.PermissionOverwrite(view_channel=False),
        m:              discord.PermissionOverwrite(view_channel=True, send_messages=True,
                                                    attach_files=True, read_message_history=True,
                                                    embed_links=True),
        g.me:           discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
    }
    for rn in STAFF_ROLE_NAMES:
        r = _find_role(g, rn)
        if r:
            ow[r] = discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_messages=True)

    ticket = await g.create_text_channel(
        f"ticket-{cat_key}-{m.name.lower()}"[:90],
        category=parent, overwrites=ow,
        topic=f"{cat['label']} • Ersteller: {m.id}",
        reason=f"Ticket: {cat['label']}",
    )

    # Ticket-Innen-Panel
    sections = [
        ("📝", "Beschreibe dein Anliegen",
         "Bitte beschreibe dein Anliegen **so genau wie möglich**.\n"
         "Füge Screenshots, Beweise oder Links bei wenn relevant."),
        ("⏱️", "Bearbeitungszeit",
         "Das Team meldet sich in der Regel innerhalb **weniger Minuten**."),
        ("🔒", "Nach dem Schließen",
         "Beim Schließen erhältst du **per DM** ein vollständiges HTML-Transcript."),
    ]
    if extra_sections:
        sections.extend(extra_sections)

    row = ui.ActionRow(TicketCloseButton(), TicketClaimButton())
    inside = ui.LayoutView()
    inside.add_item(_build_container(
        cat["emoji"], f"Ticket  ❖  {cat['label']}",
        f"**Hallo {m.mention}!** {cat['emoji']}\n"
        f"*Vielen Dank für dein Anliegen — ein Team-Mitglied meldet sich gleich.*",
        sections,
        color=cat["color"],
        thumbnail_url=m.display_avatar.url,
        extra_components=[row],
        footer_text=f"Ticket-Opener: {m.id}  ❖  Kategorie: {cat['label']}",
    ))
    await ticket.send(view=inside)

    # Response zum User
    if not interaction.response.is_done():
        await interaction.response.send_message(f"✅  Ticket erstellt: {ticket.mention}", ephemeral=True)
    else:
        await interaction.followup.send(f"✅  Ticket erstellt: {ticket.mention}", ephemeral=True)

    # Log
    log_ch = _get_log_channel(g, "ticket")
    if log_ch:
        lv = ui.LayoutView()
        lv.add_item(_build_container(
            cat["emoji"], "Ticket geöffnet",
            f"{ARROW}  **Kategorie:**  {cat['label']}\n"
            f"{ARROW}  **User:**  {m.mention}\n"
            f"{ARROW}  **Kanal:**  {ticket.mention}",
            [],
            color=cat["color"],
            thumbnail_url=m.display_avatar.url,
        ))
        await log_ch.send(view=lv)


class TicketCloseButton(ui.Button):
    def __init__(self):
        super().__init__(label="Schließen", style=discord.ButtonStyle.danger,
                         emoji="🔒", custom_id="ticket_close")

    async def callback(self, interaction: discord.Interaction):
        row = ui.ActionRow(TicketCloseConfirmYes(), TicketCloseConfirmNo())
        v = ui.LayoutView()
        v.add_item(_build_container(
            "🔒", "Ticket schließen?",
            "Möchtest du dieses Ticket wirklich schließen?",
            [
                ("📝", "Was passiert",
                 f"{DOT}  HTML-Transcript wird generiert\n"
                 f"{DOT}  Du bekommst es per DM\n"
                 f"{DOT}  Channel wird in 5s gelöscht"),
            ],
            color=ERROR_COLOR,
            extra_components=[row],
        ))
        await interaction.response.send_message(view=v)


class TicketClaimButton(ui.Button):
    def __init__(self):
        super().__init__(label="Claim", style=discord.ButtonStyle.primary,
                         emoji="🙋", custom_id="ticket_claim")

    async def callback(self, interaction: discord.Interaction):
        if not any(_find_role(interaction.guild, rn) in interaction.user.roles
                   for rn in STAFF_ROLE_NAMES if _find_role(interaction.guild, rn)):
            return await interaction.response.send_message("❌  Nur Staff kann Tickets claimen.", ephemeral=True)
        v = ui.LayoutView()
        v.add_item(_build_container(
            "🙋", "Ticket übernommen",
            f"{interaction.user.mention} *kümmert sich um dieses Ticket.*",
            [],
            color=SUCCESS_COLOR,
            thumbnail_url=interaction.user.display_avatar.url,
        ))
        await interaction.response.send_message(view=v)


class TicketCloseConfirmYes(ui.Button):
    def __init__(self):
        super().__init__(label="Ja, schließen", style=discord.ButtonStyle.danger,
                         emoji="🔒", custom_id="ticket_close_yes")

    async def callback(self, interaction: discord.Interaction):
        v = ui.LayoutView()
        v.add_item(_build_container(
            "🔒", "Ticket wird geschlossen…",
            "Transcript wird in 5 Sekunden erstellt und der Kanal gelöscht.",
            [], color=ERROR_COLOR,
        ))
        await interaction.response.edit_message(view=v)
        await asyncio.sleep(5)
        try:
            transcript = None
            try:
                from cogs.transcripts import build_transcript
                transcript = await build_transcript(interaction.channel)
            except Exception: pass

            opener_id = None
            try:
                topic = interaction.channel.topic or ""
                if "Ersteller:" in topic:
                    opener_id = int(topic.split("Ersteller:")[1].strip().split()[0])
            except Exception: pass

            log_ch = _get_log_channel(interaction.guild, "ticket")
            if log_ch:
                lv = ui.LayoutView()
                lv.add_item(_build_container(
                    "🔒", "Ticket geschlossen",
                    f"{ARROW}  **Channel:**  `{interaction.channel.name}`\n"
                    f"{ARROW}  **Geschlossen von:**  {interaction.user.mention}\n"
                    f"{ARROW}  **Opener:**  {f'<@{opener_id}>' if opener_id else '—'}",
                    [], color=ERROR_COLOR,
                    thumbnail_url=interaction.user.display_avatar.url,
                ))
                if transcript:
                    await log_ch.send(view=lv, files=[transcript])
                else:
                    await log_ch.send(view=lv)

            if opener_id:
                opener = interaction.guild.get_member(opener_id)
                if opener:
                    try:
                        dmv = ui.LayoutView()
                        dmv.add_item(_build_container(
                            "📝", "Dein Ticket wurde geschlossen",
                            f"*Dein Ticket `{interaction.channel.name}` wurde von "
                            f"{interaction.user.mention} geschlossen.*\n\n"
                            "Im Anhang findest du das vollständige Transcript.",
                            [], color=ERROR_COLOR,
                            thumbnail_url=opener.display_avatar.url,
                        ))
                        from cogs.transcripts import build_transcript
                        t2 = await build_transcript(interaction.channel)
                        await opener.send(view=dmv, files=[t2])
                    except Exception: pass

            await interaction.channel.delete(reason="Ticket geschlossen")
        except Exception: pass


class TicketCloseConfirmNo(ui.Button):
    def __init__(self):
        super().__init__(label="Abbrechen", style=discord.ButtonStyle.secondary,
                         emoji="✖️", custom_id="ticket_close_no")

    async def callback(self, interaction: discord.Interaction):
        v = ui.LayoutView()
        v.add_item(_build_container(
            "✖️", "Abgebrochen",
            "Ticket bleibt offen.",
            [], color=INFO_COLOR,
        ))
        await interaction.response.edit_message(view=v)


# ─── SETUP-WIZARD ─────────────────────────────────────────────────
def setup_wizard_panel(ctx_guild: discord.Guild, author_id: int) -> ui.LayoutView:
    row = ui.ActionRow(
        SetupCancelButton(author_id),
        SetupAddButton(author_id),
        SetupFreshButton(author_id),
    )
    v = ui.LayoutView(timeout=180)
    v.add_item(_build_container(
        "⚙️", f"{SERVER_TAG}  ❖  Setup Wizard",
        "*Willkommen zum Server-Setup. Wähle unten eine Option.*",
        [
            ("🛑", "Abbruch",            "Nichts tun, Wizard schließen."),
            ("➕", "Nur Hinzufügen",      "Fehlende Rollen & Kanäle ergänzen — **Bestehendes bleibt**."),
            ("♻️", "Komplett neu",        "**ALLES** löschen & neu erstellen *(mit Sicherheitsfrage)*."),
            ("⚠️", "Voraussetzungen",
             f"{ARROW}  **Bot-Rolle ganz oben** in der Hierarchie\n"
             f"{ARROW}  **Administrator-Rechte** erteilt"),
        ],
        color=BRAND_COLOR,
        thumbnail_url=ctx_guild.icon.url if ctx_guild.icon else None,
        extra_components=[row],
        footer_text="nur Admins",
    ))
    return v


class _AuthorCheckMixin:
    def __init__(self, author_id: int):
        self.author_id = author_id

    async def _check(self, interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("❌  Nur der Befehls-Autor.", ephemeral=True)
            return False
        return True


class SetupCancelButton(ui.Button, _AuthorCheckMixin):
    def __init__(self, author_id: int):
        ui.Button.__init__(self, label="Abbruch", style=discord.ButtonStyle.danger, emoji="🛑")
        _AuthorCheckMixin.__init__(self, author_id)

    async def callback(self, interaction):
        if not await self._check(interaction): return
        v = ui.LayoutView()
        v.add_item(_build_container("🛑", "Setup abgebrochen", "Keine Änderungen vorgenommen.", [],
                                    color=ERROR_COLOR))
        await interaction.response.edit_message(view=v)


class SetupAddButton(ui.Button, _AuthorCheckMixin):
    def __init__(self, author_id: int):
        ui.Button.__init__(self, label="Nur Hinzufügen", style=discord.ButtonStyle.primary, emoji="➕")
        _AuthorCheckMixin.__init__(self, author_id)

    async def callback(self, interaction):
        if not await self._check(interaction): return
        v = ui.LayoutView()
        v.add_item(_build_container("⏳", "Setup läuft…",
                                    "Fehlende Rollen & Kanäle werden ergänzt.", [],
                                    color=INFO_COLOR))
        await interaction.response.edit_message(view=v)
        msg = await interaction.original_response()
        from bot import run_setup
        await run_setup(interaction.guild, msg, wipe=False)


class SetupFreshButton(ui.Button, _AuthorCheckMixin):
    def __init__(self, author_id: int):
        ui.Button.__init__(self, label="Komplett neu", style=discord.ButtonStyle.success, emoji="♻️")
        _AuthorCheckMixin.__init__(self, author_id)

    async def callback(self, interaction):
        if not await self._check(interaction): return
        row = ui.ActionRow(WipeYesButton(self.author_id), WipeNoButton(self.author_id))
        v = ui.LayoutView()
        v.add_item(_build_container(
            "⚠️", "Wirklich komplett neu?",
            "**ALLE Kanäle und Rollen werden gelöscht!**\nDieser Vorgang ist **NICHT** rückgängig zu machen.",
            [], color=ERROR_COLOR, extra_components=[row],
        ))
        await interaction.response.edit_message(view=v)


class WipeYesButton(ui.Button, _AuthorCheckMixin):
    def __init__(self, author_id: int):
        ui.Button.__init__(self, label="Ja, alles löschen", style=discord.ButtonStyle.danger, emoji="♻️")
        _AuthorCheckMixin.__init__(self, author_id)

    async def callback(self, interaction):
        if not await self._check(interaction): return
        v = ui.LayoutView()
        v.add_item(_build_container("⏳", "Server wird zurückgesetzt…",
                                    "Alle Kanäle & Rollen werden gelöscht und neu aufgebaut.", [],
                                    color=INFO_COLOR))
        await interaction.response.edit_message(view=v)
        msg = await interaction.original_response()
        from bot import run_setup
        await run_setup(interaction.guild, msg, wipe=True)


class WipeNoButton(ui.Button, _AuthorCheckMixin):
    def __init__(self, author_id: int):
        ui.Button.__init__(self, label="Abbrechen", style=discord.ButtonStyle.secondary, emoji="✖️")
        _AuthorCheckMixin.__init__(self, author_id)

    async def callback(self, interaction):
        if not await self._check(interaction): return
        v = ui.LayoutView()
        v.add_item(_build_container("🛑", "Abgebrochen", "Es wurde nichts geändert.", [],
                                    color=ERROR_COLOR))
        await interaction.response.edit_message(view=v)


# ─── STATUS / SIMPLE PANELS ───────────────────────────────────────
def status_panel(emoji: str, title: str, body: str, color: discord.Color = INFO_COLOR,
                 guild: Optional[discord.Guild] = None) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(emoji, title, body, [], color=color,
                                 thumbnail_url=guild.icon.url if (guild and guild.icon) else None))
    return v


def setup_done_panel(guild: discord.Guild, n_roles: int, n_cats: int, n_chans: int) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "✅", "Setup abgeschlossen!",
        f"**{SERVER_TAG}** *ist komplett eingerichtet.* 🎉",
        [
            ("📊", "Statistik",
             f"{ARROW}  🎭  Rollen:        **{n_roles}**\n"
             f"{ARROW}  📁  Kategorien:   **{n_cats}**\n"
             f"{ARROW}  💬  Kanäle:        **{n_chans}**"),
            ("⚠️", "Wichtig",
             "Lasse die **Bot-Rolle** ganz oben in der Hierarchie.\n"
             "Nutze `!stats-setup` für Live-Counter-Channels."),
            ("🚀", "Nächste Schritte",
             f"{DOT}  `!stats-setup` für Live-Stats\n"
             f"{DOT}  Slash-Commands sind nach ~1 Min aktiv\n"
             f"{DOT}  Owner-Rolle dir selbst vergeben"),
        ],
        color=SUCCESS_COLOR,
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


# ─── ANN / BOOSTS / CHAT / PARTNER ────────────────────────────────
def announcement_panel(guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "🔔", "Ankündigungen",
        "*Hier postet das Team alle wichtigen News.*",
        [("📣", "Themen",
          f"{ARROW}  Updates & Patches\n{ARROW}  Events & Meetings\n{ARROW}  Regel-Änderungen")],
        color=BRAND_COLOR, thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


def boost_panel(guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "🚀", "Server Boosts",
        f"**Danke an alle Booster!** 💖",
        [("🎁", "Vorteile",
          f"{ARROW}  💖  Booster-Rolle\n"
          f"{ARROW}  🔒  Locked-Lounges\n"
          f"{ARROW}  🎨  Eigene Farbe")],
        color=discord.Color(0xF47FFF),
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


def chat_panel(guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "💬", "Community-Chat",
        "Hier kannst du **frei mit anderen Membern quatschen**.\n"
        "Halte dich an die Regeln und hab Spaß!",
        [], color=BRAND_COLOR,
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


def partner_panel(guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "🤝", "Partnerschaft",
        "*Interesse an einer Partnerschaft?*",
        [
            ("📑", "Anforderungen",
             f"{ARROW}  **min. 50 Member**\n"
             f"{ARROW}  aktive Community\n"
             f"{ARROW}  keine NSFW / Toxic Server"),
            ("📨", "Interesse?",
             "Öffne ein Ticket und wähle **Partnerschaft**."),
        ],
        color=discord.Color(0x1ABC9C),
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


def owner_chat_panel(guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "👑", "Owner-Chat",
        "*Privater Kanal **ausschließlich** für Owner & Co-Owner.*",
        [], color=discord.Color(0xFF0000),
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v


def admin_chat_panel(guild) -> ui.LayoutView:
    v = ui.LayoutView()
    v.add_item(_build_container(
        "⚡", "Admin-Chat",
        "*Privater Kanal für das **Admin-Team**.*",
        [], color=discord.Color(0xFF8000),
        thumbnail_url=guild.icon.url if guild.icon else None,
    ))
    return v
