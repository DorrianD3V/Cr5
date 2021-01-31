import discord
from discord.ext import commands

from urllib.parse import quote
from humanize import naturaldelta


class Utils(commands.Cog, name='Утилиты'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name='skin',
                      usage='<ник или UUID игрока>')
    async def skin(self, ctx: commands.Context, player):
        """Получить скин Minecraft-игрока"""
        async with self.bot.session.get(f'https://mc-heads.net/minecraft/profile/{player}') as resp:
            if resp.status != 200:
                await ctx.send('Неизвестный игрок. Убедитесь, что вы ввели корректный никнейм или UUID.')
            else:
                await ctx.send(embed=discord.Embed() \
                                            .set_author(name=f'Скин игрока {player}',
                                                        icon_url=f'https://mc-heads.net/avatar/{player}') \
                                            .set_image(url=f'https://mc-heads.net/body/{player}'))

    @commands.command(name='osu!',
                      aliases=['osu'],
                      usage='<ник игрока>')
    async def osu(self, ctx: commands.Context, player):
        """Получить информацию про osu!-игрока"""
        async with self.bot.session.get('https://osu.ppy.sh/api/get_user'
                                        f'?k={self.bot.config.tokens["osu!"]}'
                                        f'&u={quote(player)}') as resp:
            data = await resp.json()
            if not data:
                return await ctx.send(f'Неизвестный игрок.')
            data = data[0]

            embed = discord.Embed(title=data['username'])

            embed.description = (
                f'**{int(data.get("count_rank_ss", 0)) + int(data.get("count_rank_ssh", 0))} <:osu_rank_x:797788644239867934> | '
                f'{int(data.get("count_rank_s", 0)) + int(data.get("count_rank_sh", 0))} <:osu_rank_s:797788644173414420> | '
                f'{data.get("count_rank_a", 0)} <:osu_rank_a:797788644047978556>**'
            )
            
            embed.set_thumbnail(url=f'https://a.ppy.sh/{data["user_id"]}')

            embed.add_field(name='Счёт',
                            value=f'Всего: {data.get("total_score", 0)}\n'
                                  f'Ранговый: {data.get("ranked_score", 0)}')

            embed.add_field(name='Игр сыграно',
                            value=f'{data.get("playcount", "0")}')

            embed.add_field(name='Времени сыграно',
                            value=naturaldelta(int(data.get("total_seconds_played", "0"))))

            embed.add_field(name='Страна',
                            value=f'{data.get("country", "Unknown")}')

            embed.add_field(name='Ранг страны',
                            value=f'{data.get("pp_country_rank", "Unknown")}')

            embed.add_field(name='Ранг',
                            value=f'{data.get("pp_rank", "Unknown")}')

            embed.add_field(name='PP',
                            value=f'{round(float(data.get("pp_raw", 0)))}')

            embed.add_field(name='Аккуратность',
                            value=f'{round(float(data.get("accuracy", 0)))}%')
                
            embed.add_field(name='Зарегистрирован',
                            value=data.get('join_date', "Unknown"))

            await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))
