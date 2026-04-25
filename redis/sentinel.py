import random
import weakref
from typing import Optional, Union

from redis._parsers.socket import SENTINEL
from redis.client import Redis
from redis.commands import SentinelCommands
from redis.connection import Connection, ConnectionPool, SSLConnection
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
        pool = self.connection_pool
        s = (
            f"<{type(self).__module__}.{type(self).__name__}"
            f"(service={pool.service_name}%s)>"
        )
        if self.host:
            host_info = f",host={self.host},port={self.port}"
            s = s % host_info
        return s

    def connect_to(self, address):
        pass

    def _connect_retry(self):
        pass

    def connect(self):
        return self.retry.call_with_retry(self._connect_retry, lambda error: None)

    def read_response(
        self,
        disable_decoding=False,
        *,
        timeout: Union[float, object] = SENTINEL,
        disconnect_on_error: Optional[bool] = False,
        push_request: Optional[bool] = False,
    ):
        try:
            return super().read_response(
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
                self.disconnect()
                raise ConnectionError("The previous master is now a slave")
            raise


class SentinelManagedSSLConnection(SentinelManagedConnection, SSLConnection):
    pass


class SentinelConnectionPoolProxy:
    def __init__(
        self,
        connection_pool,
        is_master,
        check_connection,
        service_name,
        sentinel_manager,
    ):
        self.connection_pool_ref = weakref.ref(connection_pool)
        self.is_master = is_master
        self.check_connection = check_connection
        self.service_name = service_name
        self.sentinel_manager = sentinel_manager
        self.reset()

    def reset(self):
        self.master_address = None
        self.slave_rr_counter = None

    def get_master_address(self):
        pass

    def rotate_slaves(self):
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
        self.proxy = SentinelConnectionPoolProxy(
            connection_pool=self,
            is_master=self.is_master,
            check_connection=self.check_connection,
            service_name=service_name,
            sentinel_manager=sentinel_manager,
        )
        super().__init__(**kwargs)
        self.connection_kwargs["connection_pool"] = self.proxy
        self.service_name = service_name
        self.sentinel_manager = sentinel_manager

    def __repr__(self):
        role = "master" if self.is_master else "slave"
        return (
            f"<{type(self).__module__}.{type(self).__name__}"
            f"(service={self.service_name}({role}))>"
        )

    def reset(self):
        super().reset()
        self.proxy.reset()

    @property
    def master_address(self):
        pass

    def owns_connection(self, connection):
        check = not self.is_master or (
            self.is_master and self.master_address == (connection.host, connection.port)
        )
        parent = super()
        return check and parent.owns_connection(connection)

    def get_master_address(self):
        pass

    def rotate_slaves(self):
        "Round-robin slave balancer"
        pass


class Sentinel(SentinelCommands):
    """
    Redis Sentinel cluster client

    >>> from redis.sentinel import Sentinel
    >>> sentinel = Sentinel([('localhost', 26379)], socket_timeout=0.1)
    >>> master = sentinel.master_for('mymaster', socket_timeout=0.1)
    >>> master.set('foo', 'bar')
    >>> slave = sentinel.slave_for('mymaster', socket_timeout=0.1)
    >>> slave.get('foo')
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
            Redis(hostname, port, **self.sentinel_kwargs)
            for hostname, port in sentinels
        ]
        self.min_other_sentinels = min_other_sentinels
        self.connection_kwargs = connection_kwargs
        self._force_master_ip = force_master_ip

    def execute_command(self, *args, **kwargs):
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
            response = random.choice(self.sentinels).execute_command(*args, **kwargs)
            if return_responses:
                return [response]
            else:
                return True if response else False

        responses = []
        for sentinel in self.sentinels:
            responses.append(sentinel.execute_command(*args, **kwargs))

        if return_responses:
            return responses

        return all(responses)

    def __repr__(self):
        sentinel_addresses = []
        for sentinel in self.sentinels:
            sentinel_addresses.append(
                "{host}:{port}".format_map(sentinel.connection_pool.connection_kwargs)
            )
        return (
            f"<{type(self).__module__}.{type(self).__name__}"
            f"(sentinels=[{','.join(sentinel_addresses)}])>"
        )

    def check_master_state(self, state, service_name):
        pass

    def discover_master(self, service_name):
        """
        Asks sentinel servers for the Redis master's address corresponding
        to the service labeled ``service_name``.

        Returns a pair (address, port) or raises MasterNotFoundError if no
        master is found.
        """
        pass

    def filter_slaves(self, slaves):
        "Remove slaves that are in an ODOWN or SDOWN state"
        pass

    def discover_slaves(self, service_name):
        "Returns a list of alive slaves for service ``service_name``"
        pass

    def master_for(
        self,
        service_name,
        redis_class=Redis,
        connection_pool_class=SentinelConnectionPool,
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
        service_name,
        redis_class=Redis,
        connection_pool_class=SentinelConnectionPool,
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
