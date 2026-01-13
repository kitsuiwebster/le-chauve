"""Music cog for playing songs in voice channels"""

import os
import random
import asyncio
import discord
from discord import FFmpegPCMAudio, ConnectionClosed, ClientException
from discord.ext import commands
from pydub import AudioSegment

from src.utils.config import (
    VOICE_CHANNEL_IDS as channel_ids,
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
                continue
            try:
                # Check if too many empty channels encountered
                if empty_channel_count >= EMPTY_CHANNEL_THRESHOLD:
                    if self.voice_client:
                        await self.voice_client.disconnect()
                    await asyncio.sleep(PAUSE_AFTER_EMPTY_CHANNELS)
                    empty_channel_count = 0
                    continue

                # Choose random voice channel
                target_voice_channel_id = random.choice(channel_ids)
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
                    empty_channel_count += 1
                    continue
                else:
                    empty_channel_count = 0

                # Get audio files
                audio_files = [
                    file for file in os.listdir("sounds")
                    if file.endswith((".mp3", ".wav"))
                ]
                if not audio_files:
                    break

                # Play random song
                random.shuffle(audio_files)
                random_audio_file = audio_files.pop(0)

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
                except (ConnectionClosed, ClientException) as e:
                    break

                # Wait for song to finish
                await asyncio.sleep(audio_duration)

                # Wait after song
                await asyncio.sleep(WAIT_AFTER_SONG)

                # Move to wait channel
                wait_channel = self.bot.get_channel(WAIT_CHANNEL_ID)
                if wait_channel:
                    if self.voice_client:
                        await self.voice_client.disconnect()
                    self.voice_client = await wait_channel.connect()
                    await asyncio.sleep(WAIT_IN_WAIT_CHANNEL)

            except discord.errors.ConnectionClosed as e:
                target_voice_channel_id = random.choice(channel_ids)
                target_voice_channel = self.bot.get_channel(target_voice_channel_id)
                self.voice_client = await target_voice_channel.connect()
                continue


async def setup(bot, song_titles):
    """Setup function to add the cog"""
    cog = MusicCog(bot, song_titles)
    await bot.add_cog(cog)
    return cog
