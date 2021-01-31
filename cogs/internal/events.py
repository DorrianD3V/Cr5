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

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if not channel.guild.me.guild_permissions.manage_roles:
            return
        role = discord.utils.get(channel.guild.roles, name='[Cr5] Muted')
        if not role:
            return
        await channel.set_permissions(role,
                                      send_messages=False,
                                      add_reactions=False,
                                      speak=False)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        channel = await self.bot.fetch_channel(self.bot.config.channels['server_log'])
        await channel.send(f'Меня добавили на **{guild}** ({guild.id}) с {guild.member_count} участниками\n'
                           f'Теперь у меня **{len(self.bot.guilds)}** серверов')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        channel = await self.bot.fetch_channel(self.bot.config.channels['server_log'])
        await channel.send(f'Меня убрали с сервера **{guild}** ({guild.id})\n'
                           f'Теперь у меня **{len(self.bot.guilds)}** серверов')


def setup(bot: commands.Bot):
    bot.add_cog(Events(bot))
