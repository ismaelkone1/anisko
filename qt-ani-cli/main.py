#!/usr/bin/env python3
import sys
import shutil
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QStackedWidget, QComboBox,
    QFrame, QSizePolicy, QScrollArea, QGridLayout, QFileDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import (
    QColor, QFont, QPixmap, QPainter, QPainterPath,
    QLinearGradient, QBrush, QRadialGradient
)
import requests
from api import AniCliAPI
import store


# ─────────────────────────────────────────────────────────────────────────────
#  Themes  (light=True → true light-mode palette)
# ─────────────────────────────────────────────────────────────────────────────

THEMES = {
    "royal_indigo": dict(
        name="Royal Indigo", mode="Mode Sombre",
        a="#7c3aed", b="#c084fc",
        bg="#0c0c18", card="#12121e", border="#1c1c2e",
        sidebar="#0f0f1c", pill="#1a1030",
        fg="#dde0f0", fg2="#444466", fgh="#22223a",
    ),
    "crimson_black": dict(
        name="Crimson Black", mode="Mode Sombre",
        a="#dc2626", b="#f87171",
        bg="#100808", card="#140d0d", border="#2a1414",
        sidebar="#0e0808", pill="#2a0d0d",
        fg="#f0dede", fg2="#885555", fgh="#2a1414",
    ),
    "neon_cyan": dict(
        name="Neon Cyan", mode="Mode Sombre",
        a="#0891b2", b="#22d3ee",
        bg="#06090c", card="#0a1014", border="#0f2430",
        sidebar="#080d10", pill="#082030",
        fg="#cceeff", fg2="#336677", fgh="#0f2430",
    ),
    "indigo_cloud": dict(
        name="Indigo Cloud", mode="Mode Sombre",
        a="#6366f1", b="#a5b4fc",
        bg="#0c0c1a", card="#101022", border="#1a1a30",
        sidebar="#0e0e1a", pill="#131330",
        fg="#dde2f8", fg2="#44447a", fgh="#1a1a30",
    ),
    # ── Light themes ──────────────────────────────────────────────────────────
    "crystal_azure": dict(
        name="Crystal Azure", mode="Mode Clair",
        light=True,
        a="#2563eb", b="#1d4ed8",
        bg="#eef2ff", card="#ffffff", border="#c7d2fe",
        sidebar="#e0e7ff", pill="#dbeafe",
        fg="#1e1b4b", fg2="#4c4994", fgh="#c7d2fe",
    ),
    "soft_rose": dict(
        name="Soft Rose", mode="Mode Clair",
        light=True,
        a="#e11d48", b="#be123c",
        bg="#fff1f2", card="#ffffff", border="#fecdd3",
        sidebar="#ffe4e6", pill="#fce7f3",
        fg="#4c0519", fg2="#9f1239", fgh="#fecdd3",
    ),
}


def make_stylesheet(tk: str) -> str:
    t   = THEMES.get(tk, THEMES["royal_indigo"])
    lm  = t.get("light", False)
    a, b        = t["a"], t["b"]
    bg          = t["bg"]
    card        = t["card"]
    border      = t["border"]
    sb          = t["sidebar"]
    pill        = t["pill"]
    fg          = t["fg"]            # primary text
    fg2         = t["fg2"]           # secondary text
    fgh         = t["fgh"]           # placeholder / hint bg
    sb_text     = fg2 if lm else "#404060"
    sb_active   = b   if lm else b
    scroll_bar  = border
    inp_bg      = card if lm else card
    like_off    = fg2  if lm else "#2a2a44"

    return f"""
QMainWindow, QWidget {{ font-family:"Inter","Segoe UI",sans-serif; }}
QWidget#Root    {{ background:{bg}; }}
QWidget#Sidebar {{ background:{sb}; border-right:1px solid {border}; }}
QWidget#Content {{ background:{bg}; }}

/* ── Transparent scrolling ── */
QScrollArea, QAbstractScrollArea            {{ background:transparent; border:none; }}
QScrollArea>QWidget, QScrollArea>QWidget>QWidget {{ background:transparent; }}

/* ── Sidebar ── */
QLabel#AppName {{
    color:{b}; font-size:19px; font-weight:800; letter-spacing:2px;
}}
QPushButton#NavBtn {{
    background:transparent; border:none; border-left:3px solid transparent;
    border-radius:0; color:{sb_text};
    font-size:13px; font-weight:600; text-align:left; padding:11px 16px;
}}
QPushButton#NavBtn:hover  {{ background:{pill}; color:{fg}; }}
QPushButton#NavBtn[active="true"] {{ background:{pill}; color:{sb_active}; border-left:3px solid {a}; }}

/* ── Inputs ── */
QLineEdit#Search, QLineEdit#NameInput {{
    background:{inp_bg}; border:1.5px solid {border}; border-radius:12px;
    color:{fg}; font-size:14px; padding:10px 16px;
}}
QLineEdit#Search:focus, QLineEdit#NameInput:focus {{ border-color:{a}; }}
QLineEdit#Search::placeholder, QLineEdit#NameInput::placeholder {{ color:{fgh}; }}

/* ── Buttons ── */
QPushButton#PrimaryBtn {{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {a},stop:1 {b});
    border:none; border-radius:12px; color:white; font-size:13px; font-weight:700; padding:11px 24px;
}}
QPushButton#PrimaryBtn:hover {{ opacity:0.85; }}
QPushButton#PrimaryBtn:disabled {{ background:{border}; color:{fg2}; }}

QPushButton#GhostBtn {{
    background:transparent; border:1.5px solid {border};
    border-radius:10px; color:{fg2}; font-size:12px; padding:8px 18px;
}}
QPushButton#GhostBtn:hover {{ border-color:{a}; color:{a}; }}

QPushButton#IconBtn {{
    background:transparent; border:1.5px solid {border};
    border-radius:8px; color:{fg2}; font-size:14px; padding:4px 8px;
}}
QPushButton#IconBtn:hover {{ border-color:{a}; color:{a}; background:{pill}; }}

QPushButton#LikeBtn {{
    background:transparent; border:none;
    color:{like_off}; font-size:18px; font-weight:900; padding:4px 6px;
}}
QPushButton#LikeBtn[liked="true"] {{ color:{a}; }}

QPushButton#SaveNameBtn {{
    background:{a}; border:none; border-radius:10px;
    color:white; font-size:16px; font-weight:700; padding:4px 12px;
}}
QPushButton#SaveNameBtn:hover {{ background:{b}; }}

/* ── Filter tabs ── */
QPushButton#FilterTab {{
    background:transparent; border:1.5px solid {border};
    border-radius:20px; color:{fg2}; font-size:11px; font-weight:600; padding:5px 14px;
}}
QPushButton#FilterTab:hover {{ border-color:{a}; color:{fg}; }}
QPushButton#FilterTab[active="true"] {{ background:{pill}; border-color:{a}; color:{a}; font-weight:700; }}

/* ── Cards ── */
QFrame#Card {{
    background:{card}; border:1px solid {border}; border-radius:12px;
}}
QFrame#Card:hover {{ border-color:{a}; background:{pill}; }}
QLabel#CardTitle {{ color:{fg};  font-size:13px; font-weight:600; }}
QLabel#CardSub   {{ color:{fg2}; font-size:11px; }}
QFrame#Accent    {{ background:{a}; border-radius:2px; }}

/* ── Episode buttons ── */
QPushButton#EpBtn {{
    background:{card}; border:1.5px solid {border};
    border-radius:8px; color:{fg2}; font-size:11px;
}}
QPushButton#EpBtn:hover   {{ border-color:{a}; color:{a}; background:{pill}; }}
QPushButton#EpBtn:checked {{ background:{a};   border-color:{a}; color:white; font-weight:700; }}

/* ── Badges ── */
QLabel#EpBadge {{
    background:{a}; color:white; font-size:10px; font-weight:700;
    border-radius:6px; padding:2px 8px;
}}
QLabel#TypeBadge {{
    background:{border}; color:{fg2}; font-size:9px; font-weight:700;
    border-radius:4px; padding:1px 6px; letter-spacing:1px;
}}

/* ── Theme tile ── */
QFrame#ThemeTile {{
    background:{card}; border:1.5px solid {border}; border-radius:12px;
}}
QFrame#ThemeTile:hover {{ border-color:{a}; }}
QFrame#ThemeTile[selected="true"] {{ background:{pill}; border-color:{a}; }}

/* ── Scrollbars ── */
QScrollBar:vertical   {{ background:transparent; width:4px; }}
QScrollBar:horizontal {{ background:transparent; height:4px; }}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
    background:{scroll_bar}; border-radius:2px; min-height:20px;
}}
QScrollBar::add-line:vertical,  QScrollBar::sub-line:vertical,
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ height:0; width:0; }}

/* ── Misc labels ── */
QFrame#Divider         {{ background:{border}; max-height:1px; border:none; }}
QLabel#PageTitle       {{ color:{fg};  font-size:22px; font-weight:800; }}
QLabel#SectionLbl      {{ color:{a};   font-size:10px; font-weight:700; letter-spacing:2px; }}
QLabel#SubLbl          {{ color:{fg2}; font-size:12px; }}
QLabel#Hint            {{ color:{fgh}; font-size:13px; }}
QLabel#Loading         {{ color:{fg2}; font-size:13px; }}
QLabel#ProfileName     {{ color:{fg};  font-size:20px; font-weight:800; }}
QLabel#ProfileStatNum  {{ color:{a};   font-size:26px; font-weight:800; }}
QLabel#ProfileStatLbl  {{ color:{fg2}; font-size:10px; letter-spacing:1px; }}
QLabel#ThemeName       {{ color:{fg};  font-size:12px; font-weight:600; }}
QLabel#ThemeMode       {{ color:{fg2}; font-size:10px; }}
QLabel#CheckMark       {{ color:{a};   font-size:14px; font-weight:800; }}

/* ── Combo ── */
QComboBox#ModeBox {{
    background:{card}; border:1.5px solid {border};
    border-radius:8px; color:{fg2}; font-size:12px; padding:6px 12px;
}}
QComboBox#ModeBox::drop-down {{ border:none; }}
QComboBox#ModeBox QAbstractItemView {{
    background:{card}; color:{fg};
    selection-background-color:{a}; border:1px solid {border};
}}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  Workers
# ─────────────────────────────────────────────────────────────────────────────

class SearchWorker(QThread):
    results_ready = Signal(list)
    error = Signal(str)
    def __init__(self, api, query):
        super().__init__(); self.api = api; self.query = query
    def run(self):
        try: self.results_ready.emit(self.api.search_anime(self.query))
        except Exception as e: self.error.emit(str(e))


class EpisodeWorker(QThread):
    results_ready = Signal(list)
    error = Signal(str)
    def __init__(self, api, show_id):
        super().__init__(); self.api = api; self.show_id = show_id
    def run(self):
        try: self.results_ready.emit(self.api.get_episodes(self.show_id))
        except Exception as e: self.error.emit(str(e))


class ImageWorker(QThread):
    done = Signal(str)
    def __init__(self, show_id, url):
        super().__init__(); self.show_id = show_id; self.url = url
    def run(self):
        try:
            r = requests.get(self.url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                p = store.get_cover_path(self.show_id)
                p.write_bytes(r.content)
                self.done.emit(str(p))
        except Exception:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  CoverLabel
# ─────────────────────────────────────────────────────────────────────────────

class CoverLabel(QLabel):
    def __init__(self, anime: dict, w=56, h=78, radius=8, parent=None):
        super().__init__(parent)
        self.setFixedSize(w, h)
        self._w = w; self._h = h; self._r = radius
        self._px = None; self._worker = None
        self._load(anime)

    def _load(self, anime):
        show_id = anime.get("id", "")
        url     = anime.get("thumbnail", "")
        if not show_id: return
        cache = store.get_cover_path(show_id)
        if cache.exists(): self._apply(str(cache))
        elif url:
            self._worker = ImageWorker(show_id, url)
            self._worker.done.connect(self._apply)
            self._worker.start()

    def reload(self, anime):
        self._px = None
        if self._worker and self._worker.isRunning(): self._worker.terminate()
        self._load(anime); self.update()

    def _apply(self, path):
        px = QPixmap(path)
        if not px.isNull(): self._px = px; self.update()

    def paintEvent(self, _):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(0, 0, self._w, self._h, self._r, self._r)
        p.setClipPath(path)
        if self._px:
            sc = self._px.scaled(self._w, self._h, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = max(0, (sc.width()  - self._w) // 2)
            y = max(0, (sc.height() - self._h) // 2)
            p.drawPixmap(0, 0, sc, x, y, self._w, self._h)
        else:
            g = QLinearGradient(0, 0, 0, self._h)
            g.setColorAt(0, QColor("#1a1a30")); g.setColorAt(1, QColor("#0f0f1c"))
            p.fillPath(path, QBrush(g))


# ─────────────────────────────────────────────────────────────────────────────
#  AvatarLabel  – painted circle + custom photo + clickable
# ─────────────────────────────────────────────────────────────────────────────

class AvatarLabel(QLabel):
    changed = Signal()   # emitted when avatar image changes

    def __init__(self, initial="I", size=84, theme_key="royal_indigo", parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._size     = size
        self._initial  = initial.upper()
        self._theme_key = theme_key
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip("Cliquer pour changer la photo")

    def set_initial(self, name: str):
        self._initial = (name[0] if name else "?").upper()
        self.update()

    def set_theme(self, key):
        self._theme_key = key; self.update()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            path, _ = QFileDialog.getOpenFileName(
                self, "Choisir une photo de profil", "",
                "Images (*.png *.jpg *.jpeg *.webp *.gif)")
            if path:
                shutil.copy2(path, str(store.get_avatar_path()))
                self.update()
                self.changed.emit()

    def paintEvent(self, _):
        t   = THEMES.get(self._theme_key, THEMES["royal_indigo"])
        p   = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s   = self._size
        m   = 4   # margin
        d   = s - 2 * m

        clip = QPainterPath()
        clip.addEllipse(m, m, d, d)
        p.setClipPath(clip)

        av = store.get_avatar_path()
        if av.exists():
            px = QPixmap(str(av)).scaled(d, d, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            ox = max(0, (px.width()  - d) // 2)
            oy = max(0, (px.height() - d) // 2)
            p.drawPixmap(m, m, px, ox, oy, d, d)
        else:
            g = QRadialGradient(s / 2, s / 3, s * 0.7)
            g.setColorAt(0, QColor(t["b"]))
            g.setColorAt(1, QColor(t["a"]))
            p.fillPath(clip, QBrush(g))
            p.setClipping(False)
            p.setPen(QColor("white"))
            font = QFont("Inter", d // 3, QFont.Bold); p.setFont(font)
            p.drawText(m, m, d, d, Qt.AlignCenter, self._initial)
            p.setClipping(True)

        # Camera badge
        p.setClipping(False); p.setPen(Qt.NoPen)
        r = s // 5
        bx, by = s - r - 2, s - r - 2
        p.setBrush(QBrush(QColor(t["a"])))
        p.drawEllipse(bx, by, r, r)
        p.setPen(QColor("white"))
        f2 = QFont("Inter", r // 3, QFont.Bold); p.setFont(f2)
        p.drawText(bx, by, r, r, Qt.AlignCenter, "+")


# ─────────────────────────────────────────────────────────────────────────────
#  ThemeTile
# ─────────────────────────────────────────────────────────────────────────────

class ThemeTile(QFrame):
    clicked = Signal(str)

    def __init__(self, key: str, t: dict, selected=False, parent=None):
        super().__init__(parent)
        self._key = key
        self.setObjectName("ThemeTile")
        self.setFixedHeight(60)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("selected", selected)

        lay = QHBoxLayout(self); lay.setContentsMargins(14, 0, 14, 0); lay.setSpacing(10)
        dot = QFrame(); dot.setFixedSize(10, 10)
        dot.setStyleSheet(f"background:{t['a']}; border-radius:5px;")
        lay.addWidget(dot)
        col = QVBoxLayout(); col.setSpacing(1)
        col.addWidget(QLabel(t["name"], objectName="ThemeName"))
        col.addWidget(QLabel(t["mode"], objectName="ThemeMode"))
        lay.addLayout(col); lay.addStretch()
        if selected:
            lay.addWidget(QLabel("✓", objectName="CheckMark", fixedWidth=20))

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton: self.clicked.emit(self._key)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_like_btn(size=30) -> QPushButton:
    btn = QPushButton("♥", objectName="LikeBtn")
    btn.setFixedSize(size, size); btn.setCursor(Qt.PointingHandCursor)
    return btn


def set_liked(btn: QPushButton, liked: bool):
    btn.setProperty("liked", liked)
    btn.style().unpolish(btn); btn.style().polish(btn)


class Spinner(QLabel):
    FRAMES = ["⠋","⠙","⠸","⠴","⠦","⠇"]
    def __init__(self, text="Chargement", parent=None):
        super().__init__(parent)
        self._text = text; self._i = 0
        self.setObjectName("Loading"); self.setAlignment(Qt.AlignCenter)
        self._t = QTimer(self); self._t.timeout.connect(self._tick)
    def start(self, text=None):
        if text: self._text = text
        self._i = 0; self._t.start(80); self.show()
    def stop(self): self._t.stop(); self.hide()
    def _tick(self):
        self._i = (self._i + 1) % len(self.FRAMES)
        self.setText(f"{self.FRAMES[self._i]}  {self._text}")


def _divider():
    f = QFrame(); f.setObjectName("Divider"); f.setFrameShape(QFrame.HLine)
    return f


def _type_label(raw: str) -> str:
    return {"TV":"SÉRIE","TV_SHORT":"SÉRIE","ONA":"ONA",
            "OVA":"OVA","MOVIE":"FILM","SPECIAL":"SPÉCIAL","MUSIC":"MUSIC"
            }.get((raw or "").upper(), "")


def _filter_results(results: list, category: str) -> list:
    if category == "all": return results
    out = []
    for a in results:
        t   = (a.get("type") or "").upper()
        eps = a.get("episodes", 0)
        if category == "series":
            if t in ("TV","TV_SHORT","ONA") or (eps > 1 and t not in ("MOVIE","OVA","SPECIAL","MUSIC")):
                out.append(a)
        elif category == "films":
            if t == "MOVIE" or (eps == 1 and t not in ("OVA","SPECIAL","MUSIC")):
                out.append(a)
        elif category == "extras":
            if t in ("OVA","SPECIAL","MUSIC") or any(k in a.get("title","").upper() for k in ("OVA","SPECIAL","EXTRA")):
                out.append(a)
    return out


def _scroll_area(container: QWidget) -> QScrollArea:
    s = QScrollArea(); s.setWidgetResizable(True)
    s.setFrameShape(QFrame.NoFrame)
    s.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    s.viewport().setAutoFillBackground(False)
    container.setAutoFillBackground(False)
    s.setWidget(container)
    return s


# ─────────────────────────────────────────────────────────────────────────────
#  AnimeCard
# ─────────────────────────────────────────────────────────────────────────────

class AnimeCard(QFrame):
    clicked      = Signal(dict)
    like_toggled = Signal(dict, bool)

    def __init__(self, anime: dict, parent=None):
        super().__init__(parent)
        self.anime = anime; self.setObjectName("Card")
        self.setFixedHeight(82); self.setCursor(Qt.PointingHandCursor)
        row = QHBoxLayout(self); row.setContentsMargins(10,0,10,0); row.setSpacing(12)
        row.addWidget(CoverLabel(anime, w=46, h=64, radius=6))
        col = QVBoxLayout(); col.setSpacing(4)
        tl = QLabel(anime.get("title","—"), objectName="CardTitle")
        tl.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred); col.addWidget(tl)
        mr = QHBoxLayout(); mr.setSpacing(6)
        mr.addWidget(QLabel(f"{anime.get('episodes',0)} ép.", objectName="CardSub"))
        kind = _type_label(anime.get("type",""))
        if kind: mr.addWidget(QLabel(kind, objectName="TypeBadge"))
        mr.addStretch(); col.addLayout(mr); row.addLayout(col)
        self._like_btn = make_like_btn(30)
        set_liked(self._like_btn, store.is_liked(anime["id"]))
        self._like_btn.clicked.connect(self._on_like); row.addWidget(self._like_btn)

    def _on_like(self):
        liked = store.toggle_like(self.anime)
        set_liked(self._like_btn, liked)
        self.like_toggled.emit(self.anime, liked)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton: self.clicked.emit(self.anime)


# ─────────────────────────────────────────────────────────────────────────────
#  ProfileFavoriteCard
# ─────────────────────────────────────────────────────────────────────────────

class ProfileFavoriteCard(QFrame):
    clicked      = Signal(dict)
    like_toggled = Signal()

    def __init__(self, anime: dict, parent=None):
        super().__init__(parent)
        self.anime = anime; self.setObjectName("Card")
        self.setFixedHeight(108); self.setCursor(Qt.PointingHandCursor)
        row = QHBoxLayout(self); row.setContentsMargins(12,12,12,12); row.setSpacing(12)
        row.addWidget(CoverLabel(anime, w=60, h=84, radius=8))
        col = QVBoxLayout(); col.setSpacing(4)
        tr = QHBoxLayout(); tr.setSpacing(4)
        tr.addWidget(QLabel("•", objectName="SubLbl"))
        tl = QLabel(anime.get("title","—"), objectName="CardTitle"); tr.addWidget(tl, 1)
        col.addLayout(tr)
        br = QHBoxLayout(); br.setSpacing(6)
        eb = QLabel(f"{anime.get('episodes',0)} EP", objectName="EpBadge"); eb.setFixedHeight(17)
        br.addWidget(eb)
        kind = _type_label(anime.get("type",""))
        if kind: br.addWidget(QLabel(kind, objectName="TypeBadge"))
        br.addStretch(); col.addLayout(br); col.addStretch()
        lr = QHBoxLayout()
        self._like_btn = make_like_btn(26)
        set_liked(self._like_btn, store.is_liked(anime["id"]))
        self._like_btn.clicked.connect(self._on_like)
        lr.addWidget(self._like_btn); lr.addStretch(); col.addLayout(lr)
        row.addLayout(col)

    def _on_like(self):
        store.toggle_like(self.anime)
        set_liked(self._like_btn, store.is_liked(self.anime["id"]))
        self.like_toggled.emit()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton: self.clicked.emit(self.anime)


# ─────────────────────────────────────────────────────────────────────────────
#  SearchPage
# ─────────────────────────────────────────────────────────────────────────────

class SearchPage(QWidget):
    anime_selected = Signal(dict)
    FILTERS = [("all","Tout"),("series","Séries"),("films","Films"),("extras","Extras")]

    def __init__(self, api):
        super().__init__(); self.api = api
        self._worker = None; self._all = []; self._active = "series"
        self._filter_btns = {}; self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(36,32,36,0); root.setSpacing(14)
        root.addWidget(QLabel("EXPLORER", objectName="SectionLbl"))
        root.addWidget(QLabel("Rechercher", objectName="PageTitle"))
        row = QHBoxLayout(); row.setSpacing(10)
        self._input = QLineEdit(objectName="Search", placeholderText="Titre de l'animé…")
        self._input.returnPressed.connect(self._search); row.addWidget(self._input)
        btn = QPushButton("Rechercher", objectName="PrimaryBtn")
        btn.setFixedHeight(44); btn.clicked.connect(self._search); row.addWidget(btn)
        root.addLayout(row)
        # Filter tabs
        tab_row = QHBoxLayout(); tab_row.setSpacing(8); tab_row.setAlignment(Qt.AlignLeft)
        for key, label in self.FILTERS:
            b = QPushButton(label, objectName="FilterTab")
            b.setProperty("active", key == "series")
            b.clicked.connect(lambda _, k=key: self._apply_filter(k))
            self._filter_btns[key] = b; tab_row.addWidget(b)
        tab_row.addStretch()
        self._tabs_w = QWidget(); self._tabs_w.setLayout(tab_row); self._tabs_w.hide()
        root.addWidget(self._tabs_w)
        self._spin = Spinner("Recherche en cours"); self._spin.hide(); root.addWidget(self._spin)
        self._hint = QLabel("Tape le nom d'un animé pour commencer",
                            objectName="Hint", alignment=Qt.AlignCenter); root.addWidget(self._hint)
        self._cont = QWidget()
        self._vbox = QVBoxLayout(self._cont); self._vbox.setContentsMargins(0,0,0,16)
        self._vbox.setSpacing(6); self._vbox.addStretch()
        self._scroll = _scroll_area(self._cont); self._scroll.hide(); root.addWidget(self._scroll)

    def _search(self):
        q = self._input.text().strip()
        if not q or (self._worker and self._worker.isRunning()): return
        self._clear(); self._scroll.hide(); self._tabs_w.hide()
        self._hint.hide(); self._spin.start()
        self._worker = SearchWorker(self.api, q)
        self._worker.results_ready.connect(self._on_results)
        self._worker.error.connect(self._on_error); self._worker.start()

    def _on_results(self, results):
        self._spin.stop(); self._all = results; self._active = "series"
        if not results: self._hint.setText("Aucun résultat."); self._hint.show(); return
        self._tabs_w.show(); self._render(_filter_results(results, "series")); self._update_tabs("series")

    def _apply_filter(self, key):
        self._active = key
        self._render(_filter_results(self._all, key)); self._update_tabs(key)

    def _update_tabs(self, active):
        for k, btn in self._filter_btns.items():
            btn.setProperty("active", k == active)
            btn.style().unpolish(btn); btn.style().polish(btn)

    def _render(self, results):
        while self._vbox.count():
            it = self._vbox.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        self._vbox.addStretch()
        if not results:
            self._vbox.insertWidget(0, QLabel("Aucun résultat dans cette catégorie.",
                                    objectName="Hint", alignment=Qt.AlignCenter))
            self._scroll.show(); return
        self._scroll.show()
        for i, a in enumerate(results):
            card = AnimeCard(a)
            card.clicked.connect(self.anime_selected)
            self._vbox.insertWidget(i, card)

    def _on_error(self, msg):
        self._spin.stop(); self._hint.setText(f"Erreur : {msg}"); self._hint.show()

    def _clear(self):
        while self._vbox.count():
            it = self._vbox.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        self._vbox.addStretch()


# ─────────────────────────────────────────────────────────────────────────────
#  EpisodePage
# ─────────────────────────────────────────────────────────────────────────────

class EpisodePage(QWidget):
    back   = Signal()
    played = Signal(dict, str)

    def __init__(self, api, get_mode=None):
        super().__init__(); self.api = api
        self._get_mode = get_mode or (lambda: "sub")
        self._worker = None; self._anime = None; self._ep = None; self._ep_btns = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(36,28,36,20); root.setSpacing(12)
        bar = QHBoxLayout()
        back = QPushButton("← Retour", objectName="GhostBtn"); back.clicked.connect(self.back)
        bar.addWidget(back); bar.addStretch()
        self._like_btn = make_like_btn(40); self._like_btn.clicked.connect(self._toggle_like)
        bar.addWidget(self._like_btn); root.addLayout(bar)
        # Hero
        hero = QHBoxLayout(); hero.setSpacing(20)
        self._cover = CoverLabel({}, w=90, h=126, radius=10)
        hero.addWidget(self._cover, 0, Qt.AlignTop)
        ic = QVBoxLayout(); ic.setSpacing(6)
        ic.addWidget(QLabel("ÉPISODES", objectName="SectionLbl"))
        self._title_lbl = QLabel("", objectName="PageTitle"); self._title_lbl.setWordWrap(True)
        ic.addWidget(self._title_lbl)
        self._ep_count = QLabel("", objectName="SubLbl"); ic.addWidget(self._ep_count)
        ic.addStretch(); hero.addLayout(ic, 1); root.addLayout(hero)
        root.addWidget(_divider())
        self._spin = Spinner("Chargement des épisodes"); self._spin.hide(); root.addWidget(self._spin)
        gw = QWidget(); gw.setAutoFillBackground(False)
        self._grid_vbox = QVBoxLayout(gw); self._grid_vbox.setContentsMargins(0,4,0,4)
        self._grid_vbox.setSpacing(8); self._grid_vbox.setAlignment(Qt.AlignTop)
        root.addWidget(_scroll_area(gw))
        action = QHBoxLayout(); action.addStretch()
        self._sel_lbl = QLabel("Aucun épisode sélectionné", objectName="SubLbl"); action.addWidget(self._sel_lbl)
        action.addSpacing(16)
        self._watch_btn = QPushButton("▶  Regarder", objectName="PrimaryBtn")
        self._watch_btn.setFixedHeight(46); self._watch_btn.setEnabled(False)
        self._watch_btn.clicked.connect(self._play)
        action.addWidget(self._watch_btn); root.addLayout(action)

    def load(self, anime):
        self._anime = anime; self._ep = None; self._ep_btns = []
        self._title_lbl.setText(anime["title"]); self._ep_count.setText("Chargement…")
        self._watch_btn.setEnabled(False); self._sel_lbl.setText("Aucun épisode sélectionné")
        set_liked(self._like_btn, store.is_liked(anime["id"]))
        self._cover.reload(anime); self._clear_grid(); self._spin.start()
        self._worker = EpisodeWorker(self.api, anime["id"])
        self._worker.results_ready.connect(self._on_episodes)
        self._worker.error.connect(self._on_error); self._worker.start()

    def _toggle_like(self):
        if self._anime: set_liked(self._like_btn, store.toggle_like(self._anime))

    def _on_episodes(self, eps):
        self._spin.stop(); cnt = len(eps)
        self._ep_count.setText(f"{cnt} épisode{'s' if cnt != 1 else ''}")
        COLS = 9; row_lay = None
        for i, ep in enumerate(eps):
            if i % COLS == 0:
                row_lay = QHBoxLayout(); row_lay.setSpacing(6); row_lay.setAlignment(Qt.AlignLeft)
                self._grid_vbox.addLayout(row_lay)
            btn = QPushButton(ep, objectName="EpBtn")
            btn.setFixedSize(66, 36); btn.setCheckable(True); btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, e=ep, b=btn: self._select_ep(e, b))
            self._ep_btns.append(btn); row_lay.addWidget(btn)
        if row_lay and cnt % COLS != 0: row_lay.addStretch()
        self._grid_vbox.addStretch()

    def _on_error(self, msg): self._spin.stop(); self._ep_count.setText(f"Erreur : {msg}")

    def _clear_grid(self):
        while self._grid_vbox.count():
            item = self._grid_vbox.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
            else:
                sub = item.layout()
                if sub:
                    while sub.count():
                        si = sub.takeAt(0)
                        if si.widget(): si.widget().deleteLater()

    def _select_ep(self, ep, btn):
        self._ep = ep
        for b in self._ep_btns:
            if b is not btn: b.setChecked(False)
        btn.setChecked(True); self._sel_lbl.setText(f"Épisode {ep} sélectionné")
        self._watch_btn.setEnabled(True)

    def _play(self):
        if not self._anime or not self._ep: return
        cmd = ["ani-cli"]
        if self._get_mode() == "dub": cmd.append("--dub")
        cmd += ["-S", "1", "-e", str(self._ep), self._anime["title"]]
        store.add_history(self._anime, self._ep); self.played.emit(self._anime, self._ep)
        subprocess.Popen(cmd, start_new_session=True)


# ─────────────────────────────────────────────────────────────────────────────
#  LibraryPage
# ─────────────────────────────────────────────────────────────────────────────

class LibraryPage(QWidget):
    anime_selected = Signal(dict)

    def __init__(self):
        super().__init__(); self._build()

    def _build(self):
        root = QVBoxLayout(self); root.setContentsMargins(36,32,36,0); root.setSpacing(14)
        root.addWidget(QLabel("COLLECTION", objectName="SectionLbl"))
        root.addWidget(QLabel("Mes Animés", objectName="PageTitle"))
        root.addWidget(_divider())
        self._hint = QLabel("Aucun favori.\nClique sur ♥ dans les résultats.",
                            objectName="Hint", alignment=Qt.AlignCenter); root.addWidget(self._hint)
        self._cont = QWidget()
        self._vbox = QVBoxLayout(self._cont); self._vbox.setContentsMargins(0,0,0,16)
        self._vbox.setSpacing(6); self._vbox.addStretch()
        self._scroll = _scroll_area(self._cont); self._scroll.hide(); root.addWidget(self._scroll)

    def refresh(self):
        while self._vbox.count():
            it = self._vbox.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        self._vbox.addStretch()
        likes = store.get_likes()
        if not likes: self._hint.show(); self._scroll.hide(); return
        self._hint.hide(); self._scroll.show()
        self._vbox.takeAt(self._vbox.count() - 1)
        for a in likes:
            card = AnimeCard(a)
            card.clicked.connect(self.anime_selected)
            card.like_toggled.connect(lambda *_: self.refresh())
            self._vbox.addWidget(card)
        self._vbox.addStretch()


# ─────────────────────────────────────────────────────────────────────────────
#  ProfilePage  – with editable name + clickable avatar
# ─────────────────────────────────────────────────────────────────────────────

class ProfilePage(QWidget):
    theme_changed  = Signal(str)
    anime_selected = Signal(dict)

    def __init__(self):
        super().__init__()
        self._current_theme = store.get_theme()
        self._tile_widgets  = {}
        self._build()

    def _build(self):
        outer = QVBoxLayout(self); outer.setContentsMargins(0,0,0,0)
        inner = QWidget(); inner.setAutoFillBackground(False)
        root  = QVBoxLayout(inner); root.setContentsMargins(36,32,36,40); root.setSpacing(24)
        outer.addWidget(_scroll_area(inner))

        # ── Hero card ───────────────────────────────────────────────────────
        hero = QFrame(); hero.setObjectName("Card")
        hl = QHBoxLayout(hero); hl.setContentsMargins(28,22,28,22); hl.setSpacing(20)

        profile = store.get_profile()
        self._avatar = AvatarLabel(
            profile.get("name","I"), size=84, theme_key=self._current_theme)
        self._avatar.changed.connect(self._on_avatar_changed)
        hl.addWidget(self._avatar)

        nc = QVBoxLayout(); nc.setSpacing(8)

        # ── Name display / edit toggle ──────────────────────────────────
        # State 0: label + pencil
        self._name_display_w = QWidget()
        dr = QHBoxLayout(self._name_display_w); dr.setContentsMargins(0,0,0,0); dr.setSpacing(8)
        self._name_lbl = QLabel(profile.get("name","Ismael"), objectName="ProfileName")
        dr.addWidget(self._name_lbl)
        pencil = QPushButton("✎", objectName="IconBtn"); pencil.setFixedSize(28,28)
        pencil.clicked.connect(self._start_name_edit); dr.addWidget(pencil); dr.addStretch()

        # State 1: input + save
        self._name_edit_w = QWidget()
        er = QHBoxLayout(self._name_edit_w); er.setContentsMargins(0,0,0,0); er.setSpacing(8)
        self._name_input = QLineEdit(objectName="NameInput")
        self._name_input.setFixedHeight(38); self._name_input.returnPressed.connect(self._save_name)
        er.addWidget(self._name_input)
        save_btn = QPushButton("✓", objectName="SaveNameBtn"); save_btn.setFixedSize(38,38)
        save_btn.clicked.connect(self._save_name); er.addWidget(save_btn)

        self._name_stack = QStackedWidget()
        self._name_stack.addWidget(self._name_display_w)
        self._name_stack.addWidget(self._name_edit_w)
        self._name_stack.setCurrentIndex(0)
        nc.addWidget(self._name_stack)

        nc.addWidget(QLabel("Membre Premium Anisko", objectName="SubLbl"))
        nc.addStretch(); hl.addLayout(nc, 1)

        # Favorites badge
        badge = QFrame(); badge.setObjectName("Card"); badge.setFixedSize(76,76)
        bl = QVBoxLayout(badge); bl.setContentsMargins(8,8,8,8); bl.setSpacing(0)
        self._fav_num = QLabel("0", objectName="ProfileStatNum", alignment=Qt.AlignCenter)
        font_n = self._fav_num.font(); font_n.setPointSize(22); font_n.setBold(True)
        self._fav_num.setFont(font_n); bl.addWidget(self._fav_num)
        bl.addWidget(QLabel("FAVORIS", objectName="ProfileStatLbl", alignment=Qt.AlignCenter))
        hl.addWidget(badge, 0, Qt.AlignTop)
        root.addWidget(hero)

        # ── Apparence ───────────────────────────────────────────────────────
        root.addWidget(_divider())
        root.addWidget(QLabel("APPARENCE", objectName="SectionLbl"))
        self._tiles_layout = QGridLayout(); self._tiles_layout.setSpacing(10)
        root.addLayout(self._tiles_layout)
        self._rebuild_tiles()

        # ── Mes Favoris ─────────────────────────────────────────────────────
        root.addWidget(_divider())
        root.addWidget(QLabel("MES FAVORIS", objectName="SectionLbl"))
        self._fav_hint = QLabel("Aucun favori.", objectName="Hint", alignment=Qt.AlignCenter)
        root.addWidget(self._fav_hint)
        self._fav_grid_w = QWidget(); self._fav_grid_w.setAutoFillBackground(False)
        self._fav_grid   = QGridLayout(self._fav_grid_w); self._fav_grid.setSpacing(10)
        root.addWidget(self._fav_grid_w); self._fav_grid_w.hide()
        root.addStretch()

    # ── Name editing ────────────────────────────────────────────────────────

    def _start_name_edit(self):
        self._name_input.setText(self._name_lbl.text())
        self._name_stack.setCurrentIndex(1)
        self._name_input.setFocus()
        self._name_input.selectAll()

    def _save_name(self):
        name = self._name_input.text().strip()
        if name:
            store.set_profile(name=name)
            self._name_lbl.setText(name)
            self._avatar.set_initial(name)
        self._name_stack.setCurrentIndex(0)

    def _on_avatar_changed(self):
        self._avatar.update()

    # ── Themes ──────────────────────────────────────────────────────────────

    def _rebuild_tiles(self):
        while self._tiles_layout.count():
            it = self._tiles_layout.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        self._tile_widgets.clear()
        for i, (key, t) in enumerate(THEMES.items()):
            tile = ThemeTile(key, t, selected=(key == self._current_theme))
            tile.clicked.connect(self._select_theme)
            self._tile_widgets[key] = tile
            self._tiles_layout.addWidget(tile, i // 3, i % 3)

    def _select_theme(self, key):
        self._current_theme = key; store.set_theme(key)
        self._avatar.set_theme(key)
        self._rebuild_tiles(); self.theme_changed.emit(key)

    def sync_theme(self, key):
        self._current_theme = key; self._rebuild_tiles()
        self._avatar.set_theme(key)

    # ── Refresh ─────────────────────────────────────────────────────────────

    def refresh(self):
        profile = store.get_profile()
        name = profile.get("name", "Ismael")
        self._name_lbl.setText(name)
        self._avatar.set_initial(name)
        likes = store.get_likes()
        self._fav_num.setText(str(len(likes)))
        while self._fav_grid.count():
            it = self._fav_grid.takeAt(0)
            if it.widget(): it.widget().deleteLater()
        if not likes: self._fav_hint.show(); self._fav_grid_w.hide(); return
        self._fav_hint.hide(); self._fav_grid_w.show()
        for i, a in enumerate(likes):
            card = ProfileFavoriteCard(a)
            card.clicked.connect(self.anime_selected); card.like_toggled.connect(self.refresh)
            self._fav_grid.addWidget(card, i // 2, i % 2)


# ─────────────────────────────────────────────────────────────────────────────
#  MainWindow
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Anisko"); self.setMinimumSize(880, 640); self.resize(1020, 720)
        self.api = AniCliAPI(mode="sub"); self._mode = "sub"; self._theme = store.get_theme()
        self._build(); self._apply_theme(self._theme); self._nav("search")

    def _build(self):
        root = QWidget(objectName="Root"); self.setCentralWidget(root)
        hbox = QHBoxLayout(root); hbox.setContentsMargins(0,0,0,0); hbox.setSpacing(0)
        hbox.addWidget(self._make_sidebar())
        content = QWidget(objectName="Content"); self._stack = QStackedWidget()
        cl = QVBoxLayout(content); cl.setContentsMargins(0,0,0,0); cl.addWidget(self._stack)
        hbox.addWidget(content, 1)
        self._search_page  = SearchPage(self.api)
        self._episode_page = EpisodePage(self.api, get_mode=lambda: self._mode)
        self._library_page = LibraryPage()
        self._profile_page = ProfilePage()
        self._search_page.anime_selected.connect(self._open_anime)
        self._episode_page.back.connect(lambda: self._nav("search"))
        self._episode_page.played.connect(self._on_played)
        self._library_page.anime_selected.connect(self._open_anime)
        self._profile_page.anime_selected.connect(self._open_anime)
        self._profile_page.theme_changed.connect(self._apply_theme)
        for p in [self._search_page, self._episode_page, self._library_page, self._profile_page]:
            self._stack.addWidget(p)

    def _make_sidebar(self):
        sb = QWidget(objectName="Sidebar"); sb.setFixedWidth(210)
        lay = QVBoxLayout(sb); lay.setContentsMargins(0,28,0,24); lay.setSpacing(2)
        lw = QWidget(); ll = QHBoxLayout(lw); ll.setContentsMargins(20,0,20,0)
        ll.addWidget(QLabel("ANISKO", objectName="AppName")); ll.addStretch(); lay.addWidget(lw)
        lay.addSpacing(24)
        self._nav_btns = {}
        for key, label in [("search","Rechercher"),("library","Ma Bibliothèque"),("profile","Mon Profil")]:
            btn = QPushButton(label, objectName="NavBtn")
            btn.clicked.connect(lambda _, k=key: self._nav(k))
            lay.addWidget(btn); self._nav_btns[key] = btn
        lay.addSpacing(16)
        dw = QWidget(); dl = QHBoxLayout(dw); dl.setContentsMargins(16,0,16,0); dl.addWidget(_divider()); lay.addWidget(dw)
        lay.addSpacing(12)
        aw = QWidget(); al = QVBoxLayout(aw); al.setContentsMargins(20,0,20,0)
        al.addWidget(QLabel("AUDIO", objectName="SectionLbl"))
        self._mode_box = QComboBox(objectName="ModeBox"); self._mode_box.addItems(["Sub","Dub"])
        self._mode_box.currentTextChanged.connect(lambda t: self._set_mode(t))
        al.addWidget(self._mode_box); lay.addWidget(aw); lay.addStretch()
        self._status = QLabel("", objectName="SubLbl", wordWrap=True)
        sw = QWidget(); sl = QHBoxLayout(sw); sl.setContentsMargins(20,0,20,0)
        sl.addWidget(self._status); lay.addWidget(sw)
        return sb

    def _set_mode(self, text): self._mode = text.lower(); self.api.mode = self._mode

    def _apply_theme(self, key):
        self._theme = key; self.setStyleSheet(make_stylesheet(key))
        self._profile_page.sync_theme(key)

    def _nav(self, key):
        for k, btn in self._nav_btns.items():
            btn.setProperty("active", k == key)
            btn.style().unpolish(btn); btn.style().polish(btn)
        pages = {"search":self._search_page,"episode":self._episode_page,
                 "library":self._library_page,"profile":self._profile_page}
        if key == "library": self._library_page.refresh()
        if key == "profile": self._profile_page.refresh()
        self._stack.setCurrentWidget(pages.get(key, self._search_page))

    def _open_anime(self, anime):
        self._nav("episode"); self._episode_page.load(anime)

    def _on_played(self, anime, ep):
        self._status.setText(f"▶ {anime['title'][:20]}… ep.{ep}")
        QTimer.singleShot(5000, lambda: self._status.setText(""))
        self._profile_page.refresh()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Anisko")
    font = QFont("Inter"); font.setPointSize(10); app.setFont(font)
    win = MainWindow(); win.show()
    sys.exit(app.exec())
