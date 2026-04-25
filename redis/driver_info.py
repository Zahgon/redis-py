from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

_BRACES = {"(", ")", "[", "]", "{", "}"}


def _validate_no_invalid_chars(value: str, field_name: str) -> None:
    """Ensure value contains only printable ASCII without spaces or braces.

    This mirrors the constraints enforced by other Redis clients for values that
    will appear in CLIENT LIST / CLIENT INFO output.
    """
    pass


def _validate_driver_name(name: str) -> None:
    """Validate an upstream driver name.

    The name should look like a typical Python distribution or package name,
    following a simplified form of PEP 503 normalisation rules:

    * start with a lowercase ASCII letter
    * contain only lowercase letters, digits, hyphens and underscores

    Examples of valid names: ``"django-redis"``, ``"celery"``, ``"rq"``.
    """
    pass


def _validate_driver_version(version: str) -> None:
    pass


def _format_driver_entry(driver_name: str, driver_version: str) -> str:
    pass


@dataclass
class DriverInfo:
    """Driver information used to build the CLIENT SETINFO LIB-NAME and LIB-VER values.

    This class consolidates all driver metadata (redis-py version and upstream drivers)
    into a single object that is propagated through connection pools and connections.

    The formatted name follows the pattern::

        name(driver1_vVersion1;driver2_vVersion2)

    Parameters
    ----------
    name : str, optional
        The base library name (default: "redis-py")
    lib_version : str, optional
        The redis-py library version. If None, the version will be determined
        automatically from the installed package.

    Examples
    --------
    >>> info = DriverInfo()
    >>> info.formatted_name
    'redis-py'

    >>> info = DriverInfo().add_upstream_driver("django-redis", "5.4.0")
    >>> info.formatted_name
    'redis-py(django-redis_v5.4.0)'

    >>> info = DriverInfo(lib_version="5.0.0")
    >>> info.lib_version
    '5.0.0'
    """

    name: str = "redis-py"
    lib_version: Optional[str] = None
    _upstream: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize lib_version if not provided."""
        if self.lib_version is None:
            from redis.utils import get_lib_version

            self.lib_version = get_lib_version()

    @property
    def upstream_drivers(self) -> List[str]:
        """Return a copy of the upstream driver entries.

        Each entry is in the form ``"driver-name_vversion"``.
        """
        pass

    def add_upstream_driver(
        self, driver_name: str, driver_version: str
    ) -> "DriverInfo":
        """Add an upstream driver to this instance and return self.

        The most recently added driver appears first in :pyattr:`formatted_name`.
        """
        pass

    @property
    def formatted_name(self) -> str:
        """Return the base name with upstream drivers encoded, if any.

        With no upstream drivers, this is just :pyattr:`name`. Otherwise::

            name(driver1_vX;driver2_vY)
        """
        pass


def resolve_driver_info(
    driver_info: Optional[DriverInfo],
    lib_name: Optional[str],
    lib_version: Optional[str],
) -> DriverInfo:
    """Resolve driver_info from parameters.

    If driver_info is provided, use it. Otherwise, create DriverInfo from
    lib_name and lib_version (using defaults if not provided).

    Parameters
    ----------
    driver_info : DriverInfo, optional
        The DriverInfo instance to use
    lib_name : str, optional
        The library name (default: "redis-py")
    lib_version : str, optional
        The library version (default: auto-detected)

    Returns
    -------
    DriverInfo
        The resolved DriverInfo instance
    """
    pass
