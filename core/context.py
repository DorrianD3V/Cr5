import discord
from discord.ext import commands


class Context(commands.Context):
    async def send(self, *args, **kwargs):
        return await self.reply(*args, **kwargs, mention_author=True)

    async def react(self, *emojis):
        async def _reaction_add_task():
            for emoji in emojis:
                await self.message.add_reaction(emoji)
        self.bot.loop.create_task(_reaction_add_task())
