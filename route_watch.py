#!/usr/bin/env python

import os
import requests
import json
import pkiutils
from IPAClient import IPAClient
from OpenSSL import crypto
from OpenShiftWatcher import OpenShiftWatcher


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
            route_fqdn = event['object']['spec']['host']
            try:
                #TODO: Create Private Key and CSR
                key = pkiutils.create_rsa_key(bits=2048,
                                              keyfile=None,
                                              format='PEM',
                                              passphrase=None)
                csr = pkiutils.create_csr(key,
                                          "/CN={0}/C=US/O=Test organisation/".format(route_fqdn),
                                          csrfilename=None,
                                          attributes=None)

                print "    CSR and Key Create Complete"
            #print csr
            except Exception as e:
                raise Exception("Create CSR Exception: {0}".format(e))

            ipa_client = IPAClient(ipa_user=os.environ['IPA_USER'],
                                   ipa_password=os.environ['IPA_PASSWORD'],
                                   ipa_url=os.environ['IPA_URL'])
            ipa_client.create_host(route_fqdn)
            ipa_client.create_cert(route_fqdn, os.environ['IPA_REALM'], key, csr)

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

def main():
    watch_routes()

if __name__ == '__main__':
    main()
