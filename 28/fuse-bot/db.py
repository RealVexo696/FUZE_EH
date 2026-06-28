"""
Einfache JSON-Datenbank für FUSE | FS Bot.
Thread-safe innerhalb des Event-Loops (discord.py ist single-threaded).
"""
import os
import json
import threading
from typing import Any

DATA_FILE = "data.json"
_lock = threading.Lock()

_DEFAULT = {
    "cooldowns":           {},          # user_id -> ISO datetime
    "applications":        {},          # message_id -> {applicant_id, posted_ts, decided, reminded, channel_id}
    "warns":               {},          # user_id -> [{reason, mod_id, ts}]
    "xp":                  {},          # user_id -> {xp, level, msgs, voice_minutes, last_msg_ts}
    "birthdays":           {},          # user_id -> {day, month}
    "giveaways":           {},          # message_id -> {prize, end_ts, winners, host_id, channel_id, role_required, ended, entries}
    "automod_violations":  {},          # user_id -> [{type, ts}]
    "stats_channels":      {},          # type -> channel_id
    "monthly_winners":     {},          # YYYY-MM -> [user_ids]
    "config":              {},          # misc config
}


def _load() -> dict:
    if not os.path.exists(DATA_FILE):
        return json.loads(json.dumps(_DEFAULT))
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        d = json.loads(json.dumps(_DEFAULT))
    # Ensure all keys exist
    for k, v in _DEFAULT.items():
        d.setdefault(k, v)
    return d


def _save(data: dict) -> None:
    try:
        tmp = DATA_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, DATA_FILE)
    except Exception as e:
        print(f"[DB] Save failed: {e}")


DATA: dict = _load()


def save() -> None:
    """Sofort speichern."""
    with _lock:
        _save(DATA)


def get(key: str, default: Any = None) -> Any:
    return DATA.get(key, default)


def reload() -> None:
    """Datei neu laden (für Dashboard)."""
    global DATA
    with _lock:
        DATA = _load()
