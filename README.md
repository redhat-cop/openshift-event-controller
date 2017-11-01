# OpenShift Event Controller

The OpenShift Event Controller is a utility used as a service integrator for OpenShift and other third party components.

## Getting Started

To skip right to a first deployment, check out our [Quickstart Tutorial](./QUICKSTART.md)

## Plugins

We currently support the following plugins:

* [Simple Plugin](./plugin_simple)
 * Watches for new resources and logs those events to the console
* [DNS Plugin](./plugin_dns)
 * Creates DNS records for new routes
* [Certificates Plugin](./plugin_ipa)
 * Creates certificates and automatically secures new routes as they get created. Works against an IPA or IDM server

## Configuration

The event controller can be configured either through Environment Variables or a Config Files. We recommend the config file.

A sample config file looks like:

```
[global]
k8s_resource=routes
watcher_plugin=simple
log_level=INFO

[plugin_simple]
#message_log_level=WARNING

[plugin_ipa]
need_cert_annotation=openshift.io/managed.cert
ipa_user=ldap-user
ipa_password=mypassword
ipa_url=https://idm.example.com/ipa/
ipa_realm=MYREALM.EXAMPLE.COM
ca_trust=/etc/ldap-ca/ca.crt

[plugin_dns]
application_router_ip=192.168.2.3
dns_server=192.168.5.6
dns_key_file=/path/to/cloudapps.example.com.key
resolv_conf=/path/to/tmp_resolv.conf
```

### Global Config Options

| Environment Variable | ini Variable | Required | Description |
| ------------- | ------------- | -------| --------- |
| K8S_API_ENDPOINT | k8s_api_endpoint | True | OpenShift/Kubernetes API hostname:port |
| K8S_TOKEN  | k8s_token | True; will be pulled from Pod | Login token (`oc whoami -t`) |
| K8S_NAMESPACED | k8s_namespaced | True | Whether the resource is namespace scoped |
| K8S_NAMESPACE | k8s_namespace | When `K8S_NAMESPACED` is `True`; will be pulled from Pod | Namespace you want to listen watch resources in |
| K8S_API_PATH | k8s_api_path | False | The full API resource path. Override API path construction based on other values |
| K8S_API_GROUP | k8s_api_group | False | Kubernetes API group |
| K8S_API_VERSION | k8s_api_version | False | Kubernetes API Version |
| K8S_RESOURCE | k8s_resource | True | The `Kind` of the Kubernetes or OpenShift resource |
| K8S_CA | k8s_ca | False; will be pulled from Pod | Path to the `ca.crt` file for the cluster |
| LOG_LEVEL | log_level | False | Logging threshold to be output. Options: DEBUG, INFO, WARNING, ERROR, CRITICAL; Default: INFO
| WATCHER_PLUGIN | watcher_plugin | False | Name of the Plugin you want to run in the Watcher. Default: 'simple' |

### Configuring A Plugin

Check the documentation for the individual plugins for more details on how they are configured.
