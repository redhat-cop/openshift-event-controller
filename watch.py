#!/usr/bin/env python

import os
import requests
import json
import logging
import signal
from config import WatcherConfig
from OpenShiftWatcher import OpenShiftWatcher

config = WatcherConfig()

logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger('watcher')
logger.setLevel(config.LOG_LEVEL)
logger.debug(json.dumps(dict(os.environ), indent=2, sort_keys=True))
logger.debug("CA Trust: {0}".format(config.k8s_ca))

def watch(resource_type, plugin_name, *args, **kwargs):
    plugin = load_plugin(plugin_name)
    watcher = OpenShiftWatcher(os_api_endpoint=config.k8s_endpoint,
                               os_resource=resource_type,
                               os_namespace=config.k8s_namespace,
                               os_auth_token=config.k8s_token,
                               ca_trust=config.k8s_ca)

    for event in watcher.stream():
        if type(event) is dict and 'type' in event:
            result,level = plugin.handle_event(event, *args, **kwargs)
            log(result, level)

def log(message, level):
    logger.log(logger.level, message)

def load_plugin(name):
    mod = __import__("plugin_%s" % name)
    return mod

def main():
    resource_type = os.getenv('K8S_RESOURCE')
    plugin_name = os.getenv('WATCHER_PLUGIN', 'simple')
    watch(resource_type, plugin_name)

if __name__ == '__main__':
    main()
