
import os
import os.path
import requests

import sys
import dns.name
import dns.resolver
import dns.update
import dns.tsigkeyring

def handle_event(watcher, event, config):
    message = "Kind: {0}; Name: {1}; Event Type:{2};".format(
                  event['object']['kind'],
                  event['object']['metadata']['name'],
                  event['type']
              )
    log_level = config.get('message_log_level','INFO')
    logger = watcher.logger


    if type(event) is dict and 'type' in event:
        if event['type'] == 'ADDED':
            remove_dns(event, config, logger)
            if add_dns(event, config, logger):
                message = 'DNS record \'{0}\' added for route \'{1}\''.format(
                              event['object']['spec']['host'],
                              event['object']['metadata']['name']
                          )
        elif event['type'] == 'DELETED':
            if remove_dns(event, config, logger):
                message = 'DNS record \'{0}\' removed for route \'{1}\''.format(
                              event['object']['spec']['host'],
                              event['object']['metadata']['name']
                          )
        elif event['type'] == 'MODIFIED':
            route = get_route(watcher, event, config)
            if route.status_code == 404:
                if remove_dns(event, config, logger):
                    message = 'DNS record \'{0}\' removed for route \'{1}\''.format(
                                  event['object']['spec']['host'],
                                  event['object']['metadata']['name']
                              )
            else:
                message = 'Route \'{0}\' modified, but no action taken.'.format(
                              event['object']['metadata']['name']
                          )

    return message, log_level


def get_route(watcher, event, config):
    route_name = event['object']['metadata']['name']
    k8s_endpoint = watcher.config.k8s_endpoint
    k8s_namespace = watcher.config.k8s_namespace
    k8s_token = watcher.config.k8s_token
    k8s_ca = watcher.config.k8s_ca

    req = requests.get(
                  'https://{0}/oapi/v1/namespaces/{1}/routes/{2}'
                  .format(k8s_endpoint, k8s_namespace, route_name),
              headers={
                  'Authorization': 'Bearer {0}'.format(k8s_token),
                  'Content-Type':'application/strategic-merge-patch+json'
              },
              verify=k8s_ca)

    return req

# This function initially sourced from https://gist.github.com/pklaus/4619865
# - modifications have been made afterwards
def get_key(file_name, logger):
    if os.path.exists(file_name) == False:
        logger.error("Specified key file does not exist. Please correct") 
        return False

    f = open(file_name)
    keyfile = f.read().splitlines()
    f.close()

    hostname = keyfile[0].rsplit(' ')[1].replace('"', '').strip()
    algo = keyfile[1].split()[1].replace(';','').replace('-','_').upper().strip()
    key = keyfile[2].split()[1].replace('}','').replace(';','').replace('"', '').strip()

    k = {hostname:key}

    try:
        key_ring = dns.tsigkeyring.from_text(k)
    except:
        logger.error(
            '\'{0}\' is not a valid key. '
            'The file should be in DNS KEY record format. See dnssec-keygen(8)'
            .format(k)
        )
        return False
    return [key_ring, algo]


def get_zone(dns_a_record, config, logger):
    resolv_conf = config.get('resolv_conf')
    if not resolv_conf:
        return None
 
    if os.path.exists(resolv_conf) == False:
        logger.warning("Specified resolv.conf does not exist. Please correct") 
    else:
        try:
            resolver = dns.resolver.Resolver(resolv_conf)
        except Exception as e:
            logger.error("Failed to create a valid Resolver. (error: {0})".format(e))

        dns_zone = dns.resolver.zone_for_name(dns_a_record, resolver=resolver)

    try:
        dns_zone
    except NameError:
        dns_zone = dns.resolver.zone_for_name(dns_a_record)

    return dns_zone
 

def modify_dns(action, event, config, logger):
    dns_server = config.get('dns_server')
    dns_key_file = config.get('dns_key_file')
    application_router_ip = config.get('application_router_ip')

    dns_a_record = event['object']['spec']['host']

    try:
        name_object = dns.name.from_text(dns_a_record)
    except Exception as e:
        logger.error("Not a valid DNS name: {0} (error: {1})".format(dns_a_record, e));
        return False

    dns_zone = get_zone(dns_a_record, config, logger)
    dns_name = name_object.relativize(dns_zone) 

    logger.debug('Zone: {0}, DNS Name: {1}'.format(dns_zone, dns_name))

    key_ring, key_algorithm = get_key(dns_key_file, logger)
    dns_update = dns.update.Update(
                     dns_zone,
                     keyring=key_ring,
                     keyalgorithm=getattr(dns.tsig, key_algorithm)
                 )

    if action == 'add':
        dns_update.add(dns_name, '180', 'A', application_router_ip)
    elif action == 'del':
        dns_update.delete(dns_name, 'A', application_router_ip)

    logger.debug('dns_update {0}'.format(dns_update))

    try:
        dns_response = dns.query.tcp(dns_update, dns_server)
    except dns.tsig.PeerBadKey:
        logger.error("Invalid key for server {0}".format(dns_server))
        return False
    except dns.tsig.PeerBadSignature:
        logger.error("Invalid key signature for server {0}".format(dns_server))
    except Exception as e:
        logger.error("Failed to update DNS with error {0}".format(e)) 
        return False
    return True


def remove_dns(event, config, logger):
    return modify_dns('del', event, config, logger)


def add_dns(event, config, logger):
    return modify_dns('add', event, config, logger)


