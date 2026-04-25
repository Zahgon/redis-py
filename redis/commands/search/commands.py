import itertools
import time
from typing import Any, Dict, List, Optional, Union

from redis._parsers.helpers import pairs_to_dict
from redis.client import NEVER_DECODE, Pipeline
from redis.commands.search.hybrid_query import (
    CombineResultsMethod,
    HybridCursorQuery,
    HybridPostProcessingConfig,
    HybridQuery,
)
from redis.commands.search.hybrid_result import HybridCursorResult, HybridResult
from redis.utils import (
    check_protocol_version,
    decode_field_value,
    deprecated_function,
    experimental_method,
    str_if_bytes,
)

from ..helpers import get_protocol_version
from .aggregation import (
    AggregateRequest,
    AggregateResult,
    Cursor,
)
from .document import Document
from .field import Field
from .index_definition import IndexDefinition
from .profile_information import ProfileInformation
from .query import Query
from .result import Result
from .suggestion import SuggestionParser

NUMERIC = "NUMERIC"

CREATE_CMD = "FT.CREATE"
ALTER_CMD = "FT.ALTER"
SEARCH_CMD = "FT.SEARCH"
ADD_CMD = "FT.ADD"
ADDHASH_CMD = "FT.ADDHASH"
DROPINDEX_CMD = "FT.DROPINDEX"
EXPLAIN_CMD = "FT.EXPLAIN"
EXPLAINCLI_CMD = "FT.EXPLAINCLI"
DEL_CMD = "FT.DEL"
AGGREGATE_CMD = "FT.AGGREGATE"
PROFILE_CMD = "FT.PROFILE"
CURSOR_CMD = "FT.CURSOR"
SPELLCHECK_CMD = "FT.SPELLCHECK"
DICT_ADD_CMD = "FT.DICTADD"
DICT_DEL_CMD = "FT.DICTDEL"
DICT_DUMP_CMD = "FT.DICTDUMP"
MGET_CMD = "FT.MGET"
CONFIG_CMD = "FT.CONFIG"
TAGVALS_CMD = "FT.TAGVALS"
ALIAS_ADD_CMD = "FT.ALIASADD"
ALIAS_UPDATE_CMD = "FT.ALIASUPDATE"
ALIAS_DEL_CMD = "FT.ALIASDEL"
INFO_CMD = "FT.INFO"
SUGADD_COMMAND = "FT.SUGADD"
SUGDEL_COMMAND = "FT.SUGDEL"
SUGLEN_COMMAND = "FT.SUGLEN"
SUGGET_COMMAND = "FT.SUGGET"
SYNUPDATE_CMD = "FT.SYNUPDATE"
SYNDUMP_CMD = "FT.SYNDUMP"
HYBRID_CMD = "FT.HYBRID"

NOOFFSETS = "NOOFFSETS"
NOFIELDS = "NOFIELDS"
NOHL = "NOHL"
NOFREQS = "NOFREQS"
MAXTEXTFIELDS = "MAXTEXTFIELDS"
TEMPORARY = "TEMPORARY"
STOPWORDS = "STOPWORDS"
SKIPINITIALSCAN = "SKIPINITIALSCAN"
WITHSCORES = "WITHSCORES"
FUZZY = "FUZZY"
WITHPAYLOADS = "WITHPAYLOADS"


class SearchCommands:
    """Search commands."""

    def _init_module_callbacks(self):
        """Build the RESP2/RESP3 module callback maps.

        Called from ``Search.__init__``, ``Pipeline.__init__`` and
        ``AsyncPipeline.__init__`` so that the mapping is defined in a
        single place rather than duplicated across all three classes.
        """
        pass

    # Commands whose parsers require a ``query`` kwarg.  When invoked as a
    # pipeline response-callback the kwarg is carried inside the options dict
    # that ``execute_command`` stored earlier.  If the key is absent (e.g. a
    # raw ``execute_command("FT.SEARCH", ...)`` call), return the response
    # unparsed so we don't crash.
    _QUERY_REQUIRED_CMDS = frozenset(
        {SEARCH_CMD, AGGREGATE_CMD, CURSOR_CMD, HYBRID_CMD, PROFILE_CMD}
    )

    def _parse_results(self, cmd, res, **kwargs):
        if cmd in self._QUERY_REQUIRED_CMDS and "query" not in kwargs:
            return res
        if check_protocol_version(get_protocol_version(self.client), 3):
            cb = self._RESP3_MODULE_CALLBACKS.get(cmd)
        else:
            cb = self._RESP2_MODULE_CALLBACKS.get(cmd)
        if cb:
            return cb(res, **kwargs)
        return res

    # ---- RESP2 parsers ----

    # Known FT.INFO attribute keys that are followed by a value (key-value pairs)
    _INFO_ATTR_PAIR_KEYS = frozenset(
        {"identifier", "attribute", "type", "WEIGHT", "SEPARATOR", "PHONETIC"}
    )

    def _parse_info(self, res, **kwargs):
        pass

    @staticmethod
    def _normalize_info_attribute(attr_list):
        """Convert a RESP2 flat attribute list to a RESP3-style dict.

        RESP2 format: [identifier, name, attribute, alias, type, TEXT, WEIGHT, 1,
                        SORTABLE, NOSTEM]
        RESP3 format: {"identifier": name, "attribute": alias, "type": "TEXT",
                        "WEIGHT": "1", "flags": ["SORTABLE", "NOSTEM"]}
        """
        pass

    def _parse_search(self, res, **kwargs):
        pass

    def _parse_hybrid_search(self, res, **kwargs):
        pass

    def _parse_aggregate(self, res, **kwargs):
        pass

    def _parse_profile(self, res, **kwargs):
        pass

    def _parse_spellcheck(self, res, **kwargs):
        pass

    def _parse_config_get(self, res, **kwargs):
        pass

    def _parse_syndump(self, res, **kwargs):
        pass

    # ---- RESP3 parsers ----

    def _parse_search_resp3(self, res, **kwargs):
        """Parse RESP3 FT.SEARCH response into a Result object."""
        pass

    def _parse_aggregate_resp3(self, res, **kwargs):
        """Parse RESP3 FT.AGGREGATE response into an AggregateResult object."""
        pass

    def _parse_hybrid_search_resp3(self, res, **kwargs):
        """Parse RESP3 FT.HYBRID response into HybridResult/HybridCursorResult."""
        pass

    def _parse_spellcheck_resp3(self, res, **kwargs):
        """Parse RESP3 FT.SPELLCHECK response into unified format.

        RESP3 format:
            {"results": {"term": [{"suggestion": score}, ...], ...}}
        Unified format (matches RESP2 parsed output):
            {"term": [{"score": score_str, "suggestion": suggestion}, ...], ...}
        """
        pass

    def _parse_profile_resp3(self, res, **kwargs):
        """Parse RESP3 FT.PROFILE response into (result, ProfileInformation) tuple.

        RESP3 format (aligned, RediSearch >= MOD-6816):
            {"Results": {search/aggregate result dict},
             "Profile": {profile information dict}}

        Older RediSearch versions may return a list (same as RESP2) even
        when the connection uses RESP3.  In that case we delegate to the
        RESP2 ``_parse_profile`` parser.
        """
        pass

    @staticmethod
    def _resp3_profile_dict_to_list(data):
        """Convert RESP3 profile dict into RESP2-style list-of-pairs.

        On pre-7.9.0 servers, RESP2 returns profile data as a list of
        ``[key, value]`` pairs where nested structures are flat alternating
        key-value lists.  RESP3 returns the same data as nested dicts.
        This converts the RESP3 dict back to the RESP2 list format so
        consumers see a consistent structure regardless of protocol.

        Key structural difference: when a dict value is a list of dicts
        (e.g. ``"Child iterators": [{...}, {...}]``), RESP2 expands each
        dict as a separate sibling element in the parent flat list rather
        than keeping them nested inside a single value.
        """
        pass

    @staticmethod
    def _to_string_recursive(obj):
        """Recursively convert bytes keys/values to strings in nested structures.

        Handles dicts, lists, and scalar values. Non-bytes, non-container
        values (int, float, None, bool) are left unchanged.
        """
        pass

    def _parse_info_resp3(self, res, **kwargs):
        """Parse RESP3 FT.INFO response, normalising bytes to strings.

        RESP3 returns a native dict with bytes keys/values. This converts
        all keys and string-like values to ``str`` so that the returned
        dict has the same shape as the RESP2 parser output.
        """
        pass

    def _parse_config_get_resp3(self, res, **kwargs):
        """Parse RESP3 FT.CONFIG GET response, normalising bytes to strings.

        RESP3 already returns a dict, but keys and values are bytes.
        Convert them to match the RESP2 output format.
        """
        pass

    def _parse_syndump_resp3(self, res, **kwargs):
        """Parse RESP3 FT.SYNDUMP response, normalising bytes to strings.

        RESP3 already returns a dict, but keys and values are bytes.
        Convert them to match the RESP2 output format.
        """
        pass

    def batch_indexer(self, chunk_size=100):
        """
        Create a new batch indexer from the client with a given chunk size
        """
        pass

    def create_index(
        self,
        fields: List[Field],
        no_term_offsets: bool = False,
        no_field_flags: bool = False,
        stopwords: Optional[List[str]] = None,
        definition: Optional[IndexDefinition] = None,
        max_text_fields=False,
        temporary=None,
        no_highlight: bool = False,
        no_term_frequencies: bool = False,
        skip_initial_scan: bool = False,
    ):
        """
        Creates the search index. The index must not already exist.

        For more information, see https://redis.io/commands/ft.create/

        Args:
            fields: A list of Field objects.
            no_term_offsets: If `true`, term offsets will not be saved in the index.
            no_field_flags: If true, field flags that allow searching in specific fields
                            will not be saved.
            stopwords: If provided, the index will be created with this custom stopword
                       list. The list can be empty.
            definition: If provided, the index will be created with this custom index
                        definition.
            max_text_fields: If true, indexes will be encoded as if there were more than
                             32 text fields, allowing for additional fields beyond 32.
            temporary: Creates a lightweight temporary index which will expire after the
                       specified period of inactivity. The internal idle timer is reset
                       whenever the index is searched or added to.
            no_highlight: If true, disables highlighting support. Also implied by
                          `no_term_offsets`.
            no_term_frequencies: If true, term frequencies will not be saved in the
                                 index.
            skip_initial_scan: If true, the initial scan and indexing will be skipped.

        """
        pass

    def alter_schema_add(self, fields: Union[Field, List[Field]]):
        """
        Alter the existing search index by adding new fields. The index
        must already exist.

        ### Parameters:

        - **fields**: a list of Field objects to add for the index

        For more information see `FT.ALTER <https://redis.io/commands/ft.alter>`_.
        """  # noqa
        pass

    def dropindex(self, delete_documents: bool = False):
        """
        Drop the index if it exists.
        Replaced `drop_index` in RediSearch 2.0.
        Default behavior was changed to not delete the indexed documents.

        ### Parameters:

        - **delete_documents**: If `True`, all documents will be deleted.

        For more information see `FT.DROPINDEX <https://redis.io/commands/ft.dropindex>`_.
        """  # noqa
        pass

    def _add_document(
        self,
        doc_id,
        conn=None,
        nosave=False,
        score=1.0,
        payload=None,
        replace=False,
        partial=False,
        language=None,
        no_create=False,
        **fields,
    ):
        """
        Internal add_document used for both batch and single doc indexing
        """
        pass

    def _add_document_hash(
        self, doc_id, conn=None, score=1.0, language=None, replace=False
    ):
        """
        Internal add_document_hash used for both batch and single doc indexing
        """
        pass

    @deprecated_function(
        version="2.0.0", reason="deprecated since redisearch 2.0, call hset instead"
    )
    def add_document(
        self,
        doc_id: str,
        nosave: bool = False,
        score: float = 1.0,
        payload: Optional[bool] = None,
        replace: bool = False,
        partial: bool = False,
        language: Optional[str] = None,
        no_create: bool = False,
        **fields: List[str],
    ):
        """
        Add a single document to the index.

        Args:

            doc_id: the id of the saved document.
            nosave: if set to true, we just index the document, and don't
                      save a copy of it. This means that searches will just
                      return ids.
            score: the document ranking, between 0.0 and 1.0
            payload: optional inner-index payload we can save for fast
                     access in scoring functions
            replace: if True, and the document already is in the index,
                     we perform an update and reindex the document
            partial: if True, the fields specified will be added to the
                       existing document.
                       This has the added benefit that any fields specified
                       with `no_index`
                       will not be reindexed again. Implies `replace`
            language: Specify the language used for document tokenization.
            no_create: if True, the document is only updated and reindexed
                         if it already exists.
                         If the document does not exist, an error will be
                         returned. Implies `replace`
            fields: kwargs dictionary of the document fields to be saved
                    and/or indexed.
                    NOTE: Geo points shoule be encoded as strings of "lon,lat"
        """  # noqa
        pass

    @deprecated_function(
        version="2.0.0", reason="deprecated since redisearch 2.0, call hset instead"
    )
    def add_document_hash(self, doc_id, score=1.0, language=None, replace=False):
        """
        Add a hash document to the index.

        ### Parameters

        - **doc_id**: the document's id. This has to be an existing HASH key
                      in Redis that will hold the fields the index needs.
        - **score**:  the document ranking, between 0.0 and 1.0
        - **replace**: if True, and the document already is in the index, we
                      perform an update and reindex the document
        - **language**: Specify the language used for document tokenization.
        """  # noqa
        pass

    @deprecated_function(version="2.0.0", reason="deprecated since redisearch 2.0")
    def delete_document(self, doc_id, conn=None, delete_actual_document=False):
        """
        Delete a document from index
        Returns 1 if the document was deleted, 0 if not

        ### Parameters

        - **delete_actual_document**: if set to True, RediSearch also delete
                                      the actual document if it is in the index
        """  # noqa
        pass

    def load_document(self, id, field_encodings=None):
        """
        Load a single document by id

        - **field_encodings**: optional dict mapping field names to encodings.
          If a field's encoding is ``None`` the raw bytes value is preserved
          (useful for binary data such as vectors).
        """
        pass

    @deprecated_function(version="2.0.0", reason="deprecated since redisearch 2.0")
    def get(self, *ids):
        """
        Returns the full contents of multiple documents.

        ### Parameters

        - **ids**: the ids of the saved documents.

        """

        return self.execute_command(MGET_CMD, self.index_name, *ids)

    def info(self):
        """
        Get info an stats about the the current index, including the number of
        documents, memory consumption, etc

        For more information see `FT.INFO <https://redis.io/commands/ft.info>`_.
        """

        res = self.execute_command(INFO_CMD, self.index_name)
        return self._parse_results(INFO_CMD, res)

    def get_params_args(
        self, query_params: Optional[Dict[str, Union[str, int, float, bytes]]]
    ):
        if query_params is None:
            return []
        args = []
        if len(query_params) > 0:
            args.append("PARAMS")
            args.append(len(query_params) * 2)
            for key, value in query_params.items():
                args.append(key)
                args.append(value)
        return args

    def _mk_query_args(
        self, query, query_params: Optional[Dict[str, Union[str, int, float, bytes]]]
    ):
        args = [self.index_name]

        if isinstance(query, str):
            # convert the query from a text to a query object
            query = Query(query)
        if not isinstance(query, Query):
            raise ValueError(f"Bad query type {type(query)}")

        args += query.get_args()
        args += self.get_params_args(query_params)

        return args, query

    def search(
        self,
        query: Union[str, Query],
        query_params: Union[Dict[str, Union[str, int, float, bytes]], None] = None,
    ):
        """
        Search the index for a given query, and return a result of documents

        ### Parameters

        - **query**: the search query. Either a text for simple queries with
                     default parameters, or a Query object for complex queries.
                     See RediSearch's documentation on query format

        For more information see `FT.SEARCH <https://redis.io/commands/ft.search>`_.
        """  # noqa
        args, query = self._mk_query_args(query, query_params=query_params)
        st = time.monotonic()

        options = {}
        if get_protocol_version(self.client) not in ["3", 3]:
            options[NEVER_DECODE] = True
        options["query"] = query

        res = self.execute_command(SEARCH_CMD, *args, **options)

        if isinstance(res, Pipeline):
            return res

        return self._parse_results(
            SEARCH_CMD, res, query=query, duration=(time.monotonic() - st) * 1000.0
        )

    @experimental_method()
    def hybrid_search(
        self,
        query: HybridQuery,
        combine_method: Optional[CombineResultsMethod] = None,
        post_processing: Optional[HybridPostProcessingConfig] = None,
        params_substitution: Optional[Dict[str, Union[str, int, float, bytes]]] = None,
        timeout: Optional[int] = None,
        cursor: Optional[HybridCursorQuery] = None,
    ) -> Union[HybridResult, HybridCursorResult, Pipeline]:
        """
        Execute a hybrid search using both text and vector queries

        Args:
            - **query**: HybridQuery object
                        Contains the text and vector queries
            - **combine_method**: CombineResultsMethod object
                        Contains the combine method and parameters
            - **post_processing**: HybridPostProcessingConfig object
                        Contains the post processing configuration
            - **params_substitution**: Dict[str, Union[str, int, float, bytes]]
                        Contains the parameters substitution
            - **timeout**: int - contains the timeout in milliseconds
            - **cursor**: HybridCursorQuery object - contains the cursor configuration


        For more information see `FT.SEARCH <https://redis.io/commands/ft.hybrid>`.
        """
        pass

    def explain(
        self,
        query: Union[str, Query],
        query_params: Optional[Dict[str, Union[str, int, float, bytes]]] = None,
    ):
        """Returns the execution plan for a complex query.

        For more information see `FT.EXPLAIN <https://redis.io/commands/ft.explain>`_.
        """  # noqa
        pass

    def explain_cli(self, query: Union[str, Query]):  # noqa
        raise NotImplementedError("EXPLAINCLI will not be implemented.")

    def aggregate(
        self,
        query: Union[AggregateRequest, Cursor],
        query_params: Optional[Dict[str, Union[str, int, float, bytes]]] = None,
    ):
        """
        Issue an aggregation query.

        ### Parameters

        **query**: This can be either an `AggregateRequest`, or a `Cursor`

        An `AggregateResult` object is returned. You can access the rows from
        its `rows` property, which will always yield the rows of the result.

        For more information see `FT.AGGREGATE <https://redis.io/commands/ft.aggregate>`_.
        """  # noqa
        pass

    def _get_aggregate_result(
        self, raw: List, query: Union[AggregateRequest, Cursor], has_cursor: bool
    ):
        pass

    def profile(
        self,
        query: Union[Query, AggregateRequest],
        limited: bool = False,
        query_params: Optional[Dict[str, Union[str, int, float, bytes]]] = None,
    ):
        """
        Performs a search or aggregate command and collects performance
        information.

        ### Parameters

        **query**: This can be either an `AggregateRequest` or `Query`.
        **limited**: If set to True, removes details of reader iterator.
        **query_params**: Define one or more value parameters.
        Each parameter has a name and a value.

        """
        pass

    def spellcheck(self, query, distance=None, include=None, exclude=None):
        """
        Issue a spellcheck query

        Args:

            query: search query.
            distance: the maximal Levenshtein distance for spelling
                       suggestions (default: 1, max: 4).
            include: specifies an inclusion custom dictionary.
            exclude: specifies an exclusion custom dictionary.

        For more information see `FT.SPELLCHECK <https://redis.io/commands/ft.spellcheck>`_.
        """  # noqa
        pass

    def dict_add(self, name: str, *terms: List[str]):
        """Adds terms to a dictionary.

        ### Parameters

        - **name**: Dictionary name.
        - **terms**: List of items for adding to the dictionary.

        For more information see `FT.DICTADD <https://redis.io/commands/ft.dictadd>`_.
        """  # noqa
        pass

    def dict_del(self, name: str, *terms: List[str]):
        """Deletes terms from a dictionary.

        ### Parameters

        - **name**: Dictionary name.
        - **terms**: List of items for removing from the dictionary.

        For more information see `FT.DICTDEL <https://redis.io/commands/ft.dictdel>`_.
        """  # noqa
        pass

    def dict_dump(self, name: str):
        """Dumps all terms in the given dictionary.

        ### Parameters

        - **name**: Dictionary name.

        For more information see `FT.DICTDUMP <https://redis.io/commands/ft.dictdump>`_.
        """  # noqa
        pass

    @deprecated_function(
        version="8.0.0",
        reason="deprecated since Redis 8.0, call config_set from core module instead",
    )
    def config_set(self, option: str, value: str) -> bool:
        """Set runtime configuration option.

        ### Parameters

        - **option**: the name of the configuration option.
        - **value**: a value for the configuration option.

        For more information see `FT.CONFIG SET <https://redis.io/commands/ft.config-set>`_.
        """  # noqa
        cmd = [CONFIG_CMD, "SET", option, value]
        raw = self.execute_command(*cmd)
        return raw == "OK"

    @deprecated_function(
        version="8.0.0",
        reason="deprecated since Redis 8.0, call config_get from core module instead",
    )
    def config_get(self, option: str) -> str:
        """Get runtime configuration option value.

        ### Parameters

        - **option**: the name of the configuration option.

        For more information see `FT.CONFIG GET <https://redis.io/commands/ft.config-get>`_.
        """  # noqa
        pass

    def tagvals(self, tagfield: str):
        """
        Return a list of all possible tag values

        ### Parameters

        - **tagfield**: Tag field name

        For more information see `FT.TAGVALS <https://redis.io/commands/ft.tagvals>`_.
        """  # noqa
        pass

    def aliasadd(self, alias: str):
        """
        Alias a search index - will fail if alias already exists

        ### Parameters

        - **alias**: Name of the alias to create

        For more information see `FT.ALIASADD <https://redis.io/commands/ft.aliasadd>`_.
        """  # noqa
        pass

    def aliasupdate(self, alias: str):
        """
        Updates an alias - will fail if alias does not already exist

        ### Parameters

        - **alias**: Name of the alias to create

        For more information see `FT.ALIASUPDATE <https://redis.io/commands/ft.aliasupdate>`_.
        """  # noqa
        pass

    def aliasdel(self, alias: str):
        """
        Removes an alias to a search index

        ### Parameters

        - **alias**: Name of the alias to delete

        For more information see `FT.ALIASDEL <https://redis.io/commands/ft.aliasdel>`_.
        """  # noqa
        pass

    def sugadd(self, key, *suggestions, **kwargs):
        """
        Add suggestion terms to the AutoCompleter engine. Each suggestion has
        a score and string.
        If kwargs["increment"] is true and the terms are already in the
        server's dictionary, we increment their scores.

        For more information see `FT.SUGADD <https://redis.io/commands/ft.sugadd/>`_.
        """  # noqa
        pass

    def suglen(self, key: str) -> int:
        """
        Return the number of entries in the AutoCompleter index.

        For more information see `FT.SUGLEN <https://redis.io/commands/ft.suglen>`_.
        """  # noqa
        pass

    def sugdel(self, key: str, string: str) -> int:
        """
        Delete a string from the AutoCompleter index.
        Returns 1 if the string was found and deleted, 0 otherwise.

        For more information see `FT.SUGDEL <https://redis.io/commands/ft.sugdel>`_.
        """  # noqa
        pass

    def sugget(
        self,
        key: str,
        prefix: str,
        fuzzy: bool = False,
        num: int = 10,
        with_scores: bool = False,
        with_payloads: bool = False,
    ) -> List[SuggestionParser]:
        """
        Get a list of suggestions from the AutoCompleter, for a given prefix.

        Parameters:

        prefix : str
            The prefix we are searching. **Must be valid ascii or utf-8**
        fuzzy : bool
            If set to true, the prefix search is done in fuzzy mode.
            **NOTE**: Running fuzzy searches on short (<3 letters) prefixes
            can be very
            slow, and even scan the entire index.
        with_scores : bool
            If set to true, we also return the (refactored) score of
            each suggestion.
            This is normally not needed, and is NOT the original score
            inserted into the index.
        with_payloads : bool
            Return suggestion payloads
        num : int
            The maximum number of results we return. Note that we might
            return less. The algorithm trims irrelevant suggestions.

        Returns:

        list:
             A list of Suggestion objects. If with_scores was False, the
             score of all suggestions is 1.

        For more information see `FT.SUGGET <https://redis.io/commands/ft.sugget>`_.
        """  # noqa
        pass

    def synupdate(self, groupid: str, skipinitial: bool = False, *terms: List[str]):
        """
        Updates a synonym group.
        The command is used to create or update a synonym group with
        additional terms.
        Only documents which were indexed after the update will be affected.

        Parameters:

        groupid :
            Synonym group id.
        skipinitial : bool
            If set to true, we do not scan and index.
        terms :
            The terms.

        For more information see `FT.SYNUPDATE <https://redis.io/commands/ft.synupdate>`_.
        """  # noqa
        pass

    def syndump(self):
        """
        Dumps the contents of a synonym group.

        The command is used to dump the synonyms data structure.
        Returns a list of synonym terms and their synonym group ids.

        For more information see `FT.SYNDUMP <https://redis.io/commands/ft.syndump>`_.
        """  # noqa
        pass


class AsyncSearchCommands(SearchCommands):
    async def info(self):
        """
        Get info an stats about the the current index, including the number of
        documents, memory consumption, etc

        For more information see `FT.INFO <https://redis.io/commands/ft.info>`_.
        """

        res = await self.execute_command(INFO_CMD, self.index_name)
        return self._parse_results(INFO_CMD, res)

    async def search(
        self,
        query: Union[str, Query],
        query_params: Optional[Dict[str, Union[str, int, float, bytes]]] = None,
    ):
        """
        Search the index for a given query, and return a result of documents

        ### Parameters

        - **query**: the search query. Either a text for simple queries with
                     default parameters, or a Query object for complex queries.
                     See RediSearch's documentation on query format

        For more information see `FT.SEARCH <https://redis.io/commands/ft.search>`_.
        """  # noqa
        args, query = self._mk_query_args(query, query_params=query_params)
        st = time.monotonic()

        options = {}
        if get_protocol_version(self.client) not in ["3", 3]:
            options[NEVER_DECODE] = True
        options["query"] = query

        res = await self.execute_command(SEARCH_CMD, *args, **options)

        if isinstance(res, Pipeline):
            return res

        return self._parse_results(
            SEARCH_CMD, res, query=query, duration=(time.monotonic() - st) * 1000.0
        )

    @experimental_method()
    async def hybrid_search(
        self,
        query: HybridQuery,
        combine_method: Optional[CombineResultsMethod] = None,
        post_processing: Optional[HybridPostProcessingConfig] = None,
        params_substitution: Optional[Dict[str, Union[str, int, float, bytes]]] = None,
        timeout: Optional[int] = None,
        cursor: Optional[HybridCursorQuery] = None,
    ) -> Union[HybridResult, HybridCursorResult, Pipeline]:
        """
        Execute a hybrid search using both text and vector queries

        Args:
            - **query**: HybridQuery object
                        Contains the text and vector queries
            - **combine_method**: CombineResultsMethod object
                        Contains the combine method and parameters
            - **post_processing**: HybridPostProcessingConfig object
                        Contains the post processing configuration
            - **params_substitution**: Dict[str, Union[str, int, float, bytes]]
                        Contains the parameters substitution
            - **timeout**: int - contains the timeout in milliseconds
            - **cursor**: HybridCursorQuery object - contains the cursor configuration


        For more information see `FT.SEARCH <https://redis.io/commands/ft.hybrid>`.
        """
        pass

    async def aggregate(
        self,
        query: Union[AggregateResult, Cursor],
        query_params: Optional[Dict[str, Union[str, int, float, bytes]]] = None,
    ):
        """
        Issue an aggregation query.

        ### Parameters

        **query**: This can be either an `AggregateRequest`, or a `Cursor`

        An `AggregateResult` object is returned. You can access the rows from
        its `rows` property, which will always yield the rows of the result.

        For more information see `FT.AGGREGATE <https://redis.io/commands/ft.aggregate>`_.
        """  # noqa
        pass

    async def profile(
        self,
        query: Union[Query, AggregateRequest],
        limited: bool = False,
        query_params: Optional[Dict[str, Union[str, int, float, bytes]]] = None,
    ):
        """
        Performs a search or aggregate command and collects performance
        information.

        ### Parameters

        **query**: This can be either an `AggregateRequest` or `Query`.
        **limited**: If set to True, removes details of reader iterator.
        **query_params**: Define one or more value parameters.
        Each parameter has a name and a value.

        """
        pass

    async def spellcheck(self, query, distance=None, include=None, exclude=None):
        """
        Issue a spellcheck query

        ### Parameters

        **query**: search query.
        **distance***: the maximal Levenshtein distance for spelling
                       suggestions (default: 1, max: 4).
        **include**: specifies an inclusion custom dictionary.
        **exclude**: specifies an exclusion custom dictionary.

        For more information see `FT.SPELLCHECK <https://redis.io/commands/ft.spellcheck>`_.
        """  # noqa
        pass

    @deprecated_function(
        version="8.0.0",
        reason="deprecated since Redis 8.0, call config_set from core module instead",
    )
    async def config_set(self, option: str, value: str) -> bool:
        """Set runtime configuration option.

        ### Parameters

        - **option**: the name of the configuration option.
        - **value**: a value for the configuration option.

        For more information see `FT.CONFIG SET <https://redis.io/commands/ft.config-set>`_.
        """  # noqa
        cmd = [CONFIG_CMD, "SET", option, value]
        raw = await self.execute_command(*cmd)
        return raw == "OK"

    @deprecated_function(
        version="8.0.0",
        reason="deprecated since Redis 8.0, call config_get from core module instead",
    )
    async def config_get(self, option: str) -> str:
        """Get runtime configuration option value.

        ### Parameters

        - **option**: the name of the configuration option.

        For more information see `FT.CONFIG GET <https://redis.io/commands/ft.config-get>`_.
        """  # noqa
        pass

    async def load_document(self, id, field_encodings=None):
        """
        Load a single document by id

        - **field_encodings**: optional dict mapping field names to encodings.
          If a field's encoding is ``None`` the raw bytes value is preserved
          (useful for binary data such as vectors).
        """
        pass

    async def sugadd(self, key, *suggestions, **kwargs):
        """
        Add suggestion terms to the AutoCompleter engine. Each suggestion has
        a score and string.
        If kwargs["increment"] is true and the terms are already in the
        server's dictionary, we increment their scores.

        For more information see `FT.SUGADD <https://redis.io/commands/ft.sugadd>`_.
        """  # noqa
        pass

    async def sugget(
        self,
        key: str,
        prefix: str,
        fuzzy: bool = False,
        num: int = 10,
        with_scores: bool = False,
        with_payloads: bool = False,
    ) -> List[SuggestionParser]:
        """
        Get a list of suggestions from the AutoCompleter, for a given prefix.

        Parameters:

        prefix : str
            The prefix we are searching. **Must be valid ascii or utf-8**
        fuzzy : bool
            If set to true, the prefix search is done in fuzzy mode.
            **NOTE**: Running fuzzy searches on short (<3 letters) prefixes
            can be very
            slow, and even scan the entire index.
        with_scores : bool
            If set to true, we also return the (refactored) score of
            each suggestion.
            This is normally not needed, and is NOT the original score
            inserted into the index.
        with_payloads : bool
            Return suggestion payloads
        num : int
            The maximum number of results we return. Note that we might
            return less. The algorithm trims irrelevant suggestions.

        Returns:

        list:
             A list of Suggestion objects. If with_scores was False, the
             score of all suggestions is 1.

        For more information see `FT.SUGGET <https://redis.io/commands/ft.sugget>`_.
        """  # noqa
        pass
