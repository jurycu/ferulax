import json
import yaml

t="""apiVersion: v1
kind: Endpoints
metadata:
  name: custom
  namespace: monitoring
  labels:
    k8s-app: custom
subsets:
- addresses:
  - ip: 172.22.104.89
    nodeName: dx-172-22-104-89.aiaas.cn
  ports:
  - name: custom
    port: 10000
    protocol: TCP
    """

a=json.dumps(yaml.load(t, Loader=yaml.FullLoader))
print a
