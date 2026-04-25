from typing import Any, Awaitable, Dict, List, Tuple, overload

from redis.exceptions import DataError
from redis.typing import (
    AsyncClientProtocol,
    EncodableT,
    KeyT,
    Number,
    SyncClientProtocol,
    TimeSeriesRangeResponse,
    TimeSeriesSample,
)

from .info import TSInfo

ADD_CMD = "TS.ADD"
ALTER_CMD = "TS.ALTER"
CREATERULE_CMD = "TS.CREATERULE"
CREATE_CMD = "TS.CREATE"
DECRBY_CMD = "TS.DECRBY"
DELETERULE_CMD = "TS.DELETERULE"
DEL_CMD = "TS.DEL"
GET_CMD = "TS.GET"
INCRBY_CMD = "TS.INCRBY"
INFO_CMD = "TS.INFO"
MADD_CMD = "TS.MADD"
MGET_CMD = "TS.MGET"
MRANGE_CMD = "TS.MRANGE"
MREVRANGE_CMD = "TS.MREVRANGE"
QUERYINDEX_CMD = "TS.QUERYINDEX"
RANGE_CMD = "TS.RANGE"
REVRANGE_CMD = "TS.REVRANGE"


class TimeSeriesCommands:
    """RedisTimeSeries Commands."""

    @overload
    def create(
        self: SyncClientProtocol,
        key: KeyT,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> bool: ...

    @overload
    def create(
        self: AsyncClientProtocol,
        key: KeyT,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> Awaitable[bool]: ...

    def create(
        self,
        key: KeyT,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> bool | Awaitable[bool]:
        """
        Create a new time-series.

        For more information see https://redis.io/commands/ts.create/

        Args:
            key:
                The time-series key.
            retention_msecs:
                Maximum age for samples, compared to the highest reported timestamp in
                milliseconds. If `None` or `0` is passed, the series is not trimmed at
                all.
            uncompressed:
                Changes data storage from compressed (default) to uncompressed.
            labels:
                A dictionary of label-value pairs that represent metadata labels of the
                key.
            chunk_size:
                Memory size, in bytes, allocated for each data chunk. Must be a multiple
                of 8 in the range `[48..1048576]`. In earlier versions of the module the
                minimum value was different.
            duplicate_policy:
                Policy for handling multiple samples with identical timestamps. Can be
                one of:

                - 'block': An error will occur and the new value will be ignored.
                - 'first': Ignore the new value.
                - 'last': Override with the latest value.
                - 'min': Only override if the value is lower than the existing value.
                - 'max': Only override if the value is higher than the existing value.
                - 'sum': If a previous sample exists, add the new sample to it so
                  that the updated value is equal to (previous + new). If no
                  previous sample exists, set the updated value equal to the new
                  value.

            ignore_max_time_diff:
                A non-negative integer value, in milliseconds, that sets an ignore
                threshold for added timestamps. If the difference between the last
                timestamp and the new timestamp is lower than this threshold, the new
                entry is ignored. Only applicable if `duplicate_policy` is set to
                `last`, and if `ignore_max_val_diff` is also set. Available since
                RedisTimeSeries version 1.12.0.
            ignore_max_val_diff:
                A non-negative floating point value, that sets an ignore threshold for
                added values. If the difference between the last value and the new value
                is lower than this threshold, the new entry is ignored. Only applicable
                if `duplicate_policy` is set to `last`, and if `ignore_max_time_diff` is
                also set. Available since RedisTimeSeries version 1.12.0.
        """
        pass

    @overload
    def alter(
        self: SyncClientProtocol,
        key: KeyT,
        retention_msecs: int | None = None,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> bool: ...

    @overload
    def alter(
        self: AsyncClientProtocol,
        key: KeyT,
        retention_msecs: int | None = None,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> Awaitable[bool]: ...

    def alter(
        self,
        key: KeyT,
        retention_msecs: int | None = None,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> bool | Awaitable[bool]:
        """
        Update an existing time series.

        For more information see https://redis.io/commands/ts.alter/

        Args:
            key:
                The time-series key.
            retention_msecs:
                Maximum age for samples, compared to the highest reported timestamp in
                milliseconds. If `None` or `0` is passed, the series is not trimmed at
                all.
            labels:
                A dictionary of label-value pairs that represent metadata labels of the
                key.
            chunk_size:
                Memory size, in bytes, allocated for each data chunk. Must be a multiple
                of 8 in the range `[48..1048576]`. In earlier versions of the module the
                minimum value was different. Changing this value does not affect
                existing chunks.
            duplicate_policy:
                Policy for handling multiple samples with identical timestamps. Can be
                one of:

                - 'block': An error will occur and the new value will be ignored.
                - 'first': Ignore the new value.
                - 'last': Override with the latest value.
                - 'min': Only override if the value is lower than the existing value.
                - 'max': Only override if the value is higher than the existing value.
                - 'sum': If a previous sample exists, add the new sample to it so
                  that the updated value is equal to (previous + new). If no
                  previous sample exists, set the updated value equal to the new
                  value.

            ignore_max_time_diff:
                A non-negative integer value, in milliseconds, that sets an ignore
                threshold for added timestamps. If the difference between the last
                timestamp and the new timestamp is lower than this threshold, the new
                entry is ignored. Only applicable if `duplicate_policy` is set to
                `last`, and if `ignore_max_val_diff` is also set. Available since
                RedisTimeSeries version 1.12.0.
            ignore_max_val_diff:
                A non-negative floating point value, that sets an ignore threshold for
                added values. If the difference between the last value and the new value
                is lower than this threshold, the new entry is ignored. Only applicable
                if `duplicate_policy` is set to `last`, and if `ignore_max_time_diff` is
                also set. Available since RedisTimeSeries version 1.12.0.
        """
        pass

    @overload
    def add(
        self: SyncClientProtocol,
        key: KeyT,
        timestamp: int | str,
        value: Number | str,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
        on_duplicate: str | None = None,
    ) -> int: ...

    @overload
    def add(
        self: AsyncClientProtocol,
        key: KeyT,
        timestamp: int | str,
        value: Number | str,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
        on_duplicate: str | None = None,
    ) -> Awaitable[int]: ...

    def add(
        self,
        key: KeyT,
        timestamp: int | str,
        value: Number | str,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
        on_duplicate: str | None = None,
    ) -> int | Awaitable[int]:
        """
        Append a sample to a time series. When the specified key does not exist, a new
        time series is created.

        For more information see https://redis.io/commands/ts.add/

        Args:
            key:
                The time-series key.
            timestamp:
                Timestamp of the sample. `*` can be used for automatic timestamp (using
                the system clock).
            value:
                Numeric data value of the sample.
            retention_msecs:
                Maximum age for samples, compared to the highest reported timestamp in
                milliseconds. If `None` or `0` is passed, the series is not trimmed at
                all.
            uncompressed:
                Changes data storage from compressed (default) to uncompressed.
            labels:
                A dictionary of label-value pairs that represent metadata labels of the
                key.
            chunk_size:
                Memory size, in bytes, allocated for each data chunk. Must be a multiple
                of 8 in the range `[48..1048576]`. In earlier versions of the module the
                minimum value was different.
            duplicate_policy:
                Policy for handling multiple samples with identical timestamps. Can be
                one of:

                - 'block': An error will occur and the new value will be ignored.
                - 'first': Ignore the new value.
                - 'last': Override with the latest value.
                - 'min': Only override if the value is lower than the existing value.
                - 'max': Only override if the value is higher than the existing value.
                - 'sum': If a previous sample exists, add the new sample to it so
                  that the updated value is equal to (previous + new). If no
                  previous sample exists, set the updated value equal to the new
                  value.

            ignore_max_time_diff:
                A non-negative integer value, in milliseconds, that sets an ignore
                threshold for added timestamps. If the difference between the last
                timestamp and the new timestamp is lower than this threshold, the new
                entry is ignored. Only applicable if `duplicate_policy` is set to
                `last`, and if `ignore_max_val_diff` is also set. Available since
                RedisTimeSeries version 1.12.0.
            ignore_max_val_diff:
                A non-negative floating point value, that sets an ignore threshold for
                added values. If the difference between the last value and the new value
                is lower than this threshold, the new entry is ignored. Only applicable
                if `duplicate_policy` is set to `last`, and if `ignore_max_time_diff` is
                also set. Available since RedisTimeSeries version 1.12.0.
            on_duplicate:
                Use a specific duplicate policy for the specified timestamp. Overrides
                the duplicate policy set by `duplicate_policy`.
        """
        params: list[EncodableT] = [key, timestamp, value]
        self._append_retention(params, retention_msecs)
        self._append_uncompressed(params, uncompressed)
        self._append_chunk_size(params, chunk_size)
        self._append_duplicate_policy(params, duplicate_policy)
        self._append_labels(params, labels)
        self._append_insertion_filters(
            params, ignore_max_time_diff, ignore_max_val_diff
        )
        self._append_on_duplicate(params, on_duplicate)

        return self.execute_command(ADD_CMD, *params)

    @overload
    def madd(
        self: SyncClientProtocol,
        ktv_tuples: List[Tuple[KeyT, int | str, Number | str]],
    ) -> list[int]: ...

    @overload
    def madd(
        self: AsyncClientProtocol,
        ktv_tuples: List[Tuple[KeyT, int | str, Number | str]],
    ) -> Awaitable[list[int]]: ...

    def madd(
        self, ktv_tuples: List[Tuple[KeyT, int | str, Number | str]]
    ) -> list[int] | Awaitable[list[int]]:
        """
        Append new samples to one or more time series.

        Each time series must already exist.

        The method expects a list of tuples. Each tuple should contain three elements:
        (`key`, `timestamp`, `value`). The `value` will be appended to the time series
        identified by 'key', at the given 'timestamp'.

        For more information see https://redis.io/commands/ts.madd/

        Args:
            ktv_tuples:
                A list of tuples, where each tuple contains:
                    - `key`: The key of the time series.
                    - `timestamp`: The timestamp at which the value should be appended.
                    - `value`: The value to append to the time series.

        Returns:
            A list that contains, for each sample, either the timestamp that was used,
            or an error, if the sample could not be added.
        """
        pass

    @overload
    def incrby(
        self: SyncClientProtocol,
        key: KeyT,
        value: Number,
        timestamp: int | str | None = None,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> int: ...

    @overload
    def incrby(
        self: AsyncClientProtocol,
        key: KeyT,
        value: Number,
        timestamp: int | str | None = None,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> Awaitable[int]: ...

    def incrby(
        self,
        key: KeyT,
        value: Number,
        timestamp: int | str | None = None,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> int | Awaitable[int]:
        """
        Increment the latest sample's of a series. When the specified key does not
        exist, a new time series is created.

        This command can be used as a counter or gauge that automatically gets history
        as a time series.

        For more information see https://redis.io/commands/ts.incrby/

        Args:
            key:
                The time-series key.
            value:
                Numeric value to be added (addend).
            timestamp:
                Timestamp of the sample. `*` can be used for automatic timestamp (using
                the system clock). `timestamp` must be equal to or higher than the
                maximum existing timestamp in the series. When equal, the value of the
                sample with the maximum existing timestamp is increased. If it is
                higher, a new sample with a timestamp set to `timestamp` is created, and
                its value is set to the value of the sample with the maximum existing
                timestamp plus the addend.
            retention_msecs:
                Maximum age for samples, compared to the highest reported timestamp in
                milliseconds. If `None` or `0` is passed, the series is not trimmed at
                all.
            uncompressed:
                Changes data storage from compressed (default) to uncompressed.
            labels:
                A dictionary of label-value pairs that represent metadata labels of the
                key.
            chunk_size:
                Memory size, in bytes, allocated for each data chunk. Must be a multiple
                of 8 in the range `[48..1048576]`. In earlier versions of the module the
                minimum value was different.
            duplicate_policy:
                Policy for handling multiple samples with identical timestamps. Can be
                one of:

                - 'block': An error will occur and the new value will be ignored.
                - 'first': Ignore the new value.
                - 'last': Override with the latest value.
                - 'min': Only override if the value is lower than the existing value.
                - 'max': Only override if the value is higher than the existing value.
                - 'sum': If a previous sample exists, add the new sample to it so
                  that the updated value is equal to (previous + new). If no
                  previous sample exists, set the updated value equal to the new
                  value.

            ignore_max_time_diff:
                A non-negative integer value, in milliseconds, that sets an ignore
                threshold for added timestamps. If the difference between the last
                timestamp and the new timestamp is lower than this threshold, the new
                entry is ignored. Only applicable if `duplicate_policy` is set to
                `last`, and if `ignore_max_val_diff` is also set. Available since
                RedisTimeSeries version 1.12.0.
            ignore_max_val_diff:
                A non-negative floating point value, that sets an ignore threshold for
                added values. If the difference between the last value and the new value
                is lower than this threshold, the new entry is ignored. Only applicable
                if `duplicate_policy` is set to `last`, and if `ignore_max_time_diff` is
                also set. Available since RedisTimeSeries version 1.12.0.

        Returns:
            The timestamp of the sample that was modified or added.
        """
        pass

    @overload
    def decrby(
        self: SyncClientProtocol,
        key: KeyT,
        value: Number,
        timestamp: int | str | None = None,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> int: ...

    @overload
    def decrby(
        self: AsyncClientProtocol,
        key: KeyT,
        value: Number,
        timestamp: int | str | None = None,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> Awaitable[int]: ...

    def decrby(
        self,
        key: KeyT,
        value: Number,
        timestamp: int | str | None = None,
        retention_msecs: int | None = None,
        uncompressed: bool | None = False,
        labels: Dict[str, str] | None = None,
        chunk_size: int | None = None,
        duplicate_policy: str | None = None,
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ) -> int | Awaitable[int]:
        """
        Decrement the latest sample's of a series. When the specified key does not
        exist, a new time series is created.

        This command can be used as a counter or gauge that automatically gets history
        as a time series.

        For more information see https://redis.io/commands/ts.decrby/

        Args:
            key:
                The time-series key.
            value:
                Numeric value to subtract (subtrahend).
            timestamp:
                Timestamp of the sample. `*` can be used for automatic timestamp (using
                the system clock). `timestamp` must be equal to or higher than the
                maximum existing timestamp in the series. When equal, the value of the
                sample with the maximum existing timestamp is decreased. If it is
                higher, a new sample with a timestamp set to `timestamp` is created, and
                its value is set to the value of the sample with the maximum existing
                timestamp minus subtrahend.
            retention_msecs:
                Maximum age for samples, compared to the highest reported timestamp in
                milliseconds. If `None` or `0` is passed, the series is not trimmed at
                all.
            uncompressed:
                Changes data storage from compressed (default) to uncompressed.
            labels:
                A dictionary of label-value pairs that represent metadata labels of the
                key.
            chunk_size:
                Memory size, in bytes, allocated for each data chunk. Must be a multiple
                of 8 in the range `[48..1048576]`. In earlier versions of the module the
                minimum value was different.
            duplicate_policy:
                Policy for handling multiple samples with identical timestamps. Can be
                one of:

                - 'block': An error will occur and the new value will be ignored.
                - 'first': Ignore the new value.
                - 'last': Override with the latest value.
                - 'min': Only override if the value is lower than the existing value.
                - 'max': Only override if the value is higher than the existing value.
                - 'sum': If a previous sample exists, add the new sample to it so
                  that the updated value is equal to (previous + new). If no
                  previous sample exists, set the updated value equal to the new
                  value.

            ignore_max_time_diff:
                A non-negative integer value, in milliseconds, that sets an ignore
                threshold for added timestamps. If the difference between the last
                timestamp and the new timestamp is lower than this threshold, the new
                entry is ignored. Only applicable if `duplicate_policy` is set to
                `last`, and if `ignore_max_val_diff` is also set. Available since
                RedisTimeSeries version 1.12.0.
            ignore_max_val_diff:
                A non-negative floating point value, that sets an ignore threshold for
                added values. If the difference between the last value and the new value
                is lower than this threshold, the new entry is ignored. Only applicable
                if `duplicate_policy` is set to `last`, and if `ignore_max_time_diff` is
                also set. Available since RedisTimeSeries version 1.12.0.

        Returns:
            The timestamp of the sample that was modified or added.
        """
        pass

    @overload
    def delete(
        self: SyncClientProtocol, key: KeyT, from_time: int, to_time: int
    ) -> int: ...

    @overload
    def delete(
        self: AsyncClientProtocol, key: KeyT, from_time: int, to_time: int
    ) -> Awaitable[int]: ...

    def delete(self, key: KeyT, from_time: int, to_time: int) -> int | Awaitable[int]:
        """
        Delete all samples between two timestamps for a given time series.

        The given timestamp interval is closed (inclusive), meaning that samples whose
        timestamp equals `from_time` or `to_time` are also deleted.

        For more information see https://redis.io/commands/ts.del/

        Args:
            key:
                The time-series key.
            from_time:
                Start timestamp for the range deletion.
            to_time:
                End timestamp for the range deletion.

        Returns:
            The number of samples deleted.
        """
        return self.execute_command(DEL_CMD, key, from_time, to_time)

    @overload
    def createrule(
        self: SyncClientProtocol,
        source_key: KeyT,
        dest_key: KeyT,
        aggregation_type: str,
        bucket_size_msec: int,
        align_timestamp: int | None = None,
    ) -> bool: ...

    @overload
    def createrule(
        self: AsyncClientProtocol,
        source_key: KeyT,
        dest_key: KeyT,
        aggregation_type: str,
        bucket_size_msec: int,
        align_timestamp: int | None = None,
    ) -> Awaitable[bool]: ...

    def createrule(
        self,
        source_key: KeyT,
        dest_key: KeyT,
        aggregation_type: str,
        bucket_size_msec: int,
        align_timestamp: int | None = None,
    ) -> bool | Awaitable[bool]:
        """
        Create a compaction rule from values added to `source_key` into `dest_key`.

        For more information see https://redis.io/commands/ts.createrule/

        Args:
            source_key:
                Key name for source time series.
            dest_key:
                Key name for destination (compacted) time series.
            aggregation_type:
                Aggregation type: One of the following:
                [`avg`, `sum`, `min`, `max`, `range`, `count`, `first`, `last`, `std.p`,
                `std.s`, `var.p`, `var.s`, `twa`, 'countNaN', 'countAll']
            bucket_size_msec:
                Duration of each bucket, in milliseconds.
            align_timestamp:
                Assure that there is a bucket that starts at exactly align_timestamp and
                align all other buckets accordingly.
        """
        pass

    @overload
    def deleterule(
        self: SyncClientProtocol, source_key: KeyT, dest_key: KeyT
    ) -> bool: ...

    @overload
    def deleterule(
        self: AsyncClientProtocol, source_key: KeyT, dest_key: KeyT
    ) -> Awaitable[bool]: ...

    def deleterule(self, source_key: KeyT, dest_key: KeyT) -> bool | Awaitable[bool]:
        """
        Delete a compaction rule from `source_key` to `dest_key`.

        For more information see https://redis.io/commands/ts.deleterule/
        """
        pass

    def __range_params(
        self,
        key: KeyT,
        from_time: int | str,
        to_time: int | str,
        count: int | None,
        aggregation_type: str | list[str] | None,
        bucket_size_msec: int | None,
        filter_by_ts: List[int] | None,
        filter_by_min_value: int | None,
        filter_by_max_value: int | None,
        align: int | str | None,
        latest: bool | None,
        bucket_timestamp: str | None,
        empty: bool | None,
    ):
        """Create TS.RANGE and TS.REVRANGE arguments."""
        pass

    @overload
    def range(
        self: SyncClientProtocol,
        key: KeyT,
        from_time: int | str,
        to_time: int | str,
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> TimeSeriesRangeResponse: ...

    @overload
    def range(
        self: AsyncClientProtocol,
        key: KeyT,
        from_time: int | str,
        to_time: int | str,
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> Awaitable[TimeSeriesRangeResponse]: ...

    def range(
        self,
        key: KeyT,
        from_time: int | str,
        to_time: int | str,
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> TimeSeriesRangeResponse | Awaitable[TimeSeriesRangeResponse]:
        """
        Query a range in forward direction for a specific time-series.

        For more information see https://redis.io/commands/ts.range/

        Args:
            key:
                Key name for timeseries.
            from_time:
                Start timestamp for the range query. `-` can be used to express the
                minimum possible timestamp (0).
            to_time:
                End timestamp for range query, `+` can be used to express the maximum
                possible timestamp.
            count:
                Limits the number of returned samples.
            aggregation_type:
                Optional aggregation type. Can be a single string or a list of strings
                for multiple aggregators (requires Redis 8.8+). Valid values:
                [`avg`, `sum`, `min`, `max`, `range`, `count`, `first`, `last`,
                `std.p`, `std.s`, `var.p`, `var.s`, `twa`, `countNaN`, `countAll`].
                When a list is passed, each sample in the response contains values
                in the same order as the specified aggregators.
            bucket_size_msec:
                Time bucket for aggregation in milliseconds.
            filter_by_ts:
                List of timestamps to filter the result by specific timestamps.
            filter_by_min_value:
                Filter result by minimum value (must mention also
                `filter by_max_value`).
            filter_by_max_value:
                Filter result by maximum value (must mention also
                `filter by_min_value`).
            align:
                Timestamp for alignment control for aggregation.
            latest:
                Used when a time series is a compaction, reports the compacted value of
                the latest possibly partial bucket.
            bucket_timestamp:
                Controls how bucket timestamps are reported. Can be one of [`-`, `low`,
                `+`, `high`, `~`, `mid`].
            empty:
                Reports aggregations for empty buckets.
        """
        pass

    @overload
    def revrange(
        self: SyncClientProtocol,
        key: KeyT,
        from_time: int | str,
        to_time: int | str,
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> TimeSeriesRangeResponse: ...

    @overload
    def revrange(
        self: AsyncClientProtocol,
        key: KeyT,
        from_time: int | str,
        to_time: int | str,
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> Awaitable[TimeSeriesRangeResponse]: ...

    def revrange(
        self,
        key: KeyT,
        from_time: int | str,
        to_time: int | str,
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> TimeSeriesRangeResponse | Awaitable[TimeSeriesRangeResponse]:
        """
        Query a range in reverse direction for a specific time-series.

        **Note**: This command is only available since RedisTimeSeries >= v1.4

        For more information see https://redis.io/commands/ts.revrange/

        Args:
            key:
                Key name for timeseries.
            from_time:
                Start timestamp for the range query. `-` can be used to express the
                minimum possible timestamp (0).
            to_time:
                End timestamp for range query, `+` can be used to express the maximum
                possible timestamp.
            count:
                Limits the number of returned samples.
            aggregation_type:
                Optional aggregation type. Can be a single string or a list of strings
                for multiple aggregators (requires Redis 8.8+). Valid values:
                [`avg`, `sum`, `min`, `max`, `range`, `count`, `first`, `last`,
                `std.p`, `std.s`, `var.p`, `var.s`, `twa`, `countNaN`, `countAll`].
                When a list is passed, each sample in the response contains values
                in the same order as the specified aggregators.
            bucket_size_msec:
                Time bucket for aggregation in milliseconds.
            filter_by_ts:
                List of timestamps to filter the result by specific timestamps.
            filter_by_min_value:
                Filter result by minimum value (must mention also
                `filter_by_max_value`).
            filter_by_max_value:
                Filter result by maximum value (must mention also
                `filter_by_min_value`).
            align:
                Timestamp for alignment control for aggregation.
            latest:
                Used when a time series is a compaction, reports the compacted value of
                the latest possibly partial bucket.
            bucket_timestamp:
                Controls how bucket timestamps are reported. Can be one of [`-`, `low`,
                `+`, `high`, `~`, `mid`].
            empty:
                Reports aggregations for empty buckets.
        """
        pass

    def __mrange_params(
        self,
        aggregation_type: str | list[str] | None,
        bucket_size_msec: int | None,
        count: int | None,
        filters: List[str],
        from_time: int | str,
        to_time: int | str,
        with_labels: bool | None,
        filter_by_ts: List[int] | None,
        filter_by_min_value: int | None,
        filter_by_max_value: int | None,
        groupby: str | None,
        reduce: str | None,
        select_labels: List[str] | None,
        align: int | str | None,
        latest: bool | None,
        bucket_timestamp: str | None,
        empty: bool | None,
    ):
        """Create TS.MRANGE and TS.MREVRANGE arguments."""
        pass

    @overload
    def mrange(
        self: SyncClientProtocol,
        from_time: int | str,
        to_time: int | str,
        filters: List[str],
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        with_labels: bool | None = False,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        groupby: str | None = None,
        reduce: str | None = None,
        select_labels: List[str] | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> list[Any] | dict[str, list[Any]]: ...

    @overload
    def mrange(
        self: AsyncClientProtocol,
        from_time: int | str,
        to_time: int | str,
        filters: List[str],
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        with_labels: bool | None = False,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        groupby: str | None = None,
        reduce: str | None = None,
        select_labels: List[str] | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> Awaitable[list[Any] | dict[str, list[Any]]]: ...

    def mrange(
        self,
        from_time: int | str,
        to_time: int | str,
        filters: List[str],
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        with_labels: bool | None = False,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        groupby: str | None = None,
        reduce: str | None = None,
        select_labels: List[str] | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> (list[Any] | dict[str, list[Any]]) | Awaitable[
        list[Any] | dict[str, list[Any]]
    ]:
        """
        Query a range across multiple time-series by filters in forward direction.

        For more information see https://redis.io/commands/ts.mrange/

        Args:
            from_time:
                Start timestamp for the range query. `-` can be used to express the
                minimum possible timestamp (0).
            to_time:
                End timestamp for range query, `+` can be used to express the maximum
                possible timestamp.
            filters:
                Filter to match the time-series labels.
            count:
                Limits the number of returned samples.
            aggregation_type:
                Optional aggregation type. Can be a single string or a list of strings
                for multiple aggregators (requires Redis 8.8+). Valid values:
                [`avg`, `sum`, `min`, `max`, `range`, `count`, `first`, `last`,
                `std.p`, `std.s`, `var.p`, `var.s`, `twa`, `countNaN`, `countAll`].
                When a list is passed, each sample in the response contains values
                in the same order as the specified aggregators.
                Note: GROUPBY is not allowed when multiple aggregators are specified.
            bucket_size_msec:
                Time bucket for aggregation in milliseconds.
            with_labels:
                Include in the reply all label-value pairs representing metadata labels
                of the time series.
            filter_by_ts:
                List of timestamps to filter the result by specific timestamps.
            filter_by_min_value:
                Filter result by minimum value (must mention also
                `filter_by_max_value`).
            filter_by_max_value:
                Filter result by maximum value (must mention also
                `filter_by_min_value`).
            groupby:
                Grouping by fields the results (must mention also `reduce`).
            reduce:
                Applying reducer functions on each group. Can be one of [`avg` `sum`,
                `min`, `max`, `range`, `count`, `std.p`, `std.s`, `var.p`, `var.s`].
            select_labels:
                Include in the reply only a subset of the key-value pair labels of a
                series.
            align:
                Timestamp for alignment control for aggregation.
            latest:
                Used when a time series is a compaction, reports the compacted value of
                the latest possibly partial bucket.
            bucket_timestamp:
                Controls how bucket timestamps are reported. Can be one of [`-`, `low`,
                `+`, `high`, `~`, `mid`].
            empty:
                Reports aggregations for empty buckets.
        """
        pass

    @overload
    def mrevrange(
        self: SyncClientProtocol,
        from_time: int | str,
        to_time: int | str,
        filters: List[str],
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        with_labels: bool | None = False,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        groupby: str | None = None,
        reduce: str | None = None,
        select_labels: List[str] | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> list[Any] | dict[str, list[Any]]: ...

    @overload
    def mrevrange(
        self: AsyncClientProtocol,
        from_time: int | str,
        to_time: int | str,
        filters: List[str],
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        with_labels: bool | None = False,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        groupby: str | None = None,
        reduce: str | None = None,
        select_labels: List[str] | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> Awaitable[list[Any] | dict[str, list[Any]]]: ...

    def mrevrange(
        self,
        from_time: int | str,
        to_time: int | str,
        filters: List[str],
        count: int | None = None,
        aggregation_type: str | list[str] | None = None,
        bucket_size_msec: int | None = 0,
        with_labels: bool | None = False,
        filter_by_ts: List[int] | None = None,
        filter_by_min_value: int | None = None,
        filter_by_max_value: int | None = None,
        groupby: str | None = None,
        reduce: str | None = None,
        select_labels: List[str] | None = None,
        align: int | str | None = None,
        latest: bool | None = False,
        bucket_timestamp: str | None = None,
        empty: bool | None = False,
    ) -> (list[Any] | dict[str, list[Any]]) | Awaitable[
        list[Any] | dict[str, list[Any]]
    ]:
        """
        Query a range across multiple time-series by filters in reverse direction.

        For more information see https://redis.io/commands/ts.mrevrange/

        Args:
            from_time:
                Start timestamp for the range query. '-' can be used to express the
                minimum possible timestamp (0).
            to_time:
                End timestamp for range query, '+' can be used to express the maximum
                possible timestamp.
            filters:
                Filter to match the time-series labels.
            count:
                Limits the number of returned samples.
            aggregation_type:
                Optional aggregation type. Can be a single string or a list of strings
                for multiple aggregators (requires Redis 8.8+). Valid values:
                [`avg`, `sum`, `min`, `max`, `range`, `count`, `first`, `last`,
                `std.p`, `std.s`, `var.p`, `var.s`, `twa`, `countNaN`, `countAll`].
                When a list is passed, each sample in the response contains values
                in the same order as the specified aggregators.
                Note: GROUPBY is not allowed when multiple aggregators are specified.
            bucket_size_msec:
                Time bucket for aggregation in milliseconds.
            with_labels:
                Include in the reply all label-value pairs representing metadata labels
                of the time series.
            filter_by_ts:
                List of timestamps to filter the result by specific timestamps.
            filter_by_min_value:
                Filter result by minimum value (must mention also
                `filter_by_max_value`).
            filter_by_max_value:
                Filter result by maximum value (must mention also
                `filter_by_min_value`).
            groupby:
                Grouping by fields the results (must mention also `reduce`).
            reduce:
                Applying reducer functions on each group. Can be one of [`avg` `sum`,
                `min`, `max`, `range`, `count`, `std.p`, `std.s`, `var.p`, `var.s`].
            select_labels:
                Include in the reply only a subset of the key-value pair labels of a
                series.
            align:
                Timestamp for alignment control for aggregation.
            latest:
                Used when a time series is a compaction, reports the compacted value of
                the latest possibly partial bucket.
            bucket_timestamp:
                Controls how bucket timestamps are reported. Can be one of [`-`, `low`,
                `+`, `high`, `~`, `mid`].
            empty:
                Reports aggregations for empty buckets.
        """
        pass

    @overload
    def get(
        self: SyncClientProtocol, key: KeyT, latest: bool | None = False
    ) -> TimeSeriesSample | None: ...

    @overload
    def get(
        self: AsyncClientProtocol, key: KeyT, latest: bool | None = False
    ) -> Awaitable[TimeSeriesSample | None]: ...

    def get(self, key: KeyT, latest: bool | None = False) -> (
        TimeSeriesSample | None
    ) | Awaitable[TimeSeriesSample | None]:
        """
        Get the last sample of `key`.

        For more information see https://redis.io/commands/ts.get/

        Args:
            latest:
                Used when a time series is a compaction, reports the compacted value of
                the latest (possibly partial) bucket.
        """
        params: list[EncodableT] = [key]
        self._append_latest(params, latest)
        return self.execute_command(GET_CMD, *params, keys=[key])

    @overload
    def mget(
        self: SyncClientProtocol,
        filters: List[str],
        with_labels: bool | None = False,
        select_labels: List[str] | None = None,
        latest: bool | None = False,
    ) -> list[Any] | dict[str, list[Any]]: ...

    @overload
    def mget(
        self: AsyncClientProtocol,
        filters: List[str],
        with_labels: bool | None = False,
        select_labels: List[str] | None = None,
        latest: bool | None = False,
    ) -> Awaitable[list[Any] | dict[str, list[Any]]]: ...

    def mget(
        self,
        filters: List[str],
        with_labels: bool | None = False,
        select_labels: List[str] | None = None,
        latest: bool | None = False,
    ) -> (list[Any] | dict[str, list[Any]]) | Awaitable[
        list[Any] | dict[str, list[Any]]
    ]:
        """
        Get the last samples matching the specific `filter`.

        For more information see https://redis.io/commands/ts.mget/

        Args:
            filters:
                Filter to match the time-series labels.
            with_labels:
                Include in the reply all label-value pairs representing metadata labels
                of the time series.
            select_labels:
                Include in the reply only a subset of the key-value pair labels o the
                time series.
            latest:
                Used when a time series is a compaction, reports the compacted value of
                the latest possibly partial bucket.
        """
        pass

    @overload
    def info(self: SyncClientProtocol, key: KeyT) -> TSInfo | dict[str, Any]: ...

    @overload
    def info(
        self: AsyncClientProtocol, key: KeyT
    ) -> Awaitable[TSInfo | dict[str, Any]]: ...

    def info(self, key: KeyT) -> (TSInfo | dict[str, Any]) | Awaitable[
        TSInfo | dict[str, Any]
    ]:
        """
        Get information of `key`.

        For more information see https://redis.io/commands/ts.info/
        """
        return self.execute_command(INFO_CMD, key, keys=[key])

    @overload
    def queryindex(
        self: SyncClientProtocol, filters: List[str]
    ) -> list[bytes | str]: ...

    @overload
    def queryindex(
        self: AsyncClientProtocol, filters: List[str]
    ) -> Awaitable[list[bytes | str]]: ...

    def queryindex(
        self, filters: List[str]
    ) -> list[bytes | str] | Awaitable[list[bytes | str]]:
        """
        Get all time series keys matching the `filter` list.

        For more information see https://redis.io/commands/ts.queryindex/
        """
        pass

    @staticmethod
    def _append_uncompressed(params: list[EncodableT], uncompressed: bool | None):
        """Append UNCOMPRESSED tag to params."""
        if uncompressed:
            params.extend(["ENCODING", "UNCOMPRESSED"])

    @staticmethod
    def _append_with_labels(
        params: list[EncodableT],
        with_labels: bool | None,
        select_labels: list[str] | None,
    ):
        """Append labels behavior to params."""
        pass

    @staticmethod
    def _append_groupby_reduce(
        params: list[EncodableT], groupby: str | None, reduce: str | None
    ):
        """Append GROUPBY REDUCE property to params."""
        pass

    @staticmethod
    def _append_retention(params: list[EncodableT], retention: int | None):
        """Append RETENTION property to params."""
        if retention is not None:
            params.extend(["RETENTION", retention])

    @staticmethod
    def _append_labels(params: list[EncodableT], labels: dict[str, str] | None):
        """Append LABELS property to params."""
        if labels:
            params.append("LABELS")
            for k, v in labels.items():
                params.extend([k, v])

    @staticmethod
    def _append_count(params: list[EncodableT], count: int | None):
        """Append COUNT property to params."""
        pass

    @staticmethod
    def _append_timestamp(params: list[EncodableT], timestamp: int | None):
        """Append TIMESTAMP property to params."""
        pass

    @staticmethod
    def _append_align(params: list[EncodableT], align: int | str | None):
        """Append ALIGN property to params."""
        pass

    @staticmethod
    def _append_aggregation(
        params: list[EncodableT],
        aggregation_type: str | list[str] | None,
        bucket_size_msec: int | None,
    ):
        """Append AGGREGATION property to params."""
        pass

    @staticmethod
    def _append_chunk_size(params: list[EncodableT], chunk_size: int | None):
        """Append CHUNK_SIZE property to params."""
        if chunk_size is not None:
            params.extend(["CHUNK_SIZE", chunk_size])

    @staticmethod
    def _append_duplicate_policy(
        params: list[EncodableT], duplicate_policy: str | None
    ):
        """Append DUPLICATE_POLICY property to params."""
        if duplicate_policy is not None:
            params.extend(["DUPLICATE_POLICY", duplicate_policy])

    @staticmethod
    def _append_on_duplicate(params: list[EncodableT], on_duplicate: str | None):
        """Append ON_DUPLICATE property to params."""
        if on_duplicate is not None:
            params.extend(["ON_DUPLICATE", on_duplicate])

    @staticmethod
    def _append_filer_by_ts(params: list[EncodableT], ts_list: list[int] | None):
        """Append FILTER_BY_TS property to params."""
        pass

    @staticmethod
    def _append_filer_by_value(
        params: list[EncodableT], min_value: int | None, max_value: int | None
    ):
        """Append FILTER_BY_VALUE property to params."""
        pass

    @staticmethod
    def _append_latest(params: list[EncodableT], latest: bool | None):
        """Append LATEST property to params."""
        if latest:
            params.append("LATEST")

    @staticmethod
    def _append_bucket_timestamp(
        params: list[EncodableT], bucket_timestamp: str | None
    ):
        """Append BUCKET_TIMESTAMP property to params."""
        pass

    @staticmethod
    def _append_empty(params: list[EncodableT], empty: bool | None):
        """Append EMPTY property to params."""
        pass

    @staticmethod
    def _append_insertion_filters(
        params: list[EncodableT],
        ignore_max_time_diff: int | None = None,
        ignore_max_val_diff: Number | None = None,
    ):
        """Append insertion filters to params."""
        if (ignore_max_time_diff is None) != (ignore_max_val_diff is None):
            raise ValueError(
                "Both ignore_max_time_diff and ignore_max_val_diff must be set."
            )

        if ignore_max_time_diff is not None and ignore_max_val_diff is not None:
            params.extend(
                ["IGNORE", str(ignore_max_time_diff), str(ignore_max_val_diff)]
            )
