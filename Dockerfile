FROM centos

RUN mkdir -p /opt/watcher

RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-8.noarch.rpm; \
    yum install -y python-devel python-requests python-pip openssl-devel gcc; \
    pip install --upgrade pip; \
    pip install pkiutils pyopenssl; \
    yum clean all;

COPY OpenShiftWatcher /opt/watcher/OpenShiftWatcher

COPY IPAClient /opt/watcher/IPAClient

COPY ipa /opt/watcher/ipa

RUN chown -R 1001:1001 /opt/watcher

USER 1001

ENTRYPOINT ["python", "/opt/watcher/ipa/route_watch.py"]
