import traceback, sys, os, requests, json, six
from IPAClient import IPAClient

def handle_event(watcher, event, config):

    route_fqdn = event['object']['spec']['host']
    route_name = event['object']['metadata']['name']

    if need_cert(event, config, watcher.logger):
        watcher.logger.info("[ROUTE NEEDS CERT]: {0}".format(route_fqdn))
        if event['type'] == 'ADDED':
            watcher.logger.info("[ROUTE ADDED]: {0}".format(route_fqdn))
            watcher.logger.debug("[ROUTE ADDED]: {0}".format(event))
            update_route(route_fqdn, route_name, config, watcher.logger, watcher)
        elif event['type'] == 'MODIFIED':
            update_route(route_fqdn, route_name, config, watcher.logger, watcher)
            watcher.logger.info("[ROUTE MODIFIED]: {0}".format(route_fqdn))
            watcher.logger.debug("[ROUTE MODIFIED]: {0}".format(event))

            #TODO: Get modified cert route and make sure cert data matches hostname. If not, regenerate cert
        elif event['type'] == 'DELETED':
                delete_route(route_fqdn, config, watcher.logger)
                watcher.logger.info("[ROUTE DELETED]: {0}".format(route_fqdn))
        else:
            watcher.logger.debug("[UNKNOWN EVENT TYPE]: {0}".format(event))
    else:
        watcher.logger.debug("No cert needed")


    message = "Kind: {0}; Name: {1}".format(event['object']['kind'], event['object']['metadata']['name'])
    log_level = "INFO"
    return message, log_level

def get_route(route_name, logger, watcher):
    req = requests.get('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(watcher.config.k8s_endpoint, watcher.config.k8s_namespace, route_name),
                       headers={'Authorization': 'Bearer {0}'.format(watcher.config.k8s_token), 'Content-Type':'application/strategic-merge-patch+json'},
                       verify=watcher.config.k8s_ca)
    return req

def need_cert(event, config, logger):
    try:
        route_annotation = event['object']['metadata']['annotations'][config.get('need_cert_annotation')]
        try:
            route_annotation_state = event['object']['metadata']['annotations']['{0}.state'.format(config.get('need_cert_annotation'))]
        except KeyError:
            route_annotation_state = False
        logger.debug("Found annotation: {0}={1}".format(config.get('need_cert_annotation'),route_annotation))
        return route_annotation == "true" and route_annotation_state != 'created'
    except KeyError:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logger.debug("Error message: {0}".format(repr(traceback.format_exception(exc_type, exc_value, exc_traceback,
                              limit=2))))
        logger.debug("Got an event with no annotation, so nothing to do: {0}".format(event))
        return False
    else:
        logger.debug("Unknown error")
        return False

def update_route(route_fqdn, route_name, config, logger, watcher):
    ipa_client = IPAClient(
                    ipa_user = config.get('ipa_user'),
                    ipa_password = config.get('ipa_password'),
                    ipa_url = config.get('ipa_url'),
                    ca_trust = config.get('ca_trust', False)
                )
    ipa_client.create_host(route_fqdn)
    certificate, key = ipa_client.create_cert(route_fqdn, config.get('ipa_realm'))
    logger.info("[CERT CREATED]: {0}".format(route_fqdn))
    logger.debug("Cert: {0}\nKey: {1}\n".format(certificate, key.exportKey().decode('UTF-8')))

    req = requests.patch('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(watcher.config.k8s_endpoint, watcher.config.k8s_namespace, route_name),
                         headers={'Authorization': 'Bearer {0}'.format(watcher.config.k8s_token), 'Content-Type':'application/strategic-merge-patch+json'},
                         data=json.dumps({'metadata': {'annotations': {'{0}.state'.format(config.get('need_cert_annotation')): 'created'}}, 'spec': {'tls': {'certificate': '-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----'.format(
                             '\n'.join(certificate[i:i+65] for i in six.moves.range(0, len(certificate), 65))),
                                                           'key': '{0}'.format(key.exportKey('PEM').decode('UTF-8'))}}}),
                         params="", verify=watcher.config.k8s_ca)
    logger.info("[ROUTE UPDATED]: {0}".format(route_fqdn))

def delete_route(route_fqdn, config, logger):
    ipa_client = IPAClient(
                ipa_user = config.get('ipa_user'),
                ipa_password = config.get('ipa_password'),
                ipa_url = config.get('ipa_url'),
                ca_trust = config.get('ca_trust', False)
            )
    ipa_client.delete_host(route_fqdn)
    logger.info("[CERT DELETED]: {0}".format(route_fqdn))
