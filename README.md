# OpenShift Event Watcher

The OpenShift Event Watcher is a utility used as a service integrator for OpenShift and other third party components

## Deploying to OpenShift

```
oc new-build --name=event-watcher --binary=true --strategy=docker -n event-watcher
oc start-build event-watcher --from-dir=. --wait=true --follow=true -n event-watcher
oc create configmap event-watcher --from-file=kubernetes.io/config.ini -n event-watcher
oc new-app event-watcher -n event-watcher
oc volumes dc/event-watcher --add --type=configmap --configmap-name=event-watcher --mount-path=/etc/config -n event-watcher
```
