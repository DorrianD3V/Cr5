import discord
from discord.ext import commands

from typing import Union


class Utils(commands.Cog, name='Утилиты'):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(name='idea',
                    usage='<текст>',
                    invoke_without_command=True)
    async def idea(self, ctx: commands.Context, *, text):
        """Предложить идею.
        
        Для того чтобы отредактировать свою идею восспользуйтесь `idea edit <ID> <текст>`
        
        Чтобы принять или отклонить идею, восспользуйтесь `idea accept/decline <ID> [комментарий]`
        Вы также можете добавить комментарий к идее, процитировав сообщение с идеей"""
        text = text.replace('[', '\\[') # remove masked links

        if len(text) > 1000:
            return await ctx.send(f'Максимальная длина идеи — **1000 символов**.')

        try:
            channel = await self.bot.db.execute('SELECT * FROM idea_channel WHERE guild_id=$1', [ctx.guild.id])
            if not channel:
                raise ValueError()

            channel = await self.bot.fetch_channel(channel['channel_id'])
            idea_id = await self.bot.db.utils.Counter.add(f'ideas_{ctx.guild.id}', 1)

            embed = discord.Embed(title=f'Предложение #{idea_id}',
                                  description=text)
            embed.set_footer(text=ctx.author.name, icon_url=ctx.author.avatar_url)

            if ctx.message.attachments:
                images = [x for x in ctx.message.attachments
                        if x.filename.split('.')[-1] in ('png', 'jpg', 'jpeg', 'gif')]
                if images:
                    embed.set_image(url=str(images[0].url))
                    if len(ctx.message.attachments) > 1:
                        embed.description += ('\n\n**Прикреплённые файлы**\n'
                                            + '\n'.join(f'[{x.filename}]({x.url})' for x in ctx.message.attachments
                                                        if x.filename != images[0].filename))
                else:
                    embed.description += ('\n\n**Прикреплённые файлы**\n'
                                        + '\n'.join(f'[{x.filename}]({x.url})' for x in ctx.message.attachments))

            message = await channel.send(embed=embed)

            await self.bot.db.execute('INSERT INTO ideas VALUES ($1, $2, $3, $4)',
                                      [ctx.guild.id, idea_id, message.id, ctx.author.id])

            await message.add_reaction('👍')
            await message.add_reaction('👎')

            if channel.id != ctx.channel.id:
                await ctx.send(embed=discord.Embed(description=f'**Ваша идея успешно отправлена в канал {channel.mention}**') \
                                            .add_field(name='Подсказка',
                                                       value='Если вы ошиблись, вы можете изменить идею с помощью команды '
                                                             '`idea edit <ID идеи> <новое содержание идеи>`'))
        except (discord.Forbidden, discord.NotFound, ValueError):
            return await ctx.send('Канал для идей не был установлен на этом сервере, '
                                  'или у меня нету прав отправлять туда сообщения. '
                                  'Установить канал для идей можно с помощью `idea channel <#канал>`.')

    @idea.command(name='channel',
                  usage='[канал/reset]')
    @commands.has_permissions(manage_guild=True)
    async def idea_channel(self, ctx: commands.Context,
                           channel: Union[discord.TextChannel, str] = None):
        """Изменить канал для предложений на этом сервере."""
        if not channel:
            channel = await self.bot.db.execute('SELECT * FROM idea_channel WHERE guild_id=$1', [ctx.guild.id])
            if not channel:
                await ctx.send('Канал для идей **не установлен** на этом сервере.')
            else:
                await ctx.send(f'Канал для идей на этом сервере: <#{channel["channel_id"]}>')
        
        else:
            if type(channel) != discord.TextChannel and channel != 'reset':
                raise commands.UserInputError()

            if channel == 'reset':
                deleted = await self.bot.db.execute('DELETE FROM idea_channel WHERE guild_id=$1 RETURNING *', [ctx.guild.id])
                if not deleted:
                    await ctx.send('Канал для идей **не установлен** на этом сервере.')
                else:
                    await ctx.send('Канал для идей успешно удалён. :ok_hand:')

            else:
                if not channel.permissions_for(ctx.guild.me).send_messages:
                    await ctx.send(f'У меня нету прав на **Отправление сообщений** в указанном вами канале.')
                
                else:
                    await self.bot.db.execute('INSERT INTO idea_channel VALUES ($1, $2) '
                                              'ON CONFLICT(guild_id) DO UPDATE '
                                              'SET channel_id = EXCLUDED.channel_id',
                                              [ctx.guild.id, channel.id])
                    await ctx.send(f'Канал для идей был успешно изменён на {channel.mention}. :ok_hand:')

    @idea.command(name='accept',
                  usage='<ID идеи> [комментарий]')
    @commands.has_permissions(manage_messages=True)
    async def accept(self, ctx: commands.Context, id: int, *, comment = None):
        """Принять идею"""
        channel = await self.bot.db.execute('SELECT * FROM idea_channel WHERE guild_id=$1', [ctx.guild.id])
        if not channel:
            return await ctx.send('На этом сервере не установлен канал для идей. '
                                  'Установить канал для идей можно с помощью `idea channel <#канал>`')
        
        idea = await self.bot.db.execute('SELECT * FROM ideas WHERE guild_id=$1 AND idea_id=$2', [ctx.guild.id, id])
        if not idea:
            return await ctx.send('Неизвестная идея. Убедитесь, что вы верно указали ID идеи.')
        
        try:
            channel = await self.bot.fetch_channel(channel['channel_id'])
            message = await channel.fetch_message(idea['message_id'])
        except discord.NotFound:
            return await ctx.send('Неизвесная идея. Убедитесь, что вы верно указали ID идеи.')

        embed = message.embeds[0]
        embed.title = f'Предложение #{id} (принято)'
        embed.color = discord.Colour.green().value
        embed.clear_fields()
        if comment:
            embed.add_field(name=f'Ответ от {ctx.author}:',
                            value=comment)

        await message.edit(embed=embed)
        await ctx.react('👌')

        try:
            user = await self.bot.fetch_user(idea['author_id'])
            await user.send(embed=discord.Embed(description=f'**[Ваша идея была принята]({message.jump_url})**',
                                                color=discord.Colour.green()) \
                                         .set_footer(text=ctx.guild.name,
                                                     icon_url=ctx.guild.icon_url))
        except (discord.Forbidden, discord.NotFound):
            pass

    @idea.command(name='edit',
                  usage='<ID идеи> <текст>')
    async def edit(self, ctx: commands.Context, id: int, *, text):
        """Отредактировать идею"""
        text = text.replace('[', '\\[') # remove masked links
        if len(text) > 1000:
            return await ctx.send('Максимальная длина идеи — **1000 символов.**')

        channel = await self.bot.db.execute('SELECT * FROM idea_channel WHERE guild_id=$1', [ctx.guild.id])
        if not channel:
            return await ctx.send('На этом сервере не установлен канал для идей. '
                                  'Установить канал для идей можно с помощью `idea channel <#канал>`')
        
        idea = await self.bot.db.execute('SELECT * FROM ideas WHERE guild_id=$1 AND idea_id=$2', [ctx.guild.id, id])
        if not idea:
            return await ctx.send('Неизвестная идея. Убедитесь, что вы верно указали ID идеи.')
        
        if idea['author_id'] != ctx.author.id:
            return await ctx.send('Только автор идеи может её отредактировать')

        try:
            channel = await self.bot.fetch_channel(channel['channel_id'])
            message = await channel.fetch_message(idea['message_id'])
        except discord.NotFound:
            return await ctx.send('Неизвесная идея. Убедитесь, что вы верно указали ID идеи.')

        embed = message.embeds[0]
        if embed.title != f'Предложение #{id}':
            return await ctx.send(f'Вы не можете отредактировать идею которая уже была принята или отклонена.')

        embed.description = text + ' (отредактировано автором)'
        embed._image = None
        if ctx.message.attachments:
            images = [x for x in ctx.message.attachments
                      if x.filename.split('.')[-1] in ('png', 'jpg', 'jpeg', 'gif')]
            if images:
                embed.set_image(url=str(images[0].url))
                if len(ctx.message.attachments) > 1:
                    embed.description += ('\n\n**Прикреплённые файлы**\n'
                                        + '\n'.join(f'[{x.filename}]({x.url})' for x in ctx.message.attachments
                                                    if x.filename != images[0].filename))
            else:
                embed.description += ('\n\n**Прикреплённые файлы**\n'
                                      + '\n'.join(f'[{x.filename}]({x.url})' for x in ctx.message.attachments))


        await message.edit(embed=embed)
        await ctx.react('👌')

    @idea.command(name='decline',
                  usage='<ID идеи> [комментарий]')
    @commands.has_permissions(manage_messages=True)
    async def decline(self, ctx: commands.Context, id: int, *, comment = None):
        """Отклонить идею"""
        channel = await self.bot.db.execute('SELECT * FROM idea_channel WHERE guild_id=$1', [ctx.guild.id])
        if not channel:
            return await ctx.send('На этом сервере не установлен канал для идей. '
                                  'Установить канал для идей можно с помощью `idea channel <#канал>`')
        
        idea = await self.bot.db.execute('SELECT * FROM ideas WHERE guild_id=$1 AND idea_id=$2', [ctx.guild.id, id])
        if not idea:
            return await ctx.send('Неизвестная идея. Убедитесь, что вы верно указали ID идеи.')
        
        try:
            channel = await self.bot.fetch_channel(channel['channel_id'])
            message = await channel.fetch_message(idea['message_id'])
        except discord.NotFound:
            return await ctx.send('Неизвесная идея. Убедитесь, что вы верно указали ID идеи.')

        embed = message.embeds[0]
        embed.title = f'Предложение #{id} (отказано)'
        embed.color = discord.Colour.red().value
        embed.clear_fields()
        if comment:
            embed.add_field(name=f'Ответ от {ctx.author}:',
                            value=comment)

        await message.edit(embed=embed)
        await ctx.react('👌')
    
        try:
            user = await self.bot.fetch_user(idea['author_id'])
            await user.send(embed=discord.Embed(description=f'**[Ваша идея была отказана]({message.jump_url})**',
                                                color=discord.Colour.red()) \
                                         .set_footer(text=ctx.guild.name,
                                                     icon_url=ctx.guild.icon_url))
        except (discord.Forbidden, discord.NotFound):
            pass

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.reference and message.guild and message.channel.permissions_for(message.author).manage_messages:
            message_id = message.reference.message_id
            idea = await self.bot.db.execute('SELECT * FROM ideas WHERE message_id=$1', [message_id])
            if not idea:
                return
            
            msg = await message.channel.fetch_message(message_id)
            embed = msg.embeds[0]
            embed.clear_fields()
            embed.add_field(name=f'Ответ от {message.author}:',
                            value=message.content)
            await msg.edit(embed=embed)

            try:
                user = await self.bot.fetch_user(idea['author_id'])
                await user.send(embed=discord.Embed(description=f'**[Модератор добавил комментарий на вашу идею]({msg.jump_url})**') \
                                            .set_footer(text=msg.guild.name,
                                                        icon_url=msg.guild.icon_url))
            except (discord.Forbidden, discord.NotFound):
                pass

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if not payload.guild_id or str(payload.emoji) not in ('✅', '❌'):
            return
        
        idea = await self.bot.db.execute('SELECT * FROM ideas WHERE message_id=$1', [payload.message_id])
        if not idea:
            return
        
        channel = await self.bot.fetch_channel(payload.channel_id)
        member = await channel.guild.fetch_member(payload.user_id)
        if not member.guild_permissions.manage_messages:
            return
        message = await channel.fetch_message(payload.message_id)
        embed = message.embeds[0]

        if str(payload.emoji) == '✅' and not embed.title.endswith('(принято)'):
            embed.title = f'Предложение #{idea["idea_id"]} (принято)'
            embed.color = discord.Colour.green().value
            try:
                user = await self.bot.fetch_user(idea['author_id'])
                await user.send(embed=discord.Embed(description=f'**[Ваша идея была принята]({message.jump_url})**',
                                                    color=discord.Colour.green()) \
                                            .set_footer(text=channel.guild.name,
                                                        icon_url=channel.guild.icon_url))
            except (discord.Forbidden, discord.NotFound):
                pass
        elif str(payload.emoji) == '❌' and not embed.title.endswith('(отказано)'):
            embed.title = f'Предложение #{idea["idea_id"]} (отказано)'
            embed.color = discord.Colour.red().value
            try:
                user = await self.bot.fetch_user(idea['author_id'])
                await user.send(embed=discord.Embed(description=f'**[Ваша идея была отказана]({message.jump_url})**',
                                                    color=discord.Colour.red()) \
                                            .set_footer(text=channel.guild.name,
                                                        icon_url=channel.guild.icon_url))
            except (discord.Forbidden, discord.NotFound):
                pass
        else:
            return
        
        await message.edit(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Utils(bot))