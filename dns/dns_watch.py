#!/bin/python

import os
import requests
import json
import subprocess
from OpenShiftWatcher import OpenShiftWatcher


def watch_routes():
    watcher = OpenShiftWatcher(os_api_endpoint=os.environ['OS_API'],
                               os_resource=os.environ['OS_RESOURCE'],
                               os_namespace=os.environ['OS_NAMESPACE'],
                               os_auth_token=os.environ['OS_TOKEN'])

    for event in watcher.stream():
        if type(event) is dict and 'type' in event:
            if event['type'] == 'ADDED':
                remove_dns(event)
                add_dns(event)
            elif event['type'] == 'MODIFIED':
                route = get_route(event)
                if route.status_code == 404:
                    remove_dns(event)
                else:
                    print 'Route \'{0}\' modified'.format(event['object']['metadata']['name'])


def get_route(event):
    route_name = event['object']['metadata']['name']

    req = requests.get('https://{0}/oapi/v1/namespaces/{1}/routes/{2}'.format(os.environ['OS_API'], os.environ['OS_NAMESPACE'], route_name),
                       headers={'Authorization': 'Bearer {0}'.format(os.environ['OS_TOKEN']), 'Content-Type':'application/strategic-merge-patch+json'},
                       verify=False
                       )

    return req
 

def modify_dns(action):
    try:
        command  = "server %s\n" % os.environ['DNS_SERVER']
        command += action
        command += "send\n"
        command = "nsupdate -k {0} -v << EOF\n{1}\nEOF\n".format(os.environ['DNS_KEY_FILE'], command)

        subprocess.call(command, shell=True)

    except Exception as e:
        print "Exception: ", e


def remove_dns(event):
    dns_a_record = event['object']['spec']['host']
    action = "update delete %s A\n" % dns_a_record
    modify_dns(action)


def add_dns(event):
    dns_a_record = event['object']['spec']['host']
    action = "update add %s 180  A %s\n" % (dns_a_record, os.environ['OS_ROUTER_IPV4'])
    modify_dns(action)


watch_routes()
