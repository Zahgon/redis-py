def _pairs_to_dict(pairs):
    """Convert a list of [key, value] pairs to a dict without forcing str."""
    pass


def parse_range(response, **kwargs):
    """Parse range response. Used by TS.RANGE and TS.REVRANGE."""
    pass


def parse_m_range(response):
    """Parse multi range response. Used by TS.MRANGE and TS.MREVRANGE.

    Returns a dict keyed by time series name, matching RESP3 native format.
    Each value is [labels_dict, metadata, samples] where metadata is an empty
    list for RESP2 (RESP2 does not include the reducers/aggregators metadata
    that RESP3 returns as the second element).
    """
    pass


def parse_get(response):
    """Parse get response. Used by TS.GET."""
    pass


def parse_m_get(response):
    """Parse multi get response. Used by TS.MGET.

    Returns a dict keyed by time series name, matching RESP3 native format.
    Each value is [labels_dict, [timestamp, value]] or [labels_dict, []] when
    no sample exists.
    """
    pass
