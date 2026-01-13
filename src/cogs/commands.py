"""Slash commands cog for playing specific sounds"""

import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord import FFmpegPCMAudio
from pydub import AudioSegment

from src.utils.config import WAIT_AFTER_SOUND, WAIT_CHANNEL_ID
from src.utils.logger import log_sound_play, log_slash_command_registered


class SoundCommandsCog(commands.Cog):
    """Handle slash commands for playing sounds"""

    def __init__(self, bot):
        self.bot = bot
        self.sounds_dir = "sounds"
        self.sound_files = []

    def load_sound_files(self):
        """Load list of available sound files"""
        if not os.path.exists(self.sounds_dir):
            return

        self.sound_files = [
            f for f in os.listdir(self.sounds_dir)
            if f.endswith((".mp3", ".wav"))
        ]
        self.sound_files.sort()

    async def play_sound_in_voice(self, interaction: discord.Interaction, sound_file: str):
        """Play a specific sound in the user's voice channel and reset the cycle"""
        # Check if user is in a voice channel
        if not interaction.user.voice:
            await interaction.response.send_message("❌ Vous devez être dans un canal vocal!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        sound_path = os.path.join(self.sounds_dir, sound_file)

        if not os.path.exists(sound_path):
            await interaction.response.send_message(f"❌ Fichier introuvable: {sound_file}", ephemeral=True)
            return

        # Get the soundboard cog
        soundboard_cog = self.bot.get_cog('SoundboardCog')
        if not soundboard_cog:
            await interaction.response.send_message("❌ Erreur: Soundboard cog non trouvé", ephemeral=True)
            return

        try:
            # Check if bot is already in the user's voice channel
            if soundboard_cog.voice_client and soundboard_cog.voice_client.channel == voice_channel:
                # Already in the same channel, just play the sound
                pass
            else:
                # Need to move to the user's channel
                if soundboard_cog.voice_client:
                    await soundboard_cog.voice_client.disconnect()
                # Connect to user's voice channel
                soundboard_cog.voice_client = await voice_channel.connect()

            # Get audio duration
            audio = AudioSegment.from_mp3(sound_path)
            audio_duration = len(audio) / 1000

            # Play the sound
            audio_source = FFmpegPCMAudio(executable="ffmpeg", source=sound_path)
            soundboard_cog.voice_client.play(audio_source)

            log_sound_play(sound_file, source='command')
            await interaction.response.send_message(f"🎵 Lecture de: **{sound_file}**", ephemeral=False)

            # Wait for sound to finish playing
            await asyncio.sleep(audio_duration)

            # Wait 20 minutes in the channel (same as normal cycle)
            await asyncio.sleep(WAIT_AFTER_SOUND)

            # Move to wait channel
            wait_channel = self.bot.get_channel(WAIT_CHANNEL_ID)
            if wait_channel:
                if soundboard_cog.voice_client:
                    await soundboard_cog.voice_client.disconnect()
                soundboard_cog.voice_client = await wait_channel.connect()
                await asyncio.sleep(1800)

            # Signal to restart the normal cycle
            soundboard_cog.restart_cycle()

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

    async def sound_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for sound file selection"""
        # Filter sounds based on current input
        filtered = [
            sound for sound in self.sound_files
            if current.lower() in sound.lower()
        ]

        # Return max 25 choices (Discord limit)
        return [
            app_commands.Choice(name=sound[:100], value=sound)
            for sound in filtered[:25]
        ]

    @app_commands.command(name="play", description="Jouer un son dans votre canal vocal")
    @app_commands.describe(sound="Choisissez un son à jouer")
    @app_commands.autocomplete(sound=sound_autocomplete)
    async def play_sound(self, interaction: discord.Interaction, sound: str):
        """Play a sound command"""
        await self.play_sound_in_voice(interaction, sound)


async def setup(bot):
    """Setup function to add the cog"""
    cog = SoundCommandsCog(bot)
    await bot.add_cog(cog)

    # Load sound files
    cog.load_sound_files()

    # Sync commands with Discord
    try:
        await bot.tree.sync()
        log_slash_command_registered(len(cog.sound_files))
    except Exception as e:
        pass

    return cog
