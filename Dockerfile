FROM openshift/python-33-centos7

USER root

RUN yum -y install libffi-devel; \
  scl enable python33 "pip install requests pkiutils pyopenssl"

RUN mkdir -p /opt/watcher

COPY OpenShiftWatcher /opt/watcher/OpenShiftWatcher

COPY IPAClient /opt/watcher/IPAClient

COPY ipa /opt/watcher/ipa

RUN chown -R 1001:1001 /opt/watcher

USER 1001

ENTRYPOINT ["scl", "enable", "python33", "/opt/watcher/ipa/route_watch.py"]
