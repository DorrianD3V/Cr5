import asyncpg
import os

from ext import Logger
from ext.db_utils import DatabaseUtils


class Database:
    def __init__(self, config):
        self.connection: asyncpg.Pool = None
        self._config = config
        self.utils = DatabaseUtils(self)

    async def connect(self):
        if self.connection and not self.connection._closed:
            return
        Logger.debug(f'Connecting to database...')
        self.connection = await asyncpg.create_pool(self._config['url'])
        Logger.info(f'Connected to database')
    
    async def execute(self, query, params = [], as_dict = True):
        if not self.connection or self.connection._closed:
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

