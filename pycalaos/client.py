import json
import logging
import ssl
import time
import urllib.request

from .item import new_item
from .item.common import Event

_LOGGER = logging.getLogger(__name__)

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

    def _add_item(self, item):
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

def _poll_events_to_map(pollEvents):
    events = {}
    for rawEvent in pollEvents:
        try:
            eventData = rawEvent["data"]
        except:
            _LOGGER.debug(f"Poll received event without data: {rawEvent}")
            continue

        try:
            key = eventData["id"]
        except:
            _LOGGER.debug(f"Poll received event without ID: {rawEvent}")
            continue

        try:
            value = eventData["state"]
        except:
            _LOGGER.debug(f"Poll received event without state: {rawEvent}")
            continue

        events[key] = value
    return events

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
                room._add_item(item)
            rooms.append(room)
        self._rooms = rooms
        self._items = items
        self._items_by_type = items_by_type

    def _register_polling(self):
        resp = self._conn.send({"action": "poll_listen", "type": "register"})
        self._polling_id = resp["uuid"]
        return self.update_all()

    def _update_from_map(self, eventsTuples):
        events = []
        for kv in eventsTuples:
            try:
                item = self.items[kv[0]]
            except KeyError:
                _LOGGER.debug(f"Calaos event with unknown ID: {kv[0]}")
                continue

            changed = item.internal_set_state(kv[1])
            if changed:
                events.append(Event(item))
        return events

    def update_all(self):
        """Check all states and return events

        Return events for states changes (list of pycalaos.item.common.Event)
        """
        _LOGGER.debug("Getting all states from known items")
        resp = self._conn.send(
            {"action": "get_state", "items": list(self.items.keys())}
        )
        return self._update_from_map(resp.items())

    def poll(self):
        """Change items states and return all events since the last poll

        Return events for states changes (list of pycalaos.item.common.Event)
        """
        if self._polling_id is None:
            _LOGGER.debug("Registering to the polling")
            events = self._register_polling()
        else:
            resp = self._conn.send(
                {"action": "poll_listen", "type": "get", "uuid": self._polling_id}
            )
            if resp["success"] == "true":
                _LOGGER.debug("Polling new values")
                events = self._update_from_map(
                    _poll_events_to_map(resp["events"])
                )
            else:
                _LOGGER.debug("Polling failed, re-registering")
                events = self._register_polling()
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
