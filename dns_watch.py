#!/bin/python

import os
import requests
import json
import pkiutils
import subprocess
from OpenSSL import crypto
from OpenShiftWatcher import OpenShiftWatcher

router_ipv4 = os.environ['OS_ROUTER_IPV4']

dns_server = os.environ['DNS_SERVER']
dns_keyfile = os.environ['DNS_KEY_FILE']


def watch_routes():
    watcher = OpenShiftWatcher(os_api_endpoint=os.environ['OS_API'],
                               os_resource=os.environ['OS_RESOURCE'],
                               os_namespace=os.environ['OS_NAMESPACE'],
                               os_auth_token=os.environ['OS_TOKEN'])

    for event in watcher.stream():
        if type(event) is dict and 'type' in event:
            try:
                dns_a_record = event['object']['spec']['host']

                command  = "server %s\n" % dns_server
                command += "update delete %s A\n" % dns_a_record

                if event['type'] == 'ADDED':
                    command += "update add %s 180    A %s\n" % (dns_a_record, router_ipv4)

                command += "send\n"
                command = "nsupdate -k {0} -v << EOF\n{1}\nEOF\n".format(dns_keyfile, command)

                print("Calling the following command now:\n\n" + command)
  
                subprocess.call(command, shell=True)

            except Exception as e:
                print "Exception: ", e
                continue

watch_routes()
