#!/bin/bash

if [ -z ${CONFIG_FILE+x} ]; then
  python /opt/event-watcher/watch.py
else
  python /opt/event-watcher/watch.py --config ${CONFIG_FILE}
fi
