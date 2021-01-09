import asyncio
import discord

from discord.ext import commands


CACHED_RESPONSES = {}

class Context(commands.Context):
    async def send(self, *args, **kwargs):
        if self.message.edited_at and CACHED_RESPONSES.get(self.message.id, None):
            msg = await self.channel.fetch_message(CACHED_RESPONSES[self.message.id])

            if self.bot.paginators.get(msg.id):
                await self.bot.paginators[msg.id].stop()
            
            for reaction in msg.reactions:
                self.bot.loop.create_task(msg.remove_reaction(reaction, self.guild.me))
            
            if args:
                kwargs['content'] = args[0]

            kwargs['content'] = kwargs.get('content', None)
            kwargs['embed'] = kwargs.get('embed', None)
            
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

    async def deleteable_message(self, *args, **kwargs):
        msg = await self.send(*args, **kwargs)
        await msg.add_reaction('🚮')
        try:
            await self.bot.wait_for('reaction_add',
                                    check=lambda r, u: r.message.id == msg.id
                                                       and u.id == self.author.id
                                                       and str(r) == '🚮',
                                    timeout=60)
        except asyncio.TimeoutError:
            return await msg.remove_reaction('🚮', self.guild.me)
        else:
            await msg.delete()
            del CACHED_RESPONSES[self.message.id]
