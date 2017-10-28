import argparse
import configparser
import constants
import os
from errors import *
class WatcherConfig(object):
    def __init__(self):

        # Parse Arguments from the command line
        parser = argparse.ArgumentParser(description=constants.DESCRIPTION)
        parser.add_argument('-c', '--config')
        args = parser.parse_args()
        self.config_file = args.config

        # First validate arguments
        self.validated = self.validateArgs(args)
        if self.validated['is_valid']:
            self.config = configparser.ConfigParser()
            if self.config_file is not None:
                self.config.read(self.config_file)

            # Get Plugin so we know how to parse the rest of the args
            self.plugin = self.getPlugin()

            self.log_level = self.getParam(constants.ENV_LOG_LEVEL, '', constants.DEFAULT_LOG_LEVEL)

            self.k8s_token = self.getParam(constants.ENV_K8S_TOKEN, constants.DEFAULT_K8S_TOKEN)
            self.k8s_namespace = self.getParam(constants.ENV_K8S_NAMESPACE, constants.DEFAULT_K8S_NAMESPACE)
            self.k8s_endpoint = self.getParam(constants.ENV_K8S_API, '', constants.DEFAULT_K8S_API)
            self.k8s_ca = self.getParam(constants.ENV_K8S_CA, '', constants.DEFAULT_K8S_CA)
            self.k8s_namespaced = self.getParam(constants.ENV_K8S_NAMESPACED, constants.DEFAULT_K8S_NAMESPACED)
            self.k8s_api_path = self.getParam(constants.ENV_K8S_API_PATH)
            self.k8s_api_group = self.getParam(constants.ENV_K8S_API_GROUP)
            self.k8s_api_version = self.getParam(constants.ENV_K8S_API_VERSION, constants.DEFAULT_K8S_API_VERSION)
            self.k8s_resource = self.getParam(constants.ENV_K8S_RESOURCE)

    def getPlugin(self):
        try:
            return os.environ[constants.ENV_PLUGIN.upper()]
        except KeyError:
            try:
                return self.config['global'][constants.ENV_PLUGIN.lower()]
            except KeyError:
                return constants.DEFAULT_WATCHER_PLUGIN

    def getPluginConfig(self):
        if self.config_file is not None:
            return self.config["plugin_{0}".format(self.plugin)]
        else:
            return {}

    def getParam(self, env = '', file='', default = ''):
        try:
            return os.environ[env.upper()]
        except KeyError:
            try:
                if 'global' in self.config:
                    if self.config['global'].get(env.lower()) == None:
                        raise KeyError('No Log Level Set')
                    return self.config['global'].get(env.lower())
            except KeyError:
                try:
                    return open(file, 'r').read().strip()
                except IOError:
                    return default

    def validateArgs(self, args):
        validated = {}
        if (self.config_file is not None) and (not os.path.exists(self.config_file)):
            validated['is_valid'] = False
            validated['reason'] = 'Config file not found: {0}'.format(self.config_file)
            validated['log_level'] = 'CRITICAL'
        else:
            validated['is_valid'] = True
        return validated

    def validateConfig(self):
        # Kube resource should be set when API path not set
        if not self.k8s_api_path and not self.k8s_resource:
            raise InvalidResourceError(
                'Kubernetes resource not set. Either export {0}=<kind>, or set {1}=<kind> in {2}'.format(
                    constants.ENV_K8S_RESOURCE.upper(),
                    constants.ENV_K8S_RESOURCE.lower(),
                    self.config_file
                )
            )
        # Namespace should be set when namespace is expected
        if self.k8s_namespaced and not self.k8s_namespace:
            raise InvalidNamespaceError(
                'Namespace is not set. Either export {0}=<kind>, or set {1}=<kind> in {2}'.format(
                    constants.ENV_K8S_NAMESPACE.upper(),
                    constants.ENV_K8S_NAMESPACE.lower(),
                    self.config_file
                )
            )
        # API URL should be set
        if not self.k8s_endpoint:
            raise InvalidEndpointError(
                'Kubeneretes API Endpoint is not set. Either export {0}=<kind>, or set {1}=<kind> in {2}'.format(
                    constants.ENV_K8S_API.upper(),
                    constants.ENV_K8S_API.lower(),
                    self.config_file
                )
            )
        # Token should be set
        if not self.k8s_token:
            raise InvalidTokenError(
                'Kubeneretes Token is not set. Either export {0}=<kind>, or set {1}=<kind> in {2}'.format(
                    constants.ENV_K8S_TOKEN.upper(),
                    constants.ENV_K8S_TOKEN.lower(),
                    self.config_file
                )
            )
        # We should warn if CA is not set
        if not self.k8s_ca:
            raise InsecureError(
                'No Kubernetes CA file was loaded. Errors are likely. To remove this warning, export {0}=/path/to/ca.crt or set {1}=/path/to/ca.crt in {2}'.format(
                    constants.ENV_K8S_CA.upper(),
                    constants.ENV_K8S_CA.lower(),
                    self.config_file
                )
            )
