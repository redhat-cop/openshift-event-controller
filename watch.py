#!/usr/bin/env python

import os
import requests
import json
import logging
import signal
import sys
from config import WatcherConfig
from errors import *
from OpenShiftWatcher import OpenShiftWatcher

class EventWatcher(object):
    def __init__(self):

        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s")
        self.logger = logging.getLogger('watcher')
        self.config = self.getConfig()

        self.logger.setLevel(self.config.log_level)
        self.logger.debug(json.dumps(dict(os.environ), indent=2, sort_keys=True))
        self.logger.debug("CA Trust: {0}".format(self.config.k8s_ca))
        self.logger.info("Loading config file from {0}".format(self.config.config_file))

        self.watch(self.config.k8s_resource, self.config.plugin)

    def watch(self, resource_type, plugin_name, *args, **kwargs):
        plugin = self.load_plugin(plugin_name)
        watcher = OpenShiftWatcher(os_api_endpoint=self.config.k8s_endpoint,
                                   os_resource=resource_type,
                                   os_namespace=self.config.k8s_namespace,
                                   os_auth_token=self.config.k8s_token,
                                   ca_trust=self.config.k8s_ca)

        for event in watcher.stream():
            if type(event) is dict and 'type' in event:
                result,level = plugin.handle_event(event, self.config.config['plugin_{0}'.format(plugin_name)], *args, **kwargs)
                self.log(result, level)

    def getConfig(self):
        config = WatcherConfig()

        # Check that args are properly set
        if not config.validated['is_valid']:
            log_level = config.validated['log_level']
            self.log(config.validated['reason'], log_level)
            sys.exit(1)

        try:
            config.validateConfig()
        except Error as error:
            if isinstance(error, FatalError):
                self.log(error.message, 'CRITICAL')
                sys.exit(error.exit_code)
            elif isinstance(error, WarningError):
                self.log(error.message, 'WARNING')
            else:
                self.log(error.message, 'ERROR')

        return config


    def log(self, message, log_level):
        self.logger.debug('Log level: {0}'.format(log_level))
        self.logger.log(logging.getLevelName(log_level), message)

    def load_plugin(self, name):
        mod = __import__("plugin_%s" % name)
        return mod

if __name__ == '__main__':
    EventWatcher()
