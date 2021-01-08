import discord
from discord.ext import commands

from pyowm import OWM
from pyowm.commons.exceptions import NotFoundError
from urllib.parse import quote

from typing import Union


class Utils(commands.Cog, name='Утилиты'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.owm = OWM(self.bot.config.tokens['OWM'])
        self.owm.config['language'] = 'ru'

        self.weather_mananger = self.owm.weather_manager()

    @commands.command(name='calculate',
                      aliases=['calc'],
                      usage='<математическое выражение>')
    async def calculate(self, ctx: commands.Context, *, expression):
        """Тригонометрический калькулятор с возможностью переводить одни еденицы измерения в другие
        
        **Примеры:**
        `calc sin(2)*cos(5)`
        `calc sqrt(10)/-2`
        `calc 5 kilobytes in bytes`
        `calc 0.58 km in meters`"""
        async with self.bot.session.get(f'https://api.mathjs.org/v4/?expr={quote(expression)}') as resp:
            res = await resp.text()
            res = res.replace('`', '\u200b`\u200b')[:500]

            await ctx.send(embed=discord.Embed(title='Калькулятор') \
                                        .add_field(name='Результат:',
                                                   value=res) \
                                        .set_thumbnail(url='https://cdn.discordapp.com/emojis/796686124684279839.png') \
                                        .set_footer(text='Powered by MathJS API: https://api.mathjs.org/'))

    @commands.command(name='weather',
                      usage='<город>')
    async def weather(self, ctx: commands.Context, *, city):
        """Узнать погоду в определённом городе/посёлке/стране."""
        try:
            observation = self.weather_mananger.weather_at_place(city)
            weather = observation.weather
        except NotFoundError:
            return await ctx.send(f'Неизвестный город. Убедитесь, что указанный город существует и правильно написан.')
        
        embed = discord.Embed(title=f'Погода в {observation.location.name}',
                              description=weather.detailed_status.capitalize())
        embed.set_thumbnail(url=weather.weather_icon_url())

        temperature = weather.temperature('celsius')
        wind = weather.wind('km_hour')

        embed.add_field(name='Температура',
                        value=f'Температура сейчас: **{temperature["temp"]}°C**\n'
                              f'Ощущается как: **{temperature["feels_like"]}°C**\n'
                              f'Средняя температура: **{(temperature["temp_min"]+temperature["temp_max"])/2}°C** '
                              f'(от **{temperature["temp_min"]}°C** до **{temperature["temp_max"]}°C**)')

        embed.add_field(name='Ветер',
                        value=f'Скорость: **{wind["speed"]} км/ч**\n'
                              f'Направление: **{wind["deg"]}°**')
            
        embed.add_field(name='Влажность',
                        value=f'{weather.humidity}%')
        
        embed.add_field(name='Время рассвета',
                        value=weather.sunrise_time('date').strftime('%H:%M'))
        
        embed.add_field(name='Время захода',
                        value=weather.sunset_time('date').strftime('%H:%M'))

        embed.add_field(name='\u200b', value='\u200b')

        embed.set_footer(text=f'Последнее обновление')
        embed.timestamp = weather.reference_time('date')

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))