import discord
from discord.ext import commands

from hashlib import shake_128

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

        if isinstance(error, commands.CommandNotFound):
            return
        
        elif isinstance(error, commands.NotOwner):
            return await ctx.send(embed=self.error_message('Отсувствуют нужные права',
                                                           'Вы должны быть **разработчиком бота**, чтобы выполнить эту команду.'))

        elif isinstance(error, commands.BotMissingPermissions):
            perms = [f'— **{PERMISSIONS[perm]}**' for perm in error.missing_perms]
            return await ctx.send(embed=self.error_message('Отсувствуют нужные права',
                                                           'Бот должен иметь следующие права, чтобы выполнить эту команду:\n' +
                                                           '\n'.join(perms)))

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


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))
