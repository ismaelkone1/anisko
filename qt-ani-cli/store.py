import json
from pathlib import Path

DATA_DIR     = Path.home() / ".local" / "share" / "anisko"
LIKES_FILE   = DATA_DIR / "likes.json"
HISTORY_FILE = DATA_DIR / "history.json"
SETTINGS_FILE= DATA_DIR / "settings.json"
PROFILE_FILE = DATA_DIR / "profile.json"


def _ensure():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for f in [LIKES_FILE, HISTORY_FILE]:
        if not f.exists():
            f.write_text("[]")
    for f in [SETTINGS_FILE, PROFILE_FILE]:
        if not f.exists():
            f.write_text("{}")


def get_cover_path(show_id: str) -> Path:
    d = DATA_DIR / "covers"; d.mkdir(exist_ok=True)
    safe = "".join(c for c in show_id if c.isalnum() or c in "-_")
    return d / f"{safe}.jpg"


def get_avatar_path() -> Path:
    _ensure()
    return DATA_DIR / "avatar.jpg"


# ── Profile ────────────────────────────────────────────────────────────────

def get_profile() -> dict:
    _ensure()
    try:
        return json.loads(PROFILE_FILE.read_text()) or {}
    except Exception:
        return {}


def set_profile(**kwargs):
    p = get_profile()
    p.update(kwargs)
    PROFILE_FILE.write_text(json.dumps(p, indent=2))


# ── Likes ──────────────────────────────────────────────────────────────────

def get_likes():
    _ensure()
    try:   return json.loads(LIKES_FILE.read_text())
    except: return []


def is_liked(show_id):
    return any(a["id"] == show_id for a in get_likes())


def add_like(anime):
    likes = get_likes()
    if not any(a["id"] == anime["id"] for a in likes):
        likes.append(anime)
        LIKES_FILE.write_text(json.dumps(likes, ensure_ascii=False, indent=2))


def remove_like(show_id):
    LIKES_FILE.write_text(json.dumps(
        [a for a in get_likes() if a["id"] != show_id],
        ensure_ascii=False, indent=2))


def toggle_like(anime):
    if is_liked(anime["id"]): remove_like(anime["id"]); return False
    else: add_like(anime); return True


# ── History ────────────────────────────────────────────────────────────────

def add_history(anime, episode):
    _ensure()
    try:    hist = json.loads(HISTORY_FILE.read_text())
    except: hist = []
    hist = [h for h in hist if h["id"] != anime["id"]]
    hist.insert(0, {**anime, "last_episode": str(episode)})
    HISTORY_FILE.write_text(json.dumps(hist[:50], ensure_ascii=False, indent=2))


def get_history():
    _ensure()
    try:    return json.loads(HISTORY_FILE.read_text())
    except: return []


# ── Settings ───────────────────────────────────────────────────────────────

def _get_settings():
    _ensure()
    try:    return json.loads(SETTINGS_FILE.read_text()) or {}
    except: return {}


def get_theme():
    return _get_settings().get("theme", "royal_indigo")


def set_theme(key):
    s = _get_settings(); s["theme"] = key
    SETTINGS_FILE.write_text(json.dumps(s, indent=2))
