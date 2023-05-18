# Python Calaos dev doc

## Calaos IOs

When implementing a new item type, look at the
[Calaos source code](https://github.com/calaos/calaos_base/blob/master/src/bin/calaos_server/IO/).
Once the require device type is found, two things are important:

- the calls to `ioDoc->actionAdd` allow knowing all available actions, that
  may be implemented in pycalaos
- the call to `EventManager::create` allows knowing which data we may receive
  as events

If the type inherits from another one, these calls may be defined in that other
type.

## Item types

To support a new Calaos IO, either use an existing item type (see the mapping
section in the README) or create a new one.

An item type must inherit `Item` and be declared in the `types` dictionary at
the end of the `item.py` file.

An item type may:

- have an `_translate(self, state)` method, to translate from the Calaos
  state value (as provided to `EventManager::create` in the Calaos source code)
  to the pycalaos state value (optional if they are identical)
- have other methods, to send commands to Calaos (ideally, these methods must be
  named after the actions decribed in the `ioDoc->actionAdd` calls)

After creating a new item type, Add a line in the mapping table in `README.md`,
and add a subsection.
