# DNS plugin

The DNS plugin is used to update a target DNS server with application route specific configuration. This allows for application specific DNS records rather than using wildcard dns records for resolution. 

## Testing Locally

In addition to the instructions part of the top-level README, please add the following `plugin_dns` specific parameters.

- A "nsupdate" enabled DNS server, such as `named`
- A valid nsupdate key that allows for add/delete of DNS records on the target DNS server

Once the above requirements are met, and the below listed configuration has been populated, updates to routes in OpenShift will be pushed to the DNS server.

## Configuration

### Global Configuration Options

| Environment Variable | ini Variable | Required | Description |
| ------------- | ------------- |
| K8S_API_ENDPOINT | k8s_api_endpoint | True | OpenShift/Kubernetes API hostname:port |
| K8S_TOKEN  | k8s_token | True | Login token (`oc whoami -t`) |
| K8S_NAMESPACE | k8s_namespace | True | Namespace you want to watch for route changes in |
| K8S_RESOURCE | k8s_resource | True | Needs to be set to `routes` for this plugin |
| WATCHER_PLUGIN | watcher_plugin | True | Needs to be set to `dns` for this plugin |


### DNS Plugin Configuration Options

| ini Variable | Required | Description |
| ------------- | ------------- |
| application_router_ip | True | IP address for the DNS A-record to be pointed to, for example a load balancer or the OpenShift router |
| dns_server | True | The target DNS server (FQDN or IP) |
| dns_key_file | True | The DNS server key used with nsupdate |

