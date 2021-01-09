import asyncio


__all__ = ('CacheManager',)

class CachedObject:
    def __init__(self, name, loop):
        self._timeout = 60
        self._name = name
        self._loop = loop
        self._data = {}
    
    async def _waiter(self, name):
        await asyncio.sleep(self._timeout)
        del self._data[name]

    def insert(self, name, value = None):
        if name in self._data:
            return False
        self._data[name] = value
        self._loop.create_task(self._waiter(name))

    def get(self, name):
        return self._data.get(name)

    def update(self, name, value):
        if name in self._data:
            self._data[name] = value
    
    def resolve(self, timeout=None):
        self._timeout = timeout or self._timeout
        return self

class CacheManager:
    def __init__(self, loop):
        self._loop = loop
        self._cache = {}

    def resolve_object(self, name, timeout=60):
        if name not in self._cache:
            self._cache[name] = CachedObject(name, self._loop)

        return self._cache[name].resolve(timeout)
