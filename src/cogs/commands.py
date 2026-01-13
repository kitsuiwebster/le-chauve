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
from config.sound_titles import sound_titles


class SoundCommandsCog(commands.Cog):
    """Handle slash commands for playing sounds"""

    def __init__(self, bot):
        self.bot = bot
        self.sounds_dir = "sounds"
        self.sound_files = []
        self.sounds_by_letter = {}

    def load_sound_files(self):
        """Load list of available sound files and organize by first letter"""
        if not os.path.exists(self.sounds_dir):
            return

        self.sound_files = [
            f for f in os.listdir(self.sounds_dir)
            if f.endswith((".mp3", ".wav"))
        ]
        self.sound_files.sort()

        # Organize sounds by first letter
        self.sounds_by_letter = {}
        for sound_file in self.sound_files:
            first_letter = sound_file[0].lower()
            if first_letter not in self.sounds_by_letter:
                self.sounds_by_letter[first_letter] = []
            self.sounds_by_letter[first_letter].append(sound_file)

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
            audio_source = FFmpegPCMAudio(
                executable="ffmpeg",
                source=sound_path,
                options='-loglevel panic'
            )
            soundboard_cog.voice_client.play(audio_source)

            # Get sound title from mapping, or use filename without extension
            sound_display = sound_titles.get(
                sound_file,
                os.path.splitext(sound_file)[0].replace('_', ' ').title()
            )
            log_sound_play(sound_display, source='command')
            await interaction.response.send_message(f"{interaction.user.display_name} a lancé {sound_display}", ephemeral=False)

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

    def create_letter_autocomplete(self, letter: str):
        """Create an autocomplete function for a specific letter"""
        async def autocomplete(
            self,
            interaction: discord.Interaction,
            current: str,
        ) -> list[app_commands.Choice[str]]:
            sounds = self.sounds_by_letter.get(letter, [])

            # Return all sounds starting with this letter (max 25 for Discord limit)
            return [
                app_commands.Choice(
                    name=sound_titles.get(sound, sound)[:100],
                    value=sound
                )
                for sound in sounds[:25]
            ]
        return autocomplete

    def create_letter_command(self, letter: str):
        """Create a command for a specific letter"""
        @app_commands.command(name=letter, description=f"Jouer un son commençant par '{letter.upper()}'")
        @app_commands.describe(sound="Choisissez un son")
        async def letter_command(interaction: discord.Interaction, sound: str):
            await self.play_sound_in_voice(interaction, sound)

        # Add autocomplete
        autocomplete_func = self.create_letter_autocomplete(letter)
        letter_command.autocomplete('sound')(autocomplete_func.__get__(self, SoundCommandsCog))

        return letter_command


async def setup(bot):
    """Setup function to add the cog"""
    cog = SoundCommandsCog(bot)
    await bot.add_cog(cog)

    # Load sound files
    cog.load_sound_files()

    # Create and add commands for each letter that has sounds
    for letter in sorted(cog.sounds_by_letter.keys()):
        command = cog.create_letter_command(letter)
        bot.tree.add_command(command)

    # Sync commands with Discord
    try:
        await bot.tree.sync()
        log_slash_command_registered(len(cog.sounds_by_letter))
    except Exception as e:
        pass

    return cog
