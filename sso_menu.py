
#!/usr/bin/env python3

import os
import sys

device_user = os.environ.get("USER")
if not device_user:
    print("Cannot detect USER, exiting.")
    sys.exit(1)

def prompt():
    sys.stdout.write("search or select one:")
    sys.stdout.flush()

while True:
    prompt()

    line = sys.stdin.readline()

    if line is None:
        continue

    ip = line.strip()

    if not ip:
        continue

    if ip.lower() in ("exit", "quit"):
        sys.exit(0)

    break

cmd = [
    "ssh",
    "-o", "StrictHostKeyChecking=no",
    "{}@{}".format(device_user, ip)
]

os.execvp(cmd[0], cmd)
