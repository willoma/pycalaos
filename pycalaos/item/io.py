from enum import Enum, StrEnum

from .common import Item


class InPlageHoraire(Item):
    def _translate(self, state: str):
        return state == "true"


class InputAnalog(Item):
    def _translate(self, state: str):
        return float(state)


class InputString(Item):
    pass


class InputSwitch(Item):
    def _translate(self, state: str):
        return state == "true"


class InputSwitchLongPressState(Enum):
    NONE = 0
    SHORT = 1
    LONG = 2


class InputSwitchLongPress(Item):
    def _translate(self, state: str):
        return InputSwitchLongPressState(int(state))


class InputSwitchTripleState(Enum):
    NONE = 0
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3


class InputSwitchTriple(Item):
    def _translate(self, state: str):
        return InputSwitchTripleState(int(state))


class InputTemp(Item):
    def _translate(self, state: str):
        return float(state)


class InputTime(Item):
    def _translate(self, state: str):
        return state == "true"


class InputTimer(Item):
    def _translate(self, state: str):
        return state == "true"

    def start(self):
        self._send("start")
        self._update_state()

    def stop(self):
        self._send("stop")
        self._update_state()

    def reset(self, hours, minutes, seconds, milliseconds):
        self._send(f"{hours}:{minutes}:{seconds}:{milliseconds}")
        self._update_state()


class InternalBool(Item):
    def _translate(self, state: str):
        return state == "true"

    def true(self):
        self._send("true")
        self._state = True

    def false(self):
        self._send("false")
        self._state = False

    def toggle(self):
        self._send("toggle")
        self._update_state()

    def impulse(self, *pattern):
        cmd = "impulse"
        for step in pattern:
            cmd += f" {step}"
        self._send(cmd)
        print(cmd)
        self._update_state()


class InternalInt(Item):
    def _translate(self, state: str):
        return int(state)

    def set(self, value):
        self._send(f"{value}")
        self._state = value

    def inc(self, value=0):
        if value == 0:
            self._send("inc")
        else:
            self._send(f"inc {value}")
        self._update_state()

    def dec(self, value=0):
        if value == 0:
            self._send("dec")
        else:
            self._send(f"dec {value}")
        self._update_state()


class InternalString(Item):
    def set(self, value):
        self._send(value)
        self._state = value


class OutputLight(Item):
    def _translate(self, state: str):
        return state == "true"

    def true(self):
        self._send("true")
        self._state = True

    def false(self):
        self._send("false")
        self._state = False

    def toggle(self):
        self._send("toggle")
        self._update_state()

    def impulse(self, *pattern):
        cmd = "impulse"
        for step in pattern:
            cmd += f" {step}"
        self._send(cmd)
        print(cmd)
        self._update_state()


class OutputLightDimmer(Item):
    def _translate(self, state: str):
        value = int(state)
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        return value

    def true(self):
        self._send("true")
        self._update_state()

    def false(self):
        self._send("false")
        self._state = 0

    def toggle(self):
        self._send("toggle")
        self._update_state()

    def impulse(self, *pattern):
        cmd = "impulse"
        for step in pattern:
            cmd += f" {step}"
        self._send(cmd)
        print(cmd)
        self._update_state()

    def set_off(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        self._send(f"set off {value}")
        if self._state != 0:
            self._state = value

    def set(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        self._send(f"set {value}")
        self._state = value

    def up(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        self._send(f"up {value}")
        self._update_state()

    def down(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        self._send(f"down {value}")
        self._update_state()

    def hold_press(self):
        self._send("hold press")

    def hold_stop(self):
        self._send("hold stop")
        self._update_state()


class OutputShutterAction(StrEnum):
    STATIONARY = ""
    UP = "up"
    DOWN = "down"
    STOP = "stop"
    CALIBRATION = "calibrate"


class OutputShutterSmart(Item):
    def _translate(self, state: str):
        infos = state.split()
        return {"action": OutputShutterAction(infos[0]), "position": int(infos[1])}

    def up(self):
        self._send("up")

    def down(self):
        self._send("down")

    def stop(self):
        self._send("stop")
        self._update_state()

    def toggle(self):
        self._send("toggle")
        self._update_state()

    def impulse_up(self, duration):
        self._send(f"impulse up {duration}")

    def impulse_down(self, duration):
        self._send(f"impulse down {duration}")

    def set(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        self._send(f"set {value}")
        self._state = value

    def up(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        self._send(f"up {value}")
        self._update_state()

    def down(self, value):
        if value < 1:
            value = 1
        elif value > 100:
            value = 100
        self._send(f"down {value}")
        self._update_state()

    def calibrate(self):
        self._send(f"calibrate")


class Scenario(Item):
    def _translate(self, state: str):
        return state == "true"

    def true(self):
        self._send("true")
        self._state = True

    def false(self):
        self._send("false")
        self._state = False
