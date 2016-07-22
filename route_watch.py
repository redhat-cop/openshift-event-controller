#!/bin/python

import os
import requests
import json
import pkiutils
from OpenSSL import crypto
from OpenShiftWatcher import OpenShiftWatcher

#ipaurl="https://idm-1.etl.lab.eng.rdu2.redhat.com/ipa/"
ipaurl = os.environ['IPA_URL']
#realm="ETL.LAB.ENG.RDU2.REDHAT.COM"
realm = os.environ['IPA_REALM']
ipa_user = os.environ['IPA_USER']
ipa_password = os.environ['IPA_PASSWORD']


def watch_routes():
    watcher = OpenShiftWatcher(os_api_endpoint=os.environ['OS_API'],
                               os_resource=os.environ['OS_RESOURCE'],
                               os_namespace=os.environ['OS_NAMESPACE'],
                               os_auth_token=os.environ['OS_TOKEN'])

    for event in watcher.stream():
        print event
        if type(event) is dict and 'type' in event and event['type'] == 'ADDED':
            print event
            print
            session = requests.Session()

            try:
                #TODO: Create Private Key and CSR
                key = pkiutils.create_rsa_key(bits=2048, keyfile=None, format='PEM', passphrase=None)
                csr = pkiutils.create_csr(key, "/CN={0}/C=US/O=Test organisation/".format(event['object']['spec']['host']), csrfilename=None, attributes=None)
                print "    CSR and Key Create Complete"
            #print csr
            except Exception as e:
                print "Create CSR Exception: ", e

class ipa_api(object):

    def __init__(self,ipa_user,ipa_password,ipa_host):
        self.session = requests.Session()
        self.ipa_url = ipa_host
        #TODO: Sign Request with Dynamic CA (IPA)
        # authenticate to IPA Server
        try:
            resp = session.post('{0}session/login_password'.format(ipaurl),
                            params="", data = {'user':ipa_user,'password':ipa_password}, verify=False,
                            headers={'Content-Type':'application/x-www-form-urlencoded', 'Accept':'applicaton/json'})
        except Exception as e:
            print "IPA Auth Exception: ", e

        self.header = {'referer': ipaurl, 'Content-Type':'application/json', 'Accept':'application/json'}

    def create_host(self,host):
                try:

                    # CREATE HOST [event['object']['spec']['host']]
                    create_host = self.session.post('{0}session/json'.format(self.ipa_url), headers=self.header,
                                               data=json.dumps({'id': 0, 'method': 'host_add', 'params': [host, {'force': True}]}), verify=False)

                    print "    Host Create Return Code: {0}".format(create_host.status_code)
                except Exception as e:
                    print "Create Host Exception: ", e

    def create_cert(self):

                try:
                    # CREATE CERT
                    cert_request = self.session.post('{0}session/json'.format(self.ipa_url), headers=header,
                                                data=json.dumps({'id': 0, 'method': 'cert_request', 'params': [[csr], {'principal': 'host/{0}@{1}'.format(event['object']['spec']['host'], realm),
                                                                                                                       'request_type': 'pkcs10', 'add': False}]}), verify=False)

                    print "    Certificate Signing Return Code: {0}".format(cert_request.status_code)
                    #print "  {0}".format(cert_request.json())
                    cert_resp = cert_request.json()
                except Exception as e:
                    print "Cert Create Exception", e

                print "CERTIFICATE:\n-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----".format(
                    '\n'.join(cert_resp['result']['result']['certificate'][i:i+65] for i in xrange(0, len(cert_resp['result']['result']['certificate']), 65)))
                print
                print "KEY:\n {0}".format(key.exportKey('PEM'))

def update_route():
            try:
                #TODO: Update Route
                req = requests.patch('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(os.environ['OS_API'], os.environ['OS_NAMESPACE'], event['object']['metadata']['name']),
                                     headers={'Authorization': 'Bearer {0}'.format(os.environ['OS_TOKEN']), 'Content-Type':'application/strategic-merge-patch+json'},
                                     data=json.dumps({'spec': {'tls': {'certificate': '-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----'.format(
                                         '\n'.join(cert_resp['result']['result']['certificate'][i:i+65] for i in xrange(0, len(cert_resp['result']['result']['certificate']), 65))),
                                                                       'key': '{0}'.format(key.exportKey('PEM'))}}}),
                                     params="", verify=False)

                print "    OpenShift Route Update Return Code: {0}".format(req.status_code)
            except Exception as e:
                print "Route update exception: ", e


watch_routes()
