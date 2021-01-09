import discord
from discord.ext import commands


class Moderation(commands.Cog, name='Модерация'):
    """Команды, позволяющие вам модерировать сервер."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name='kick',
                      usage='<пользователь> [причина]')
    @commands.has_permissions(kick_members=True)
    @commands.bot_has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason = None):
        """Выгнать пользователя с сервера"""
        if reason and len(reason) > 200:
            return await ctx.send('Максимальная длина причины — **200 символов**.')

        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send('Вы не можете выгнать этого пользователя, '
                                  'так как его роль выше или на равне с вашей.')
        if member.guild_permissions > ctx.author.guild_permissions:
            return await ctx.send('Вы не можете выгнать этого пользователя, '
                                  'так как его права выше чем ваши')

        if member.top_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send('Я не могу выгнать этого пользователя, '
                                  'так как его роль выше или на равне с моей.')
        if member.guild_permissions > ctx.guild.me.guild_permissions:
            return await ctx.send('Я не могу выгнать этого пользователя, '
                                  'так как его права выше чем мои')

        try:
            await member.send(embed=discord.Embed(title=f'Вы были выгнаны с {ctx.guild}') \
                                           .set_thumbnail(url=ctx.guild.icon_url) \
                                           .add_field(name='Модератор',
                                                      value=str(ctx.author)) \
                                           .add_field(name='Причина',
                                                      value=reason or 'Не установлена'))
        except discord.Forbidden:
            pass
        finally:
            await member.kick(reason=f'[Выгнан {ctx.author}] {reason or "Причина не установлена"}')
            await ctx.send(f'Вы успешно выгнали **{member}** :ok_hand:')
    
    @commands.command(name='ban',
                      usage='<пользователь> [причина]')
    @commands.has_permissions(ban_members=True)
    @commands.bot_has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason = None):
        """Забанить пользователя на сервере"""
        if reason and len(reason) > 200:
            return await ctx.send('Максимальная длина причины — **200 символов**.')

        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send('Вы не можете забанить этого пользователя, '
                                  'так как его роль выше или на равне с вашей.')
        if member.guild_permissions > ctx.author.guild_permissions:
            return await ctx.send('Вы не можете забанить этого пользователя, '
                                  'так как его права выше чем ваши')

        if member.top_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send('Я не могу забанить этого пользователя, '
                                  'так как его роль выше или на равне с моей.')
        if member.guild_permissions > ctx.guild.me.guild_permissions:
            return await ctx.send('Я не могу забанить этого пользователя, '
                                  'так как его права выше чем мои')

        try:
            await member.send(embed=discord.Embed(title=f'Вы были забанены на {ctx.guild}') \
                                           .set_thumbnail(url=ctx.guild.icon_url) \
                                           .add_field(name='Модератор',
                                                      value=str(ctx.author)) \
                                           .add_field(name='Причина',
                                                      value=reason or 'Не установлена'))
        except discord.Forbidden:
            pass
        finally:
            await member.ban(reason=f'[Забанен {ctx.author}] {reason or "Причина не установлена"}')
            await ctx.send(f'Вы успешно забанили **{member}** :ok_hand:')


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
