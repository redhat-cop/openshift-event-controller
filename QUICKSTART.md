# Event Controller Quickstart Tutorial

Let's walk through a simple example of how the Event Controller works.

```
oc new-project event-controller
oc create -f watcher-template.yml
oc new-app --template=event-controller
```

The Event Controller is now deployed in a project called `event-controller`. Let's look at what was created:

```
$ oc get all | grep event-controller
bc/event-controller           Docker                                                Git@containerize   2
builds/event-controller-1     Docker                                                Git@86e5d9b        Complete   About an hour ago   2m1s
is/event-controller           172.30.226.234:5000/event-controller/event-controller       latest             41 minutes ago
is/python-35-centos7       172.30.226.234:5000/event-controller/python-35-centos7   latest             About an hour ago
dc/event-controller           3                                                     1                  1         config,image(event-controller:latest)
rc/event-controller-1         0                                                     0                  1h
po/event-controller-1-tkkk3   1/1                                                   Running            0          32m
```

That covers most of it, but we also created a `ConfigMap`. Let's look at that really quick.

```
$ oc get configmap event-controller --template={{.data}}
map[config.ini:
[global]
k8s_resource=routes
watcher_plugin=simple

[plugin_simple]
]
```

From this config we can see that the Event Controller is watching `Route` resources and has a `simple` plugin enabled.

Now let's put it into action! First, open a new tab and start watching the pod logs.

```
$ oc get pods
NAME                    READY     STATUS      RESTARTS   AGE
event-controller-1-build   0/1       Completed   0          1h
event-controller-3-tkkk3   1/1       Running     0          29m <-- Make sure to pick the one that's running
$ oc logs -f event-controller-3-tkkk3
2017-03-17 04:42:51,576 [INFO] Loading config file from /etc/config/config.ini
```
There. We can see that the watcher has started and is waiting for new events.

```
oc new-app https://github.com/openshift/nodejs-ex.git
```

Notice no new logs yet. That's because a route has not been created yet. So let's do that.

```
$ oc expose svc/nodejs-ex
route "nodejs-ex" exposed
```

Check out the logs now!
```
2017-03-17 05:24:38,339 [INFO] Kind: Route; Name: nodejs-ex; Event Type:ADDED
```

Cool, so at a very basic level, with the `simple` plugin enabled, the watcher will detect when a route gets created, and log it.

Think about the other ways we could use that information...
