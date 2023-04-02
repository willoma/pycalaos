import logging
from enum import Enum

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
        self.set_state(data["state"])
        self._room = room
        self._conn = conn

    def __repr__(self):
        return f"{self.info} = {self.state}"

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

    def _set_state(self, state):
        if state == self._state:
            return False
        self._state = state
        return True

    def _send_set_state(self, value):
        _LOGGER.debug(
            f"Setting state of {self._id} ({self._name}) with value: {value}")
        self._conn.send({
            "action": "set_state",
            "type": self._type,
            "id": self._id,
            "value": value
        })


class BinaryInput(Item):
    def set_state(self, state):
        return self._set_state(state == "true")


class BinaryOutput(BinaryInput):

    def turn_on(self):
        self._send_set_state("true")
        self._state = True

    def turn_off(self):
        self._send_set_state("false")
        self._state = False


class PercentageOutput(Item):

    @staticmethod
    def translate(state):
        value = int(state)
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        return value

    def set_state(self, state):
        return self._set_state(PercentageOutput.translate(state))

    def turn_on(self):
        self._send_set_state("true")
        result = self._conn.send({
            "action": "get_state",
            "items": [
                self._id
            ]
        })
        self._state = PercentageOutput.translate(result[self._id])

    def turn_off(self):
        self._send_set_state("false")
        self._state = 0

    def set_brightness(self, brightness):
        if brightness < 1:
            brightness = 1
        elif brightness > 100:
            brightness = 100
        self._send_set_state("set "+str(brightness))
        self._state = brightness

    def set_brightness_off(self, brightness):
        if brightness < 1:
            brightness = 1
        elif brightness > 100:
            brightness = 100
        self._send_set_state("set off "+str(brightness))
        if self._state != 0:
            self._state = brightness


class Scenario(BinaryInput):

    def run(self):
        self._send_set_state("true")


class NbClicks(Enum):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3


class Switch3(Item):
    def set_state(self, state):
        return self._set_state(NbClicks(int(state)))


class ClickType(Enum):
    NONE = 0
    SHORT = 1
    LONG = 2


class SwitchLong(Item):
    def set_state(self, state):
        return self._set_state(ClickType(int(state)))


types = {
    # Inputs
    "switch": BinaryInput,
    "switch3": Switch3,
    "switch_long": SwitchLong,
    "time_range": BinaryInput,
    # Inouts
    "scenario": Scenario,
    # Outputs
    "light": BinaryOutput,
    "light_dimmer": PercentageOutput
}


def new_item(data, room, conn):
    try:
        return types[data["gui_type"]](data, room, conn)
    except:
        return None
