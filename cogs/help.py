import discord
from discord.ext import commands
from ext.paginator import Paginator


class HelpCommand:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.bot = ctx.bot
        self.author = ctx.author

    def base_embed(self, **kwargs):
        return discord.Embed(color=discord.Colour(0x6965A7), **kwargs) \
                      .set_author(name=f'{self.bot.user.name}: Справка',
                                  icon_url=self.bot.user.avatar_url) \
                      .set_thumbnail(url=self.bot.user.avatar_url_as(size=2048))

    async def can_run(self, check):
        try:
            c = check(self.ctx)
            if type(c).__name__ == 'coroutine':
                c = await c
        except:
            return False
        else:
            return c

    async def get_cogs(self):
        cogs = []
        for cog in self.bot.cogs.values():
            if await self.can_run(cog.cog_check):
                cogs.append(cog)
        return cogs
    
    async def get_cog_commands(self, cog):
        commands = []
        for command in self.bot.commands:
            if command.cog_name == cog.__cog_name__ and not command.hidden and await self.can_run(command.can_run):
                commands.append(command)
        return commands
    
    async def cog_help(self, cog):
        commands = await self.get_cog_commands(cog)
        if not commands:
            return None
        return self.base_embed(title=cog.__cog_name__,
                               description=cog.__doc__ or "") \
                    .add_field(name='Команды',
                               value=', '.join(f'`{x.qualified_name}`' for x in commands))
        
    async def command_help(self, command):
        embed = self.base_embed(description=f'```{self.ctx.prefix}{command.qualified_name} {command.usage or command.signature}```\n' +
                                            (command.help or ""))

        if len(command.aliases) > 0:
            embed.add_field(name='Псевдонимы',
                            value='\n'.join(f'`{x}`' for x in command.aliases))

        if command.cog:
            embed.add_field(name='Категория',
                            value=command.cog_name)

        if hasattr(command, 'commands'):
            embed.add_field(name='Под-команды',
                            value=', '.join(f'`{x.name}`' for x in command.commands),
                            inline=False)

        return embed


@commands.command(name='help',
                    usage='help [команда]')
async def help_command(ctx: commands.Context, *, command = None):
    """Справка по командам"""
    help_command = HelpCommand(ctx)
    if not command:
        paginator = Paginator(ctx)
        for cog in await help_command.get_cogs():
            info = await help_command.cog_help(cog)
            if info:
                paginator.pages.append(info)

        [x.set_footer(text=f'Страница {n+1}/{len(paginator.pages)}'
                            f' • примечание: показаны только те команды, которые вы можете выполнить')                
            for n, x in enumerate(paginator.pages)]
        
        await paginator.start()
    
    else:
        cmd = ctx.bot.get_command(command)

        if not cmd:
            return await ctx.send(f'Неизвестная команда.')

        await ctx.send(embed=await help_command.command_help(cmd))


def setup(bot: commands.Bot):
    bot.add_command(help_command)
