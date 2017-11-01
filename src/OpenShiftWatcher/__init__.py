import requests
import json

class OpenShiftWatcher(object):
    def __init__(self, os_api_endpoint, os_auth_token, os_namespaced, os_namespace, os_api_path, os_api_group, os_api_version, os_resource, ca_trust='/etc/ssl/certs/ca-bundle.trust.crt'):
        ''' os_auth_token generated from `oc whoami -t`

            Example:
            watcher = OpenShiftWatcher(os_api_endpoint="master1.example.com:8443",
                                       os_auth_token="lTBiDnvYlHhuOl3C9Tj_Mb-FvL0hcMMONIua0E0D5CE",
                                       os_namespaced='True',
                                       os_namespace="joe",
                                       os_api_path="",
                                       os_api_group="oapi",
                                       os_api_version="v1",
                                       os_resource="routes")
        '''
        self.os_api_url = self.generate_url_resource(os_api_endpoint, os_namespaced, os_namespace, os_api_path, os_api_group, os_api_version, os_resource)
        self.os_auth_token = os_auth_token
        self.session = requests.Session()
        self.ca_trust = ca_trust

    def stream(self):
        req = requests.Request("GET", self.os_api_url,
                               headers={'Authorization': 'Bearer {0}'.format(self.os_auth_token)},
                               params=""
                               ).prepare()

        resp = self.session.send(req, stream=True, verify=self.ca_trust)

        if resp.status_code != 200:
            raise Exception("Unable to contact OpenShift API at {0}. Message from server: {1}".format(self.os_api_url, resp.text))

        for line in resp.iter_lines():
            if line:
                try:
                    yield json.loads(line.decode('utf-8'))
                    # TODO: Use the specific exception type here.
                    # TODO: Logging -> "No Json Object could be decoded."
                except Exception as e:
                    raise Exception("Watcher error: {0}".format(e))

    def generate_url_resource(self, os_api_endpoint, os_namespaced, os_namespace, os_api_path, os_api_group, os_api_version, os_resource):
        if os_api_path:
            return "https://{0}/{1}?watch=true".format(os_api_endpoint, os_api_path)
        else:
            if os_namespaced == 'True':
                return "https://{0}/{1}/{2}/namespaces/{3}/{4}?watch=true".format(os_api_endpoint, os_api_group, os_api_version, os_namespace, os_resource)
            else:
                return "https://{0}/{1}/{2}/{3}?watch=true".format(os_api_endpoint, os_api_group, os_api_version, os_resource)
