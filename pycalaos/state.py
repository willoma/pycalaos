from enum import Enum


class generic:
    def parse(state):
        return state

    def raw(state):
        return str(state)


class binary(generic):
    def parse(state):
        return state == "true" or state == True

    def raw(state):
        return "true" if state else "false"


class NbClicks(Enum):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3


class up_to_triple(generic):
    def parse(state):
        return NbClicks(int(state))

    def raw(state):
        return str(state.value)


class ClickType(Enum):
    NONE = 0
    SHORT = 1
    LONG = 2


class short_or_long(generic):
    def parse(state):
        return ClickType(int(state))

    def raw(state):
        return str(state.value)


class Running(Enum):
    NOT_RUNNING = 0
    RUNNING = 1


class running(generic):
    def parse(state):
        return Running.RUNNING if state == "true" else Running.NOT_RUNNING

    def raw(state):
        return state == Running.RUNNING


class percentage(generic):
    def parse(state):
        if state == True:
            return 100
        if state == False:
            return 0
        value = int(state)
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        return value


_translation_map = {
    "InPlageHoraire": binary,
    "scenario": running,
    "WIDigitalBP": binary,
    "WIDigitalLong": short_or_long,
    "WIDigitalTriple": up_to_triple,
    "WODali": percentage,
    "WODigital": binary
}


def _get_translation(name):
    try:
        return _translation_map[name]
    except KeyError:
        return generic
