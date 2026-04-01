import discord
import asyncio
import os
from discord.ext import commands, tasks
from datetime import datetime

# ── Configuration ────────────────────────────────────────────────────────────
TOKEN        = os.getenv("DISCORD_TOKEN")           # Token du bot
GUILD_ID     = int(os.getenv("GUILD_ID", "0"))      # ID de ton serveur
CHANNEL_ID   = int(os.getenv("CHANNEL_ID", "0"))    # ID du salon vocal
SOUND_FILE   = os.getenv("SOUND_FILE", "sound.mp3") # Son joué toutes les heures

# Son déclenché quand un membre spécifique rejoint le vocal
# Format : { ID_MEMBRE: "fichier_son.mp3" }
# Tu peux en ajouter autant que tu veux !
MEMBER_SOUNDS = {
    int(os.getenv("SPECIAL_MEMBER_ID", "0")): os.getenv("SPECIAL_SOUND", "special.mp3"),
    # Exemple d'entrées supplémentaires :
    # 123456789012345678: "rizz.mp3",
    # 987654321098765432: "loser.mp3",
}
# ─────────────────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.members = True  # Nécessaire pour on_voice_state_update
bot = commands.Bot(command_prefix="!", intents=intents)


async def play_sound(channel: discord.VoiceChannel, sound_file: str = None) -> None:
    """Se connecte au salon vocal, joue le son, puis se déconnecte."""
    sound_file = sound_file or SOUND_FILE
    vc = None
    try:
        # Si le bot est déjà dans un salon, le déplacer
        guild = channel.guild
        existing_vc = guild.voice_client
        if existing_vc:
            if existing_vc.is_playing():
                existing_vc.stop()
            await existing_vc.move_to(channel)
            vc = existing_vc
        else:
            vc = await channel.connect()
        print(f"[{datetime.now():%H:%M:%S}] Connecté à #{channel.name}")

        # Jouer le fichier audio
        source = discord.FFmpegPCMAudio(sound_file)
        vc.play(source)

        # Attendre la fin de la lecture
        while vc.is_playing():
            await asyncio.sleep(1)

        print(f"[{datetime.now():%H:%M:%S}] Son joué avec succès")

    except Exception as e:
        print(f"[ERREUR] {e}")

    finally:
        pass  # Le bot reste dans le salon


@tasks.loop(hours=1)
async def hourly_sound() -> None:
    """Tâche lancée toutes les heures."""
    guild = bot.get_guild(GUILD_ID)
    if guild is None:
        print("[ERREUR] Serveur introuvable. Vérifie GUILD_ID.")
        return

    channel = guild.get_channel(CHANNEL_ID)
    if channel is None or not isinstance(channel, discord.VoiceChannel):
        print("[ERREUR] Salon vocal introuvable. Vérifie CHANNEL_ID.")
        return

    await play_sound(channel)


@hourly_sound.before_loop
async def before_hourly():
    """Attend que le bot soit prêt avant de démarrer la boucle."""
    await bot.wait_until_ready()

    # Jouer immédiatement au démarrage
    guild = bot.get_guild(GUILD_ID)
    if guild:
        channel = guild.get_channel(CHANNEL_ID)
        if channel and isinstance(channel, discord.VoiceChannel):
            await play_sound(channel)

    # Puis synchroniser sur l'heure pile (ex: 14:00:00 plutôt que 14:07:23)
    now = datetime.now()
    seconds_until_next_hour = 3600 - (now.minute * 60 + now.second)
    print(f"[INFO] Prochain son dans {seconds_until_next_hour // 60}m {seconds_until_next_hour % 60}s")
    await asyncio.sleep(seconds_until_next_hour)


@bot.event
async def on_voice_state_update(member, before, after):
    """Détecte quand un membre rejoint un salon vocal."""

    # Reconnexion automatique si le bot est déconnecté
    if member == bot.user and before.channel is not None and after.channel is None:
        await asyncio.sleep(3)
        guild = bot.get_guild(GUILD_ID)
        if guild:
            channel = guild.get_channel(CHANNEL_ID)
            if channel and isinstance(channel, discord.VoiceChannel):
                await channel.connect()
                print(f"[INFO] Reconnecté à #{channel.name}")
        return

    # Ignorer si le membre ne vient pas d'arriver dans un salon
    if after.channel is None or before.channel == after.channel:
        return

    # Vérifier si ce membre a un son associé
    sound_file = MEMBER_SOUNDS.get(member.id)
    if not sound_file:
        return

    if not os.path.exists(sound_file):
        print(f"[WARN] Son introuvable pour {member.display_name} : {sound_file}")
        return

    print(f"[{datetime.now():%H:%M:%S}] {member.display_name} a rejoint #{after.channel.name} → lecture de {sound_file}")
    await play_sound(after.channel, sound_file)


@bot.event
async def on_ready():
    print(f"[OK] Connecté en tant que {bot.user} (ID: {bot.user.id})")
    print(f"[INFO] Serveur cible : {GUILD_ID} | Salon cible : {CHANNEL_ID}")
    hourly_sound.start()


# Commande manuelle pour tester sans attendre une heure
@bot.command(name="test")
@commands.is_owner()
async def test_sound(ctx):
    """!test — Joue le son immédiatement (owner uniquement)."""
    guild = bot.get_guild(GUILD_ID)
    channel = guild.get_channel(CHANNEL_ID) if guild else None
    if channel:
        await ctx.send("▶️ Lecture du son...")
        await play_sound(channel)
        await ctx.send("✅ Terminé.")
    else:
        await ctx.send("❌ Salon introuvable.")


bot.run(TOKEN)
