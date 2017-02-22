import constants
import os

class WatcherConfig(object):
    def __init__(self):
        self.LOG_LEVEL = self.getParam(constants.ENV_LOG_LEVEL, '', 'INFO')

        self.k8s_token = self.getParam(constants.ENV_K8S_TOKEN, constants.FILE_K8S_TOKEN)
        self.k8s_namespace = self.getParam(constants.ENV_K8S_NAMESPACE, constants.FILE_K8S_NAMESPACE)
        self.k8s_endpoint = self.getParam(constants.ENV_K8S_API)
        self.k8s_ca = self.getParam(constants.ENV_K8S_CA)

    def getParam(self, env = '', file = '', default = ''):
        try:
            return os.environ[env]
        except KeyError:
            try:
                return open(file, 'r').read().strip()
            except IOError:
                return default
