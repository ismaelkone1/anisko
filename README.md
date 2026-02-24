<div align="center">
  <img src="anisko.png" width="120" alt="Anisko Icon"/>
  <h1>Anisko</h1>
  <p>Interface graphique Qt pour <strong>ani-cli</strong> — regardez vos animés sans quitter le confort d'une vraie app.</p>
</div>

---

## Fonctionnalités

- 🔍 **Recherche** d'animés via l'API AllAnime
- 🎛️ **Filtres** : Séries / Films / Extras / Tout
- 🖼️ **Cover art** chargé automatiquement et mis en cache
- ❤️ **Favoris** persistants (likes)
- 📖 **Historique** de lecture (50 dernières entrées)
- 👤 **Profil** : pseudo modifiable, photo de profil personnalisable
- 🎨 **6 thèmes** (4 sombres + 2 clairs) sauvegardés
- 🔊 **Sub / Dub** depuis la sidebar
- ▶️ Lance `ani-cli` pour la lecture via mpv (ou vlc)

---

## Prérequis

### 1. ani-cli

```bash
# Via le dépôt officiel
curl -fsSL https://raw.githubusercontent.com/pystardust/ani-cli/master/ani-cli \
  | sudo tee /usr/local/bin/ani-cli && sudo chmod +x /usr/local/bin/ani-cli
```

Vérification :
```bash
ani-cli --version
```

### 2. Lecteur vidéo (mpv recommandé)

```bash
# Ubuntu / Debian
sudo apt install mpv

# Arch
sudo pacman -S mpv

# Fedora
sudo dnf install mpv
```

### 3. Dépendances système

```bash
sudo apt install python3 python3-pip curl fzf
```

### 4. PySide6 et requests

```bash
pip install PySide6 requests
```

---

## Installation

### 🪟 Windows

#### Étape 1 : Installer Python 3

1. Télécharge Python 3.9+ depuis [python.org](https://www.python.org/downloads/)
2. Lance l'installateur
3. **⚠️ Important** : Coche **« Add Python to PATH »** lors de l'installation
4. Clique « Install Now »

Vérifie l'installation dans PowerShell ou CMD :
```bash
python --version
pip --version
```

#### Étape 2 : Installer les dépendances Python

Ouvre PowerShell ou CMD, puis :
```bash
pip install PySide6 requests
```

#### Étape 3 : Installer mpv (lecteur vidéo)

**Option A : Via Chocolatey** (recommandé)
```bash
# Si tu as Chocolatey installé :
choco install mpv
```

**Option B : Télécharger manuellement**
1. Accède à [mpv.io/installation](https://mpv.io/installation/)
2. Télécharge la version Windows
3. Décompresse dans `C:\Program Files\mpv`
4. Ajoute `C:\Program Files\mpv` au PATH Windows

Vérifie :
```bash
mpv --version
```

#### Étape 4 : Installer ani-cli sur Windows

**Option A : Via Git Bash / PowerShell**
```bash
# Clone le dépôt ani-cli
git clone https://github.com/pystardust/ani-cli.git
cd ani-cli

# Place le script ani-cli dans un dossier du PATH
# Par exemple, crée C:\anisko\bin et ajoute-le au PATH
```

**Option B : Installation manuelle simplifiée**
1. Télécharge `ani-cli` depuis le [repo officiel](https://github.com/pystardust/ani-cli)
2. Crée un dossier `C:\anisko\bin`
3. Place le script `ani-cli` dans ce dossier
4. Ajoute `C:\anisko\bin` aux variables d'environnement PATH

**Pour ajouter un dossier au PATH Windows :**
1. Appuie sur `Win + X` → « Paramètres » (Settings)
2. Cherche « Variables d'environnement »
3. Clique sur « Modifier les variables d'environnement du système »
4. Clique sur « Variables d'environnement »
5. Sous « Variables utilisateur », clique « Nouveau »
6. Nom : `PATH`, Valeur : `C:\anisko\bin`
7. OK et redémarre PowerShell

Vérifie :
```bash
ani-cli --version
```

#### Étape 5 : Installer Anisko

1. **Clone ou télécharge** le projet Anisko :
```bash
git clone https://github.com/ton-user/anisko.git C:\anisko
cd C:\anisko
```

Ou télécharge le ZIP depuis GitHub et décompresse-le dans `C:\anisko`

2. **Lance l'application** :
```bash
python main.py
```

Ou crée un raccourci :
- Clique droit sur `main.py` → « Créer un raccourci »
- Renomme-le en `Anisko`
- Déplace-le sur le Bureau ou le menu Démarrer

#### Étape 6 : Créer un lanceur Windows (optionnel)

Crée un fichier `anisko.bat` dans `C:\anisko` :
```batch
@echo off
python "%~dp0main.py"
pause
```

Double-clique sur `anisko.bat` pour lancer l'app.

---

### 🐧 Linux / macOS

#### Cloner le projet

```bash
git clone https://github.com/ton-user/anisko.git ~/anisko
# ou si tu as déjà les fichiers dans ~/qt-ani-cli :
cd ~/qt-ani-cli
```

### Installer la commande `anisko`

```bash
chmod +x anisko
mkdir -p ~/.local/bin
ln -sf "$(pwd)/anisko" ~/.local/bin/anisko
```

### Ajouter `~/.local/bin` au PATH (si nécessaire)

Vérifie que cette ligne est dans ton `~/.bashrc` ou `~/.zshrc` :

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Puis recharge :
```bash
source ~/.bashrc   # ou source ~/.zshrc
```

### Ajouter au menu du bureau (optionnel)

```bash
mkdir -p ~/.local/share/applications
cp anisko.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

---

## Utilisation

### Lancer depuis le terminal

```bash
anisko
```

### Lancer depuis le menu du bureau

Cherche **Anisko** dans le menu application de ton environnement (GNOME, KDE, XFCE…).

---

## Utilisation de l'app

| Étape | Action |
|-------|--------|
| **Rechercher** | Tape un titre et appuie sur Entrée ou clique « Rechercher » |
| **Filtrer** | Utilise les onglets Séries / Films / Extras / Tout |
| **Sélectionner** | Clique sur une carte pour voir les épisodes |
| **Regarder** | Sélectionne un épisode et clique « ▶ Regarder » |
| **Liker** | Clique sur ♥ sur n'importe quelle carte |
| **Profil** | Clique sur « Mon Profil » dans la sidebar |
| **Changer de thème** | Profil → section Apparence → clique un thème |

---

## Structure du projet

```
~/qt-ani-cli/
├── main.py          # Application Qt (UI + logique)
├── api.py           # Requêtes GraphQL vers AllAnime
├── store.py         # Persistance locale (likes, historique, profil, thème)
├── anisko           # Script de lancement
├── anisko.desktop   # Entrée menu bureau
└── anisko.png       # Icône de l'application

~/.local/share/anisko/
├── likes.json       # Animés likés
├── history.json     # Historique de lecture
├── profile.json     # Profil utilisateur (pseudo)
├── settings.json    # Thème sauvegardé
├── avatar.jpg       # Photo de profil (si définie)
└── covers/          # Cache des cover art
```

---

## Données locales

Toutes les données sont stockées localement dans :

```
~/.local/share/anisko/
```

Aucune connexion autre que l'API AllAnime (même source que `ani-cli`).

---

## Dépendances

| Paquet | Usage |
|--------|-------|
| `PySide6` | Interface graphique Qt |
| `requests` | Requêtes HTTP vers l'API |
| `ani-cli` | Lecture des épisodes |
| `mpv` (ou `vlc`) | Lecteur vidéo |
| `curl`, `fzf` | Requis par `ani-cli` |

---

<div align="center">
  <sub>Fait avec ♥ · Propulsé par <a href="https://github.com/pystardust/ani-cli">ani-cli</a></sub>
</div>
