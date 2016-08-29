import requests
import json

class OpenShiftWatcher(object):
    def __init__(self, os_api_endpoint, os_resource, os_namespace, os_auth_token, ca_trust='/etc/ssl/certs/ca-bundle.trust.crt'):
        ''' os_auth_token generated from `oc whoami -t`

            Example:
            watcher = OpenShiftWatcher(os_api_endpoint="master1.example.com:8443",
                                       os_resource="routes",
                                       os_namespace="joe",
                                       os_auth_token="lTBiDnvYlHhuOl3C9Tj_Mb-FvL0hcMMONIua0E0D5CE")
        '''
        self.os_api_url = "https://{0}/oapi/v1/namespaces/{1}/{2}?watch=true".format(os_api_endpoint, os_namespace, os_resource)
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
            raise Exception("Unable to contact OpenShift API. Message from server: {0}".format(resp.text))

        for line in resp.iter_lines():
            if line:
                try:
                    yield json.loads(line.decode('utf-8'))
                    # TODO: Use the specific exception type here.
                    # TODO: Logging -> "No Json Object could be decoded."
                except Exception as e:
                    raise Exception("Watcher error: {0}".format(e))
