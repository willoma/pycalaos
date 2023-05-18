# Python Calaos

Client for the Calaos v3 home automation server. This client keeps the home,
rooms and items status in cache, in order to reduce the quantity of requests
towards the Calaos server.

Use `pycalaos.discover` to discover the Calaos server IP address.

Use `pycalaos.Client` to connect to the Calaos server.

This library has been developed with
[Home Assistant](https://www.home-assistant.io/) in mind.

The library has initially been tested with a Wago 750-849 controller and:

- single-click buttons
- triple-click buttons
- long-click buttons
- binary output
- DALI lights

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
- `client.item_types`: list of item types present in this Calaos installation
- `client.items_by_type(type: str)`: returns all items of that type
- `client.item_gui_types`: list of item gui_types present in this Calaos
  installation
- `client.items_by_gui_type(type: str)`: returns all items of that gui_type

## Room

Calaos rooms are represented in pycalaos as `pycalaos.client.Room` objects.

Rooms have the following properties:

- `name`: name of the room
- `type`: type from Calaos
- `items`: items in that room, as a list of `pycalaos.item.Item` objects

## Item

All Calaos IOs are represented in pycalaos as `pycalaos.item.Item` objects, or
objects that inherit from this one.

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

All items also have a `internal_set_state` function; it should not be used
directly: it is used by the client in order to change stored value when
receiving events.

## Event

Each state change results in a `pycalaos.item.Event` object, when calling
`client.update_all()` or `client.poll()`.

Events have the following properties:

- `item`: item the event is related to, as a `pycalaos.item.Item` object
- `state`: state for this event

## Calaos IOs vs pycalaos items mapping

Mapping from Calaos IOs to pycalaos items is based on the gui_type:

| Calaos gui_type    | pycalaos object  |
| ------------------ | ---------------- |
| **Inputs**         |
| switch             | BinaryInput      |
| switch3            | Switch3          |
| switch_long        | SwitchLong       |
| time_range         | BinaryInput      |
| **Outputs**        |
| light              | BinaryOutput     |
| light_dimmer       | PercentageOutput |
| var_bool           | BinaryOutput     |
| **Inputs/outputs** |
| scenario           | BinaryOutput     |

### BinaryInput

- state: boolean: `True` or `False`
- methods: none

### BinaryOutput

- state: boolean: `True` or `False`
- methods:
  - `item.turn_on()`: turn the output on / open / activate / enable
  - `item.turn_off()`: turn the output off / close / deactivate / disable

### PercentageOutput

- state: integer, between `0` and `100`
- methods:
  - `item.turn_on()`: turn the output on
  - `item.turn_off()`: turn the output off
  - `item.set_value(value: int)` : change the value of the output,
    turning it on if it was off
  - `item.set_value_off(value: int)` : change the value of the output,
    without turning it on

### Switch3

- state: `pycalaos.item.NbClick`: `NONE`, `SINGLE`, `DOUBLE`, `TRIPLE`
- methods: none

### SwitchLong

- state: `pycalaos.item.ClickTyoe`: `NONE`, `SHORT`, `LONG`
- methods: none
