import logging

from .common import Default
from . import io

_LOGGER = logging.getLogger(__name__)


types = {
    "InPlageHoraire": io.InPlageHoraire,
    "InputTime": io.InputTime,
    "InputTimer": io.InputTimer,
    "InternalBool": io.InternalBool,
    "InternalInt": io.InternalInt,
    "InternalString": io.InternalString,
    "Scenario": io.Scenario,
    "WebInputAnalog": io.InputAnalog,
    "WebInputString": io.InputString,
    "WebInputTemp": io.InputTemp,
    "WIDigitalBP": io.InputSwitch,
    "WIDigitalLong": io.InputSwitchLongPress,
    "WIDigitalTriple": io.InputSwitchTriple,
    "WODali": io.OutputLightDimmer,
    "WODigital": io.OutputLight,
    "WOVoletSmart": io.OutputShutterSmart,
}


def new_item(data, room, conn):
    try:
        return types[data["type"]](data, room, conn)
    except:
        _LOGGER.error(f"Unknown Calaos item type, using generic item for: {data}")
        return Default(data, room, conn)
