import asyncpg
import os

from traceback import format_exc

from ext import Logger
from ext.db_utils import DatabaseUtils


class Database:
    def __init__(self, config):
        self.connection = None
        self._config = config
        self.utils = DatabaseUtils(self)

    async def connect(self):
        if self.connection:
            return
        Logger.debug(f'Connecting to database...')
        self.connection = await asyncpg.create_pool(self._config['url'])
        Logger.info(f'Connected to database')

    async def setup(self, file='setup.psql'):
        Logger.debug('Initializing database...')
        with open(file, mode='r', encoding='utf-8') as file:
            for line in file.readlines():
                await self.execute(line)
        Logger.info('Database initialized')

    async def execute(self, query, params=[], as_dict=True):
        if not self.connection:
            await self.connect()

        async with self.connection.acquire() as conn:
            output = await conn.fetch(query, *params)
            await self.connection.release(conn)
        
        if len(output) == 1 and as_dict:
            return output[0]
        
        else:
            return output

    def dump(self, filename):
        os.system(f'pg_dump {self._config["url"]} > {filename}')
        Logger.debug(f'Dumped database to {filename}')

