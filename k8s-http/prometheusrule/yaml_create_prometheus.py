import yaml
import requests
import json

requests.packages.urllib3.disable_warnings()
token="eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJtb25pdG9yaW5nIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Inpwcm9tZXRoZXVzLXRva2VuLXd2N3Y3Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Inpwcm9tZXRoZXVzIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiYzZjNmQzN2ItYTE2MS0xMWU5LTljNTAtYjA4M2ZlM2U3MTI4Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Om1vbml0b3Jpbmc6enByb21ldGhldXMifQ.CPoiVID3uKrckCnsxYf2XeV91x-_l18-P5RZz4XpZXWjX5l67UGYPV0cHfrIh_yc0HLDuctrQj8nyaDcFiw1EihKLug2__iYKvERLJjoZRzt8qaIRiJ0Ja1Y7qPT3RKEIqknVck4VaTsRyvoKE560gccR8xQFdyuuJAwbubqn1I08MckCK3VhEvACx8cBEksBB6BDgHz1vBc7IvCOt0uNDyib--xeMh2OnR6_P_nfV2BKQRMqF4oF5lhpZThOgJjVj6kXZi6vX4vnxQZ2gdJ1PHpnA2GkegmiQSlefvP4phpLpAOLnt7WXRc_Qt5lkb-9q767Dtsq3AUxtQ4HRDWxQ"
url="https://192.168.60.205:6443/apis/monitoring.coreos.com/v1/namespaces/monitoring/prometheusrules/"
header={
    "Authorization":"Bearer "+token,
    "Content-Type": "application/json"
}

req=requests.get(url=url,headers=header,verify=False)

t="""apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  labels:
    app:  alert-rules
    role: alert-rules
  name: etcdtest
  namespace: monitoring
spec:
  groups:  
  - name: test-z-222222222
    rules:
    - alert: EtcdClusterUnavailable123
      annotations:
        summary: etcd cluster small1111
        description: If one more etcd peer goes down the cluster will be unavailable
      expr: |
        count(up{job="etcd"} == 0) > (count(up{job="etcd"}) / 2 - 1)
      for: 3m
      labels:
        severity: critical
    - alert: kubeManagerDown
      expr: count(up{job='kube-controller-manager'}==1) < 3 
      annotations:
        message: 'kube-controller-manager is down'
        value: "{{ $value }} < 3"
      for: 2m
      labels:
        severity: critical    
        env: dev    
        """

a=json.dumps(yaml.load(t, Loader=yaml.FullLoader))
#print (a)
req1 = requests.post(url=url,data=a,headers=header,verify=False)
print (req1.headers)
#print (req1.status_code)
#print (a)
#print("aa")
#print(a)
#print req.json()


