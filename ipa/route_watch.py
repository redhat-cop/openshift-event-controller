#!/usr/bin/env python

import os
import requests
import json
import logging
from IPAClient import IPAClient
from OpenSSL import crypto
from OpenShiftWatcher import OpenShiftWatcher

logging.basicConfig(format="%(asctime)s %(message)s")
logger = logging.getLogger('routewatcher')
logger.setLevel(logging.INFO)


def watch_routes():
    watcher = OpenShiftWatcher(os_api_endpoint=os.environ['OS_API'],
                               os_resource=os.environ['OS_RESOURCE'],
                               os_namespace=os.environ['OS_NAMESPACE'],
                               os_auth_token=os.environ['OS_TOKEN'])

    for event in watcher.stream():
        if type(event) is dict and 'type' in event:
            route_fqdn = event['object']['spec']['host']
            route_name = event['object']['metadata']['name']
            if event['type'] == 'ADDED':
                logger.info("[ROUTE ADDED]: {0}".format(route_fqdn))
                logger.debug("[ROUTE ADDED]: {0}".format(event))
                update_route(route_fqdn, route_name)
            elif event['type'] == 'MODIFIED':
                logger.info("[ROUTE MODIFIED]: {0}".format(route_fqdn))
                logger.debug("[ROUTE MODIFIED]: {0}".format(event))

                route = get_route(route_name)
                if route.status_code == 404:
                    delete_route(route_fqdn)
                    logger.info("[ROUTE DELETED]: {0}".format(route_fqdn))
                else:
                    continue

def get_route(route_name):
    req = requests.get('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(os.environ['OS_API'], os.environ['OS_NAMESPACE'], route_name),
                       headers={'Authorization': 'Bearer {0}'.format(os.environ['OS_TOKEN']), 'Content-Type':'application/strategic-merge-patch+json'},
                       verify=False)
    return req

def update_route(route_fqdn, route_name):
    ipa_client = IPAClient(ipa_user=os.environ['IPA_USER'],
                           ipa_password=os.environ['IPA_PASSWORD'],
                           ipa_url=os.environ['IPA_URL'])
    ipa_client.create_host(route_fqdn)
    certificate, key = ipa_client.create_cert(route_fqdn, os.environ['IPA_REALM'])
    logger.info("[CERT CREATED]: {0}".format(route_fqdn))

    try:
        req = requests.patch('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(os.environ['OS_API'], os.environ['OS_NAMESPACE'], route_name),
                             headers={'Authorization': 'Bearer {0}'.format(os.environ['OS_TOKEN']), 'Content-Type':'application/strategic-merge-patch+json'},
                             data=json.dumps({'spec': {'tls': {'certificate': '-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----'.format(
                                 '\n'.join(certificate[i:i+65] for i in xrange(0, len(certificate), 65))),
                                                               'key': '{0}'.format(key.exportKey('PEM'))}}}),
                             params="", verify=False)
        logger.info("[ROUTE UPDATED]: {0}".format(route_fqdn))
    except Exception as e:
        logger.info("[ROUTE UPDATE ERROR]: Unable to update route {0}.")
        logger.debug("[ROUTE UPDATE ERROR]: {0}".format(e))

def delete_route(route_fqdn):
    try:
        ipa_client = IPAClient(ipa_user=os.environ['IPA_USER'],
                               ipa_password=os.environ['IPA_PASSWORD'],
                               ipa_url=os.environ['IPA_URL'])
        ipa_client.delete_host(route_fqdn)
        logger.info("[CERT DELETED]: {0}".format(route_fqdn))
    except Exception as e:
        logger.info("[CERT DELETE ERROR]: Unable to delete certificate {0}.")
        logger.debug("[CERT DELETE ERROR]: {0}".format(e))

def main():
    watch_routes()

if __name__ == '__main__':
    main()
