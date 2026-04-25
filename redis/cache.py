from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Optional, Union

from redis.observability.attributes import CSCReason


class CacheEntryStatus(Enum):
    VALID = "VALID"
    IN_PROGRESS = "IN_PROGRESS"


class EvictionPolicyType(Enum):
    time_based = "time_based"
    frequency_based = "frequency_based"


@dataclass(frozen=True)
class CacheKey:
    """
    Represents a unique key for a cache entry.

    Attributes:
        command (str): The Redis command being cached.
        redis_keys (tuple): The Redis keys involved in the command.
        redis_args (tuple): Additional arguments for the Redis command.
            This field is included in the cache key to ensure uniqueness
            when commands have the same keys but different arguments.
            Changing this field will affect cache key uniqueness.
    """

    command: str
    redis_keys: tuple
    redis_args: tuple = ()  # Additional arguments for the Redis command; affects cache key uniqueness.


class CacheEntry:
    def __init__(
        self,
        cache_key: CacheKey,
        cache_value: bytes,
        status: CacheEntryStatus,
        connection_ref,
    ):
        self.cache_key = cache_key
        self.cache_value = cache_value
        self.status = status
        self.connection_ref = connection_ref

    def __hash__(self):
        return hash(
            (self.cache_key, self.cache_value, self.status, self.connection_ref)
        )

    def __eq__(self, other):
        return hash(self) == hash(other)


class EvictionPolicyInterface(ABC):
    @property
    @abstractmethod
    def cache(self):
        pass

    @cache.setter
    @abstractmethod
    def cache(self, value):
        pass

    @property
    @abstractmethod
    def type(self) -> EvictionPolicyType:
        pass

    @abstractmethod
    def evict_next(self) -> CacheKey:
        pass

    @abstractmethod
    def evict_many(self, count: int) -> List[CacheKey]:
        pass

    @abstractmethod
    def touch(self, cache_key: CacheKey) -> None:
        pass


class CacheConfigurationInterface(ABC):
    @abstractmethod
    def get_cache_class(self):
        pass

    @abstractmethod
    def get_max_size(self) -> int:
        pass

    @abstractmethod
    def get_eviction_policy(self):
        pass

    @abstractmethod
    def is_exceeds_max_size(self, count: int) -> bool:
        pass

    @abstractmethod
    def is_allowed_to_cache(self, command: str) -> bool:
        pass


class CacheInterface(ABC):
    @property
    @abstractmethod
    def collection(self) -> OrderedDict:
        pass

    @property
    @abstractmethod
    def config(self) -> CacheConfigurationInterface:
        pass

    @property
    @abstractmethod
    def eviction_policy(self) -> EvictionPolicyInterface:
        pass

    @property
    @abstractmethod
    def size(self) -> int:
        pass

    @abstractmethod
    def get(self, key: CacheKey) -> Union[CacheEntry, None]:
        pass

    @abstractmethod
    def set(self, entry: CacheEntry) -> bool:
        pass

    @abstractmethod
    def delete_by_cache_keys(self, cache_keys: List[CacheKey]) -> List[bool]:
        pass

    @abstractmethod
    def delete_by_redis_keys(self, redis_keys: List[bytes]) -> List[bool]:
        pass

    @abstractmethod
    def flush(self) -> int:
        pass

    @abstractmethod
    def is_cachable(self, key: CacheKey) -> bool:
        pass


class DefaultCache(CacheInterface):
    def __init__(
        self,
        cache_config: CacheConfigurationInterface,
    ) -> None:
        self._cache = OrderedDict()
        self._cache_config = cache_config
        self._eviction_policy = self._cache_config.get_eviction_policy().value()
        self._eviction_policy.cache = self

    @property
    def collection(self) -> OrderedDict:
        pass

    @property
    def config(self) -> CacheConfigurationInterface:
        pass

    @property
    def eviction_policy(self) -> EvictionPolicyInterface:
        pass

    @property
    def size(self) -> int:
        pass

    def set(self, entry: CacheEntry) -> bool:
        pass

    def get(self, key: CacheKey) -> Union[CacheEntry, None]:
        entry = self._cache.get(key, None)

        if entry is None:
            return None

        self._eviction_policy.touch(key)
        return entry

    def delete_by_cache_keys(self, cache_keys: List[CacheKey]) -> List[bool]:
        response = []

        for key in cache_keys:
            if self.get(key) is not None:
                self._cache.pop(key)
                response.append(True)
            else:
                response.append(False)

        return response

    def delete_by_redis_keys(
        self, redis_keys: Union[List[bytes], List[str]]
    ) -> List[bool]:
        pass

    def flush(self) -> int:
        elem_count = len(self._cache)
        self._cache.clear()
        return elem_count

    def is_cachable(self, key: CacheKey) -> bool:
        return self._cache_config.is_allowed_to_cache(key.command)


class CacheProxy(CacheInterface):
    """
    Proxy object that wraps cache implementations to enable additional logic on top
    """

    def __init__(self, cache: CacheInterface):
        self._cache = cache

    @property
    def collection(self) -> OrderedDict:
        pass

    @property
    def config(self) -> CacheConfigurationInterface:
        pass

    @property
    def eviction_policy(self) -> EvictionPolicyInterface:
        pass

    @property
    def size(self) -> int:
        pass

    def get(self, key: CacheKey) -> Union[CacheEntry, None]:
        return self._cache.get(key)

    def set(self, entry: CacheEntry) -> bool:
        pass

    def delete_by_cache_keys(self, cache_keys: List[CacheKey]) -> List[bool]:
        return self._cache.delete_by_cache_keys(cache_keys)

    def delete_by_redis_keys(self, redis_keys: List[bytes]) -> List[bool]:
        pass

    def flush(self) -> int:
        return self._cache.flush()

    def is_cachable(self, key: CacheKey) -> bool:
        return self._cache.is_cachable(key)


class LRUPolicy(EvictionPolicyInterface):
    def __init__(self):
        self.cache = None

    @property
    def cache(self):
        pass

    @cache.setter
    def cache(self, cache: CacheInterface):
        pass

    @property
    def type(self) -> EvictionPolicyType:
        pass

    def evict_next(self) -> CacheKey:
        pass

    def evict_many(self, count: int) -> List[CacheKey]:
        pass

    def touch(self, cache_key: CacheKey) -> None:
        self._assert_cache()

        if self._cache.collection.get(cache_key) is None:
            raise ValueError("Given entry does not belong to the cache")

        self._cache.collection.move_to_end(cache_key)

    def _assert_cache(self):
        if self.cache is None or not isinstance(self.cache, CacheInterface):
            raise ValueError("Eviction policy should be associated with valid cache.")


class EvictionPolicy(Enum):
    LRU = LRUPolicy


class CacheConfig(CacheConfigurationInterface):
    DEFAULT_CACHE_CLASS = DefaultCache
    DEFAULT_EVICTION_POLICY = EvictionPolicy.LRU
    DEFAULT_MAX_SIZE = 10000

    DEFAULT_ALLOW_LIST = [
        "BITCOUNT",
        "BITFIELD_RO",
        "BITPOS",
        "EXISTS",
        "GEODIST",
        "GEOHASH",
        "GEOPOS",
        "GEORADIUSBYMEMBER_RO",
        "GEORADIUS_RO",
        "GEOSEARCH",
        "GET",
        "GETBIT",
        "GETRANGE",
        "HEXISTS",
        "HGET",
        "HGETALL",
        "HKEYS",
        "HLEN",
        "HMGET",
        "HSTRLEN",
        "HVALS",
        "JSON.ARRINDEX",
        "JSON.ARRLEN",
        "JSON.GET",
        "JSON.MGET",
        "JSON.OBJKEYS",
        "JSON.OBJLEN",
        "JSON.RESP",
        "JSON.STRLEN",
        "JSON.TYPE",
        "LCS",
        "LINDEX",
        "LLEN",
        "LPOS",
        "LRANGE",
        "MGET",
        "SCARD",
        "SDIFF",
        "SINTER",
        "SINTERCARD",
        "SISMEMBER",
        "SMEMBERS",
        "SMISMEMBER",
        "SORT_RO",
        "STRLEN",
        "SUBSTR",
        "SUNION",
        "TS.GET",
        "TS.INFO",
        "TS.RANGE",
        "TS.REVRANGE",
        "TYPE",
        "XLEN",
        "XPENDING",
        "XRANGE",
        "XREAD",
        "XREVRANGE",
        "ZCARD",
        "ZCOUNT",
        "ZDIFF",
        "ZINTER",
        "ZINTERCARD",
        "ZLEXCOUNT",
        "ZMSCORE",
        "ZRANGE",
        "ZRANGEBYLEX",
        "ZRANGEBYSCORE",
        "ZRANK",
        "ZREVRANGE",
        "ZREVRANGEBYLEX",
        "ZREVRANGEBYSCORE",
        "ZREVRANK",
        "ZSCORE",
        "ZUNION",
    ]

    def __init__(
        self,
        max_size: int = DEFAULT_MAX_SIZE,
        cache_class: Any = DEFAULT_CACHE_CLASS,
        eviction_policy: EvictionPolicy = DEFAULT_EVICTION_POLICY,
    ):
        self._cache_class = cache_class
        self._max_size = max_size
        self._eviction_policy = eviction_policy

    def get_cache_class(self):
        pass

    def get_max_size(self) -> int:
        pass

    def get_eviction_policy(self) -> EvictionPolicy:
        pass

    def is_exceeds_max_size(self, count: int) -> bool:
        pass

    def is_allowed_to_cache(self, command: str) -> bool:
        return command in self.DEFAULT_ALLOW_LIST


class CacheFactoryInterface(ABC):
    @abstractmethod
    def get_cache(self) -> CacheInterface:
        pass


class CacheFactory(CacheFactoryInterface):
    def __init__(self, cache_config: Optional[CacheConfig] = None):
        self._config = cache_config

        if self._config is None:
            self._config = CacheConfig()

    def get_cache(self) -> CacheInterface:
        pass
