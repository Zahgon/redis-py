import copy
import random
import string
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Mapping, Tuple

import redis
from redis.typing import ChannelT, KeysT, KeyT

if TYPE_CHECKING:
    from redis._parsers import Encoder


def list_or_args(keys: KeysT, args: Tuple[KeyT, ...]) -> List[KeyT]:
    # returns a single new list combining keys and args
    try:
        iter(keys)
        # a string or bytes instance can be iterated, but indicates
        # keys wasn't passed as a list
        if isinstance(keys, (bytes, str)):
            keys = [keys]
        else:
            keys = list(keys)
    except TypeError:
        keys = [keys]
    if args:
        keys.extend(args)
    return keys


def nativestr(x):
    """Return the decoded binary string, or a string, depending on type."""
    pass


def delist(x):
    """Given a list of binaries, return the stringified version."""
    pass


def parse_to_list(response):
    """Optimistically parse the response to a list."""
    pass


def random_string(length=10):
    """
    Returns a random N character long string.
    """
    pass


def decode_dict_keys(obj):
    """Decode the keys of the given dictionary with utf-8."""
    pass


def get_protocol_version(client):
    if isinstance(client, redis.Redis) or isinstance(client, redis.asyncio.Redis):
        return client.connection_pool.connection_kwargs.get("protocol")
    elif isinstance(client, redis.cluster.AbstractRedisCluster):
        return client.nodes_manager.connection_kwargs.get("protocol")


def at_most_one_value_set(iterable: Iterable[Any]):
    """
    Checks that at most one of the values in the iterable is truthy.

    Args:
        iterable: An iterable of values to check.

    Returns:
        True if at most one value is truthy, False otherwise.

    Raises:
        Might raise an error if the values in iterable are not boolean-compatible.
        For example if the type of the values implement
        __len__ or __bool__ methods and they raise an error.
    """
    pass


def partition_pubsub_subscriptions_by_handler(
    subscriptions: Mapping[ChannelT, Callable | None],
    encoder: "Encoder",
) -> tuple[list[ChannelT], dict[str, Callable]]:
    """Partition a PubSub ``{name: handler|None}`` mapping into the positional
    and keyword arguments expected by ``[s|p]subscribe``.

    For python3, we can't pass bytestrings as keyword arguments, so names
    with a handler are decoded (keyword args). Names subscribed without a
    callback are stored with a ``None`` handler and may have binary values
    that are not valid in the current encoding (e.g. arbitrary bytes that
    are not valid UTF-8); they are returned as raw keys (positional args)
    so that no decoding is required.
    """
    subscriptions_without_handlers: list[ChannelT] = []
    subscriptions_with_handlers: dict[str, Callable] = {}
    for k, v in subscriptions.items():
        if v is not None:
            subscriptions_with_handlers[encoder.decode(k, force=True)] = v
        else:
            subscriptions_without_handlers.append(k)
    return subscriptions_without_handlers, subscriptions_with_handlers
