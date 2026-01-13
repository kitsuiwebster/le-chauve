"""Status cog for managing bot presence"""

import asyncio
import discord
from discord.ext import commands

from src.utils.config import BOT_STATUSES, STATUS_CHANGE_INTERVAL


class StatusCog(commands.Cog):
    """Handle bot status updates"""

    def __init__(self, bot):
        self.bot = bot

    async def change_status(self):
        """Cycle through different bot statuses"""
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            statuses = [discord.Game(name=status) for status in BOT_STATUSES]
            for status in statuses:
                await self.bot.change_presence(activity=status)
                await asyncio.sleep(STATUS_CHANGE_INTERVAL)


async def setup(bot):
    """Setup function to add the cog"""
    cog = StatusCog(bot)
    await bot.add_cog(cog)
    return cog
