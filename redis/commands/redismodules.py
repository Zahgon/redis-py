from __future__ import annotations

from json import JSONDecoder, JSONEncoder
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .bf import (
        AsyncBFBloom,
        AsyncCFBloom,
        AsyncCMSBloom,
        AsyncTDigestBloom,
        AsyncTOPKBloom,
        BFBloom,
        CFBloom,
        CMSBloom,
        TDigestBloom,
        TOPKBloom,
    )
    from .json import JSON, AsyncJSON
    from .search import AsyncSearch, Search
    from .timeseries import AsyncTimeSeries, TimeSeries
    from .vectorset import AsyncVectorSet, VectorSet


class RedisModuleCommands:
    """This class contains the wrapper functions to bring supported redis
    modules into the command namespace.
    """

    def json(self, encoder=JSONEncoder(), decoder=JSONDecoder()) -> JSON:
        """Access the json namespace, providing support for redis json."""

        from .json import JSON

        jj = JSON(client=self, encoder=encoder, decoder=decoder)
        return jj

    def ft(self, index_name="idx") -> Search:
        """Access the search namespace, providing support for redis search."""
        pass

    def ts(self) -> TimeSeries:
        """Access the timeseries namespace, providing support for
        redis timeseries data.
        """
        pass

    def bf(self) -> BFBloom:
        """Access the bloom namespace."""
        pass

    def cf(self) -> CFBloom:
        """Access the bloom namespace."""
        pass

    def cms(self) -> CMSBloom:
        """Access the bloom namespace."""
        pass

    def topk(self) -> TOPKBloom:
        """Access the bloom namespace."""
        pass

    def tdigest(self) -> TDigestBloom:
        """Access the bloom namespace."""
        pass

    def vset(self) -> VectorSet:
        """Access the VectorSet commands namespace."""
        pass


class AsyncRedisModuleCommands(RedisModuleCommands):
    def json(self, encoder=JSONEncoder(), decoder=JSONDecoder()) -> AsyncJSON:
        """Access the json namespace, providing support for redis json."""

        from .json import AsyncJSON

        jj = AsyncJSON(client=self, encoder=encoder, decoder=decoder)
        return jj

    def ft(self, index_name="idx") -> AsyncSearch:
        """Access the search namespace, providing support for redis search."""
        pass

    def ts(self) -> AsyncTimeSeries:
        """Access the timeseries namespace, providing support for
        redis timeseries data.
        """
        pass

    def bf(self) -> AsyncBFBloom:
        """Access the bloom namespace."""
        pass

    def cf(self) -> AsyncCFBloom:
        """Access the bloom namespace."""
        pass

    def cms(self) -> AsyncCMSBloom:
        """Access the bloom namespace."""
        pass

    def topk(self) -> AsyncTOPKBloom:
        """Access the bloom namespace."""
        pass

    def tdigest(self) -> AsyncTDigestBloom:
        """Access the bloom namespace."""
        pass

    def vset(self) -> AsyncVectorSet:
        """Access the VectorSet commands namespace."""
        pass
