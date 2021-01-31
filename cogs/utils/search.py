import discord
from discord.ext import commands

from urllib.parse import quote


class Utils(commands.Cog, name='Утилиты'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.command(name='google',
                      usage='<запрос>')
    async def google(self, ctx: commands.Context, *, query):
        """Google Поиск"""
        cache = self.bot.cache.resolve_object('google', timeout=3600)
        if cache.get(hash(query)):
            return await ctx.send(embed=cache.get(hash(query)))

        if len(query) > 200:
            return await ctx.send('Максимальная длина запроса — **200 символов**.')
        url = (
            'https://www.googleapis.com/customsearch/v1'
            f'?key={self.bot.config.tokens["google_search"]}'
            f'&cx=e6702337c52c4f661'
            f'&q={quote(query)}'
            f'&safe={"off" if ctx.channel.nsfw else "active"}'
        )
        async with self.bot.session.get(url) as resp:
            embed = discord.Embed(title='Поиск в Google')
            embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/797593099169693707.png')
            if resp.status == 429:
                embed.add_field(name='Ошибка',
                                value='Достигнут ежедневный лимит в **100 запросов**, повторите запрос позже.')
                embed.color = discord.Colour.red().value
            elif resp.status != 200:
                embed.add_field(name='Ошибка',
                                value=f'Произошла неизвестная ошибка с кодом **{resp.status}**.\n'
                                      'Обратитесь к разработчикам бота на [сервере поддержки](https://discord.gg/rEpfsB9DUx) '
                                      'за помощью.')
                embed.color = discord.Colour.red().value
            else:
                data = await resp.json()
                embed.set_footer(text=f'Всего результатов: {data["searchInformation"]["formattedTotalResults"]} '
                                      f'({data["searchInformation"]["formattedSearchTime"]} сек)')
                
                embed.description = '\n\n'.join(
                    f"**[{result['title']}]({result['link']})**\n{result['snippet'][:200]}"
                    for result in data['items'][:5]
                )
                cache.insert(hash(query), embed)

            await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))