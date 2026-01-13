"""Music cog for playing songs in voice channels"""

import os
import random
import asyncio
import discord
from discord import FFmpegPCMAudio, ConnectionClosed, ClientException
from discord.ext import commands
from pydub import AudioSegment

from src.utils.config import (
    VOICE_CHANNEL_IDS,
    TEXT_CHANNEL_ID,
    WAIT_CHANNEL_ID,
    IGNORED_USER_ID,
    WAIT_AFTER_SONG,
    WAIT_IN_WAIT_CHANNEL,
    EMPTY_CHANNEL_THRESHOLD,
    PAUSE_AFTER_EMPTY_CHANNELS
)


class MusicCog(commands.Cog):
    """Handle music playback functionality"""

    def __init__(self, bot, song_titles):
        self.bot = bot
        self.song_titles = song_titles
        self.voice_client = None
        self.current_task = None
        self.should_restart = False

    def restart_cycle(self):
        """Signal to restart the music cycle"""
        self.should_restart = True

    async def play_random_song(self):
        """Main loop for playing random songs in voice channels"""
        text_channel = self.bot.get_channel(TEXT_CHANNEL_ID)
        empty_channel_count = 0

        while True:
            # Check if we should restart the cycle
            if self.should_restart:
                self.should_restart = False
                print("Cycle restarted by command")
                continue
            try:
                # Check if too many empty channels encountered
                if empty_channel_count >= EMPTY_CHANNEL_THRESHOLD:
                    print(f"""
=============================================================
{EMPTY_CHANNEL_THRESHOLD} empty channels encountered. Disconnecting and waiting for 30 minutes.
=============================================================
""")
                    if self.voice_client:
                        await self.voice_client.disconnect()
                    await asyncio.sleep(PAUSE_AFTER_EMPTY_CHANNELS)
                    empty_channel_count = 0
                    continue

                # Choose random voice channel
                target_voice_channel_id = random.choice(VOICE_CHANNEL_IDS)
                target_voice_channel = self.bot.get_channel(target_voice_channel_id)

                # Connect to the channel
                if self.voice_client:
                    await self.voice_client.disconnect()
                self.voice_client = await target_voice_channel.connect()

                # Check for members
                channel_members = [
                    member for member in target_voice_channel.members
                    if member.id != IGNORED_USER_ID and member != self.bot.user
                ]

                if len(channel_members) == 0:
                    print(f"""
=============================================================
Voice channel {target_voice_channel.name} is empty. Moving to the next channel.
=============================================================
""")
                    empty_channel_count += 1
                    continue
                else:
                    empty_channel_count = 0

                print(f"""
=============================================================
Currently in voice channel: {target_voice_channel.name}
Members in voice channel: {[member.name for member in channel_members]}
=============================================================
""")

                # Get audio files
                audio_files = [
                    file for file in os.listdir("sounds")
                    if file.endswith((".mp3", ".wav"))
                ]
                if not audio_files:
                    print("No more sounds in the 'sounds' directory.")
                    break

                # Play random song
                random.shuffle(audio_files)
                random_audio_file = audio_files.pop(0)
                print(f"""
=============================================================
Playing song: {random_audio_file}
=============================================================
""")

                audio_file_path = os.path.join("sounds", random_audio_file)
                audio = AudioSegment.from_mp3(audio_file_path)
                audio_duration = len(audio) / 1000
                audio_source = FFmpegPCMAudio(executable="ffmpeg", source=audio_file_path)

                try:
                    if not self.voice_client.is_playing():
                        self.voice_client.play(audio_source)
                        song_title = self.song_titles.get(random_audio_file, 'Unknown')
                        if text_channel:
                            await text_channel.send(f'Vous écoutez désormais: {song_title}')
                    else:
                        print("Bot is already playing.")
                except (ConnectionClosed, ClientException) as e:
                    print(f"Error occurred: {e}")
                    break

                # Wait for song to finish
                await asyncio.sleep(audio_duration)

                # Wait after song
                print(f"""
=============================================================
Waiting for {WAIT_AFTER_SONG // 60} minutes in the channel after playing the song.
=============================================================
""")
                await asyncio.sleep(WAIT_AFTER_SONG)

                # Move to wait channel
                wait_channel = self.bot.get_channel(WAIT_CHANNEL_ID)
                if wait_channel:
                    if self.voice_client:
                        await self.voice_client.disconnect()
                    self.voice_client = await wait_channel.connect()
                    print(f"""
=============================================================
Bot is in {wait_channel.name}. Waiting for {WAIT_IN_WAIT_CHANNEL // 60} minutes.
=============================================================
""")
                    await asyncio.sleep(WAIT_IN_WAIT_CHANNEL)

            except discord.errors.ConnectionClosed as e:
                print(f"Disconnected from voice with error: {e}")
                print("Attempting to reconnect...")
                target_voice_channel_id = random.choice(VOICE_CHANNEL_IDS)
                target_voice_channel = self.bot.get_channel(target_voice_channel_id)
                self.voice_client = await target_voice_channel.connect()
                continue


async def setup(bot, song_titles):
    """Setup function to add the cog"""
    cog = MusicCog(bot, song_titles)
    await bot.add_cog(cog)
    return cog
