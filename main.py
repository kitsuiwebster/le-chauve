"""Entry point for Romeo Bot"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import song titles
from config.song_titles import song_titles

# Import bot factory
from src.bot import create_bot


def main():
    """Main entry point"""
    bot_token = os.getenv("DISCORD_BOT_TOKEN")

    if not bot_token:
        raise ValueError("DISCORD_BOT_TOKEN not found in environment variables")

    # Create and run bot
    bot = create_bot(song_titles)
    bot.run(bot_token)


if __name__ == "__main__":
    main()
