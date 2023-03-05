# Python Calaos

Client for the Calaos v3 home automation server. This client keeps the home,
rooms and items status in cache, in order to reduce the quantity of requests
towards the Calaos server.

Use `pycalaos.discover` to discover the Calaos server IP address.

Use `pycalaos.Client` to connect to the Calaos server.

This library has been developed with
[Home Assistant](https://www.home-assistant.io/) in mind.

The library has been tested with a Wago 750-849 controller and:

- single-click buttons
- triple-click buttons
- long-click buttons
- binary output
- DALI lights
