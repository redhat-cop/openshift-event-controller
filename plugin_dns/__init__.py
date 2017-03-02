
import os
import requests
import json
import subprocess

def handle_event(self, event, config):
    message = "Kind: {0}; Name: {1}; Event Type:{2};".format(event['object']['kind'], event['object']['metadata']['name'], event['type'])
    log_level = config.get('message_log_level','INFO')

    if type(event) is dict and 'type' in event:
        if event['type'] == 'ADDED':
            remove_dns(event, config)
            add_dns(event, config)
            message = 'DNS record \'{0}\' added for route \'{1}\''.format(event['object']['spec']['host'], event['object']['metadata']['name'])
        elif event['type'] == 'DELETED':
            remove_dns(event, config)
            message = 'DNS record \'{0}\' removed for route \'{1}\''.format(event['object']['spec']['host'], event['object']['metadata']['name'])
        elif event['type'] == 'MODIFIED':
            route = get_route(self, event, config)
            if route.status_code == 404:
                remove_dns(event, config)
                message = 'DNS record \'{0}\' removed for route \'{1}\''.format(event['object']['spec']['host'], event['object']['metadata']['name'])
            else:
                message = 'Route \'{0}\' modified, but no action taken.'.format(event['object']['metadata']['name'])

    return message, log_level


def get_route(self, event, config):
    route_name = event['object']['metadata']['name']
    k8s_endpoint = self.config.k8s_endpoint
    k8s_namespace = self.config.k8s_namespace
    k8s_token = self.config.k8s_token
    k8s_ca = self.config.k8s_ca

    req = requests.get('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(k8s_endpoint, k8s_namespace, route_name),
                       headers={'Authorization': 'Bearer {0}'.format(k8s_token), 'Content-Type':'application/strategic-merge-patch+json'},
                       verify=k8s_ca)

    return req
 

def modify_dns(action, config):
    dns_server = config.get('dns_server')
    dns_key_file = config.get('dns_key_file')

    command  = "server %s\n" % dns_server
    command += action
    command += "send\n"
    command = "nsupdate -k {0} -v << EOF\n{1}\nEOF\n".format(dns_key_file, command)

    subprocess.call(command, shell=True)


def remove_dns(event, config):
    dns_a_record = event['object']['spec']['host']
    action = "update delete %s A\n" % dns_a_record
    modify_dns(action, config)


def add_dns(event, config):
    application_router_ip = config.get('application_router_ip')

    dns_a_record = event['object']['spec']['host']
    action = "update add %s 180  A %s\n" % (dns_a_record, application_router_ip)
    modify_dns(action, config)


