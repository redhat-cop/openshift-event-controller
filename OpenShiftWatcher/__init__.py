import requests
import json

class OpenShiftWatcher(object):
    def __init__(self, os_api_endpoint, os_resource, os_namespace, os_auth_token):
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

    def stream(self):
        req = requests.Request("GET", self.os_api_url,
                               headers={'Authorization': 'Bearer {0}'.format(self.os_auth_token)},
                               params="").prepare()

        resp = self.session.send(req, stream=True, verify=False)
        # TODO: Logging -> "Response"

        for line in resp.iter_lines():
            if line:
                try:
                    yield json.loads(line)
                    # TODO: Use the specific exception type here.
                    # TODO: Logging -> "No Json Object could be decoded."
                except Exception as e:
                    continue
