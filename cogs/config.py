import discord
from discord.ext import commands


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name='prefix',
                    invoke_without_command=True)
    async def prefix(self, ctx: commands.Context):
        """Узнать префикс бота.
        
        Используйте `prefix set <префикс>` чтобы изменить префикс и `prefix reset` чтобы сбросить префикс"""
        prefixes = await self.bot.get_prefix(ctx.message)
        embed = discord.Embed(title='Префикс',
                              description=f'Текущий префикс бота на сервере: **{prefixes[-1]}**') \
                       .set_footer(text='Вы также можете использовать @упоминание как префикс бота')
        
        if ctx.author.guild_permissions.manage_guild:
            embed.add_field(name='Справка',
                            value='Вы можете изменить префикс бота на сервере с помощью `prefix set <префикс>`, '
                                  'или сбросить его с помощью `prefix reset`')

        await ctx.send(embed=embed)

    @prefix.command(name='set',
                    usage='<префикс>')
    @commands.has_permissions(manage_guild=True)
    async def set_prefix(self, ctx: commands.Context, *, prefix):
        """Изменить префикс бота на сервере."""
        if len(prefix) > 15:
            return await ctx.send(f'Максимальная длина префикса — **15 символов**.')
        
        await self.bot.db.execute('INSERT INTO prefixes VALUES ($1, $2) '
                                  'ON CONFLICT(guild_id) DO UPDATE SET prefix = EXCLUDED.prefix',
                                  [ctx.guild.id, prefix])
        await ctx.send('Префикс бота был успешно изменён на этом сервере :ok_hand:')

    @prefix.command(name='reset')
    @commands.has_permissions(manage_guild=True)
    async def reset_prefix(self, ctx: commands.Context):
        """Сбросить префикс бота на сервере."""
        await self.bot.db.execute('DELETE FROM prefixes WHERE guild_id=$1', [ctx.guild.id])
        await ctx.send('Префикс бота был успешно сброшен на этом сервере :ok_hand:')


def setup(bot: commands.Bot):
    bot.add_cog(Config(bot))
