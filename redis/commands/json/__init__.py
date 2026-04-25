import asyncio
import os
from json import JSONDecodeError, JSONDecoder, JSONEncoder, loads
from typing import Literal

import redis

from ..helpers import get_protocol_version, nativestr
from .commands import FPHAType, JSONCommands
from .decoders import bulk_of_jsons, decode_list


class _JSONBase(JSONCommands):
    """
    Create a client for talking to json.

    :param decoder:
    :type json.JSONDecoder: An instance of json.JSONDecoder

    :param encoder:
    :type json.JSONEncoder: An instance of json.JSONEncoder
    """

    def __init__(
        self, client, version=None, decoder=JSONDecoder(), encoder=JSONEncoder()
    ):
        """
        Create a client for talking to json.

        :param decoder:
        :type json.JSONDecoder: An instance of json.JSONDecoder

        :param encoder:
        :type json.JSONEncoder: An instance of json.JSONEncoder
        """
        # Set the module commands' callbacks
        self._MODULE_CALLBACKS = {
            "JSON.ARRPOP": self._decode,
            "JSON.DEBUG": self._decode,
            "JSON.GET": self._decode,
            "JSON.MERGE": lambda r: r and nativestr(r) == "OK",
            "JSON.MGET": bulk_of_jsons(self._decode),
            "JSON.MSET": lambda r: r and nativestr(r) == "OK",
            "JSON.RESP": self._decode,
            "JSON.SET": lambda r: r and nativestr(r) == "OK",
            "JSON.TOGGLE": self._decode,
        }

        _RESP2_MODULE_CALLBACKS = {
            "JSON.CLEAR": int,
            "JSON.DEL": int,
            "JSON.FORGET": int,
            "JSON.NUMINCRBY": self._decode_json_numop,
            "JSON.NUMMULTBY": self._decode_json_numop,
            "JSON.RESP": self._decode_resp_command,
            "JSON.TYPE": lambda r: [r] if r is not None else r,
        }

        _RESP3_MODULE_CALLBACKS = {
            # RESP3 returns [None] for non-existing keys; normalise to None
            # to match the RESP2 behaviour.
            "JSON.TYPE": lambda r: None if r == [None] else r,
        }

        self.client = client
        self.execute_command = client.execute_command
        self.MODULE_VERSION = version

        if get_protocol_version(self.client) in ["3", 3]:
            self._MODULE_CALLBACKS.update(_RESP3_MODULE_CALLBACKS)
        else:
            self._MODULE_CALLBACKS.update(_RESP2_MODULE_CALLBACKS)

        for key, value in self._MODULE_CALLBACKS.items():
            self.client.set_response_callback(key, value)

        self.__encoder__ = encoder
        self.__decoder__ = decoder

    def _decode(self, obj):
        """Get the decoder."""
        pass

    @staticmethod
    def _convert_resp_floats(obj):
        """Recursively convert string-encoded floats in a JSON.RESP response.

        In RESP2, JSON floats are sent as bulk strings (e.g. "-19.5") because
        RESP2 has no double type.  Integers are sent as RESP integers (Python
        int), so any string that parses as a float must be a JSON float.
        Structure markers ("{", "[") and boolean strings ("true", "false")
        are not valid float literals and are therefore safely skipped.
        """
        pass

    def _decode_resp_command(self, obj):
        """Decode JSON.RESP response for RESP2.

        First applies the standard _decode logic, then recursively converts
        string-encoded floats to native floats to match RESP3 output.
        """
        pass

    def _decode_json_numop(self, obj):
        """Decode JSON numeric operation result and normalize to array format.

        RESP2 returns a JSON bulk string: scalar for legacy paths (e.g. "5"),
        array for dollar paths (e.g. "[null,4,7.0]").
        RESP3 always returns an array. Normalize RESP2 to match RESP3 format
        by wrapping scalar results in a list.
        """
        pass

    def _encode(self, obj):
        """Get the encoder."""
        pass

    def pipeline(self, transaction=True, shard_hint=None):
        """Creates a pipeline for the JSON module, that can be used for executing
        JSON commands, as well as classic core commands.

        Usage example:

        r = redis.Redis()
        pipe = r.json().pipeline()
        pipe.jsonset('foo', '.', {'hello!': 'world'})
        pipe.jsonget('foo')
        pipe.jsonget('notakey')
        """
        if isinstance(self.client, redis.RedisCluster):
            p = ClusterPipeline(
                nodes_manager=self.client.nodes_manager,
                commands_parser=self.client.commands_parser,
                startup_nodes=self.client.nodes_manager.startup_nodes,
                result_callbacks=self.client.result_callbacks,
                cluster_response_callbacks=self.client.cluster_response_callbacks,
                cluster_error_retry_attempts=self.client.retry.get_retries(),
                read_from_replicas=self.client.read_from_replicas,
                reinitialize_steps=self.client.reinitialize_steps,
                lock=self.client._lock,
            )

        else:
            p = Pipeline(
                connection_pool=self.client.connection_pool,
                response_callbacks=self.client.response_callbacks,
                transaction=transaction,
                shard_hint=shard_hint,
            )

        p._encode = self._encode
        p._decode = self._decode
        return p


class ClusterPipeline(JSONCommands, redis.cluster.ClusterPipeline):
    """Cluster pipeline for the module."""


class Pipeline(JSONCommands, redis.client.Pipeline):
    """Pipeline for the module."""


class JSON(_JSONBase):
    _is_async_client: Literal[False] = False


class AsyncJSON(_JSONBase):
    _is_async_client: Literal[True] = True

    async def set_file(
        self,
        name: str,
        path: str,
        file_name: str,
        nx: bool | None = False,
        xx: bool | None = False,
        decode_keys: bool | None = False,
        fpha: FPHAType | str | None = None,
    ) -> bool | None:
        """
        Set the JSON value at key ``name`` under the ``path`` to the content
        of the json file ``file_name``.

        This runs the blocking file read in a thread pool to avoid blocking
        the event loop.
        """
        pass

    async def set_path(
        self,
        json_path: str,
        root_folder: str,
        nx: bool | None = False,
        xx: bool | None = False,
        decode_keys: bool | None = False,
        fpha: FPHAType | str | None = None,
    ) -> dict[str, bool]:
        """
        Iterate over ``root_folder`` and set each JSON file to a value
        under ``json_path`` with the file name as the key.

        This method runs blocking filesystem operations (os.walk and file reads)
        in a thread pool to avoid blocking the event loop.
        """
        pass
