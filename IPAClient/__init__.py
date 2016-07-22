import json
import requests
from OpenSSL import crypto


class IPAClient(object):
    def __init__(self, ipa_user, ipa_password, ipa_url):
        #ipaurl="https://idm-1.etl.lab.eng.rdu2.redhat.com/ipa/"
        #realm="ETL.LAB.ENG.RDU2.REDHAT.COM"

        self.session = requests.Session()
        self.ipa_url = ipa_url

        #TODO: Sign Request with Dynamic CA (IPA)
        # authenticate to IPA Server
        try:
            resp = self.session.post('{0}session/login_password'.format(self.ipa_url),
                                                        params="",
                                                        data = {'user': ipa_user,
                                                                'password': ipa_password},
                                                        verify=False,
                                                        headers={'Content-Type':'application/x-www-form-urlencoded',
                                                                 'Accept':'applicaton/json'})
        except Exception as e:
            raise Exception("IPA Auth Exception: {0}".format(e))

        self.header = {'referer': self.ipa_url, 'Content-Type':'application/json', 'Accept':'application/json'}

    def create_host(self, host):
        try:
            # CREATE HOST [event['object']['spec']['host']]
            create_host = self.session.post('{0}session/json'.format(self.ipa_url), headers=self.header,
                                            data=json.dumps({'id': 0, 'method': 'host_add', 'params': [host, {'force': True}]}), verify=False)
            print "    Host Create Return Code: {0}".format(create_host.status_code)
        except Exception as e:
            raise Exception("Create Host Exception: {0}".format(e))

    def create_cert(self, host, realm, key, csr):
        try:
            # CREATE CERT
            cert_request = self.session.post('{0}session/json'.format(self.ipa_url), headers=self.header,
                                             data=json.dumps({'id': 0,
                                                              'method': 'cert_request',
                                                              'params': [[csr],
                                                                         {'principal': 'host/{0}@{1}'.format(host, realm),
                                                                          'request_type': 'pkcs10',
                                                                          'add': False}]}),
                                             verify=False)

            print "    Certificate Signing Return Code: {0}".format(cert_request.status_code)
            cert_resp = cert_request.json()
        except Exception as e:
            raise Exception("Cert Create Exception: {0}".format(e))

        print "CERTIFICATE:\n-----BEGIN CERTIFICATE-----\n{0}\n-----END CERTIFICATE-----".format(
            '\n'.join(cert_resp['result']['result']['certificate'][i:i+65] for i in xrange(0, len(cert_resp['result']['result']['certificate']), 65)))
        print
        print "KEY:\n {0}".format(key.exportKey('PEM'))
