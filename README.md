# 🔔 Discord Hourly Sound Bot

Bot Discord minimaliste qui rejoint un salon vocal et joue un son **toutes les heures pile**.

---

## Structure des fichiers

```
discord-hourly-bot/
├── bot.py            ← code principal
├── requirements.txt  ← dépendances Python
├── .env.example      ← modèle de configuration
└── sound.mp3         ← TON fichier audio (à ajouter)
```

---

## 1. Créer le bot sur Discord

1. Va sur https://discord.com/developers/applications
2. **New Application** → donne un nom
3. Onglet **Bot** → clique **Add Bot**
4. Copie le **Token** (tu en auras besoin)
5. Onglet **Bot** → active **"Server Members Intent"**
6. Onglet **OAuth2 > URL Generator** :
   - Scopes : `bot`
   - Bot Permissions : `Connect` + `Speak` + `View Channels`
7. Copie l'URL générée et invite le bot sur ton serveur

---

## 2. Récupérer les IDs Discord

Active le **Mode développeur** (Paramètres → Avancé → Mode développeur), puis :

- **GUILD_ID** : clic droit sur ton serveur → *Copier l'identifiant*
- **CHANNEL_ID** : clic droit sur ton salon vocal → *Copier l'identifiant*

---

## 3. Installer et tester en local

```bash
# Installer les dépendances Python
pip install -r requirements.txt

# Sur Linux/Mac — installer FFmpeg
sudo apt install ffmpeg        # Ubuntu/Debian
brew install ffmpeg            # macOS

# Copier et remplir la config
cp .env.example .env
# Édite .env avec ton éditeur

# Lancer le bot
python bot.py
```

Pour tester sans attendre une heure, tape `!test` dans n'importe quel salon texte de ton serveur.

---

## 4. Hébergement 100 % gratuit

### Option recommandée — Oracle Cloud Free Tier (le plus fiable)

Oracle offre **2 VM gratuites à vie** (ARM, 1 vCPU, 1 Go RAM chacune).

1. Crée un compte sur https://cloud.oracle.com/free
2. Lance une VM **Ubuntu 22.04 ARM**
3. Connecte-toi en SSH, puis :

```bash
# Installer les dépendances système
sudo apt update && sudo apt install -y python3-pip ffmpeg

# Copier les fichiers du bot (via scp ou git)
git clone https://github.com/TON_PSEUDO/TON_REPO.git
cd discord-hourly-bot

pip3 install -r requirements.txt

# Configurer les variables d'environnement
export DISCORD_TOKEN="ton_token"
export GUILD_ID="123..."
export CHANNEL_ID="123..."
export SOUND_FILE="sound.mp3"

# Lancer en arrière-plan avec screen
screen -S bot
python3 bot.py
# Ctrl+A puis D pour détacher
```

Pour un démarrage automatique au reboot, crée un service systemd :

```ini
# /etc/systemd/system/discord-bot.service
[Unit]
Description=Discord Hourly Sound Bot
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/discord-hourly-bot
Environment="DISCORD_TOKEN=ton_token"
Environment="GUILD_ID=123..."
Environment="CHANNEL_ID=123..."
ExecStart=/usr/bin/python3 bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
```

---

### Option alternative — fly.io

Fly.io offre un plan gratuit suffisant pour un petit bot.

1. Installe le CLI : https://fly.io/docs/hands-on/install-flyctl/
2. Dans le dossier du bot :

```bash
fly auth signup
fly launch          # choisir une région Europe (cdg = Paris)
fly secrets set DISCORD_TOKEN="ton_token" GUILD_ID="..." CHANNEL_ID="..."
fly deploy
```

> ⚠️ Fly.io nécessite un `Dockerfile`. Voici un exemple minimal :
> ```dockerfile
> FROM python:3.11-slim
> RUN apt-get update && apt-get install -y ffmpeg
> WORKDIR /app
> COPY requirements.txt .
> RUN pip install -r requirements.txt
> COPY . .
> CMD ["python", "bot.py"]
> ```

---

## Notes importantes

- Le bot se **synchronise sur l'heure pile** au démarrage (ex: si tu lances à 14h07, le premier son sera à 15h00).
- Le fichier audio doit être accessible depuis le répertoire courant. Les formats `.mp3`, `.wav`, `.ogg` fonctionnent tous.
- Si le bot est déjà dans un salon vocal au moment de jouer, il se déconnecte proprement avant de continuer.