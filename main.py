import sys
import os
import yaml

sys.dont_write_bytecode = True

import discord
from discord.ext import commands

from core import Bot, Config


if __name__ == "__main__":
    config = Config()

    for k, v in config.environ.items():
        os.environ[k] = v

    bot = Bot(config,
              command_prefix=commands.when_mentioned_or('c.'),
              intents=discord.Intents.all(),
              allowed_mentions=discord.AllowedMentions.none(),
              chunk_members_at_startup=True,
              help_command=None,
              member_cache_flags=discord.MemberCacheFlags.none())
    
    bot.run()
