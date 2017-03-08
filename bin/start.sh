#!/bin/bash

SCRIPT_BASE=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ -z ${CONFIG_FILE+x} ]; then
  python /opt/event-watcher/watch.py
else
  python /opt/event-watcher/watch.py --config ${CONFIG_FILE}
fi
