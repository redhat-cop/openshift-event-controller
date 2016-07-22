import json
import requests
import pkiutils
from OpenSSL import crypto


class IPAClient(object):
    def __init__(self, ipa_user, ipa_password, ipa_url, bits=2048):
        #ipaurl="https://idm-1.etl.lab.eng.rdu2.redhat.com/ipa/"
        #realm="ETL.LAB.ENG.RDU2.REDHAT.COM"

        self.session = requests.Session()
        self.ipa_url = ipa_url
        self.bits = bits

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
        except Exception as e:
            raise Exception("Create Host Exception: {0}".format(e))

    def delete_host(self, host):
        try:
            resp = self.session.post('{0}session/json'.format(self.ipa_url), headers=self.header,
                                            data=json.dumps({'id': 0, 'method': 'host_del', 'params': [host, {'force': True}]}), verify=False)
        except Exception as e:
            raise Exception("Delete Host Exception: {0}".format(e))


    def create_cert(self, host, realm):
        try:
            key = pkiutils.create_rsa_key(bits=self.bits,
                                          keyfile=None,
                                          format='PEM',
                                          passphrase=None)
            csr = pkiutils.create_csr(key,
                                      "/CN={0}/C=US/O=Test organisation/".format(host),
                                      csrfilename=None,
                                      attributes=None)
        except Exception as e:
            raise Exception("Create CSR Exception: {0}".format(e))


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
            cert_resp = cert_request.json()
        except Exception as e:
            raise Exception("Cert Create Exception: {0}".format(e))
        return cert_resp['result']['result']['certificate'], key
