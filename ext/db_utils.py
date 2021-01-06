
class Counter:
    def __init__(self, db):
        self.db = db
    
    async def get(self, name):
        value = await self.db.execute('SELECT * FROM counters WHERE name = $1', [name])
        if not value:
            return 0
        return value['value']
    
    async def set(self, name, value):
        return (await self.db.execute('INSERT INTO counters VALUES ($1, $2) '
                                      'ON CONFLICT(name) DO UPDATE SET value = $2 RETURNING *', [name, value]))['value']
    
    async def add(self, name, value):
        return await self.set(name, await self.get(name) + value)
    
    async def sub(self, name, value):
        return await self.set(name, await self.get(name) - value)
    

class DatabaseUtils:
    def __init__(self, db):
        self.Counter = Counter(db)
