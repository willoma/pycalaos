from .state import _get_translation


class NotAnOutputError(Exception):
    pass


class Event:
    """An item state change event"""

    def __init__(self, item):
        """Initialize the event with the item and the current item state

        Create the event after changing the item state.
        """
        self._item = item
        self._state = item.state

    def __repr__(self):
        return f"{self._item.info()} => {self._state}"

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
        return self._item


class Item:
    """An item in the Calaos installation"""

    def __init__(self, data, room, conn, state_translator):
        self._id = data["id"]
        self._gui_type = data["gui_type"]
        self._io_type = data["io_type"]
        self._name = data["name"]
        self._state = state_translator.parse(data["state"])
        self._type = data["type"]
        self._var_type = data["var_type"]
        self._visible = data["visible"] == "true"
        self._room = room
        self._conn = conn
        self._state_translator = state_translator

    def info(self):
        return f"[{self._id}] {self._name} ({self._type}/{self._io_type})"

    def __repr__(self):
        return f"{self.info()} = {self._state}"

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

    def _update_state(self, state):
        newState = self._state_translator.parse(state)
        if newState == self._state:
            return None
        self._state = newState
        return Event(self)

    @state.setter
    def state(self, state):
        if self._io_type == "output" or self._io_type == "inout":
            newState = self._state_translator.parse(state)
            self._conn.send({
                "action": "set_state",
                "type": self._type,
                "id": self._id,
                "value": self._state_translator.raw(newState)
            })
            self._state = newState
        else:
            raise NotAnOutputError


def _newItem(data, room, conn):
    return Item(data, room, conn, _get_translation(data["type"]))
