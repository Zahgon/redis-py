from __future__ import annotations

import json
from enum import Enum
from typing import Any, Awaitable, overload

from redis.client import NEVER_DECODE
from redis.commands.helpers import get_protocol_version
from redis.exceptions import DataError
from redis.typing import (
    AsyncClientProtocol,
    CommandsProtocol,
    EncodableT,
    KeyT,
    Number,
    SyncClientProtocol,
)

VADD_CMD = "VADD"
VSIM_CMD = "VSIM"
VREM_CMD = "VREM"
VDIM_CMD = "VDIM"
VCARD_CMD = "VCARD"
VEMB_CMD = "VEMB"
VLINKS_CMD = "VLINKS"
VINFO_CMD = "VINFO"
VSETATTR_CMD = "VSETATTR"
VGETATTR_CMD = "VGETATTR"
VRANDMEMBER_CMD = "VRANDMEMBER"
VRANGE_CMD = "VRANGE"

# Return type for vsim command
VSimResult = (
    list[list[EncodableT] | dict[EncodableT, Number] | dict[EncodableT, dict[str, Any]]]
    | None
)

# Return type for vemb command
VEmbResult = list[EncodableT] | dict[str, EncodableT] | None

# Return type for vlinks command
VLinksResult = list[list[str | bytes] | dict[str | bytes, Number]] | None

# Return type for vrandmember command
VRandMemberResult = list[str] | str | None

# Return type for vgetattr command
VGetAttrResult = dict | None


class QuantizationOptions(Enum):
    """Quantization options for the VADD command."""

    NOQUANT = "NOQUANT"
    BIN = "BIN"
    Q8 = "Q8"


class CallbacksOptions(Enum):
    """Options that can be set for the commands callbacks"""

    RAW = "RAW"
    WITHSCORES = "WITHSCORES"
    WITHATTRIBS = "WITHATTRIBS"
    ALLOW_DECODING = "ALLOW_DECODING"
    RESP3 = "RESP3"


class VectorSetCommands(CommandsProtocol):
    """Redis VectorSet commands"""

    @overload
    def vadd(
        self: SyncClientProtocol,
        key: KeyT,
        vector: list[float] | bytes,
        element: str,
        reduce_dim: int | None = None,
        cas: bool | None = False,
        quantization: QuantizationOptions | None = None,
        ef: Number | None = None,
        attributes: dict | str | None = None,
        numlinks: int | None = None,
    ) -> int: ...

    @overload
    def vadd(
        self: AsyncClientProtocol,
        key: KeyT,
        vector: list[float] | bytes,
        element: str,
        reduce_dim: int | None = None,
        cas: bool | None = False,
        quantization: QuantizationOptions | None = None,
        ef: Number | None = None,
        attributes: dict | str | None = None,
        numlinks: int | None = None,
    ) -> Awaitable[int]: ...

    def vadd(
        self,
        key: KeyT,
        vector: list[float] | bytes,
        element: str,
        reduce_dim: int | None = None,
        cas: bool | None = False,
        quantization: QuantizationOptions | None = None,
        ef: Number | None = None,
        attributes: dict | str | None = None,
        numlinks: int | None = None,
    ) -> Awaitable[int] | int:
        """
        Add vector ``vector`` for element ``element`` to a vector set ``key``.

        ``reduce_dim`` sets the dimensions to reduce the vector to.
                If not provided, the vector is not reduced.

        ``cas`` is a boolean flag that indicates whether to use CAS (check-and-set style)
                when adding the vector. If not provided, CAS is not used.

        ``quantization`` sets the quantization type to use.
                If not provided, int8 quantization is used.
                The options are:
                - NOQUANT: No quantization
                - BIN: Binary quantization
                - Q8: Signed 8-bit quantization

        ``ef`` sets the exploration factor to use.
                If not provided, the default exploration factor is used.

        ``attributes`` is a dictionary or json string that contains the attributes to set for the vector.
                If not provided, no attributes are set.

        ``numlinks`` sets the number of links to create for the vector.
                If not provided, the default number of links is used.

        For more information, see https://redis.io/commands/vadd.
        """
        pass

    @overload
    def vsim(
        self: SyncClientProtocol,
        key: KeyT,
        input: list[float] | bytes | str,
        with_scores: bool | None = False,
        with_attribs: bool | None = False,
        count: int | None = None,
        ef: Number | None = None,
        filter: str | None = None,
        filter_ef: str | None = None,
        truth: bool | None = False,
        no_thread: bool | None = False,
        epsilon: Number | None = None,
    ) -> VSimResult: ...

    @overload
    def vsim(
        self: AsyncClientProtocol,
        key: KeyT,
        input: list[float] | bytes | str,
        with_scores: bool | None = False,
        with_attribs: bool | None = False,
        count: int | None = None,
        ef: Number | None = None,
        filter: str | None = None,
        filter_ef: str | None = None,
        truth: bool | None = False,
        no_thread: bool | None = False,
        epsilon: Number | None = None,
    ) -> Awaitable[VSimResult]: ...

    def vsim(
        self,
        key: KeyT,
        input: list[float] | bytes | str,
        with_scores: bool | None = False,
        with_attribs: bool | None = False,
        count: int | None = None,
        ef: Number | None = None,
        filter: str | None = None,
        filter_ef: str | None = None,
        truth: bool | None = False,
        no_thread: bool | None = False,
        epsilon: Number | None = None,
    ) -> Awaitable[VSimResult] | VSimResult:
        """
        Compare a vector or element ``input``  with the other vectors in a vector set ``key``.

        ``with_scores`` sets if similarity scores should be returned for each element in the result.

        ``with_attribs`` ``with_attribs`` sets if the results should be returned with the
                attributes of the elements in the result, or None when no attributes are present.

        ``count`` sets the number of results to return.

        ``ef`` sets the exploration factor.

        ``filter`` sets the filter that should be applied for the search.

        ``filter_ef`` sets the max filtering effort.

        ``truth`` when enabled, forces the command to perform a linear scan.

        ``no_thread`` when enabled forces the command to execute the search
                on the data structure in the main thread.

        ``epsilon`` floating point between 0 and 1, if specified will return
                only elements with distance no further than the specified one.

        For more information, see https://redis.io/commands/vsim.
        """
        pass

    @overload
    def vdim(self: SyncClientProtocol, key: KeyT) -> int: ...

    @overload
    def vdim(self: AsyncClientProtocol, key: KeyT) -> Awaitable[int]: ...

    def vdim(self, key: KeyT) -> Awaitable[int] | int:
        """
        Get the dimension of a vector set.

        In the case of vectors that were populated using the `REDUCE`
        option, for random projection, the vector set will report the size of
        the projected (reduced) dimension.

        Raises `redis.exceptions.ResponseError` if the vector set doesn't exist.

        For more information, see https://redis.io/commands/vdim.
        """
        pass

    @overload
    def vcard(self: SyncClientProtocol, key: KeyT) -> int: ...

    @overload
    def vcard(self: AsyncClientProtocol, key: KeyT) -> Awaitable[int]: ...

    def vcard(self, key: KeyT) -> Awaitable[int] | int:
        """
        Get the cardinality(the number of elements) of a vector set with key ``key``.

        Raises `redis.exceptions.ResponseError` if the vector set doesn't exist.

        For more information, see https://redis.io/commands/vcard.
        """
        pass

    @overload
    def vrem(self: SyncClientProtocol, key: KeyT, element: str) -> int: ...

    @overload
    def vrem(self: AsyncClientProtocol, key: KeyT, element: str) -> Awaitable[int]: ...

    def vrem(self, key: KeyT, element: str) -> Awaitable[int] | int:
        """
        Remove an element from a vector set.

        For more information, see https://redis.io/commands/vrem.
        """
        pass

    @overload
    def vemb(
        self: SyncClientProtocol,
        key: KeyT,
        element: str,
        raw: bool | None = False,
    ) -> VEmbResult: ...

    @overload
    def vemb(
        self: AsyncClientProtocol,
        key: KeyT,
        element: str,
        raw: bool | None = False,
    ) -> Awaitable[VEmbResult]: ...

    def vemb(
        self, key: KeyT, element: str, raw: bool | None = False
    ) -> Awaitable[VEmbResult] | VEmbResult:
        """
        Get the approximated vector of an element ``element`` from vector set ``key``.

        ``raw`` is a boolean flag that indicates whether to return the
                internal representation used by the vector.


        For more information, see https://redis.io/commands/vemb.
        """
        pass

    @overload
    def vlinks(
        self: SyncClientProtocol,
        key: KeyT,
        element: str,
        with_scores: bool | None = False,
    ) -> VLinksResult: ...

    @overload
    def vlinks(
        self: AsyncClientProtocol,
        key: KeyT,
        element: str,
        with_scores: bool | None = False,
    ) -> Awaitable[VLinksResult]: ...

    def vlinks(
        self, key: KeyT, element: str, with_scores: bool | None = False
    ) -> Awaitable[VLinksResult] | VLinksResult:
        """
        Returns the neighbors for each level the element ``element`` exists in the vector set ``key``.

        The result is a list of lists, where each list contains the neighbors for one level.
        If the element does not exist, or if the vector set does not exist, None is returned.

        If the ``WITHSCORES`` option is provided, the result is a list of dicts,
        where each dict contains the neighbors for one level, with the scores as values.

        For more information, see https://redis.io/commands/vlinks
        """
        pass

    @overload
    def vinfo(self: SyncClientProtocol, key: KeyT) -> dict | None: ...

    @overload
    def vinfo(self: AsyncClientProtocol, key: KeyT) -> Awaitable[dict | None]: ...

    def vinfo(self, key: KeyT) -> (dict | None) | Awaitable[dict | None]:
        """
        Get information about a vector set.

        For more information, see https://redis.io/commands/vinfo.
        """
        pass

    @overload
    def vsetattr(
        self: SyncClientProtocol,
        key: KeyT,
        element: str,
        attributes: dict | str | None = None,
    ) -> int: ...

    @overload
    def vsetattr(
        self: AsyncClientProtocol,
        key: KeyT,
        element: str,
        attributes: dict | str | None = None,
    ) -> Awaitable[int]: ...

    def vsetattr(
        self, key: KeyT, element: str, attributes: dict | str | None = None
    ) -> Awaitable[int] | int:
        """
        Associate or remove JSON attributes ``attributes`` of element ``element``
        for vector set ``key``.

        For more information, see https://redis.io/commands/vsetattr
        """
        pass

    @overload
    def vgetattr(
        self: SyncClientProtocol, key: KeyT, element: str
    ) -> VGetAttrResult: ...

    @overload
    def vgetattr(
        self: AsyncClientProtocol, key: KeyT, element: str
    ) -> Awaitable[VGetAttrResult]: ...

    def vgetattr(
        self, key: KeyT, element: str
    ) -> Awaitable[VGetAttrResult] | VGetAttrResult:
        """
        Retrieve the JSON attributes of an element ``element `` for vector set ``key``.

        If the element does not exist, or if the vector set does not exist, None is
        returned.

        For more information, see https://redis.io/commands/vgetattr.
        """
        pass

    @overload
    def vrandmember(
        self: SyncClientProtocol, key: KeyT, count: int | None = None
    ) -> VRandMemberResult: ...

    @overload
    def vrandmember(
        self: AsyncClientProtocol, key: KeyT, count: int | None = None
    ) -> Awaitable[VRandMemberResult]: ...

    def vrandmember(
        self, key: KeyT, count: int | None = None
    ) -> Awaitable[VRandMemberResult] | VRandMemberResult:
        """
        Returns random elements from a vector set ``key``.

        ``count`` is the number of elements to return.
                If ``count`` is not provided, a single element is returned as a single string.
                If ``count`` is positive(smaller than the number of elements
                            in the vector set), the command returns a list with up to ``count``
                            distinct elements from the vector set
                If ``count`` is negative, the command returns a list with ``count`` random elements,
                            potentially with duplicates.
                If ``count`` is greater than the number of elements in the vector set,
                            only the entire set is returned as a list.

        If the vector set does not exist, ``None`` is returned.

        For more information, see https://redis.io/commands/vrandmember.
        """
        pass

    @overload
    def vrange(
        self: SyncClientProtocol,
        key: KeyT,
        start: str,
        end: str,
        count: int | None = None,
    ) -> list[str]: ...

    @overload
    def vrange(
        self: AsyncClientProtocol,
        key: KeyT,
        start: str,
        end: str,
        count: int | None = None,
    ) -> Awaitable[list[str]]: ...

    def vrange(
        self, key: KeyT, start: str, end: str, count: int | None = None
    ) -> Awaitable[list[str]] | list[str]:
        """
        Return elements in a lexicographical range from a vector set ``key``.

        ``start`` is the starting point of the lexicographical range. Can be:
                - A string prefixed with '[' for inclusive range (e.g., '[Redis')
                - A string prefixed with '(' for exclusive range (e.g., '(a7')
                - The special symbol '-' to indicate the minimum element

        ``end`` is the ending point of the lexicographical range. Can be:
                - A string prefixed with '[' for inclusive range
                - A string prefixed with '(' for exclusive range
                - The special symbol '+' to indicate the maximum element

        ``count`` is the maximum number of elements to return.
                If ``count`` is not provided or negative, all elements in the range are returned.
                If ``count`` is positive, at most ``count`` elements are returned.

        Returns an array of elements in lexicographical order within the specified range.
        Returns an empty array if the key doesn't exist.

        For more information, see https://redis.io/commands/vrange.
        """
        pass
