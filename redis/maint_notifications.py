import enum
import ipaddress
import logging
import re
import threading
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from redis.observability.attributes import get_pool_name
from redis.observability.recorder import (
    record_connection_handoff,
    record_connection_relaxed_timeout,
    record_maint_notification_count,
)
from redis.typing import Number

if TYPE_CHECKING:
    from redis.cluster import MaintNotificationsAbstractRedisCluster

logger = logging.getLogger(__name__)


class MaintenanceState(enum.Enum):
    NONE = "none"
    MOVING = "moving"
    MAINTENANCE = "maintenance"


class EndpointType(enum.Enum):
    """Valid endpoint types used in CLIENT MAINT_NOTIFICATIONS command."""

    INTERNAL_IP = "internal-ip"
    INTERNAL_FQDN = "internal-fqdn"
    EXTERNAL_IP = "external-ip"
    EXTERNAL_FQDN = "external-fqdn"
    NONE = "none"

    def __str__(self):
        """Return the string value of the enum."""
        return self.value


if TYPE_CHECKING:
    from redis.connection import (
        MaintNotificationsAbstractConnection,
        MaintNotificationsAbstractConnectionPool,
    )


class MaintenanceNotification(ABC):
    """
    Base class for maintenance notifications sent through push messages by Redis server.

    This class provides common functionality for all maintenance notifications including
    unique identification and TTL (Time-To-Live) functionality.

    Attributes:
        id (int): Unique identifier for this notification
        ttl (int): Time-to-live in seconds for this notification
        creation_time (float): Timestamp when the notification was created/read
    """

    def __init__(self, id: int, ttl: int):
        """
        Initialize a new MaintenanceNotification with unique ID and TTL functionality.

        Args:
            id (int): Unique identifier for this notification
            ttl (int): Time-to-live in seconds for this notification
        """
        self.id = id
        self.ttl = ttl
        self.creation_time = time.monotonic()
        self.expire_at = self.creation_time + self.ttl

    def is_expired(self) -> bool:
        """
        Check if this notification has expired based on its TTL
        and creation time.

        Returns:
            bool: True if the notification has expired, False otherwise
        """
        return time.monotonic() > (self.creation_time + self.ttl)

    @abstractmethod
    def __repr__(self) -> str:
        """
        Return a string representation of the maintenance notification.

        This method must be implemented by all concrete subclasses.

        Returns:
            str: String representation of the notification
        """
        pass

    @abstractmethod
    def __eq__(self, other) -> bool:
        """
        Compare two maintenance notifications for equality.

        This method must be implemented by all concrete subclasses.
        Notifications are typically considered equal if they have the same id
        and are of the same type.

        Args:
            other: The other object to compare with

        Returns:
            bool: True if the notifications are equal, False otherwise
        """
        pass

    @abstractmethod
    def __hash__(self) -> int:
        """
        Return a hash value for the maintenance notification.

        This method must be implemented by all concrete subclasses to allow
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value for the notification
        """
        pass


class NodeMovingNotification(MaintenanceNotification):
    """
    This notification is received when a node is replaced with a new node
    during cluster rebalancing or maintenance operations.
    """

    def __init__(
        self,
        id: int,
        new_node_host: Optional[str],
        new_node_port: Optional[int],
        ttl: int,
    ):
        """
        Initialize a new NodeMovingNotification.

        Args:
            id (int): Unique identifier for this notification
            new_node_host (str): Hostname or IP address of the new replacement node
            new_node_port (int): Port number of the new replacement node
            ttl (int): Time-to-live in seconds for this notification
        """
        super().__init__(id, ttl)
        self.new_node_host = new_node_host
        self.new_node_port = new_node_port

    def __repr__(self) -> str:
        expiry_time = self.expire_at
        remaining = max(0, expiry_time - time.monotonic())

        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"new_node_host='{self.new_node_host}', "
            f"new_node_port={self.new_node_port}, "
            f"ttl={self.ttl}, "
            f"creation_time={self.creation_time}, "
            f"expires_at={expiry_time}, "
            f"remaining={remaining:.1f}s, "
            f"expired={self.is_expired()}"
            f")"
        )

    def __eq__(self, other) -> bool:
        """
        Two NodeMovingNotification notifications are considered equal if they have the same
        id, new_node_host, and new_node_port.
        """
        if not isinstance(other, NodeMovingNotification):
            return False
        return (
            self.id == other.id
            and self.new_node_host == other.new_node_host
            and self.new_node_port == other.new_node_port
        )

    def __hash__(self) -> int:
        """
        Return a hash value for the notification to allow
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on notification type class name, id,
            new_node_host and new_node_port
        """
        try:
            node_port = int(self.new_node_port) if self.new_node_port else None
        except ValueError:
            node_port = 0

        return hash(
            (
                self.__class__.__name__,
                int(self.id),
                str(self.new_node_host),
                node_port,
            )
        )


class NodeMigratingNotification(MaintenanceNotification):
    """
    Notification for when a Redis cluster node is in the process of migrating slots.

    This notification is received when a node starts migrating its slots to another node
    during cluster rebalancing or maintenance operations.

    Args:
        id (int): Unique identifier for this notification
        ttl (int): Time-to-live in seconds for this notification
    """

    def __init__(self, id: int, ttl: int):
        super().__init__(id, ttl)

    def __repr__(self) -> str:
        expiry_time = self.creation_time + self.ttl
        remaining = max(0, expiry_time - time.monotonic())
        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"ttl={self.ttl}, "
            f"creation_time={self.creation_time}, "
            f"expires_at={expiry_time}, "
            f"remaining={remaining:.1f}s, "
            f"expired={self.is_expired()}"
            f")"
        )

    def __eq__(self, other) -> bool:
        """
        Two NodeMigratingNotification notifications are considered equal if they have the same
        id and are of the same type.
        """
        if not isinstance(other, NodeMigratingNotification):
            return False
        return self.id == other.id and type(self) is type(other)

    def __hash__(self) -> int:
        """
        Return a hash value for the notification to allow
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on notification type and id
        """
        return hash((self.__class__.__name__, int(self.id)))


class NodeMigratedNotification(MaintenanceNotification):
    """
    Notification for when a Redis cluster node has completed migrating slots.

    This notification is received when a node has finished migrating all its slots
    to other nodes during cluster rebalancing or maintenance operations.

    Args:
        id (int): Unique identifier for this notification
    """

    DEFAULT_TTL = 5

    def __init__(self, id: int):
        super().__init__(id, NodeMigratedNotification.DEFAULT_TTL)

    def __repr__(self) -> str:
        expiry_time = self.creation_time + self.ttl
        remaining = max(0, expiry_time - time.monotonic())
        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"ttl={self.ttl}, "
            f"creation_time={self.creation_time}, "
            f"expires_at={expiry_time}, "
            f"remaining={remaining:.1f}s, "
            f"expired={self.is_expired()}"
            f")"
        )

    def __eq__(self, other) -> bool:
        """
        Two NodeMigratedNotification notifications are considered equal if they have the same
        id and are of the same type.
        """
        if not isinstance(other, NodeMigratedNotification):
            return False
        return self.id == other.id and type(self) is type(other)

    def __hash__(self) -> int:
        """
        Return a hash value for the notification to allow
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on notification type and id
        """
        return hash((self.__class__.__name__, int(self.id)))


class NodeFailingOverNotification(MaintenanceNotification):
    """
    Notification for when a Redis cluster node is in the process of failing over.

    This notification is received when a node starts a failover process during
    cluster maintenance operations or when handling node failures.

    Args:
        id (int): Unique identifier for this notification
        ttl (int): Time-to-live in seconds for this notification
    """

    def __init__(self, id: int, ttl: int):
        super().__init__(id, ttl)

    def __repr__(self) -> str:
        expiry_time = self.creation_time + self.ttl
        remaining = max(0, expiry_time - time.monotonic())
        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"ttl={self.ttl}, "
            f"creation_time={self.creation_time}, "
            f"expires_at={expiry_time}, "
            f"remaining={remaining:.1f}s, "
            f"expired={self.is_expired()}"
            f")"
        )

    def __eq__(self, other) -> bool:
        """
        Two NodeFailingOverNotification notifications are considered equal if they have the same
        id and are of the same type.
        """
        if not isinstance(other, NodeFailingOverNotification):
            return False
        return self.id == other.id and type(self) is type(other)

    def __hash__(self) -> int:
        """
        Return a hash value for the notification to allow
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on notification type and id
        """
        return hash((self.__class__.__name__, int(self.id)))


class NodeFailedOverNotification(MaintenanceNotification):
    """
    Notification for when a Redis cluster node has completed a failover.

    This notification is received when a node has finished the failover process
    during cluster maintenance operations or after handling node failures.

    Args:
        id (int): Unique identifier for this notification
    """

    DEFAULT_TTL = 5

    def __init__(self, id: int):
        super().__init__(id, NodeFailedOverNotification.DEFAULT_TTL)

    def __repr__(self) -> str:
        expiry_time = self.creation_time + self.ttl
        remaining = max(0, expiry_time - time.monotonic())
        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"ttl={self.ttl}, "
            f"creation_time={self.creation_time}, "
            f"expires_at={expiry_time}, "
            f"remaining={remaining:.1f}s, "
            f"expired={self.is_expired()}"
            f")"
        )

    def __eq__(self, other) -> bool:
        """
        Two NodeFailedOverNotification notifications are considered equal if they have the same
        id and are of the same type.
        """
        if not isinstance(other, NodeFailedOverNotification):
            return False
        return self.id == other.id and type(self) is type(other)

    def __hash__(self) -> int:
        """
        Return a hash value for the notification to allow
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on notification type and id
        """
        return hash((self.__class__.__name__, int(self.id)))


class OSSNodeMigratingNotification(MaintenanceNotification):
    """
    Notification for when a Redis OSS API client is used and a node is in the process of migrating slots.

    This notification is received when a node starts migrating its slots to another node
    during cluster rebalancing or maintenance operations.

    Args:
        id (int): Unique identifier for this notification
        slots (Optional[List[int]]): List of slots being migrated
    """

    DEFAULT_TTL = 30

    def __init__(
        self,
        id: int,
        slots: Optional[str] = None,
    ):
        super().__init__(id, OSSNodeMigratingNotification.DEFAULT_TTL)
        self.slots = slots

    def __repr__(self) -> str:
        expiry_time = self.creation_time + self.ttl
        remaining = max(0, expiry_time - time.monotonic())
        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"slots={self.slots}, "
            f"ttl={self.ttl}, "
            f"creation_time={self.creation_time}, "
            f"expires_at={expiry_time}, "
            f"remaining={remaining:.1f}s, "
            f"expired={self.is_expired()}"
            f")"
        )

    def __eq__(self, other) -> bool:
        """
        Two OSSNodeMigratingNotification notifications are considered equal if they have the same
        id and are of the same type.
        """
        if not isinstance(other, OSSNodeMigratingNotification):
            return False
        return self.id == other.id and type(self) is type(other)

    def __hash__(self) -> int:
        """
        Return a hash value for the notification to allow
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on notification type and id
        """
        return hash((self.__class__.__name__, int(self.id)))


class OSSNodeMigratedNotification(MaintenanceNotification):
    """
    Notification for when a Redis OSS API client is used and a node has completed migrating slots.

    This notification is received when a node has finished migrating all its slots
    to other nodes during cluster rebalancing or maintenance operations.

    Args:
        id (int): Unique identifier for this notification
        nodes_to_slots_mapping (Dict[str, List[Dict[str, str]]]): Map of source node address
            to list of destination mappings. Each destination mapping is a dict with
            the destination node address as key and the slot range as value.

            Structure example:
            {
                "127.0.0.1:6379": [
                    {"127.0.0.1:6380": "1-100"},
                    {"127.0.0.1:6381": "101-200"}
                ],
                "127.0.0.1:6382": [
                    {"127.0.0.1:6383": "201-300"}
                ]
            }

            Where:
            - Key (str): Source node address in "host:port" format
            - Value (List[Dict[str, str]]): List of destination mappings where each dict
              contains destination node address as key and slot range as value
    """

    DEFAULT_TTL = 120

    def __init__(
        self,
        id: int,
        nodes_to_slots_mapping: Dict[str, List[Dict[str, str]]],
    ):
        super().__init__(id, OSSNodeMigratedNotification.DEFAULT_TTL)
        self.nodes_to_slots_mapping = nodes_to_slots_mapping

    def __repr__(self) -> str:
        expiry_time = self.creation_time + self.ttl
        remaining = max(0, expiry_time - time.monotonic())
        return (
            f"{self.__class__.__name__}("
            f"id={self.id}, "
            f"nodes_to_slots_mapping={self.nodes_to_slots_mapping}, "
            f"ttl={self.ttl}, "
            f"creation_time={self.creation_time}, "
            f"expires_at={expiry_time}, "
            f"remaining={remaining:.1f}s, "
            f"expired={self.is_expired()}"
            f")"
        )

    def __eq__(self, other) -> bool:
        """
        Two OSSNodeMigratedNotification notifications are considered equal if they have the same
        id and are of the same type.
        """
        if not isinstance(other, OSSNodeMigratedNotification):
            return False
        return self.id == other.id and type(self) is type(other)

    def __hash__(self) -> int:
        """
        Return a hash value for the notification to allow
        instances to be used in sets and as dictionary keys.

        Returns:
            int: Hash value based on notification type and id
        """
        return hash((self.__class__.__name__, int(self.id)))


def _is_private_fqdn(host: str) -> bool:
    """
    Determine if an FQDN is likely to be internal/private.

    This uses heuristics based on RFC 952 and RFC 1123 standards:
    - .local domains (RFC 6762 - Multicast DNS)
    - .internal domains (common internal convention)
    - Single-label hostnames (no dots)
    - Common internal TLDs

    Args:
        host (str): The FQDN to check

    Returns:
        bool: True if the FQDN appears to be internal/private
    """
    host_lower = host.lower().rstrip(".")

    # Single-label hostnames (no dots) are typically internal
    if "." not in host_lower:
        return True

    # Common internal/private domain patterns
    internal_patterns = [
        r"\.local$",  # mDNS/Bonjour domains
        r"\.internal$",  # Common internal convention
        r"\.corp$",  # Corporate domains
        r"\.lan$",  # Local area network
        r"\.intranet$",  # Intranet domains
        r"\.private$",  # Private domains
    ]

    for pattern in internal_patterns:
        if re.search(pattern, host_lower):
            return True

    # If none of the internal patterns match, assume it's external
    return False


notification_types_mapping: dict[type[MaintenanceNotification], str] = {
    NodeMovingNotification: "MOVING",
    NodeMigratingNotification: "MIGRATING",
    NodeMigratedNotification: "MIGRATED",
    NodeFailingOverNotification: "FAILING_OVER",
    NodeFailedOverNotification: "FAILED_OVER",
    OSSNodeMigratingNotification: "SMIGRATING",
    OSSNodeMigratedNotification: "SMIGRATED",
}


def add_debug_log_for_notification(
    connection: "MaintNotificationsAbstractConnection",
    notification: Union[str, MaintenanceNotification],
):
    pass


class MaintNotificationsConfig:
    """
    Configuration class for maintenance notifications handling behaviour. Notifications are received through
    push notifications.

    This class defines how the Redis client should react to different push notifications
    such as node moving, migrations, etc. in a Redis cluster.

    """

    def __init__(
        self,
        enabled: Union[bool, Literal["auto"]] = "auto",
        proactive_reconnect: bool = True,
        relaxed_timeout: Optional[Number] = 10,
        endpoint_type: Optional[EndpointType] = None,
    ):
        """
        Initialize a new MaintNotificationsConfig.

        Args:
            enabled (bool | "auto"): Controls maintenance notifications handling behavior.
                - True: The CLIENT MAINT_NOTIFICATIONS command must succeed during connection setup,
                otherwise a ResponseError is raised.
                - "auto": The CLIENT MAINT_NOTIFICATIONS command is attempted but failures are
                gracefully handled - a warning is logged and normal operation continues.
                - False: Maintenance notifications are completely disabled.
                Defaults to "auto".
            proactive_reconnect (bool): Whether to proactively reconnect when a node is replaced.
                Defaults to True.
            relaxed_timeout (Number): The relaxed timeout to use for the connection during maintenance.
                If -1 is provided - the relaxed timeout is disabled. Defaults to 20.
            endpoint_type (Optional[EndpointType]): Override for the endpoint type to use in CLIENT MAINT_NOTIFICATIONS.
                If None, the endpoint type will be automatically determined based on the host and TLS configuration.
                Defaults to None.

        Raises:
            ValueError: If endpoint_type is provided but is not a valid endpoint type.
        """
        self.enabled = enabled
        self.relaxed_timeout = relaxed_timeout
        self.proactive_reconnect = proactive_reconnect
        self.endpoint_type = endpoint_type

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"enabled={self.enabled}, "
            f"proactive_reconnect={self.proactive_reconnect}, "
            f"relaxed_timeout={self.relaxed_timeout}, "
            f"endpoint_type={self.endpoint_type!r}"
            f")"
        )

    def is_relaxed_timeouts_enabled(self) -> bool:
        """
        Check if the relaxed_timeout is enabled. The '-1' value is used to disable the relaxed_timeout.
        If relaxed_timeout is set to None, it will make the operation blocking
        and waiting until any response is received.

        Returns:
            True if the relaxed_timeout is enabled, False otherwise.
        """
        pass

    def get_endpoint_type(
        self, host: str, connection: "MaintNotificationsAbstractConnection"
    ) -> EndpointType:
        """
        Determine the appropriate endpoint type for CLIENT MAINT_NOTIFICATIONS command.

        Logic:
        1. If endpoint_type is explicitly set, use it
        2. Otherwise, check the original host from connection.host:
           - If host is an IP address, use it directly to determine internal-ip vs external-ip
           - If host is an FQDN, get the resolved IP to determine internal-fqdn vs external-fqdn

        Args:
            host: User provided hostname to analyze
            connection: The connection object to analyze for endpoint type determination

        Returns:
        """

        # If endpoint_type is explicitly set, use it
        if self.endpoint_type is not None:
            return self.endpoint_type

        # Check if the host is an IP address
        try:
            ip_addr = ipaddress.ip_address(host)
            # Host is an IP address - use it directly
            is_private = ip_addr.is_private
            return EndpointType.INTERNAL_IP if is_private else EndpointType.EXTERNAL_IP
        except ValueError:
            # Host is an FQDN - need to check resolved IP to determine internal vs external
            pass

        # Host is an FQDN, get the resolved IP to determine if it's internal or external
        resolved_ip = connection.get_resolved_ip()

        if resolved_ip:
            try:
                ip_addr = ipaddress.ip_address(resolved_ip)
                is_private = ip_addr.is_private
                # Use FQDN types since the original host was an FQDN
                return (
                    EndpointType.INTERNAL_FQDN
                    if is_private
                    else EndpointType.EXTERNAL_FQDN
                )
            except ValueError:
                # This shouldn't happen since we got the IP from the socket, but fallback
                pass

        # Final fallback: use heuristics on the FQDN itself
        is_private = _is_private_fqdn(host)
        return EndpointType.INTERNAL_FQDN if is_private else EndpointType.EXTERNAL_FQDN


class MaintNotificationsPoolHandler:
    def __init__(
        self,
        pool: "MaintNotificationsAbstractConnectionPool",
        config: MaintNotificationsConfig,
    ) -> None:
        self.pool = pool
        self.config = config
        self._processed_notifications = set()
        self._lock = threading.RLock()
        self.connection = None

    def set_connection(self, connection: "MaintNotificationsAbstractConnection"):
        pass

    def get_handler_for_connection(self):
        # Copy all data that should be shared between connections
        # but each connection should have its own pool handler
        # since each connection can be in a different state
        pass

    def remove_expired_notifications(self):
        pass

    def handle_notification(self, notification: MaintenanceNotification):
        pass

    def handle_node_moving_notification(self, notification: NodeMovingNotification):
        pass

    def run_proactive_reconnect(self, moving_address_src: Optional[str] = None):
        """
        Run proactive reconnect for the pool.
        Active connections are marked for reconnect after they complete the current command.
        Inactive connections are disconnected and will be connected on next use.
        """
        pass

    def handle_node_moved_notification(self, notification: NodeMovingNotification):
        """
        Handle the cleanup after a node moving notification expires.
        """
        pass


class MaintNotificationsConnectionHandler:
    # 1 = "starting maintenance" notifications, 0 = "completed maintenance" notifications
    _NOTIFICATION_TYPES: dict[type["MaintenanceNotification"], int] = {
        NodeMigratingNotification: 1,
        NodeFailingOverNotification: 1,
        OSSNodeMigratingNotification: 1,
        NodeMigratedNotification: 0,
        NodeFailedOverNotification: 0,
        OSSNodeMigratedNotification: 0,
    }

    def __init__(
        self,
        connection: "MaintNotificationsAbstractConnection",
        config: MaintNotificationsConfig,
    ) -> None:
        self.connection = connection
        self.config = config

    def _get_pool_name(self) -> str:
        """
        Get the pool name from the connection's pool handler.
        Falls back to connection representation if pool is not available.
        """
        pass

    def handle_notification(self, notification: MaintenanceNotification):
        # get the notification type by checking its class in the _NOTIFICATION_TYPES dict
        pass

    def handle_maintenance_start_notification(
        self, maintenance_state: MaintenanceState, notification: MaintenanceNotification
    ):
        pass

    def handle_maintenance_completed_notification(self, **kwargs):
        # Only reset timeouts if state is not MOVING and relaxed timeouts are enabled
        pass


class OSSMaintNotificationsHandler:
    def __init__(
        self,
        cluster_client: "MaintNotificationsAbstractRedisCluster",
        config: MaintNotificationsConfig,
    ) -> None:
        self.cluster_client = cluster_client
        self.config = config
        self._processed_notifications = set()
        self._in_progress = set()
        self._lock = threading.RLock()

    def get_handler_for_connection(self):
        # Copy all data that should be shared between connections
        # but each connection should have its own pool handler
        # since each connection can be in a different state
        pass

    def remove_expired_notifications(self):
        pass

    def handle_notification(self, notification: MaintenanceNotification):
        pass

    def handle_oss_maintenance_completed_notification(
        self, notification: OSSNodeMigratedNotification
    ):
        pass
