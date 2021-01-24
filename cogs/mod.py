import discord
from discord.ext import commands

from humanize import precisedelta


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
        except (discord.Forbidden, discord.HTTPException):
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
        except (discord.Forbidden, discord.HTTPException):
            pass
        finally:
            await member.ban(reason=f'[Забанен {ctx.author}] {reason or "Причина не установлена"}')
            await ctx.send(f'Вы успешно забанили **{member}** :ok_hand:')

    @commands.command(name='warn',
                      usage='<пользователь> [причина]')
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason = None):
        """Выдать предупреждение пользователю"""
        if reason and len(reason) > 200:
            return await ctx.send('Максимальная длина причины — **200 символов**.')

        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send('Вы не можете выдать предупреждение этому пользователю, '
                                  'так как его роль выше или на равне с вашей.')
        if member.guild_permissions > ctx.author.guild_permissions:
            return await ctx.send('Вы не можете выдать предупреждение этому пользователю, '
                                  'так как его права выше чем ваши')
        
        await self.bot.db.execute('INSERT INTO warns VALUES ($1, $2, $3, $4)',
                                  [ctx.guild.id, member.id, ctx.author.id, reason])
        warns = len(await self.bot.db.execute('SELECT * FROM warns WHERE guild_id=$1 AND user_id=$2',
                                              [ctx.guild.id, member.id],
                                              as_dict=False))
        
        try:
            await member.send(embed=discord.Embed(title=f'Вам было выдано предупреждение на сервере {ctx.guild}') \
                                           .set_thumbnail(url=ctx.guild.icon_url) \
                                           .add_field(name='Модератор',
                                                      value=str(ctx.author)) \
                                           .add_field(name='Причина',
                                                      value=reason or 'Не установлена') \
                                           .set_footer(text=f'Предупреждение #{warns}'))
        except (discord.Forbidden, discord.HTTPException):
            pass
        finally:
            await ctx.send(f'Пользователю **{member}** было выдано предупреждение :ok_hand: (предупреждение #{warns})')

    @commands.command(name='purge',
                      aliases=['clear'],
                      usage='<количество сообщений от 1 до 100>')
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int):
        """Удалить определённое количество сообщений в текущем канале"""
        if amount > 100 or amount < 1:
            return await ctx.send(f'Количество сообщений должно быть от **1** до **100**.')
        
        await ctx.channel.purge(limit=amount)

    @commands.command(name='lockdown', usage='[канал]')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def lockdown(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Запрещает всем отправлять сообщения в укзааном вами канале."""
        if not channel:
            channel = ctx.channel
        permissions = channel.overwrites_for(ctx.guild.default_role)
        if permissions.send_messages == False:
            permissions.send_messages = None
            await ctx.react('✅', '🔓')
        else:
            permissions.send_messages = False
            await ctx.react('✅', '🔒')
        await channel.set_permissions(ctx.guild.default_role, **dict(permissions))

    @commands.command(name='mute', usage='<пользователь> [время] [причина]')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, *args):
        """Замутить пользователя
        
        **Подсказка:**
        Время можно указать, написав цифру и добавив соотвествующий символ в конец.
        **s** — секунды, **m** — минуты, **h** — часы, **d** — дни
        Пример: `5s 10m` - 5 секунд 10 минут"""
        if discord.utils.get(member.roles, name='[Cr5] Muted'):
            return await ctx.send(f'**{member}** уже замучен :no_entry:')
        
        time = 0
        reason = None
        values = {
            's': 1,
            'm': 60,
            'h': 60 * 60,
            'd': 24 * 60 * 60
        }

        for i, arg in enumerate(args):
            if arg[:-1].isnumeric() and arg[-1] in values:
                time += int(arg[:-1]) * values[arg[-1]]
            else:
                reason = ' '.join(args[i:])

        if reason and len(reason) > 200:
            return await ctx.send('Максимальная длина причины — **200 символов**.')

        if member.top_role.position >= ctx.author.top_role.position:
            return await ctx.send('Вы не можете замутить этого пользователя, '
                                  'так как его роль выше или на равне с вашей.')
        if member.guild_permissions > ctx.author.guild_permissions:
            return await ctx.send('Вы не можете замутить этого пользователя, '
                                  'так как его права выше чем ваши')

        if member.top_role.position >= ctx.guild.me.top_role.position:
            return await ctx.send('Я не могу замутить этого пользователя, '
                                  'так как его роль выше или на равне с моей.')
        if member.guild_permissions > ctx.guild.me.guild_permissions:
            return await ctx.send('Я не могу замутить этого пользователя, '
                                  'так как его права выше чем мои')

        try:
            await member.send(embed=discord.Embed(title=f'Вы были замучены на {ctx.guild}') \
                                           .set_thumbnail(url=ctx.guild.icon_url) \
                                           .add_field(name='Модератор',
                                                      value=str(ctx.author)) \
                                           .add_field(name='Причина',
                                                      value=reason or 'Не установлена') \
                                           .add_field(name='Длительность мута',
                                                      value=time or '∞'))
        except (discord.Forbidden, discord.HTTPException):
            pass
        finally:
            await ctx.send(f'Пользователь **{member}** замучен {f"на {precisedelta(time)}" if time else ""}:ok_hand:')

        role = discord.utils.get(ctx.guild.roles, name='[Cr5] Muted')
        if not role:
            role = await ctx.guild.create_role(name='[Cr5] Muted',
                                               permissions=discord.Permissions(send_messages=False,
                                                                               add_reactions=False,
                                                                               speak=False),
                                               reason=f'Пользователь {member} замучен модератором {ctx.author}')
            await member.add_roles(role)
            for channel in ctx.guild.channels:
                await channel.set_permissions(role,
                                              send_messages=False,
                                              add_reactions=False,
                                              speak=False,
                                              reason=f'Пользователь {member} замучен модератором {ctx.author}')
        else:
            await member.add_roles(role, reason=f'[Замучен {ctx.author}] {reason or "Причина не установлена"}')


def setup(bot: commands.Bot):
    bot.add_cog(Moderation(bot))
