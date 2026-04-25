import asyncio
import random
import weakref
from typing import AsyncIterator, Iterable, Mapping, Optional, Sequence, Tuple, Type

from redis.asyncio.client import Redis
from redis.asyncio.connection import (
    Connection,
    ConnectionPool,
    EncodableT,
    SSLConnection,
)
from redis.commands import AsyncSentinelCommands
from redis.exceptions import (
    ConnectionError,
    ReadOnlyError,
    ResponseError,
    TimeoutError,
)


class MasterNotFoundError(ConnectionError):
    pass


class SlaveNotFoundError(ConnectionError):
    pass


class SentinelManagedConnection(Connection):
    def __init__(self, **kwargs):
        self.connection_pool = kwargs.pop("connection_pool")
        super().__init__(**kwargs)

    def __repr__(self):
        s = f"<{self.__class__.__module__}.{self.__class__.__name__}"
        if self.host:
            host_info = f",host={self.host},port={self.port}"
            s += host_info
        return s + ")>"

    async def connect_to(self, address):
        pass

    async def _connect_retry(self):
        pass

    async def connect(self):
        return await self.retry.call_with_retry(
            self._connect_retry,
            lambda error: asyncio.sleep(0),
        )

    async def read_response(
        self,
        disable_decoding: bool = False,
        timeout: Optional[float] = None,
        *,
        disconnect_on_error: Optional[float] = True,
        push_request: Optional[bool] = False,
    ):
        try:
            return await super().read_response(
                disable_decoding=disable_decoding,
                timeout=timeout,
                disconnect_on_error=disconnect_on_error,
                push_request=push_request,
            )
        except ReadOnlyError:
            if self.connection_pool.is_master:
                # When talking to a master, a ReadOnlyError when likely
                # indicates that the previous master that we're still connected
                # to has been demoted to a slave and there's a new master.
                # calling disconnect will force the connection to re-query
                # sentinel during the next connect() attempt.
                await self.disconnect()
                raise ConnectionError("The previous master is now a slave")
            raise


class SentinelManagedSSLConnection(SentinelManagedConnection, SSLConnection):
    pass


class SentinelConnectionPool(ConnectionPool):
    """
    Sentinel backed connection pool.

    If ``check_connection`` flag is set to True, SentinelManagedConnection
    sends a PING command right after establishing the connection.
    """

    def __init__(self, service_name, sentinel_manager, **kwargs):
        kwargs["connection_class"] = kwargs.get(
            "connection_class",
            (
                SentinelManagedSSLConnection
                if kwargs.pop("ssl", False)
                else SentinelManagedConnection
            ),
        )
        self.is_master = kwargs.pop("is_master", True)
        self.check_connection = kwargs.pop("check_connection", False)
        super().__init__(**kwargs)
        self.connection_kwargs["connection_pool"] = weakref.proxy(self)
        self.service_name = service_name
        self.sentinel_manager = sentinel_manager
        self.master_address = None
        self.slave_rr_counter = None

    def __repr__(self):
        return (
            f"<{self.__class__.__module__}.{self.__class__.__name__}"
            f"(service={self.service_name}({self.is_master and 'master' or 'slave'}))>"
        )

    def reset(self):
        super().reset()
        self.master_address = None
        self.slave_rr_counter = None

    def owns_connection(self, connection: Connection):
        check = not self.is_master or (
            self.is_master and self.master_address == (connection.host, connection.port)
        )
        return check and super().owns_connection(connection)

    async def get_master_address(self):
        pass

    async def rotate_slaves(self) -> AsyncIterator:
        """Round-robin slave balancer"""
        pass


class Sentinel(AsyncSentinelCommands):
    """
    Redis Sentinel cluster client

    >>> from redis.sentinel import Sentinel
    >>> sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
    >>> master = sentinel.master_for('mymaster', socket_timeout=0.1)
    >>> await master.set('foo', 'bar')
    >>> slave = sentinel.slave_for('mymaster', socket_timeout=0.1)
    >>> await slave.get('foo')
    b'bar'

    ``sentinels`` is a list of sentinel nodes. Each node is represented by
    a pair (hostname, port).

    ``min_other_sentinels`` defined a minimum number of peers for a sentinel.
    When querying a sentinel, if it doesn't meet this threshold, responses
    from that sentinel won't be considered valid.

    ``sentinel_kwargs`` is a dictionary of connection arguments used when
    connecting to sentinel instances. Any argument that can be passed to
    a normal Redis connection can be specified here. If ``sentinel_kwargs`` is
    not specified, any socket_timeout and socket_keepalive options specified
    in ``connection_kwargs`` will be used.

    ``connection_kwargs`` are keyword arguments that will be used when
    establishing a connection to a Redis server.
    """

    def __init__(
        self,
        sentinels,
        min_other_sentinels=0,
        sentinel_kwargs=None,
        force_master_ip=None,
        **connection_kwargs,
    ):
        # if sentinel_kwargs isn't defined, use the socket_* options from
        # connection_kwargs
        if sentinel_kwargs is None:
            sentinel_kwargs = {
                k: v for k, v in connection_kwargs.items() if k.startswith("socket_")
            }
        self.sentinel_kwargs = sentinel_kwargs

        self.sentinels = [
            Redis(host=hostname, port=port, **self.sentinel_kwargs)
            for hostname, port in sentinels
        ]
        self.min_other_sentinels = min_other_sentinels
        self.connection_kwargs = connection_kwargs
        self._force_master_ip = force_master_ip

    async def execute_command(self, *args, **kwargs):
        """
        Execute Sentinel command in sentinel nodes.
        once - If set to True, then execute the resulting command on a single
               node at random, rather than across the entire sentinel cluster.
        """
        once = bool(kwargs.pop("once", False))

        # Check if command is supposed to return the original
        # responses instead of boolean value.
        return_responses = bool(kwargs.pop("return_responses", False))

        if once:
            response = await random.choice(self.sentinels).execute_command(
                *args, **kwargs
            )
            if return_responses:
                return [response]
            else:
                return True if response else False

        tasks = [
            asyncio.Task(sentinel.execute_command(*args, **kwargs))
            for sentinel in self.sentinels
        ]
        responses = await asyncio.gather(*tasks)

        if return_responses:
            return responses

        return all(responses)

    def __repr__(self):
        sentinel_addresses = []
        for sentinel in self.sentinels:
            sentinel_addresses.append(
                f"{sentinel.connection_pool.connection_kwargs['host']}:"
                f"{sentinel.connection_pool.connection_kwargs['port']}"
            )
        return (
            f"<{self.__class__}.{self.__class__.__name__}"
            f"(sentinels=[{','.join(sentinel_addresses)}])>"
        )

    def check_master_state(self, state: dict, service_name: str) -> bool:
        pass

    async def discover_master(self, service_name: str):
        """
        Asks sentinel servers for the Redis master's address corresponding
        to the service labeled ``service_name``.

        Returns a pair (address, port) or raises MasterNotFoundError if no
        master is found.
        """
        pass

    def filter_slaves(
        self, slaves: Iterable[Mapping]
    ) -> Sequence[Tuple[EncodableT, EncodableT]]:
        """Remove slaves that are in an ODOWN or SDOWN state"""
        pass

    async def discover_slaves(
        self, service_name: str
    ) -> Sequence[Tuple[EncodableT, EncodableT]]:
        """Returns a list of alive slaves for service ``service_name``"""
        pass

    def master_for(
        self,
        service_name: str,
        redis_class: Type[Redis] = Redis,
        connection_pool_class: Type[SentinelConnectionPool] = SentinelConnectionPool,
        **kwargs,
    ):
        """
        Returns a redis client instance for the ``service_name`` master.
        Sentinel client will detect failover and reconnect Redis clients
        automatically.

        A :py:class:`~redis.sentinel.SentinelConnectionPool` class is
        used to retrieve the master's address before establishing a new
        connection.

        NOTE: If the master's address has changed, any cached connections to
        the old master are closed.

        By default clients will be a :py:class:`~redis.Redis` instance.
        Specify a different class to the ``redis_class`` argument if you
        desire something different.

        The ``connection_pool_class`` specifies the connection pool to
        use.  The :py:class:`~redis.sentinel.SentinelConnectionPool`
        will be used by default.

        All other keyword arguments are merged with any connection_kwargs
        passed to this class and passed to the connection pool as keyword
        arguments to be used to initialize Redis connections.
        """
        pass

    def slave_for(
        self,
        service_name: str,
        redis_class: Type[Redis] = Redis,
        connection_pool_class: Type[SentinelConnectionPool] = SentinelConnectionPool,
        **kwargs,
    ):
        """
        Returns redis client instance for the ``service_name`` slave(s).

        A SentinelConnectionPool class is used to retrieve the slave's
        address before establishing a new connection.

        By default clients will be a :py:class:`~redis.Redis` instance.
        Specify a different class to the ``redis_class`` argument if you
        desire something different.

        The ``connection_pool_class`` specifies the connection pool to use.
        The SentinelConnectionPool will be used by default.

        All other keyword arguments are merged with any connection_kwargs
        passed to this class and passed to the connection pool as keyword
        arguments to be used to initialize Redis connections.
        """
        pass
