import discord
import traceback
from discord.ext import commands
from jishaku.modules import resolve_extensions

from ext import Logger
from .database import Database
from .context import Context

from aiohttp import ClientSession


class Bot(commands.AutoShardedBot):
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.db = Database(self.config.database)
        self.session = ClientSession(loop=self.loop)
    
    async def get_context(self, message, *, cls=None):
        return await super().get_context(message, cls=Context)

    async def on_ready(self):
        Logger.info('Ready')

    async def on_connect(self):
        Logger.info(f'Connected to Discord API as {self.user} ({self.user.id})')
        await self.db.connect()
        await self.change_presence(activity=self.config.activity)

    def load_extensions(self):
        for extension in self.config.extensions:
            extensions = resolve_extensions(self, extension)
            for extension in extensions:
                try:
                    self.load_extension(extension)
                except:
                    Logger.error(f'Error in extension {extension}\n' +
                                traceback.format_exc())
                else:
                    Logger.debug(f'Loaded extension {extension}')

    def run(self):
        Logger.debug('Starting...')
        self.load_extensions()
        super().run(self.config.token)

