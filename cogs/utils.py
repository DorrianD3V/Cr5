import discord
from discord.ext import commands

from urllib.parse import quote


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

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
                                        .set_thumbnail(url='https://cdn.discordapp.com/emojis/796686124684279839.png'))


def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))