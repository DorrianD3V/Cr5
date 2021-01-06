import discord
import os, sys

from discord.ext import commands
from datetime import datetime


class Owner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context):
        return await self.bot.is_owner(ctx.author)

    @commands.group(name='owner',
                    hidden=True,
                    invoke_without_command=True)
    async def owner(self, ctx: commands.Context):
        """овнер-онли команды"""
        raise commands.UserInputError()

    @owner.command(name='comment-bug')
    async def comment_bug(self, ctx: commands.Context, id: int, *, comment):
        channel = await self.bot.fetch_channel(self.bot.config.channels['bugs'])
        message = await channel.fetch_message(id)
        
        if message.author.id == self.bot.user.id and message.embeds:
            await message.edit(embed=message.embeds[0].add_field(name=f'Статус на {datetime.now().strftime("%d.%m.%Y")}',
                                                                 value=comment,
                                                                 inline=False))

    @commands.command(name='restart')
    async def restart(self, ctx: commands.Context):
        await ctx.send(f'Restarting...')
        await self.bot.logout()
        os.execl(sys.executable, sys.executable, *sys.argv)


def setup(bot: commands.Bot):
    bot.add_cog(Owner(bot))
