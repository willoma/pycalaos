import logging

_LOGGER = logging.getLogger(__name__)


class Event:
    """An item state change event"""

    def __init__(self, item):
        """Initialize the event with the item and the current item state

        Create the event after changing the item state.
        """
        self._item = item
        self._state = item.state

    def __repr__(self):
        return f"{self._item.info} => {self._state}"

    def __eq__(self, other):
        if other == None:
            return False
        return self._item == other.item and self._state == other.state

    @property
    def item(self):
        """Item this event is related to"""
        return self._item

    @property
    def state(self):
        """State for this event"""
        return self._state


class Item:
    """An item in the Calaos installation"""

    _state = None

    def __init__(self, data, room, conn):
        self._id = data["id"]
        self._gui_type = data["gui_type"]
        self._io_type = data["io_type"]
        self._name = data["name"]
        self._type = data["type"]
        self._var_type = data["var_type"]
        self._visible = data["visible"] == "true"
        self.internal_set_state(data["state"])
        self._room = room
        self._conn = conn

    def __repr__(self):
        return f"{self.info} = {self.state}"

    def internal_set_state(self, state):
        translated = self._translate(state)
        if translated == self._state:
            return False
        self._state = translated
        return True

    @property
    def info(self):
        return f"[{self._id}] {self._name} ({self._type}/{self._io_type})"

    @property
    def id(self):
        return self._id

    @property
    def gui_type(self):
        return self._gui_type

    @property
    def io_type(self):
        return self._io_type

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def type(self):
        return self._type

    @property
    def var_type(self):
        return self._var_type

    @property
    def visible(self):
        return self._visible

    @property
    def room(self):
        return self._room

    def _send(self, value):
        _LOGGER.debug(f"Setting state of {self._id} ({self._name}) with value: {value}")
        response = self._conn.send(
            {
                "action": "set_state",
                "type": self._io_type,
                "id": self._id,
                "value": value,
            }
        )
        if not response["success"]:
            _LOGGER.error(
                f"Failed to set state of {self._id} ({self._name}) with value: {value}"
            )

    def _update_state(self):
        result = self._conn.send({"action": "get_state", "items": [self._id]})
        self._state = self._translate(result[self._id])

    def _translate(self, state: str):
        return state


class Default(Item):
    pass
