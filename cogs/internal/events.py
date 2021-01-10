import discord
from discord.ext import commands

from ext import Logger
from core.context import CACHED_RESPONSES


class Events(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.guild and not msg.author.bot:
            if msg.content in (f'<@{self.bot.user.id}>', f'<@!{self.bot.user.id}>'):
                prefixes = await self.bot.get_prefix(msg)
                resp = await msg.reply(embed=discord.Embed(description=f'Префикс бота: `{prefixes[-1]}`'),
                                       mention_author=True)
                CACHED_RESPONSES[msg.id] = resp.id
        
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.guild and not after.author.bot:
            if after.content in (f'<@{self.bot.user.id}>', f'<@!{self.bot.user.id}>'):
                prefixes = await self.bot.get_prefix(after)
                embed = discord.Embed(description=f'Префикс бота: `{prefixes[-1]}`')
                if CACHED_RESPONSES.get(after.id):
                    msg = await after.channel.fetch_message(CACHED_RESPONSES[after.id])
                    await msg.edit(content=None, embed=embed)
                else:
                    resp = await after.reply(embed=embed, mention_author=True)
                    CACHED_RESPONSES[after.id] = resp.id


def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))
