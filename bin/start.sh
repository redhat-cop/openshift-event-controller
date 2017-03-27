#!/bin/bash

if [ -z ${CONFIG_FILE+x} ]; then
  python /opt/event-controller/watch.py
else
  python /opt/event-controller/watch.py --config ${CONFIG_FILE}
fi
