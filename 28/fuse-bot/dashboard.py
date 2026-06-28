"""
🎛️ WEB-DASHBOARD (Flask)
Läuft parallel zum Bot in einem Thread.
- Discord OAuth Login
- Übersicht Member / Warns / Bewerbungen / XP
- Read-only (Schreibzugriffe via Bot-Commands)

ENV VARS (in Railway):
    OAUTH_CLIENT_ID
    OAUTH_CLIENT_SECRET
    OAUTH_REDIRECT_URI    (z.B. https://deinapp.railway.app/callback)
    DASHBOARD_SECRET      (random string für Session)
    PORT                  (von Railway gesetzt)
"""
import os
import time
import threading
import secrets

import requests
from flask import Flask, request, redirect, session, render_template_string, url_for, abort

import db

CLIENT_ID     = os.getenv("OAUTH_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "")
REDIRECT_URI  = os.getenv("OAUTH_REDIRECT_URI", "")
SECRET        = os.getenv("DASHBOARD_SECRET", secrets.token_hex(32))
PORT          = int(os.getenv("PORT", "8080"))

app = Flask(__name__)
app.secret_key = SECRET

OAUTH_BASE = "https://discord.com/api/oauth2/authorize"
TOKEN_URL  = "https://discord.com/api/oauth2/token"
USER_URL   = "https://discord.com/api/users/@me"
GUILDS_URL = "https://discord.com/api/users/@me/guilds"


# ─── Templates ────────────────────────────────────────────────────
BASE_TPL = """
<!doctype html><html><head><meta charset="utf-8"><title>{{ title }} • FUSE Dashboard</title>
<style>
  body { background:#0f1015; color:#dcddde; font-family:'Segoe UI',sans-serif; margin:0; }
  .nav { background:#1a1b22; padding:14px 24px; border-bottom:2px solid #E91E63; display:flex; gap:16px; align-items:center; }
  .nav a { color:#fff; text-decoration:none; padding:6px 12px; border-radius:6px; }
  .nav a:hover { background:#2a2c35; }
  .nav .brand { font-weight:700; color:#E91E63; font-size:18px; }
  .nav .right { margin-left:auto; display:flex; align-items:center; gap:10px; }
  .avatar { width:32px; height:32px; border-radius:50%; }
  .container { max-width:1100px; margin:24px auto; padding:0 16px; }
  .card { background:#1a1b22; border-radius:10px; padding:18px; margin-bottom:16px; border-left:4px solid #E91E63; }
  h1, h2 { color:#fff; margin-top:0; }
  table { width:100%; border-collapse:collapse; }
  th, td { padding:10px 12px; text-align:left; border-bottom:1px solid #2a2c35; }
  th { color:#E91E63; }
  .btn { background:#E91E63; color:#fff; padding:8px 16px; border-radius:6px; text-decoration:none; display:inline-block; }
  .stat { display:inline-block; background:#2a2c35; padding:14px 20px; border-radius:10px; margin-right:10px; margin-bottom:10px; }
  .stat .num { font-size:24px; font-weight:700; color:#E91E63; }
  .stat .lbl { font-size:12px; color:#a3a6aa; text-transform:uppercase; }
</style></head><body>
<div class="nav">
  <span class="brand">🎛️ FUSE Dashboard</span>
  <a href="/">Übersicht</a>
  <a href="/members">Members</a>
  <a href="/warns">Warns</a>
  <a href="/applications">Bewerbungen</a>
  <a href="/xp">XP / Leaderboard</a>
  <div class="right">
    {% if user %}
      <img class="avatar" src="https://cdn.discordapp.com/avatars/{{ user.id }}/{{ user.avatar }}.png">
      <span>{{ user.username }}</span>
      <a class="btn" href="/logout">Logout</a>
    {% else %}
      <a class="btn" href="/login">🔐 Login</a>
    {% endif %}
  </div>
</div>
<div class="container">{{ body|safe }}</div>
</body></html>
"""


def render(title, body, user=None):
    return render_template_string(BASE_TPL, title=title, body=body, user=user)


def require_login():
    if "user" not in session:
        abort(redirect("/login"))
    return session["user"]


# ─── Routes ───────────────────────────────────────────────────────
@app.route("/")
def index():
    user = session.get("user")
    db.reload()
    stats = f"""
      <div class="card">
        <h1>🎛️ FUSE | FS Dashboard</h1>
        <p>Willkommen{', <b>' + user['username'] + '</b>' if user else ''}.</p>
        <div>
          <div class="stat"><div class="num">{len(db.DATA['xp'])}</div><div class="lbl">Tracked Users</div></div>
          <div class="stat"><div class="num">{sum(len(v) for v in db.DATA['warns'].values())}</div><div class="lbl">Warns Total</div></div>
          <div class="stat"><div class="num">{len([a for a in db.DATA['applications'].values() if not a.get('decided')])}</div><div class="lbl">Offene Bewerbungen</div></div>
          <div class="stat"><div class="num">{len([g for g in db.DATA['giveaways'].values() if not g.get('ended')])}</div><div class="lbl">Aktive Giveaways</div></div>
          <div class="stat"><div class="num">{len(db.DATA['birthdays'])}</div><div class="lbl">Geburtstage</div></div>
        </div>
      </div>
      <div class="card">
        <h2>📊 Schnellzugriff</h2>
        <a class="btn" href="/members">👥 Members</a>
        <a class="btn" href="/warns">⚠️ Warns</a>
        <a class="btn" href="/applications">📋 Bewerbungen</a>
        <a class="btn" href="/xp">🏆 Leaderboard</a>
      </div>
    """
    return render("Übersicht", stats, user)


@app.route("/login")
def login():
    state = secrets.token_urlsafe(16)
    session["state"] = state
    url = (f"{OAUTH_BASE}?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}"
           f"&response_type=code&scope=identify&state={state}")
    return redirect(url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/callback")
def callback():
    code = request.args.get("code")
    if not code: return "Login abgebrochen.", 400
    data = {
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code", "code": code,
        "redirect_uri": REDIRECT_URI, "scope": "identify",
    }
    r = requests.post(TOKEN_URL, data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    if r.status_code != 200: return f"Token error: {r.text}", 400
    token = r.json()["access_token"]
    u = requests.get(USER_URL, headers={"Authorization": f"Bearer {token}"}).json()
    session["user"] = {"id": u["id"], "username": u["username"], "avatar": u.get("avatar", "")}
    return redirect("/")


@app.route("/members")
def members():
    user = require_login()
    db.reload()
    rows = ""
    sorted_xp = sorted(db.DATA["xp"].items(), key=lambda x: x[1].get("xp", 0), reverse=True)[:50]
    for uid, d in sorted_xp:
        warns = len(db.DATA["warns"].get(uid, []))
        rows += f"<tr><td>{uid}</td><td>{d.get('level',0)}</td><td>{d.get('xp',0):,}</td><td>{d.get('msgs',0):,}</td><td>{d.get('voice_minutes',0):,}</td><td>{warns}</td></tr>"
    body = f"""
      <div class="card"><h1>👥 Members (Top 50 nach XP)</h1>
      <table><tr><th>User-ID</th><th>Level</th><th>XP</th><th>Msgs</th><th>Voice min</th><th>Warns</th></tr>{rows}</table></div>
    """
    return render("Members", body, user)


@app.route("/warns")
def warns_route():
    user = require_login()
    db.reload()
    rows = ""
    for uid, ws in db.DATA["warns"].items():
        if not ws: continue
        for w in ws:
            rows += f"<tr><td>{uid}</td><td>{w['reason']}</td><td>{w['mod_id']}</td><td>{time.strftime('%d.%m.%Y %H:%M', time.gmtime(w['ts']))}</td></tr>"
    body = f"""
      <div class="card"><h1>⚠️ Warnungen</h1>
      <table><tr><th>User-ID</th><th>Grund</th><th>Mod-ID</th><th>Zeit</th></tr>{rows or '<tr><td colspan=4>Keine Warns</td></tr>'}</table></div>
    """
    return render("Warns", body, user)


@app.route("/applications")
def applications():
    user = require_login()
    db.reload()
    rows = ""
    for mid, app in db.DATA["applications"].items():
        status = app.get("decided") or "offen"
        ts = time.strftime("%d.%m.%Y %H:%M", time.gmtime(app["posted_ts"]))
        rows += f"<tr><td>{mid}</td><td>{app['applicant_id']}</td><td>{ts}</td><td>{status}</td></tr>"
    body = f"""
      <div class="card"><h1>📋 Bewerbungen</h1>
      <table><tr><th>Msg-ID</th><th>Bewerber-ID</th><th>Eingereicht</th><th>Status</th></tr>{rows or '<tr><td colspan=4>Keine</td></tr>'}</table></div>
    """
    return render("Bewerbungen", body, user)


@app.route("/xp")
def xp_route():
    user = require_login()
    db.reload()
    sorted_xp = sorted(db.DATA["xp"].items(), key=lambda x: x[1].get("xp", 0), reverse=True)[:50]
    rows = ""
    medals = ["🥇","🥈","🥉"] + ["▫️"]*47
    for i, (uid, d) in enumerate(sorted_xp):
        rows += f"<tr><td>{medals[i]}</td><td>{uid}</td><td>{d.get('level',0)}</td><td>{d.get('xp',0):,}</td><td>{d.get('msgs',0):,}</td><td>{d.get('voice_minutes',0):,}</td></tr>"
    body = f"""
      <div class="card"><h1>🏆 XP Leaderboard</h1>
      <table><tr><th></th><th>User-ID</th><th>Level</th><th>XP</th><th>Msgs</th><th>Voice min</th></tr>{rows}</table></div>
    """
    return render("Leaderboard", body, user)


def run_dashboard():
    """In Thread starten."""
    if not (CLIENT_ID and CLIENT_SECRET and REDIRECT_URI):
        print("[Dashboard] OAuth-Env-Vars fehlen — Dashboard läuft im Read-Only-Modus ohne Login.")
    app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False)


def start_in_thread():
    t = threading.Thread(target=run_dashboard, daemon=True)
    t.start()
    print(f"[Dashboard] gestartet auf Port {PORT}")
