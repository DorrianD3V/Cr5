import discord
from discord.ext import commands


CACHED_RESPONSES = {}

class Context(commands.Context):
    async def send(self, *args, **kwargs):
        if self.message.edited_at and CACHED_RESPONSES.get(self.message.id, None):
            msg = await self.channel.fetch_message(CACHED_RESPONSES[self.message.id])

            if self.bot.paginators.get(msg.id):
                await self.bot.paginators[msg.id].stop()
            
            kwargs['content'] = None
            if args:
                kwargs['content'] = args[0]
            
            await msg.edit(**kwargs)
            return msg
        
        else:
            msg = await self.reply(*args, **kwargs, mention_author=True)
            CACHED_RESPONSES[self.message.id] = msg.id
            return msg

    async def react(self, *emojis):
        async def _reaction_add_task():
            for emoji in emojis:
                await self.message.add_reaction(emoji)
        self.bot.loop.create_task(_reaction_add_task())
