# Event Watcher PKI Plugin

This plugin provides functionality to automatically secure routes with certificates generated from an external PKI system.

## Quickstart

Write the following to your config.ini:
```
...(see watcher readme for global settings)...

[plugin_ipa]
need_cert_annotation=openshift.io/managed.cert
ipa_user=<ipa/idm username>
ipa_password=<ipa/idm password>
ipa_url=<ipa/idm API URL ex: https://idm.example.com/ipa/>
ipa_realm=<realm name>
ca_trust=</path/to/ca.crt>
```

Then run the following command:

```
python3 watch.py --config conf/config.ini
```

## Plugin Configuration Options

| ini Variable | Required | Description |
| ------------- | ------------- | -------------|
| need_cert_annotation | true | Name of the annotation used to designate routes that need certificates |
| ipa_user | true | IPA/IDM user with permissions to create hosts & certificates |
| ipa_password | true | IPA/IDM password |
| ipa_url | true | Url to IPA/IDM API (include path) |
| ipa_realm | true | Realm under which new hosts/certs should be created |
| ipa_ca_cert | false | CA certificate for IPA server trust |
## Developer local Setup

### Dependencies

First, install the following packages:

```
sudo dnf install "C Development Tools and Libraries"
sudo dnf install openssl-devel
sudo dnf install python3-pip
sudo dnf install python3-devel
```

Then, install the following python modules
```
sudo pip3 install requests
sudo pip3 install pyOpenSSL
sudo pip3 install cryptography
sudo pip3 install pkiutils
sudo pip3 install six
sudo pip3 install traceback
sudo pip3 install json
```
