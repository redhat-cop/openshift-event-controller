#!/usr/bin/env python

import os
import requests
import json
from IPAClient import IPAClient
from OpenSSL import crypto
from OpenShiftWatcher import OpenShiftWatcher


def watch_routes():
    watcher = OpenShiftWatcher(os_api_endpoint=os.environ['OS_API'],
                               os_resource=os.environ['OS_RESOURCE'],
                               os_namespace=os.environ['OS_NAMESPACE'],
                               os_auth_token=os.environ['OS_TOKEN'])

    for event in watcher.stream():
        if type(event) is dict and 'type' in event:
            if event['type'] == 'ADDED':
                update_route(event)
            elif event['type'] == 'MODIFIED':
                route = get_route(event)
                if route.status_code == 404:
                    delete_route(event)
                else:
                    print 'Route \'{0}\' modified'.format(event['object']['metadata']['name'])

def get_route(event):
    route_name = event['object']['metadata']['name']

    req = requests.get('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(os.environ['OS_API'], os.environ['OS_NAMESPACE'], route_name),
                       headers={'Authorization': 'Bearer {0}'.format(os.environ['OS_TOKEN']), 'Content-Type':'application/strategic-merge-patch+json'},
                       verify=False
                       )

    return req

def update_route(event):
    route_fqdn = event['object']['spec']['host']
    route_name = event['object']['metadata']['name']

    ipa_client = IPAClient(ipa_user=os.environ['IPA_USER'],
                           ipa_password=os.environ['IPA_PASSWORD'],
                           ipa_url=os.environ['IPA_URL'])
    ipa_client.create_host(route_fqdn)
    certificate, key = ipa_client.create_cert(route_fqdn, os.environ['IPA_REALM'])

    try:
        #TODO: Update Route
#        print "Update Route Request: ", 'https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(os.environ['OS_API'], os.environ['OS_NAMESPACE'], route_name)
        req = requests.patch('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(os.environ['OS_API'], os.environ['OS_NAMESPACE'], route_name),
                             headers={'Authorization': 'Bearer {0}'.format(os.environ['OS_TOKEN']), 'Content-Type':'application/strategic-merge-patch+json'},
                             data=json.dumps({'spec': {'tls': {'certificate': '-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----'.format(
                                 '\n'.join(certificate[i:i+65] for i in xrange(0, len(certificate), 65))),
                                                               'key': '{0}'.format(key.exportKey('PEM'))}}}),
                             params="", verify=False)

        print "    OpenShift Route Update Return Code: {0}".format(req.status_code)
    except Exception as e:
        print "Route update exception: ", e

def delete_route(event):
    route_fqdn = event['object']['spec']['host']
    route_name = event['object']['metadata']['name']

    try:
        ipa_client = IPAClient(ipa_user=os.environ['IPA_USER'],
                               ipa_password=os.environ['IPA_PASSWORD'],
                               ipa_url=os.environ['IPA_URL'])
        ipa_client.delete_host(route_fqdn)
        print 'Route certificate for \'{0}\' deleted'.format(route_fqdn)
    except Exception as e:
        print "Certificate delete failed: ", e

def main():
    watch_routes()

if __name__ == '__main__':
    main()
