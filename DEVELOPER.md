# Python Calaos dev doc

## Item types

To support a new Calaos IO, either use an existing item type (see the mapping
section in the README) or create a new one.

An item type must:

- be defined in the `item.py` file
- inherit `Item`

An item type may:

- have an `internal_set_state(self, state)` function, if the state from the
  Calaos event should be translated to another value
- have other methods, to interact with Calaos

Please prefer existing names for items methods:

- `turn_on(self)`: turn on / open / activate / enable the element
- `turn_off(self)`: turn off / close / deactivate / disable the element
- `set_value(self, value)`: change the element value
- `set_value_off(self, value)`: change the element value without turning on

Add the new item type to the types dictionary at the end of the `item.py` file.
Add a line in the mapping table in `README.md`, and add a subsection.
