import discord
from discord.ext import commands

from traceback import format_exception
from hashlib import shake_128

from humanize import precisedelta

from cogs.help import HelpCommand


PERMISSIONS = {
    'create_instant_invite': 'Создавать приглашения',
    'kick_members': 'Выгонять пользователей',
    'ban_members': 'Банить пользователей',
    'administrator': 'Администратор',
    'manage_channels': 'Управлять каналами',
    'manage_guild': 'Управлять сервером',
    'add_reactions': 'Добавлять реакции',
    'view_audit_log': 'Просматривать журнал аудита',
    'manage_messages': 'Управлять сообщениями',
    'embed_links': 'Прикреплять ссылки',
    'attach_files': 'Прикреплять файлы',
    'read_message_history': 'Читать историю сообщений',
    'mention_everyone': 'Упоминать всех',
    'external_emojis': 'Использовать внешние эмодзи',
    'connect': 'Подключаться к голосовым каналам',
    'speak': 'Говорить в голосовых каналах',
    'move_members': 'Перемещять пользователей',
    'change_nickname': 'Изменять никйнейм',
    'manage_nicknames': 'Управлять никнеймами',
    'manage_roles': 'Управлять ролями',
    'manage_webhooks': 'Управлять вебхуками',
    'manage_emojis': 'Управлять эмодзи'
}

GIFS = {
    'kick_members': 'https://cdn.discordapp.com/attachments/797478058679599114/799317288850554951/kq80tI8dIn.gif',
    'ban_members': 'https://cdn.discordapp.com/attachments/797478058679599114/799317288040792104/mHPGYwEz2p.gif',
    'manage_messages': 'https://cdn.discordapp.com/attachments/797478058679599114/799317289946185809/cpSPaPBLSx.gif'
}


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def error_message(self, name, content):
        return discord.Embed(description=content,
                             color=discord.Colour(0xe74c3c)) \
                      .set_thumbnail(url=self.bot.user.avatar_url) \
                      .set_footer(text=f'Код ошибки: {shake_128(bytes(name + content, "utf8")).hexdigest(5)}') \
                      .set_author(name=name,
                                  icon_url='https://cdn.discordapp.com/emojis/796048425115844658.png')

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        error = getattr(error, 'original', error)

        if not isinstance(error, commands.CommandOnCooldown):
            ctx.command.reset_cooldown(ctx)

        if isinstance(error, commands.CommandNotFound):
            return
        
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=self.error_message('Отсувствуют нужные права',
                                                           'Вы должны быть **разработчиком бота**, чтобы выполнить эту команду.'))

        elif isinstance(error, commands.BotMissingPermissions):
            perms = [f'— **{PERMISSIONS[perm]}**' for perm in error.missing_perms]
            embed = self.error_message('Отсувствуют нужные права',
                                       'Бот должен иметь следующие права, чтобы выполнить эту команду:\n' +
                                       '\n'.join(perms))

            if error.missing_perms[0] in GIFS:
                embed.add_field(name=f'Пожалуйста, выдайте мне право "{PERMISSIONS[error.missing_perms[0]]}", '
                                      'чтобы я мог выполнить эту команду.',
                                value=f'`Настройки сервера` > `Роли` > {ctx.guild.me.top_role.mention} > '
                                      f'`"{PERMISSIONS[error.missing_perms[0]]}"`')
                embed.set_image(url=GIFS[error.missing_perms[0]])

            return await ctx.send(embed=embed)

        elif isinstance(error, commands.MissingPermissions):
            perms = [f'— **{PERMISSIONS[perm]}**' for perm in error.missing_perms]
            return await ctx.send(embed=self.error_message('Отсувствуют нужные права',
                                                           'Вы должны иметь следующие права, чтобы выполнить эту команду:\n' +
                                                           '\n'.join(perms)))

        elif isinstance(error, (commands.BadArgument, commands.UserInputError,
                                commands.MissingRequiredArgument)):
            return await ctx.send(f'<:cr5_error:796048425115844658> Вы ввели некорректные аргументы. '
                                  f'Справка по команде `{ctx.command}`:',
                                  embed=await HelpCommand(ctx).command_help(ctx.command))

        elif isinstance(error, commands.CommandOnCooldown):
            return await ctx.send(embed=self.error_message('Команда использует задержку',
                                                           'Данная команда использует задержку. '
                                                           f'Пожалуйста, повторите позже через {precisedelta(error.retry_after)}.'))

        else:
            exception = "\n".join(format_exception(type(error), error, error.__traceback__, 5, False))
            await ctx.send(embed=self.error_message('Произошла ошибка при выполнении этой команды.',
                                                    f'```py\n{exception[:1950]}\n```\n\n'
                                                    'Обратитесь к разработчикам бота на [сервере поддержки](https://discord.gg/gEHSVK5779), '
                                                    'если вы считаете, что эта ошибка должна быть исправлена.'))
            channel = await self.bot.fetch_channel(self.bot.config.channels['exceptions'])
            await channel.send(exception[:2000])


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
