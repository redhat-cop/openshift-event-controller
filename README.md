Example
---

Below is an example of how to watch for changes to routes. The python script
reads environmental variables given on the command line and outputs JSON as
described
in
[json.WatchEvent](https://docs.openshift.com/enterprise/3.2/rest_api/openshift_v1.html#json-watchevent)

```
OS_TOKEN="abcd123" OS_API='192.168.1.47:8443' OS_NAMESPACE='default' OS_RESOURCE='routes' python ./example/watch_example.py
```
