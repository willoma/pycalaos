import json
import ssl
import time
import urllib.request

from .item import _newItem

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

    def addItem(self, item):
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
            headers={'Content-Type': 'application/json'}
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
        resp = self._conn.send({
            "action": "get_home"
        })
        rooms = []
        items = {}
        for roomData in resp["home"]:
            room = Room(roomData["name"], roomData["type"])
            for itemData in roomData["items"]:
                item = _newItem(itemData, room, self._conn)
                items[item._id] = item
                room.addItem(item)
            rooms.append(room)
        self._rooms = rooms
        self._items = items

    def update_all(self):
        """Check all states and return events

        Return events for states changes (list of pycalaos.item.Event)
        """
        resp = self._conn.send({
            "action": "get_state",
            "items": list(self.items.keys())
        })
        events = []
        for kv in resp.items():
            evt = self.items[kv[0]]._update_state(kv[1])
            if evt != None:
                events.append(evt)
        return events

    def poll(self):
        """Change items states and return all events since the last poll

        Return events for states changes (list of pycalaos.item.Event)
        """
        now = time.time()
        if now - self._last_poll > POLLING_MAX_WAIT:
            # If there is no existing poll queue, create a new one and
            # try to get new states for all items
            resp = self._conn.send({
                "action": "poll_listen",
                "type": "register"
            })
            self._polling_id = resp["uuid"]
            events = self.update_all()
        else:
            resp = self._conn.send({
                "action": "poll_listen",
                "type": "get",
                "uuid": self._polling_id
            })
            events = []
            for rawEvent in resp["events"]:
                item = self.items[rawEvent["data"]["id"]]
                event = item._update_state(rawEvent["data"]["state"])
                if event not in events and event != None:
                    events.append(event)
        self._last_poll = now
        return events

    @property
    def rooms(self):
        return self._rooms

    @property
    def items(self):
        """Items referenced by their IDs (dict of str: pycalaos.item.Item)"""
        return self._items
