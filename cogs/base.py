import discord
from discord.ext import commands

from typing import Union
from socket import gethostbyname
from urllib.parse import urlparse

import datetime
import time

import humanize
import humanize.i18n

import re
import aiohttp

import platform
import psutil


humanize.i18n.activate('ru_RU')

class Base(commands.Cog, name='Основное'):
    """Все основные команды бота."""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx: commands.Context):
        """Получить пинг бота"""

        data = {}

        start = datetime.datetime.now()
        m = await ctx.send('Получение информации...')
        end = datetime.datetime.now()
        
        data['Вебсокет'] = f'{round(self.bot.latency*1000, 2)} ms'
        data['HTTP'] = f'{round((end - start).total_seconds() * 1000, 2)} ms'

        async with self.bot.session.get('https://discordstatus.com/api/v2/status.json') as resp:
            data['Статус Discord-a'] = (await resp.json())['status']['description']
        async with self.bot.session.get('https://discordstatus.com/metrics-display/ztt4777v23lf/day.json') as resp:
            data['Задержка API'] = f'{(await resp.json())["summary"]["last"]} ms'

        embed = discord.Embed(title='Пинг бота') \
                       .set_author(name=self.bot.user.name,
                                   icon_url=self.bot.user.avatar_url)

        embed.description = '\n'.join(f'**{k}:** {v}' for k, v in data.items())

        await m.edit(content=None,
                     embed=embed)

    @commands.command(name='lookup',
                      aliases=['info'],
                      usage='<пользователь, роль, приглашение на сервер и т.д.>')
    async def lookup(self, ctx: commands.Context, *,
                     arg: Union[discord.Member, discord.Role,
                                discord.User, discord.TextChannel,
                                discord.CategoryChannel, discord.VoiceChannel,
                                discord.Emoji, discord.Invite]):
        """С помощью этой команды вы сможете получить информацию о пользователе, роли, канале, приглашении и эмодзи."""
        
        if type(arg) != discord.Invite:
            embed = discord.Embed(title=arg.name)

        if type(arg) in (discord.Member, discord.User):
            embed.set_thumbnail(url=arg.avatar_url)
            embed.add_field(name='Создан', value=f'{humanize.naturaldate(arg.created_at)} ({humanize.naturaldelta(arg.created_at)} назад)')
            embed.add_field(name='ID', value=str(arg.id))
            embed.add_field(name='Бот?', value='Да' if arg.bot else 'Нет')

        if type(arg) == discord.Member:
            embed.add_field(name='Присоединился', value=f'{humanize.naturaldate(arg.joined_at)} ({humanize.naturaldelta(arg.joined_at)} назад)')
            embed.add_field(name='Цвет никнейма', value=str(arg.color))
            embed.add_field(name='\u200b', value='\u200b')
            embed.color = arg.color.value

        if type(arg) == discord.Role:
            embed.add_field(name='Цвет', value=str(arg.color))
            embed.add_field(name='Упоминаемая?', value='Да' if arg.mentionable else 'Нет')
            embed.add_field(name='Отдельная?', value='Да' if arg.hoist else 'Нет')
            embed.add_field(name='Позиция', value=str(arg.position))
            embed.add_field(name='Пользователей с этой ролью', value=str(len(arg.members)))
            embed.add_field(name='Создан', value=f'{humanize.naturaldate(arg.created_at)}')
            embed.add_field(name='ID', value=str(arg.id))
            embed.color = arg.color.value

        if type(arg) == discord.VoiceChannel:
            embed.add_field(name='Битрейт', value=f'{arg.bitrate} кБит')
            embed.add_field(name='Лимит пользователей', value=str(arg.user_limit))
            embed.add_field(name='Создан', value=f'{humanize.naturaldate(arg.created_at)}')
            embed.add_field(name='Позиция', value=str(arg.position))
            embed.add_field(name='ID', value=str(arg.id))
            embed.add_field(name='\u200b', value='\u200b')
        
        if type(arg) == discord.TextChannel:
            embed.add_field(name='Создан', value=f'{humanize.naturaldate(arg.created_at)}')
            embed.add_field(name='NSFW?', value='Да' if arg.nsfw else 'Нет')
            embed.add_field(name='Позиция', value=str(arg.position))
            embed.add_field(name='Задержка', value=f'{arg.slowmode_delay} секунд')
            embed.add_field(name='ID', value=str(arg.id))
            embed.add_field(name='\u200b', value='\u200b')
        
        if type(arg) == discord.CategoryChannel:
            embed.add_field(name='Создан', value=f'{humanize.naturaldate(arg.created_at)}')
            embed.add_field(name='Каналов', value=f'{len(arg.channels)}')
            embed.add_field(name='Позиция', value=str(arg.position))
            embed.add_field(name='ID', value=str(arg.id))

        if type(arg) == discord.Emoji:
            embed.add_field(name='Создан', value=f'{humanize.naturaldate(arg.created_at)}')
            embed.add_field(name='Raw', value=f'\\{arg}')
            embed.add_field(name='ID', value=str(arg.id), inline=False)
            embed.set_thumbnail(url=arg.url)
        
        if type(arg) == discord.Invite:
            embed = discord.Embed(title=arg.guild.name)
            embed.set_thumbnail(url=arg.guild.icon_url)
            embed.add_field(name='Пользователей', value=str(arg.approximate_member_count))
            embed.add_field(name='Пользователей в сети', value=str(arg.approximate_presence_count))
            embed.add_field(name='Пригласивший', value=f'{arg.inviter or "Unknown#0000"}')
            embed.add_field(name='Канал', value=f'{arg.channel}')

        await ctx.send(embed=embed)

    @commands.command(name='statistic', aliases=['stats'])
    async def stats(self, ctx: commands.Context):
        """Статистика бота."""

        embed = discord.Embed() \
                       .set_author(name='Статистика бота',
                                   icon_url=self.bot.user.avatar_url) \
                       .set_footer(text=f'Пинг: {round(self.bot.latency*1000, 2)}ms')
        
        embed.add_field(name='Библиотеки',
                        value=f'[Python](https://python.org) {platform.python_version()}\n'
                              f'[discord.py](https://pypi.org/project/discord.py/) {discord.__version__}\n')

        memory = psutil.virtual_memory()
        embed.add_field(name='ОЗУ',
                        value=f'{humanize.naturalsize(memory.used)}/{humanize.naturalsize(memory.total)}')
        
        embed.add_field(name='Процессор',
                        value=f'{psutil.cpu_percent()}%')
            
        embed.add_field(name='Серверов',
                        value=str(len(self.bot.guilds)))

        embed.add_field(name='Пользователей',
                        value=sum([x.member_count for x in self.bot.guilds]))

        embed.add_field(name='Эмодзи',
                        value=len(self.bot.emojis))

        await ctx.send(embed=embed)

    @commands.command(name='bug')
    async def bug(self, ctx: commands.Context, *, text):
        """Нашли ошибку в боте? Сообщите нам о ней через эту команду!"""
        if len(text) < 10 or len(text) > 255:
            return await ctx.send(f'Длина бага должна быть от 10 до 255 символов.')

        channel = await self.bot.fetch_channel(self.bot.config.channels['bugs'])
        bug_id = await self.bot.db.utils.Counter.add('bugs', 1)

        await channel.send(embed=discord.Embed(title=f'Баг #{bug_id}',
                                               description=text) \
                                        .set_footer(text=ctx.author.name,
                                                    icon_url=ctx.author.avatar_url))

        await ctx.send(embed=discord.Embed(title='Ваш баг был успешно отправлен. Спасибо вам за желание нам помочь!',
                                           description='Рекомендуем вам зайти на [сервер поддержки](https://discord.gg/rEpfsB9DUx).'))

    @commands.command(name='about')
    async def about(self, ctx: commands.Context):
        """Информация про бота"""
        embed = discord.Embed() \
                       .set_author(name='Про Cr5',
                                   icon_url=self.bot.user.avatar_url)

        embed.description = ("**Cr5** — многофункциональный дискорд-бот для вашего сервера, который поможет"
                             " вам сделать ваш сервер в разы лучше, комфортнее и уникальнее!\n\n"
                             
                             "Cr5 может много чего, начиная от простых команд позволяющих получить информацию о"
                             " пользователе или роли, заканчивая очень полезными утилитами по типу умного калькулятора,"
                             " прогноза погоды и много-много другого!\n\n"
                             
                             "Сейчас Cr5 находится в стадии раней разработки, но он всё время дорабатывается и улучшается,"
                             " становясь всё лучше и лучше.")

        embed.add_field(name='Ссылки',
                        value='[Добавить бота](https://discord.com/oauth2/authorize?client_id=795289995199381514&permissions=8&scope=bot)\n'
                              '[GitHub](https://github.com/DorrianD3V/Cr5)\n'
                              '[Сервер поддержки](https://discord.gg/rEpfsB9DUx)')

        embed.add_field(name='\u200b',
                        value='\u200b')

        embed.add_field(name='Статистика',
                        value=f'Серверов: **{len(self.bot.guilds)}**\n'
                              f'Команд: **{len(self.bot.commands)}**\n'
                              f'Пользователей: **{sum(x.member_count for x in self.bot.guilds)}**\n'
                              f'Каналов: **{sum(len(x.channels) for x in self.bot.guilds)}**')

        await ctx.send(embed=embed)

    @commands.command(name='invite',
                      usage='[бот]')
    async def invite(self, ctx: commands.Context, bot: discord.User = None):
        """Получить ссылку-приглашение на бота.
        Также, вы можете указать другого бота, чтобы получить ссылку-приглашение на него."""
        if (bot and not bot.bot) or not bot:
            bot = self.bot.user

        embed = discord.Embed(title=f'Пригласить {bot}')
        embed.set_thumbnail(url=bot.avatar_url)
        embed.description = (f'**[Со всеми правами]({discord.utils.oauth_url(bot.id, permissions=discord.Permissions(8))})**\n'
                             'Бот создаст свою роль, которая будет иметь все права.\n\n'
                             f'**[Без прав]({discord.utils.oauth_url(bot.id)})**\n'
                             'Бот не будет создавать свою роль, и будет иметь только те права, которые есть у '
                             'роли @everyone\n\n'
                             f'**[Настроить]({discord.utils.oauth_url(bot.id, permissions=discord.Permissions(-1))})**\n'
                             'Вы можете выбрать специальные права, которые бот будет иметь.')
        
        if bot.id == self.bot.user.id:
            embed.add_field(name='\u200b\nДоп. ссылки',
                            value=f'**[GitHub](https://github.com/DorrianD3V/Cr5)**\n'
                                  'GitHub-репозиторий с исходным кодом бота\n\n'
                                  f'**[Сервер поддержки](https://discord.gg/rEpfsB9DUx)**\n'
                                  'На сервере поддержки вы можете получить помощь по боту')

        await ctx.send(embed=embed)
 

def setup(bot: commands.Bot):
    bot.add_cog(Base(bot))
