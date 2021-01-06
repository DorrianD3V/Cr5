import discord
from discord.ext import commands


class Paginator:
    def __init__(self, ctx: commands.Context):
        self.bot = ctx.bot
        self.author = ctx.author
        self.ctx = ctx
        self.pages = []
        self.active = False
        self.current_page = 0
        self.reactions = {
            'left': '<:cr5_paginator_left:788127874888106015>',
            'stop': '<:cr5_paginator_stop:788127874800025621>',
            'right': '<:cr5_paginator_right:788127874942500864>'
        }

    def get_page(self, i):
        if not len(self.pages) > i >= 0:
            return None
        page = self.pages[i]
        if type(page) == dict:
            return page
        elif type(page) == discord.Embed:
            return {"embed": page}
        else:
            return {"content": str(page)}

    async def stop(self):
        self.active = False
        for reaction in self.reactions.values():
            await self.msg.remove_reaction(reaction, self.ctx.guild.me)

    async def goto(self, i):
        i = 0 if i >= len(self.pages) else (len(self.pages)-1 if i < 0 else i)
        await self.msg.edit(**self.get_page(i))

    async def listener(self, event):
        while self.active:
            try:
                r = await self.bot.wait_for(event,
                                            check=lambda r, u: u.id == self.author.id
                                                               and r.message.id == self.msg.id,
                                            timeout=120)
            except:
                return await self.stop()
            
            if str(r[0]) == self.reactions['left']:
                await self.goto(self.current_page - 1)
            
            elif str(r[0]) == self.reactions['stop']:
                return await self.stop()

            elif str(r[0]) == self.reactions['right']:
                await self.goto(self.current_page + 1)

    async def start(self):
        self.msg = await self.ctx.send(**self.get_page(0))
        for reaction in self.reactions.values():
            await self.msg.add_reaction(reaction)
        
        self.active = True
        self.bot.loop.create_task(self.listener('reaction_add'))
        self.bot.loop.create_task(self.listener('reaction_remove'))
