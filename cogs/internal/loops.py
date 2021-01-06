import discord
from discord.ext import commands, tasks

import asyncio

from ext import Logger


class Tasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_connect(self):
        await asyncio.sleep(5)
        self.bot.loop.create_task(self.database_backup())

    async def database_backup(self):
        self.bot.db.dump('backup.psql')
        
        channel = await self.bot.fetch_channel(self.bot.config.channels['backups'])
        await channel.send(file=discord.File('backup.psql'))

        await asyncio.sleep(30 * 60) # 30m
        await self.database_backup()


def setup(bot: commands.Bot):
    bot.add_cog(Tasks(bot))
