#!/usr/bin/env python

import os
import requests
import json
import logging
import signal
from OpenShiftWatcher import OpenShiftWatcher

logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger('watcher')
logger.setLevel(logging.INFO)
ca_trust = os.getenv('SSL_CA_TRUST', '/etc/ssl/certs/ca-bundle.trust.crt')
logger.debug("CA Trust: {0}".format(ca_trust))
need_cert_annotation = os.getenv('NEED_CERT_ANNOTATION', 'openshift.io/managed.cert')
logger.debug(json.dumps(dict(os.environ), indent=2, sort_keys=True))
k8s_token=os.getenv('OS_TOKEN')
k8s_namespace=os.getenv('OS_NAMESPACE')
k8s_endpoint=os.environ['OS_API']

def watch(resource_type, plugin_name, *args, **kwargs):
    plugin = load_plugin(plugin_name)
    watcher = OpenShiftWatcher(os_api_endpoint=k8s_endpoint,
                               os_resource=resource_type,
                               os_namespace=k8s_namespace,
                               os_auth_token=k8s_token,
                               ca_trust=ca_trust)

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
    resource_type = os.getenv('OS_RESOURCE')
    plugin_name = os.getenv('WATCHER_PLUGIN', 'simple')
    watch(resource_type, plugin_name)

if __name__ == '__main__':
    main()
