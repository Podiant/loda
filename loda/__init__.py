from .storage.engines.locmem import LocalMemoryEngine as locmem
from .storage.engines.disk import FileSystemEngine as disk
from .storage.engines.redis import RedisEngine as redis


__version__ = '0.1'
__all__ = [
    '__version__',
    'disk',
    'locmem',
    'redis'
]
