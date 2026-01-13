"""Soundboard cog for playing sounds in voice channels"""

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
    WAIT_AFTER_SOUND,
    WAIT_IN_WAIT_CHANNEL,
    EMPTY_CHANNEL_THRESHOLD,
    PAUSE_AFTER_EMPTY_CHANNELS
)
from src.utils.logger import (
    log_voice_join,
    log_voice_leave,
    log_sound_play,
    log_empty_channel,
    log_waiting,
    log_cycle_restart,
    log_error
)


class SoundboardCog(commands.Cog):
    """Handle soundboard playback functionality"""

    def __init__(self, bot, sound_titles):
        self.bot = bot
        self.sound_titles = sound_titles
        self.voice_client = None
        self.current_task = None
        self.should_restart = False

    def restart_cycle(self):
        """Signal to restart the soundboard cycle"""
        self.should_restart = True

    async def play_random_sound(self):
        """Main loop for playing random sounds in voice channels"""
        text_channel = self.bot.get_channel(TEXT_CHANNEL_ID)
        empty_channel_count = 0

        while True:
            # Check if we should restart the cycle
            if self.should_restart:
                self.should_restart = False
                log_cycle_restart()
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
                    log_empty_channel(target_voice_channel.name)
                    empty_channel_count += 1
                    continue
                else:
                    empty_channel_count = 0
                    log_voice_join(target_voice_channel.name, len(channel_members))

                # Get audio files
                audio_files = [
                    file for file in os.listdir("sounds")
                    if file.endswith((".mp3", ".wav"))
                ]
                if not audio_files:
                    break

                # Play random sound
                random.shuffle(audio_files)
                random_sound_file = audio_files.pop(0)

                audio_file_path = os.path.join("sounds", random_sound_file)
                audio = AudioSegment.from_mp3(audio_file_path)
                audio_duration = len(audio) / 1000
                audio_source = FFmpegPCMAudio(executable="ffmpeg", source=audio_file_path)

                try:
                    if not self.voice_client.is_playing():
                        self.voice_client.play(audio_source)
                        sound_title = self.sound_titles.get(random_sound_file, 'Unknown')
                        log_sound_play(sound_title, source='auto')
                        if text_channel:
                            await text_channel.send(f'Vous écoutez désormais: {sound_title}')
                except (ConnectionClosed, ClientException) as e:
                    log_error(f"Erreur de lecture: {e}")
                    break

                # Wait for sound to finish
                await asyncio.sleep(audio_duration)

                # Wait after sound
                log_waiting(WAIT_AFTER_SOUND // 60, target_voice_channel.name)
                await asyncio.sleep(WAIT_AFTER_SOUND)

                # Move to wait channel
                wait_channel = self.bot.get_channel(WAIT_CHANNEL_ID)
                if wait_channel:
                    if self.voice_client:
                        log_voice_leave(target_voice_channel.name)
                        await self.voice_client.disconnect()
                    self.voice_client = await wait_channel.connect()
                    log_voice_join(wait_channel.name, 0)
                    log_waiting(WAIT_IN_WAIT_CHANNEL // 60, wait_channel.name)
                    await asyncio.sleep(WAIT_IN_WAIT_CHANNEL)

            except discord.errors.ConnectionClosed as e:
                target_voice_channel_id = random.choice(channel_ids)
                target_voice_channel = self.bot.get_channel(target_voice_channel_id)
                self.voice_client = await target_voice_channel.connect()
                continue


async def setup(bot, sound_titles):
    """Setup function to add the cog"""
    cog = SoundboardCog(bot, sound_titles)
    await bot.add_cog(cog)
    return cog
