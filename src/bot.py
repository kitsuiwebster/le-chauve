"""Main bot initialization and event handlers"""

import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.cogs.soundboard import setup as soundboard_setup
from src.cogs.status import setup as status_setup
from src.cogs.commands import setup as commands_setup
from src.utils.config import VOICE_CHANNEL_IDS
from src.utils.logger import log_bot_ready, log_channels_available

# Load environment variables
load_dotenv()

# Configure logging - silence discord.py
logging.getLogger('discord').setLevel(logging.ERROR)
logging.getLogger('discord.voice_state').setLevel(logging.ERROR)
logging.getLogger('discord.player').setLevel(logging.ERROR)
logging.getLogger('discord.gateway').setLevel(logging.ERROR)
logging.getLogger('discord.client').setLevel(logging.ERROR)
logging.getLogger('discord.http').setLevel(logging.ERROR)


class RomeoBot(commands.Bot):
    """Custom Bot class for Romeo"""

    def __init__(self, song_titles):
        intents = discord.Intents.default()
        intents.typing = False
        intents.members = True
        intents.message_content = True
        intents.guilds = True

        super().__init__(command_prefix='!', intents=intents)
        self.sound_titles = sound_titles
        self.soundboard_cog = None

    async def setup_hook(self):
        """Called when the bot is starting up"""
        # Load all cogs
        await status_setup(self)
        await commands_setup(self)
        self.soundboard_cog = await soundboard_setup(self, self.sound_titles)

    async def on_ready(self):
        """Called when the bot is ready"""
        # Log bot ready
        log_bot_ready(self.user.name)

        # Display available voice channels
        channel_names = []
        for channel_id in VOICE_CHANNEL_IDS:
            channel = self.get_channel(channel_id)
            if channel:
                channel_names.append(channel.name)

        log_channels_available(channel_names)

        # Start status change task
        status_cog = self.get_cog('StatusCog')
        if status_cog:
            self.loop.create_task(status_cog.change_status())

        # Start soundboard
        if self.soundboard_cog:
            await self.soundboard_cog.play_random_sound()


def create_bot(sound_titles):
    """Factory function to create a bot instance"""
    return RomeoBot(sound_titles)
