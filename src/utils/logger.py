"""Custom logger with colors and formatting"""

import logging
from datetime import datetime


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output"""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Icons for different log types
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✓',
        'WARNING': '⚠️',
        'ERROR': '✗',
        'CRITICAL': '🔥',
    }

    def format(self, record):
        # Get color and icon
        color = self.COLORS.get(record.levelname, '')
        icon = self.ICONS.get(record.levelname, '')

        # Format time
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')

        # Build colored message
        log_message = f"{color}{icon} [{timestamp}] {record.getMessage()}{self.RESET}"

        return log_message


def setup_logger(name='romeo-bot'):
    """Setup custom logger with colors"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler with colored formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


# Create global logger instance
bot_logger = setup_logger()


def log_bot_ready(bot_name):
    """Log when bot is ready"""
    bot_logger.info(f"👋 {bot_name} est connecté et prêt !")


def log_voice_join(channel_name, member_count):
    """Log when joining a voice channel"""
    bot_logger.info(f"👉 Connexion au canal '{channel_name}' ({member_count} membre{'s' if member_count > 1 else ''})")


def log_voice_leave(channel_name):
    """Log when leaving a voice channel"""
    bot_logger.info(f"👋 Déconnexion du canal '{channel_name}'")


def log_sound_play(sound_name, source='auto'):
    """Log when playing a sound"""
    if source == 'auto':
        bot_logger.info(f"👉 Lecture: {sound_name}")
    else:
        bot_logger.info(f"🎮 Commande /play: {sound_name}")


def log_empty_channel(channel_name):
    """Log when a channel is empty"""
    bot_logger.info(f"🚫 Canal '{channel_name}' vide, passage au suivant")


def log_waiting(minutes, location):
    """Log waiting period"""
    bot_logger.info(f"⏳ Attente de {minutes} min dans {location}")


def log_cycle_restart():
    """Log when cycle restarts"""
    bot_logger.info(f"👉 Redémarrage du cycle")


def log_error(error_msg):
    """Log an error"""
    bot_logger.error(f"💥 Erreur: {error_msg}")


def log_warning(warning_msg):
    """Log a warning"""
    bot_logger.warning(f"⚠️  {warning_msg}")


def log_slash_command_registered(count):
    """Log slash commands registration"""
    bot_logger.info(f"⚡ Commande /play activée ({count} sons disponibles)")


def log_channels_available(channels):
    """Log available voice channels"""
    bot_logger.info(f"📡 {len(channels)} canaux vocaux disponibles")
