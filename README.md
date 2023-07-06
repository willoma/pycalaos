# Python Calaos

Client for the Calaos v3 home automation server. This client keeps the home,
rooms and items status in cache, in order to reduce the quantity of requests
towards the Calaos server.

Use `pycalaos.discover` to discover the Calaos server IP address.

Use `pycalaos.Client` to connect to the Calaos server.

This library has been developed with
[Home Assistant](https://www.home-assistant.io/) in mind.

## Notice

This integration is an independent project: the Calaos team is by no means
involved in its development.

## discover

The `pycalaos.discover` function broadcasts a discovery message on the network
and returns the IP address of a discovered Calaos instance, or raises
`pycalaos.NoDiscoveryError`.

## Client

`pycalaos.Client` is a client that connects to a Calaos server.
Initialize it with:

```python
from pycalaos import Client
client = Client(url, username, password)
```

When initializing the client, it automatically fetches the Calaos configuration
(rooms and items). In order to reload the configuration,
use `client.reload_home()`.

The client has the following methods and properties:

- `reload_home()`: reload the whole configuration (rooms and items)
- `client.update_all()`: checks and updates state for all known items, and
  returns `pycalaos.item.Event` objects for each change.
- `client.poll()` requests changes since the previous poll:
  - if there is no previous execution of the `poll` function, it registers
    for polling and acts as `update_all`
  - if there is a previous execution of the `poll` function, it requests only
    changes for this registration (see the
    [Calaos developer doc](https://www.calaos.fr/wiki/en/protocole_json#poll_listen)
    for more information) and returns `pycalaos.item.Event` objects for each
    change since the previous poll
- `client.rooms`: rooms as a list of `pycalaos.client.Room`
- `client.items`: items as dictionary of item ID to `pycalaos.item.Item`
- `client.item_types`: complete list of item types currently in use
- `client.items_by_type(type: type)`: returns all items of that type (see types
  in the 2nd columns of the mapping table)

## Room

Calaos rooms are represented in pycalaos as `pycalaos.client.Room` objects.

Rooms have the following properties:

- `name`: name of the room
- `type`: type from Calaos
- `items`: items in that room, as a list of `pycalaos.item.common.Item` objects

## Item

All Calaos IOs are represented in pycalaos as `pycalaos.item.common.Item`
objects, or objects that inherit from this one.

Items have the following properties:

- `info`: item description (id, name, type) as a string
- `id`: ID from Calaos
- `gui_type`: "gui_type" from Calaos
- `io_type`: "io_type" from Calaos
- `name`: name from Calaos
- `state`: current item state (see the mapping section below)
- `type`: type from Calaos
- `var_type`: "var_type" from Calaos
- `visible`: "visible" according to Calaos
- `room`: the `pycalaos.Room` object this item belongs to

Items also have the following functions for internal use
(they should not be called directly):

- `internal_set_state`
- `internal_from_event`

## Event

Each state change results in a `pycalaos.item.common.Event` object, when calling
`client.update_all()` or `client.poll()`.

Events have the following properties:

- `item`: item the event is related to, as a `pycalaos.item.common.Item` object
- `state`: state for this event

## Calaos IOs vs pycalaos items mapping

Mapping from Calaos IOs to pycalaos items is based on the Calaos type:

| Calaos type     | pycalaos object type    |
| --------------- | ----------------------- |
| **Generic**     |
| InPlageHoraire  | io.InPlageHoraire       |
| InputTime       | io.InputTime            |
| InputTimer      | io.InputTimer           |
| InternalBool    | io.InternalBool         |
| InternalInt     | io.InternalInt          |
| InternalString  | io.InternalString       |
| Scenario        | io.Scenario             |
| **Wago**        |
| WIDigitalBP     | io.InputSwitch          |
| WIDigitalLong   | io.InputSwitchLongPress |
| WIDigitalTriple | io.InputSwitchTriple    |
| WODali          | io.OutputLightDimmer    |
| WODigital       | io.OutputLight          |
| WOVoletSmart    | io.OutputShutterSmart   |
| **Web**         |
| WebInputAnalog  | io.InputAnalog          |
| WebInputString  | io.InputString          |
| WebInputTemp    | io.InputTemp            |
| **Fallback**    |
| Any other type  | common.Item             |

### common.Item

- state: string
- methods: none

### io.InPlageHoraire

- state: boolean: `True` or `False`
- methods: none

### io.InputAnalog

- state: float
- methods: none

### io.InputString

- state: string
- methods: none

### io.InputSwitch

- state: boolean: `True` or `False`
- methods: none

### io.InputSwitchLongPress

- state: `pycalaos.item.io.InputSwitchLongPressState`: `NONE`, `SHORT`, `LONG`
- methods: none

### io.InputSwitchTriple

- state: `pycalaos.item.io.InputSwitchTripleState`: `NONE`, `SINGLE`, `DOUBLE`, `TRIPLE`
- methods: none

### io.InputTemp

- state: float
- methods: none

### io.InputTime

- state: boolean: `True` or `False`
- methods: none

### io.InputTimer

- state: boolean: `True` or `False`
- methods:
  - `start()`: Start the timer
  - `stop()`: Stop the timer
  - `reset(hours, minutes, seconds, milliseconds)`: Reset the configured time to
    a value

### io.InternalBool

- state: boolean: `True` or `False`
- methods:
  - `true()`: Set a value to true
  - `false()`: Set a value to false
  - `toggle()`: Invert boolean value
  - `impulse(*pattern)`: Do an impulse on boolean value with a pattern.
    Arguments may be durations (in ms) or "old" to reset to the previous state
    after the impulse

### io.InternalInt

- state: integer
- methods:
  - `set(value)`: Set a specific integer value
  - `inc()`: Increment value with configured step
  - `dec()`: Decrement value with configured step
  - `inc(value)`: Increment value by value
  - `dec(value)`: Decrement value by value

### io.InternalString

- state: string
- methods:
  - `set(value)`: Set a specific string value

### io.OutputLight

- state: boolean: `True` or `False`
- methods:
  - `true()`: Switch the light on
  - `false()`: Switch the light off
  - `toggle()`: Invert light state
  - `impulse(*pattern)`: Do an impulse on light state with a pattern. Arguments
    may be durations (in ms) or "old" to reset to the previous state after the
    impulse

### io.OutputLightDimmer

- state: integer between 0 and 100
- methods:
  - `true()`: Switch the light on
  - `false()`: Switch the light off
  - `toggle()`: Invert light state
  - `impulse(*pattern)`: Do an impulse on light state with a pattern. Arguments
    may be durations (in ms) or "old" to reset to the previous state after the
    impulse
  - `set_off(value)`: Set light value without switching on. This will be the
    light intensity for the next ON
  - `set(value)`: Set light intensity and swith on if light is off
  - `up(value)`: Increase intensity by X percent
  - `down(value)`: Decrease intensity by X percent
  - `hold_press()`: Dynamically change light intensity when holding a switch (press action)
  - `hold_stop()`: Dynamically change light intensity when holding a switch (stop action)

### io.OutputShutterSmart

- state: dictionary, with two elements:
  - `action`: `pycalaos.item.io.OutputShutterAction`: `STATIONARY`, `UP`, `DOWN`, `STOP`, `CALIBRATION`
  - `position`: integer between 0 and 100
- methods:
  - `up()`: Open the shutter
  - `down()`: Close the shutter
  - `stop()`: Stop the shutter
  - `toggle()`: Invert shutter state
  - `impulse_up(duration)`: Open shutter for X ms
  - `impulse_down(duration)`: Close shutter for X ms
  - `set(value)`: Set shutter at position X in percent
  - `up(value)`: Open the shutter by X percent
  - `down(value)`: Close the shutter by X percent
  - `calibrate()`: Start calibration on shutter. This opens fully the shutter
    and resets all internal position values. Use this if shutter sync is lost.

### io.Scenario

- state: boolean: `True` or `False`
- methods:
  - `true()`: Start the scenario
  - `false()`: Stop the scenario (only for special looping scenarios)
