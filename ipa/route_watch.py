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
logger.setLevel(logging.DEBUG)
ca_trust = os.getenv('SSL_CA_TRUST', '/etc/ssl/certs/ca-bundle.trust.crt')
logger.debug("CA Trust: {0}".format(ca_trust))
need_cert_annotation = os.getenv('NEED_CERT_ANNOTATION', 'openshift.io/managed.cert')
logger.debug("{0}".format(os.environ))
k8s_token=os.getenv('TOKEN', open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r').read())
k8s_namespace=os.getenv('OS_NAMESPACE', open('/var/run/secrets/kubernetes.io/serviceaccount/namespace','r').read())


def watch_routes():
    watcher = OpenShiftWatcher(os_api_endpoint=os.environ['KUBERNETES_SERVICE_HOST'],
                               os_resource='routes',
                               os_namespace=k8s_namespace,
                               os_auth_token=k8s_token,
                               ca_trust=ca_trust)

    for event in watcher.stream():
        if type(event) is dict and 'type' in event:
            route_fqdn = event['object']['spec']['host']
            route_name = event['object']['metadata']['name']

            if need_cert(event):
                logger.info("[ROUTE NEEDS CERT]: {0}".format(route_fqdn))
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
                        #TODO: Get modified cert route and make sure cert data matches hostname. If not, regenerate cert
                        continue

def get_route(route_name):
    req = requests.get('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(os.environ['OS_API'], os.environ['OS_NAMESPACE'], route_name),
                       headers={'Authorization': 'Bearer {0}'.format(os.environ['OS_TOKEN']), 'Content-Type':'application/strategic-merge-patch+json'},
                       verify=ca_trust)
    return req

def need_cert(event):
    try:
        route_annotation = event['object']['metadata']['annotations'][need_cert_annotation]
        return route_annotation == "true"
    except KeyError as e:
        logger.debug("Got an event with no annotation, so nothing to do: {0}".format(event))
        return False
    else:
        return False



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
                             params="", verify=ca_trust)
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
        logger.info("[CERT DELETE ERROR]: Unable to delete certificate.")
        logger.debug("[CERT DELETE ERROR]: {0}".format(e))

def main():
    watch_routes()

if __name__ == '__main__':
    main()
