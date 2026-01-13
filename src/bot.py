"""Main bot initialization and event handlers"""

import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

from src.cogs.music import setup as music_setup
from src.cogs.status import setup as status_setup
from src.utils.config import VOICE_CHANNEL_IDS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class RomeoBot(commands.Bot):
    """Custom Bot class for Romeo"""

    def __init__(self, song_titles):
        intents = discord.Intents.default()
        intents.typing = False
        intents.members = True
        intents.message_content = True
        intents.guilds = True

        super().__init__(command_prefix='!', intents=intents)
        self.song_titles = song_titles
        self.music_cog = None

    async def setup_hook(self):
        """Called when the bot is starting up"""
        # Load all cogs
        await status_setup(self)
        self.music_cog = await music_setup(self, self.song_titles)

    async def on_ready(self):
        """Called when the bot is ready"""
        print(f"""
=============================================================
{self.user.name} is damn connected !!
=============================================================
""")

        # Display available voice channels
        channel_names = []
        for channel_id in VOICE_CHANNEL_IDS:
            channel = self.get_channel(channel_id)
            if channel:
                channel_names.append(channel.name)

        print(f"Voice channels: {', '.join(channel_names)}")

        # Start status change task
        status_cog = self.get_cog('StatusCog')
        if status_cog:
            self.loop.create_task(status_cog.change_status())

        # Start playing music
        if self.music_cog:
            await self.music_cog.play_random_song()


def create_bot(song_titles):
    """Factory function to create a bot instance"""
    return RomeoBot(song_titles)
