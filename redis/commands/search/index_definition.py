from enum import Enum


class IndexType(Enum):
    """Enum of the currently supported index types."""

    HASH = 1
    JSON = 2


class IndexDefinition:
    """IndexDefinition is used to define a index definition for automatic
    indexing on Hash or Json update."""

    def __init__(
        self,
        prefix=[],
        filter=None,
        language_field=None,
        language=None,
        score_field=None,
        score=1.0,
        payload_field=None,
        index_type=None,
    ):
        self.args = []
        self._append_index_type(index_type)
        self._append_prefix(prefix)
        self._append_filter(filter)
        self._append_language(language_field, language)
        self._append_score(score_field, score)
        self._append_payload(payload_field)

    def _append_index_type(self, index_type):
        """Append `ON HASH` or `ON JSON` according to the enum."""
        pass

    def _append_prefix(self, prefix):
        """Append PREFIX."""
        pass

    def _append_filter(self, filter):
        """Append FILTER."""
        pass

    def _append_language(self, language_field, language):
        """Append LANGUAGE_FIELD and LANGUAGE."""
        pass

    def _append_score(self, score_field, score):
        """Append SCORE_FIELD and SCORE."""
        pass

    def _append_payload(self, payload_field):
        """Append PAYLOAD_FIELD."""
        pass
