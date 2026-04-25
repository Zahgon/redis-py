import datetime

from redis.commands.core import GCRAResponse
from redis.utils import str_if_bytes


def timestamp_to_datetime(response):
    "Converts a unix timestamp to a Python datetime object"
    pass


def parse_debug_object(response):
    "Parse the results of Redis's DEBUG OBJECT command into a Python dict"
    pass


def parse_info(response):
    """Parse the result of Redis's INFO command into a Python dict"""
    pass


def parse_memory_stats(response, **kwargs):
    """Parse the results of MEMORY STATS"""
    pass


def parse_memory_stats_resp3(response, **kwargs):
    """Parse MEMORY STATS for RESP3 — decode keys to str, preserve native values."""
    pass


SENTINEL_STATE_TYPES = {
    "can-failover-its-master": int,
    "config-epoch": int,
    "down-after-milliseconds": int,
    "failover-timeout": int,
    "info-refresh": int,
    "last-hello-message": int,
    "last-ok-ping-reply": int,
    "last-ping-reply": int,
    "last-ping-sent": int,
    "master-link-down-time": int,
    "master-port": int,
    "num-other-sentinels": int,
    "num-slaves": int,
    "o-down-time": int,
    "pending-commands": int,
    "parallel-syncs": int,
    "port": int,
    "quorum": int,
    "role-reported-time": int,
    "s-down-time": int,
    "slave-priority": int,
    "slave-repl-offset": int,
    "voted-leader-epoch": int,
}


def parse_sentinel_state(item):
    pass


def parse_sentinel_master(response, **options):
    pass


def parse_sentinel_state_resp3(response, **options):
    pass


def parse_sentinel_masters(response, **options):
    pass


def parse_sentinel_masters_resp3(response, **options):
    pass


def parse_sentinel_slaves_and_sentinels(response, **options):
    pass


def parse_sentinel_slaves_and_sentinels_resp3(response, **options):
    pass


def parse_sentinel_get_master(response, **options):
    pass


def pairs_to_dict(response, decode_keys=False, decode_string_values=False):
    """Create a dict given a list of key/value pairs"""
    if response is None:
        return {}
    if decode_keys or decode_string_values:
        # the iter form is faster, but I don't know how to make that work
        # with a str_if_bytes() map
        keys = response[::2]
        if decode_keys:
            keys = map(str_if_bytes, keys)
        values = response[1::2]
        if decode_string_values:
            values = map(str_if_bytes, values)
        return dict(zip(keys, values))
    else:
        it = iter(response)
        return dict(zip(it, it))


def pairs_to_dict_typed(response, type_info):
    pass


def _wrap_score_cast_func(score_cast_func):
    """Wrap score_cast_func to handle scientific notation in RESP2 byte strings.

    Redis returns scores as byte strings in RESP2, and large numbers may use
    scientific notation (e.g., b'1.7732526297292595e+18'). Python's int() cannot
    parse scientific notation directly.  Rather than unconditionally routing
    through float() (which would change the input type for every custom
    callable), we try the original function first and only fall back to
    converting through float() on ValueError.
    """
    pass


def zset_score_pairs(response, **options):
    """
    If ``withscores`` is specified in the options, return the response as
    a list of [value, score] pairs
    """
    pass


def zset_score_for_rank(response, **options):
    """
    If ``withscores`` is specified in the options, return the response as
    a [value, score] pair
    """
    pass


def zset_score_pairs_resp3(response, **options):
    """
    If ``withscores`` is specified in the options, return the response as
    a list of [value, score] pairs
    """
    pass


def hrandfield_pairs(response, **options):
    """
    If ``withvalues`` is specified in the options, return the response as
    a list of [field, value] pairs (pairing flat interleaved list).
    """
    pass


def parse_zmpop(response, **options):
    """
    Parse ZMPOP/BZMPOP response, casting scores to float.
    Response format: [key, [[member, score], ...]] or None.
    """
    pass


def parse_lcs(response, **options):
    """
    Parse LCS response. Without modifiers returns the raw string.
    With LEN returns an integer. With IDX returns a dict with string keys.
    RESP2 with IDX returns a flat list [key, val, key, val, ...]
    which we convert to a dict. RESP3 returns a native dict.
    Both have keys normalized to strings.
    """
    pass


def zpop_score_pairs(response, **options):
    """
    Handle ZPOPMAX/ZPOPMIN RESP2 responses.
    RESP2 always returns a flat array: [member1, score1, member2, score2, ...]
    Scores are byte strings that need to be cast to float.
    Always pairs and casts scores — no ``withscores`` gate required because
    ZPOPMAX/ZPOPMIN always include scores in their response.
    """
    pass


def zpop_score_pairs_resp3(response, **options):
    """
    Handle ZPOPMAX/ZPOPMIN RESP3 responses which differ based on count:
    - Without count: flat [member, score]
    - With count: nested [[member, score], ...]
    Normalizes both to list of [member, score] pairs with score_cast_func applied.
    """
    pass


def zset_score_for_rank_resp3(response, **options):
    """
    If ``withscores`` is specified in the options, return the response as
    a [value, score] pair
    """
    pass


def sort_return_tuples(response, **options):
    """
    If ``groups`` is specified, return the response as a list of
    n-element tuples with n being the value found in options['groups']
    """
    pass


def parse_stream_list(response, **options):
    pass


def pairs_to_dict_with_str_keys(response):
    pass


def parse_list_of_dicts(response):
    pass


def parse_xclaim(response, **options):
    pass


def parse_xautoclaim(response, **options):
    pass


def parse_xinfo_stream(response, **options):
    pass


def parse_xread(response, **options):
    pass


def parse_xread_resp3(response, **options):
    pass


def parse_xpending(response, **options):
    pass


def parse_xpending_range(response):
    pass


def float_or_none(response):
    pass


def bool_ok(response, **options):
    pass


def parse_zadd(response, **options):
    pass


def parse_client_list(response, **options):
    pass


def parse_config_get(response, **options):
    pass


def parse_scan(response, **options):
    pass


def parse_hscan(response, **options):
    pass


def parse_zscan(response, **options):
    pass


def parse_zmscore(response, **options):
    # zmscore: list of scores (double precision floating point number) or nil
    pass


def parse_slowlog_get(response, **options):
    pass


def parse_client_trackinginfo(response, **kwargs):
    """
    Parse CLIENT TRACKINGINFO response into a dict with str keys.
    RESP2: flat list [key, val, key, val, ...] → dict
    RESP3: native dict with bytes keys → dict with str keys
    """
    pass


def parse_stralgo(response, **options):
    """
    Parse the response from `STRALGO` command.
    Without modifiers the returned value is string.
    When LEN is given the command returns the length of the result
    (i.e integer).
    When IDX is given the command returns a dictionary with the LCS
    length and all the ranges in both the strings, start and end
    offset for each string, where there are matches.
    When WITHMATCHLEN is given, each array representing a match will
    also have the length of the match at the beginning of the array.
    """
    pass


def parse_stralgo_resp3(response, **options):
    """Parse RESP3 ``STRALGO`` response to match RESP2 ``parse_stralgo`` output.

    RESP3 returns a dict ``{b"matches": [...], b"len": N}`` for ``idx=True``,
    an int for ``len=True``, or a plain string otherwise.  The match
    restructuring mirrors :func:`parse_stralgo` exactly so both protocols
    produce identical results.
    """
    if options.get("len", False):
        return int(response)
    if options.get("idx", False):
        if isinstance(response, dict):
            raw_matches = response.get("matches", response.get(b"matches", []))
            raw_len = response.get("len", response.get(b"len", 0))
        else:
            return str_if_bytes(response)
        if options.get("withmatchlen", False):
            matches = [
                [int(match[-1])] + [list(m) for m in match[:-1]]
                for match in raw_matches
            ]
        else:
            matches = [[list(m) for m in match] for match in raw_matches]
        return {
            "matches": matches,
            "len": int(raw_len),
        }
    return str_if_bytes(response)


def parse_cluster_links(response, **options):
    """Parse CLUSTER LINKS into a list of dicts with str keys.

    RESP2 returns a list of flat lists ``[key, val, key, val, ...]``.
    RESP3 returns a list of dicts with bytes keys.
    Both are normalised to ``[{"direction": ..., "node": ..., ...}, ...]``.
    """
    pass


def parse_cluster_info(response, **options):
    pass


def _parse_node_line(line):
    pass


def _parse_slots(slot_ranges):
    pass


def parse_cluster_nodes(response, **options):
    """
    @see: https://redis.io/commands/cluster-nodes  # string / bytes
    @see: https://redis.io/commands/cluster-replicas # list of string / bytes
    """
    pass


def parse_geosearch_generic(response, **options):
    """
    Parse the response of 'GEOSEARCH', GEORADIUS' and 'GEORADIUSBYMEMBER'
    commands according to 'withdist', 'withhash' and 'withcoord' labels.
    """
    pass


def parse_command(response, **options):
    pass


def parse_command_resp3(response, **options):
    pass


def parse_pubsub_numsub(response, **options):
    pass


def parse_client_kill(response, **options):
    pass


def parse_acl_getuser(response, **options):
    pass


def parse_acl_log(response, **options):
    pass


def parse_acl_log_resp3(response, **options):
    """Parse ACL LOG for RESP3 — normalize to match RESP2 semantic richness.
    Converts age-seconds to float and client-info to parsed dict."""
    pass


def parse_client_info(value):
    """
    Parsing client-info in ACL Log in following format.
    "key1=value1 key2=value2 key3=value3"
    """
    pass


def parse_set_result(response, **options):
    """
    Handle SET result since GET argument is available since Redis 6.2.
    Parsing SET result into:
    - BOOL
    - String when GET argument is used
    """
    pass


def parse_gcra(response, **options):
    """
    Parse the GCRA rate limiting command response into a GCRAResponse dataclass.

    Response format: [limited, max_req_num, num_avail_req, retry_after, full_burst_after]
    """
    pass


def parse_function_list(response):
    """Parse FUNCTION LIST response from RESP2 flat lists into nested dicts.

    RESP2 returns: [[key, val, key, val, ...], ...]
    where nested 'functions' values are also flat lists.
    Converts to match RESP3's native dict format.
    """
    pass


def string_keys_to_dict(key_string, callback):
    return dict.fromkeys(key_string.split(), callback)


_RedisCallbacks = {
    **string_keys_to_dict(
        "AUTH COPY EXPIRE EXPIREAT HEXISTS HMSET MOVE MSETNX PERSIST PSETEX "
        "PEXPIRE PEXPIREAT RENAMENX SETEX SETNX SMOVE",
        bool,
    ),
    **string_keys_to_dict("HINCRBYFLOAT INCRBYFLOAT", float),
    **string_keys_to_dict(
        "ASKING FLUSHALL FLUSHDB LSET LTRIM MSET PFMERGE READONLY READWRITE "
        "RENAME SAVE SELECT SHUTDOWN SLAVEOF SWAPDB WATCH UNWATCH",
        bool_ok,
    ),
    **string_keys_to_dict("XREAD XREADGROUP", parse_xread),
    **string_keys_to_dict(
        "GEORADIUS GEORADIUSBYMEMBER GEOSEARCH",
        parse_geosearch_generic,
    ),
    **string_keys_to_dict("XRANGE XREVRANGE", parse_stream_list),
    "ACL GETUSER": parse_acl_getuser,
    "ACL LOAD": bool_ok,
    "ACL LOG": parse_acl_log,
    "ACL SETUSER": bool_ok,
    "ACL SAVE": bool_ok,
    "CLIENT INFO": parse_client_info,
    "CLIENT KILL": parse_client_kill,
    "CLIENT LIST": parse_client_list,
    "CLIENT PAUSE": bool_ok,
    "CLIENT SETINFO": bool_ok,
    "CLIENT TRACKINGINFO": parse_client_trackinginfo,
    "CLIENT SETNAME": bool_ok,
    "CLIENT UNBLOCK": bool,
    "CLUSTER ADDSLOTS": bool_ok,
    "CLUSTER ADDSLOTSRANGE": bool_ok,
    "CLUSTER DELSLOTS": bool_ok,
    "CLUSTER DELSLOTSRANGE": bool_ok,
    "CLUSTER FAILOVER": bool_ok,
    "CLUSTER FORGET": bool_ok,
    "CLUSTER INFO": parse_cluster_info,
    "CLUSTER LINKS": parse_cluster_links,
    "CLUSTER MEET": bool_ok,
    "CLUSTER NODES": parse_cluster_nodes,
    "CLUSTER REPLICAS": parse_cluster_nodes,
    "CLUSTER REPLICATE": bool_ok,
    "CLUSTER RESET": bool_ok,
    "CLUSTER SAVECONFIG": bool_ok,
    "CLUSTER SET-CONFIG-EPOCH": bool_ok,
    "CLUSTER SETSLOT": bool_ok,
    "CLUSTER SLAVES": parse_cluster_nodes,
    "COMMAND": parse_command,
    "CONFIG RESETSTAT": bool_ok,
    "CONFIG SET": bool_ok,
    "FUNCTION DELETE": bool_ok,
    "FUNCTION FLUSH": bool_ok,
    "FUNCTION RESTORE": bool_ok,
    "GCRA": parse_gcra,
    "GEODIST": float_or_none,
    "HSCAN": parse_hscan,
    "INFO": parse_info,
    "LASTSAVE": timestamp_to_datetime,
    "MEMORY PURGE": bool_ok,
    "MODULE LOAD": bool,
    "MODULE UNLOAD": bool,
    "PING": lambda r: str_if_bytes(r) == "PONG",
    "PUBSUB NUMSUB": parse_pubsub_numsub,
    "PUBSUB SHARDNUMSUB": parse_pubsub_numsub,
    "QUIT": bool_ok,
    "SET": parse_set_result,
    "SCAN": parse_scan,
    "SCRIPT EXISTS": lambda r: list(map(bool, r)),
    "SCRIPT FLUSH": bool_ok,
    "SCRIPT KILL": bool_ok,
    "SCRIPT LOAD": str_if_bytes,
    "SENTINEL CKQUORUM": bool_ok,
    "SENTINEL FAILOVER": bool_ok,
    "SENTINEL FLUSHCONFIG": bool_ok,
    "SENTINEL GET-MASTER-ADDR-BY-NAME": parse_sentinel_get_master,
    "SENTINEL MONITOR": bool_ok,
    "SENTINEL RESET": bool_ok,
    "SENTINEL REMOVE": bool_ok,
    "SENTINEL SET": bool_ok,
    "SLOWLOG GET": parse_slowlog_get,
    "SLOWLOG RESET": bool_ok,
    "SORT": sort_return_tuples,
    "SSCAN": parse_scan,
    "TIME": lambda x: (int(x[0]), int(x[1])),
    "XAUTOCLAIM": parse_xautoclaim,
    "XCLAIM": parse_xclaim,
    "XGROUP CREATE": bool_ok,
    "XGROUP DESTROY": bool,
    "XGROUP SETID": bool_ok,
    "XINFO STREAM": parse_xinfo_stream,
    "XPENDING": parse_xpending,
    "ZSCAN": parse_zscan,
    "LCS": parse_lcs,
}


_RedisCallbacksRESP2 = {
    **string_keys_to_dict(
        "SDIFF SINTER SMEMBERS SUNION", lambda r: r and set(r) or set()
    ),
    **string_keys_to_dict(
        "ZDIFF ZINTER ZRANGE ZRANGEBYSCORE ZREVRANGE ZREVRANGEBYSCORE ZUNION",
        zset_score_pairs,
    ),
    **string_keys_to_dict(
        "ZPOPMAX ZPOPMIN",
        zpop_score_pairs,
    ),
    **string_keys_to_dict(
        "ZREVRANK ZRANK",
        zset_score_for_rank,
    ),
    **string_keys_to_dict("ZINCRBY ZSCORE", float_or_none),
    **string_keys_to_dict("BGREWRITEAOF BGSAVE", lambda r: True),
    **string_keys_to_dict("BLPOP BRPOP", lambda r: r and list(r) or None),
    **string_keys_to_dict(
        "BZPOPMAX BZPOPMIN",
        lambda r: r and [r[0], r[1], float(r[2])] or None,
    ),
    "ACL CAT": lambda r: list(map(str_if_bytes, r)),
    "ACL GENPASS": str_if_bytes,
    "ACL HELP": lambda r: list(map(str_if_bytes, r)),
    "ACL LIST": lambda r: list(map(str_if_bytes, r)),
    "ACL USERS": lambda r: list(map(str_if_bytes, r)),
    "ACL WHOAMI": str_if_bytes,
    "CLIENT GETNAME": str_if_bytes,
    "CONFIG GET": parse_config_get,
    "DEBUG OBJECT": parse_debug_object,
    "GEOHASH": lambda r: list(map(str_if_bytes, r)),
    "GEOPOS": lambda r: list(
        map(lambda ll: [float(ll[0]), float(ll[1])] if ll is not None else None, r)
    ),
    "HGETALL": lambda r: r and pairs_to_dict(r) or {},
    "HOTKEYS GET": lambda r: [pairs_to_dict(m) for m in r],
    "MEMORY STATS": parse_memory_stats,
    "MODULE LIST": lambda r: [pairs_to_dict(m) for m in r],
    "RESET": str_if_bytes,
    "SENTINEL MASTER": parse_sentinel_master,
    "SENTINEL MASTERS": parse_sentinel_masters,
    "SENTINEL SENTINELS": parse_sentinel_slaves_and_sentinels,
    "SENTINEL SLAVES": parse_sentinel_slaves_and_sentinels,
    "STRALGO": parse_stralgo,
    "FUNCTION LIST": parse_function_list,
    "XINFO CONSUMERS": parse_list_of_dicts,
    "XINFO GROUPS": parse_list_of_dicts,
    "HRANDFIELD": hrandfield_pairs,
    "ZADD": parse_zadd,
    "ZMPOP": parse_zmpop,
    "BZMPOP": parse_zmpop,
    "ZMSCORE": parse_zmscore,
    "ZRANDMEMBER": zset_score_pairs,
}


_RedisCallbacksRESP3 = {
    **string_keys_to_dict(
        "SDIFF SINTER SMEMBERS SUNION", lambda r: r and set(r) or set()
    ),
    **string_keys_to_dict(
        "HGETALL",
        lambda r, **kwargs: r,
    ),
    **string_keys_to_dict(
        "ZDIFF ZINTER ZRANGE ZRANGEBYSCORE ZREVRANGE ZREVRANGEBYSCORE ZUNION",
        zset_score_pairs_resp3,
    ),
    **string_keys_to_dict(
        "ZPOPMAX ZPOPMIN",
        zpop_score_pairs_resp3,
    ),
    **string_keys_to_dict(
        "ZREVRANK ZRANK",
        zset_score_for_rank_resp3,
    ),
    **string_keys_to_dict(
        "BZPOPMAX BZPOPMIN",
        lambda r: r
        and [r[0], r[1], r[2] if isinstance(r[2], float) else float(r[2])]
        or None,
    ),
    **string_keys_to_dict("XREAD XREADGROUP", parse_xread_resp3),
    **string_keys_to_dict("ZMPOP BZMPOP", parse_zmpop),
    "ZRANDMEMBER": zset_score_pairs_resp3,
    "ACL CAT": lambda r: list(map(str_if_bytes, r)),
    "ACL GENPASS": str_if_bytes,
    "ACL HELP": lambda r: list(map(str_if_bytes, r)),
    "ACL LIST": lambda r: list(map(str_if_bytes, r)),
    "ACL USERS": lambda r: list(map(str_if_bytes, r)),
    "ACL WHOAMI": str_if_bytes,
    "CLIENT GETNAME": str_if_bytes,
    "GEOHASH": lambda r: list(map(str_if_bytes, r)),
    "RESET": str_if_bytes,
    "ACL LOG": parse_acl_log_resp3,
    "COMMAND": parse_command_resp3,
    "CONFIG GET": lambda r: {
        str_if_bytes(key) if key is not None else None: (
            str_if_bytes(value) if value is not None else None
        )
        for key, value in r.items()
    },
    **string_keys_to_dict("BGREWRITEAOF BGSAVE", lambda r: True),
    "DEBUG OBJECT": parse_debug_object,
    "MEMORY STATS": parse_memory_stats_resp3,
    "SENTINEL MASTER": parse_sentinel_state_resp3,
    "SENTINEL MASTERS": parse_sentinel_masters_resp3,
    "SENTINEL SENTINELS": parse_sentinel_slaves_and_sentinels_resp3,
    "SENTINEL SLAVES": parse_sentinel_slaves_and_sentinels_resp3,
    "STRALGO": lambda r, **options: parse_stralgo_resp3(r, **options),
    "XINFO CONSUMERS": lambda r: [
        {str_if_bytes(key): value for key, value in x.items()} for x in r
    ],
    "XINFO GROUPS": lambda r: [
        {str_if_bytes(key): value for key, value in d.items()} for d in r
    ],
}
