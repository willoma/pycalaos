import json
import logging
import ssl
import time
import urllib.request

from .item import new_item
from .item.common import Event

_LOGGER = logging.getLogger(__name__)

# Calaos deletes registered polling uuids after 5 minutes
POLLING_MAX_WAIT = 5 * 60


class Room:
    """A room in the Calaos configuration"""

    def __init__(self, name: str, type: str):
        """Initialize the room

        Parameters:
            name (str):
                Name of the room

            type (str):
                Type of the room
        """
        self._name = name
        self._type = type
        self._items = []

    def __repr__(self):
        return f"{self._name} ({self._type}): {len(self._items)} items"

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def items(self):
        return self._items

    def _addItem(self, item):
        """Add a new item in the room

        Parameters:
            item (pycalaos.item.Item):
                The item to add

        Return nothing
        """
        self._items.append(item)


class _Conn:
    def __init__(self, uri, username, password):
        self._uri = f"{uri}/api.php"
        self._username = username
        self._password = password
        self._context = ssl._create_unverified_context()

    def send(self, request):
        request["cn_user"] = self._username
        request["cn_pass"] = self._password
        req = urllib.request.Request(
            self._uri,
            data=json.dumps(request).encode("ascii"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, context=self._context) as response:
            return json.load(response)


class Client:
    """A Calaos client"""

    def __init__(self, uri: str, username: str, password: str):
        """Initialize the client and load the home configuration and state.

        Parameters:
            uri (str):
                URI of the Calaos server (usually, "http[s]://A.B.C.D")

            username (str):
                Username to connect to the Calaos server

            password (str):
                Password to connect to the Calaos server
        """
        self._conn = _Conn(uri, username, password)
        self._polling_id = None
        self._last_poll = 0
        self.reload_home()

    def __repr__(self):
        return f"Calaos Client with {len(self.rooms)} rooms"

    def reload_home(self):
        """Reload the complete home configuration, resetting rooms and items

        This could be necessary if the Calaos server is reconfigured with
        Calaos Installer and the client is not restarted).

        Return nothing
        """
        _LOGGER.debug("Getting the whole home")
        resp = self._conn.send({"action": "get_home"})
        rooms = []
        items = {}
        items_by_type = {}
        for roomData in resp["home"]:
            room = Room(roomData["name"], roomData["type"])
            for itemData in roomData["items"]:
                item = new_item(itemData, room, self._conn)
                items[item._id] = item
                try:
                    items_by_type[type(item)].append(item)
                except KeyError:
                    items_by_type[type(item)] = [item]
                room._addItem(item)
            rooms.append(room)
        self._rooms = rooms
        self._items = items
        self._items_by_type = items_by_type

    def update_all(self):
        """Check all states and return events

        Return events for states changes (list of pycalaos.item.common.Event)
        """
        _LOGGER.debug("Getting all states from known items")
        resp = self._conn.send(
            {"action": "get_state", "items": list(self.items.keys())}
        )
        events = []
        for kv in resp.items():
            changed = self.items[kv[0]].internal_set_state(kv[1])
            if changed:
                events.append(Event(self.items[kv[0]]))
        return events

    def poll(self):
        """Change items states and return all events since the last poll

        Return events for states changes (list of pycalaos.item.common.Event)
        """
        now = time.time()
        if now - self._last_poll > POLLING_MAX_WAIT:
            _LOGGER.debug("Registering to the polling")
            # If there is no existing poll queue, create a new one and
            # try to get new states for all items
            resp = self._conn.send({"action": "poll_listen", "type": "register"})
            self._polling_id = resp["uuid"]
            events = self.update_all()
        else:
            resp = self._conn.send(
                {"action": "poll_listen", "type": "get", "uuid": self._polling_id}
            )
            if len(resp["events"]) > 0:
                _LOGGER.debug(f"Raw events from polling: {resp['events']}")

            events = []
            for rawEvent in resp["events"]:
                try:
                    eventData = rawEvent["data"]
                except:
                    _LOGGER.error(f"Poll received event without data: {rawEvent}")
                    continue

                try:
                    itemID = eventData["id"]
                except:
                    _LOGGER.error(f"Poll received event without ID: {rawEvent}")
                    continue

                try:
                    state = eventData["state"]
                except:
                    _LOGGER.debug(f"Poll received event without state: {rawEvent}")
                    continue

                try:
                    item = self.items[itemID]
                except KeyError:
                    _LOGGER.error(f"Poll received event with unknown ID: {rawEvent}")
                    continue

                changed = item.internal_from_event(state)
                if changed:
                    events.append(Event(item))

        self._last_poll = now
        if len(events) > 0:
            _LOGGER.debug(f"Events: {events}")
        return events

    @property
    def rooms(self):
        return self._rooms

    @property
    def items(self):
        """Items referenced by their IDs (dict of str: pycalaos.item.Item)"""
        return self._items

    @property
    def item_types(self):
        """Complete list of item types currently in use"""
        return list(self._items_by_type.keys())

    def items_by_type(self, type):
        """Return only the items of the given type"""
        try:
            return self._items_by_type[type]
        except KeyError:
            return []
