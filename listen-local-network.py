#!/usr/bin/env python3

import json, time

from pycalaos import discover, Client

ip_address = discover(5)

if ip_address == "":
    ip_address = input(f"Please provide the Calaos server IP address: ")

try:
    f = open(f"credentials-{ip_address}.json")
    credentials = json.load(f)
    username = credentials["username"]
    password = credentials["password"]
except:
    username = input(f"Please provide the username for {ip_address}: ")
    password = input(f"Please provide the password for {ip_address}: ")

    f = open(f"credentials-{ip_address}.json", mode="w")
    json.dump({"username": username, "password": password}, f)

print("Connecting...")
client = Client("https://"+ip_address, username, password)
print("Connected.", end="", flush=True)

while True:
    time.sleep(0.5)
    events = client.poll()
    if len(events) > 0:
        print("\n")
        for ev in events:
            print(ev)
    else:
        print(".", end="", flush=True)
