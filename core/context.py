import discord
from discord.ext import commands


class Context(commands.Context):
    async def send(self, *args, **kwargs):
        return await self.reply(*args, **kwargs, mention_author=True)
