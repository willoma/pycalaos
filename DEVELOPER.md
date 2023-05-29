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

An item type may have:

- a `_translate(self, state: str)` method, to translate from the Calaos state
  value (see `EventManager::create` calls in the Calaos source code) to the
  pycalaos state value (optional if they are identical, ie. raw strings)
- other methods, to send commands to Calaos (ideally, these methods must be
  named after the actions decribed in the `ioDoc->actionAdd` calls)

After creating a new item type, Add a line in the mapping table in `README.md`,
and add a subsection in the same section of the `README.md`.

## Publishing a release

These notes are here just in case I forget the process, because I do those
things too rarely to remember them correctly...

Firstn change version in `setup.py`, then execute:

```plain
python setup.py sdist
twine upload dist/*
```
