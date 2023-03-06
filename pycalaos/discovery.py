import netifaces
import socket
import time

DISCOVER_UDP_PORT = 4545
DISCOVER_MESSAGE = b"CALAOS_DISCOVER"
DISCOVER_BUFFER_SIZE = 64
DISCOVER_TIMEOUT = 0.5  # seconds
DISCOVER_MAXTIME = 10  # seconds


class NoDiscoveryError(Exception):
    """This error indicates no Calaos server has been discovered"""
    pass


def discover(timeout=DISCOVER_MAXTIME) -> str:
    """Discover Calaos server on local networks

    This function sends a magic discovery packet on all network interfaces to
    discover a Calaos server.

    Return IP address of the first Calaos server to answer.

    If no Calaos server answers within the provided timeout or the default
     value of 10 seconds, raise NoDiscoveryError.
    """

    broadcast_addresses = []
    for iface in netifaces.interfaces():
        try:
            for net in netifaces.ifaddresses(iface)[netifaces.AF_INET]:
                try:
                    broadcast_addresses.append(net["broadcast"])
                except KeyError:
                    pass
        except KeyError:
            pass

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(DISCOVER_TIMEOUT)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    start = time.time()
    while time.time() < start + timeout:
        for addr in broadcast_addresses:
            sock.sendto(DISCOVER_MESSAGE, (addr, DISCOVER_UDP_PORT))
            try:
                resp = sock.recvfrom(DISCOVER_BUFFER_SIZE)
                if resp[0][:10] == b"CALAOS_IP ":
                    return resp[0][10:].decode()
            except socket.timeout:
                pass
    raise NoDiscoveryError
