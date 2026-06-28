"""
📝 TICKET-TRANSCRIPT GENERATOR
Erzeugt eine schön gestylte HTML-Datei beim Schließen eines Tickets.
"""
import io
import html as html_lib
from datetime import datetime

import discord


def escape(s: str) -> str:
    return html_lib.escape(s or "")


async def build_transcript(channel: discord.TextChannel) -> discord.File:
    messages = []
    async for m in channel.history(limit=2000, oldest_first=True):
        messages.append(m)

    rows_html = []
    for m in messages:
        avatar = m.author.display_avatar.url
        name = escape(str(m.author))
        ts = m.created_at.strftime("%d.%m.%Y %H:%M")
        content = escape(m.content).replace("\n", "<br>")
        attachments = ""
        for a in m.attachments:
            if a.content_type and a.content_type.startswith("image/"):
                attachments += f'<div><img src="{a.url}" style="max-width:300px;border-radius:8px;margin-top:6px"></div>'
            else:
                attachments += f'<div><a href="{a.url}">📎 {escape(a.filename)}</a></div>'
        embeds = ""
        for e in m.embeds:
            t = escape(e.title or "")
            d = escape(e.description or "").replace("\n", "<br>")
            embeds += f'<div class="embed"><div class="embed-title">{t}</div><div>{d}</div></div>'
        rows_html.append(f'''
        <div class="msg">
          <img class="avatar" src="{avatar}">
          <div class="body">
            <div class="head"><span class="name">{name}</span><span class="ts">{ts}</span></div>
            <div class="content">{content}</div>
            {attachments}
            {embeds}
          </div>
        </div>
        ''')

    html_doc = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Transcript — #{channel.name}</title>
<style>
  body {{ background:#1e1f22; color:#dcddde; font-family:'Segoe UI',sans-serif; margin:0; padding:24px; }}
  .head-bar {{ background:#2b2d31; padding:16px 24px; border-radius:12px; margin-bottom:16px; border-left:4px solid #E91E63; }}
  .head-bar h1 {{ margin:0; color:#fff; font-size:22px; }}
  .head-bar small {{ color:#b9bbbe; }}
  .msg {{ display:flex; padding:8px 0; border-bottom:1px solid #2a2c31; }}
  .avatar {{ width:42px; height:42px; border-radius:50%; margin-right:12px; }}
  .name {{ font-weight:600; color:#fff; }}
  .ts {{ color:#a3a6aa; font-size:12px; margin-left:8px; }}
  .content {{ margin-top:2px; word-wrap:break-word; }}
  .embed {{ border-left:4px solid #E91E63; background:#2b2d31; padding:10px 14px; margin-top:8px; border-radius:4px; max-width:520px; }}
  .embed-title {{ font-weight:600; color:#fff; margin-bottom:4px; }}
  a {{ color:#00aff4; }}
</style></head><body>
<div class="head-bar">
  <h1>📝 Ticket-Transcript — #{escape(channel.name)}</h1>
  <small>Erstellt: {datetime.utcnow().strftime('%d.%m.%Y %H:%M UTC')} • {len(messages)} Nachrichten</small>
</div>
{"".join(rows_html)}
</body></html>"""

    buf = io.BytesIO(html_doc.encode("utf-8"))
    return discord.File(buf, filename=f"transcript-{channel.name}.html")
