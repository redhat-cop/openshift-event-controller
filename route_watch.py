#!/bin/python

import os
import requests
import json
import pkiutils
from OpenSSL import crypto

#ipaurl="https://idm-1.etl.lab.eng.rdu2.redhat.com/ipa/"
ipaurl = os.environ['IPA_URL']
#realm="ETL.LAB.ENG.RDU2.REDHAT.COM"
realm = os.environ['IPA_REALM']
ipa_user = os.environ['IPA_USER']
ipa_password = os.environ['IPA_PASSWORD']

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
            print line
            if line:
                try:
                    yield json.loads(line)
                    # TODO: Use the specific exception type here.
                    # TODO: Logging -> "No Json Object could be decoded."
                except Exception as e:
                    continue

def watch_routes():
    watcher = OpenShiftWatcher(os_api_endpoint=os.environ['OS_API'],
                               os_resource=os.environ['OS_RESOURCE'],
                               os_namespace=os.environ['OS_NAMESPACE'],
                               os_auth_token=os.environ['OS_TOKEN'])

    for event in watcher.stream():
        if event['type'] == 'ADDED':
            print event
            print
            session = requests.Session()

            #TODO: Create Private Key and CSR
            key = pkiutils.create_rsa_key(bits=2048, keyfile=None, format='PEM', passphrase=None)
            csr = pkiutils.create_csr(key, "/CN={0}/C=US/O=Test organisation/".format(event['object']['spec']['host']), csrfilename=None, attributes=None)
            print "    CSR and Key Create Complete"
            #print csr

            #TODO: Sign Request with Dynamic CA (IPA)

            resp = session.post('{0}session/login_password'.format(ipaurl),
                                params="", data = {'user':ipa_user,'password':ipa_password}, verify=False,
                                headers={'Content-Type':'application/x-www-form-urlencoded', 'Accept':'applicaton/json'})

            header={'referer': ipaurl, 'Content-Type':'application/json', 'Accept':'application/json'}

            # CREATE HOST
            create_host = session.post('{0}session/json'.format(ipaurl), headers=header,
                                       data=json.dumps({'id': 0, 'method': 'host_add', 'params': [[event['object']['spec']['host']], {'force': True}]}), verify=False)

            print "    Host Create Return Code: {0}".format(create_host.status_code)

            # CREATE CERT
            cert_request = session.post('{0}session/json'.format(ipaurl), headers=header,
                                        data=json.dumps({'id': 0, 'method': 'cert_request', 'params': [[csr], {'principal': 'host/{0}@{1}'.format(event['object']['spec']['host'], realm),
                                                                                                               'request_type': 'pkcs10', 'add': False}]}), verify=False)

            print "    Certificate Signing Return Code: {0}".format(cert_request.status_code)
            #print "  {0}".format(cert_request.json())
            cert_resp = cert_request.json()

            print "CERTIFICATE:\n-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----".format(
                '\n'.join(cert_resp['result']['result']['certificate'][i:i+65] for i in xrange(0, len(cert_resp['result']['result']['certificate']), 65)))
            print
            print "KEY:\n {0}".format(key.exportKey('PEM'))

            #TODO: Update Route
            req = requests.patch('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(openshift_api, namespace, event['object']['metadata']['name']),
                                 headers={'Authorization': 'Bearer {0}'.format(token), 'Content-Type':'application/strategic-merge-patch+json'},
                                 data=json.dumps({'spec': {'tls': {'certificate': '-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----'.format(
                                     '\n'.join(cert_resp['result']['result']['certificate'][i:i+65] for i in xrange(0, len(cert_resp['result']['result']['certificate']), 65))),
                                                                   'key': '{0}'.format(key.exportKey('PEM'))}}}),
                                 params="", verify=False)

            print "    OpenShift Route Update Return Code: {0}".format(req.status_code)

watch_routes()
