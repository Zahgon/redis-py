from typing import List, Optional, Tuple, Union

from redis.commands.search.dialect import DEFAULT_DIALECT


class Query:
    """
    Query is used to build complex queries that have more parameters than just
    the query string. The query string is set in the constructor, and other
    options have setter functions.

    The setter functions return the query object so they can be chained.
    i.e. `Query("foo").verbatim().filter(...)` etc.
    """

    def __init__(self, query_string: str) -> None:
        """
        Create a new query object.
        The query string is set in the constructor, and other options have
        setter functions.
        """

        self._query_string: str = query_string
        self._offset: int = 0
        self._num: int = 10
        self._no_content: bool = False
        self._no_stopwords: bool = False
        self._fields: Optional[List[str]] = None
        self._verbatim: bool = False
        self._with_payloads: bool = False
        self._with_scores: bool = False
        self._scorer: Optional[str] = None
        self._filters: List = list()
        self._ids: Optional[Tuple[str, ...]] = None
        self._slop: int = -1
        self._timeout: Optional[float] = None
        self._in_order: bool = False
        self._sortby: Optional[SortbyField] = None
        self._return_fields: List = []
        self._return_fields_decode_as: dict = {}
        self._summarize_fields: List = []
        self._highlight_fields: List = []
        self._language: Optional[str] = None
        self._expander: Optional[str] = None
        self._dialect: int = DEFAULT_DIALECT

    def query_string(self) -> str:
        """Return the query string of this query only."""
        pass

    def limit_ids(self, *ids) -> "Query":
        """Limit the results to a specific set of pre-known document
        ids of any length."""
        pass

    def return_fields(self, *fields) -> "Query":
        """Add fields to return fields."""
        pass

    def return_field(
        self,
        field: str,
        as_field: Optional[str] = None,
        decode_field: Optional[bool] = True,
        encoding: Optional[str] = "utf8",
    ) -> "Query":
        """
        Add a field to the list of fields to return.

        - **field**: The field to include in query results
        - **as_field**: The alias for the field
        - **decode_field**: Whether to decode the field from bytes to string
        - **encoding**: The encoding to use when decoding the field
        """
        pass

    def _mk_field_list(self, fields: Optional[Union[List[str], str]]) -> List:
        pass

    def summarize(
        self,
        fields: Optional[List] = None,
        context_len: Optional[int] = None,
        num_frags: Optional[int] = None,
        sep: Optional[str] = None,
    ) -> "Query":
        """
        Return an abridged format of the field, containing only the segments of
        the field that contain the matching term(s).

        If `fields` is specified, then only the mentioned fields are
        summarized; otherwise, all results are summarized.

        Server-side defaults are used for each option (except `fields`)
        if not specified

        - **fields** List of fields to summarize. All fields are summarized
        if not specified
        - **context_len** Amount of context to include with each fragment
        - **num_frags** Number of fragments per document
        - **sep** Separator string to separate fragments
        """
        pass

    def highlight(
        self, fields: Optional[List[str]] = None, tags: Optional[List[str]] = None
    ) -> "Query":
        """
        Apply specified markup to matched term(s) within the returned field(s).

        - **fields** If specified, then only those mentioned fields are
        highlighted, otherwise all fields are highlighted
        - **tags** A list of two strings to surround the match.
        """
        pass

    def language(self, language: str) -> "Query":
        """
        Analyze the query as being in the specified language.

        :param language: The language (e.g. `chinese` or `english`)
        """
        pass

    def slop(self, slop: int) -> "Query":
        """Allow a maximum of N intervening non-matched terms between
        phrase terms (0 means exact phrase).
        """
        pass

    def timeout(self, timeout: float) -> "Query":
        """overrides the timeout parameter of the module"""
        self._timeout = timeout
        return self

    def in_order(self) -> "Query":
        """
        Match only documents where the query terms appear in
        the same order in the document.
        i.e., for the query "hello world", we do not match "world hello"
        """
        pass

    def scorer(self, scorer: str) -> "Query":
        """
        Use a different scoring function to evaluate document relevance.
        Default is `TFIDF`.

        Since Redis 8.0 default was changed to BM25STD.

        :param scorer: The scoring function to use
                       (e.g. `TFIDF.DOCNORM` or `BM25`)
        """
        pass

    def get_args(self) -> List[Union[str, int, float]]:
        """Format the redis arguments for this query and return them."""
        args: List[Union[str, int, float]] = [self._query_string]
        args += self._get_args_tags()
        args += self._summarize_fields + self._highlight_fields
        args += ["LIMIT", self._offset, self._num]
        return args

    def _get_args_tags(self) -> List[Union[str, int, float]]:
        pass

    def paging(self, offset: int, num: int) -> "Query":
        """
        Set the paging for the query (defaults to 0..10).

        - **offset**: Paging offset for the results. Defaults to 0
        - **num**: How many results do we want
        """
        pass

    def verbatim(self) -> "Query":
        """Set the query to be verbatim, i.e., use no query expansion
        or stemming.
        """
        pass

    def no_content(self) -> "Query":
        """Set the query to only return ids and not the document content."""
        pass

    def no_stopwords(self) -> "Query":
        """
        Prevent the query from being filtered for stopwords.
        Only useful in very big queries that you are certain contain
        no stopwords.
        """
        pass

    def with_payloads(self) -> "Query":
        """Ask the engine to return document payloads."""
        pass

    def with_scores(self) -> "Query":
        """Ask the engine to return document search scores."""
        pass

    def limit_fields(self, *fields: str) -> "Query":
        """
        Limit the search to specific TEXT fields only.

        - **fields**: Each element should be a string, case sensitive field name
        from the defined schema.
        """
        pass

    def add_filter(self, flt: "Filter") -> "Query":
        """
        Add a numeric or geo filter to the query.
        **Currently, only one of each filter is supported by the engine**

        - **flt**: A NumericFilter or GeoFilter object, used on a
        corresponding field
        """
        pass

    def sort_by(self, field: str, asc: bool = True) -> "Query":
        """
        Add a sortby field to the query.

        - **field** - the name of the field to sort by
        - **asc** - when `True`, sorting will be done in ascending order
        """
        pass

    def expander(self, expander: str) -> "Query":
        """
        Add an expander field to the query.

        - **expander** - the name of the expander
        """
        pass

    def dialect(self, dialect: int) -> "Query":
        """
        Add a dialect field to the query.

        - **dialect** - dialect version to execute the query under
        """
        pass


class Filter:
    def __init__(self, keyword: str, field: str, *args: Union[str, float]) -> None:
        self.args = [keyword, field] + list(args)


class NumericFilter(Filter):
    INF = "+inf"
    NEG_INF = "-inf"

    def __init__(
        self,
        field: str,
        minval: Union[int, str],
        maxval: Union[int, str],
        minExclusive: bool = False,
        maxExclusive: bool = False,
    ) -> None:
        args = [
            minval if not minExclusive else f"({minval}",
            maxval if not maxExclusive else f"({maxval}",
        ]

        Filter.__init__(self, "FILTER", field, *args)


class GeoFilter(Filter):
    METERS = "m"
    KILOMETERS = "km"
    FEET = "ft"
    MILES = "mi"

    def __init__(
        self, field: str, lon: float, lat: float, radius: float, unit: str = KILOMETERS
    ) -> None:
        Filter.__init__(self, "GEOFILTER", field, lon, lat, radius, unit)


class SortbyField:
    def __init__(self, field: str, asc=True) -> None:
        self.args = [field, "ASC" if asc else "DESC"]
