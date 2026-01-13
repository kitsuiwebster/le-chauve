"""Slash commands cog for playing specific sounds"""

import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from discord import FFmpegPCMAudio
from pydub import AudioSegment

from src.utils.config import WAIT_AFTER_SONG, WAIT_CHANNEL_ID


class SoundCommandsCog(commands.Cog):
    """Handle slash commands for playing sounds"""

    def __init__(self, bot):
        self.bot = bot
        self.sounds_dir = "sounds"

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

        # Get the music cog
        music_cog = self.bot.get_cog('MusicCog')
        if not music_cog:
            await interaction.response.send_message("❌ Erreur: Music cog non trouvé", ephemeral=True)
            return

        try:
            # Disconnect from current voice channel if any
            if music_cog.voice_client:
                await music_cog.voice_client.disconnect()

            # Connect to user's voice channel
            music_cog.voice_client = await voice_channel.connect()

            # Get audio duration
            audio = AudioSegment.from_mp3(sound_path)
            audio_duration = len(audio) / 1000

            # Play the sound
            audio_source = FFmpegPCMAudio(executable="ffmpeg", source=sound_path)
            music_cog.voice_client.play(audio_source)

            await interaction.response.send_message(f"🎵 Lecture de: **{sound_file}**", ephemeral=False)

            # Wait for sound to finish playing
            await asyncio.sleep(audio_duration)

            # Wait 20 minutes in the channel (same as normal cycle)
            print(f"""
=============================================================
Waiting for {WAIT_AFTER_SONG // 60} minutes in the channel after command sound.
=============================================================
""")
            await asyncio.sleep(WAIT_AFTER_SONG)

            # Move to wait channel
            wait_channel = self.bot.get_channel(WAIT_CHANNEL_ID)
            if wait_channel:
                if music_cog.voice_client:
                    await music_cog.voice_client.disconnect()
                music_cog.voice_client = await wait_channel.connect()
                print(f"""
=============================================================
Bot is in wait channel after command. Waiting for 30 minutes.
=============================================================
""")
                await asyncio.sleep(1800)

            # Signal to restart the normal cycle
            music_cog.restart_cycle()

        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)
            print(f"Error in sound command: {e}")

    async def create_sound_commands(self):
        """Dynamically create slash commands for each sound file"""
        if not os.path.exists(self.sounds_dir):
            print(f"Warning: {self.sounds_dir} directory not found")
            return

        sound_files = [
            f for f in os.listdir(self.sounds_dir)
            if f.endswith((".mp3", ".wav"))
        ]

        for sound_file in sound_files:
            # Create command name from filename (remove extension, make lowercase, replace spaces)
            command_name = os.path.splitext(sound_file)[0].lower().replace(" ", "_").replace("-", "_")

            # Remove special characters
            command_name = ''.join(c for c in command_name if c.isalnum() or c == '_')

            # Limit to 32 characters (Discord slash command limit)
            if len(command_name) > 32:
                command_name = command_name[:32]

            # Skip if command name is invalid
            if not command_name or command_name[0].isdigit():
                print(f"Skipping invalid command name for: {sound_file}")
                continue

            # Create the slash command
            async def sound_command_func(interaction: discord.Interaction, filename=sound_file):
                await self.play_sound_in_voice(interaction, filename)

            # Set proper attributes for the command
            sound_command_func.__name__ = f"sound_{command_name}"

            command = app_commands.Command(
                name=command_name,
                description=f"Jouer {sound_file[:50]}",
                callback=sound_command_func
            )

            # Add command to the bot's tree
            self.bot.tree.add_command(command)

        print(f"Created {len(sound_files)} sound commands")


async def setup(bot):
    """Setup function to add the cog"""
    cog = SoundCommandsCog(bot)
    await bot.add_cog(cog)

    # Create sound commands
    await cog.create_sound_commands()

    # Sync commands with Discord
    try:
        await bot.tree.sync()
        print("Slash commands synced with Discord")
    except Exception as e:
        print(f"Error syncing commands: {e}")

    return cog
