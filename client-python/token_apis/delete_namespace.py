#!/usr/bin/env python3.6

""" the monitor api restful for prometheus  """
"""this tool is designed for k8s pod restart monitor"""
__author__ = "gjpei"

from kubernetes import client, config
import logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='rc_api.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

configuration = client.Configuration()
Token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJtb25pdG9yaW5nIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Inpwcm9tZXRoZXVzLXRva2VuLXd2N3Y3Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Inpwcm9tZXRoZXVzIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiYzZjNmQzN2ItYTE2MS0xMWU5LTljNTAtYjA4M2ZlM2U3MTI4Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Om1vbml0b3Jpbmc6enByb21ldGhldXMifQ.CPoiVID3uKrckCnsxYf2XeV91x-_l18-P5RZz4XpZXWjX5l67UGYPV0cHfrIh_yc0HLDuctrQj8nyaDcFiw1EihKLug2__iYKvERLJjoZRzt8qaIRiJ0Ja1Y7qPT3RKEIqknVck4VaTsRyvoKE560gccR8xQFdyuuJAwbubqn1I08MckCK3VhEvACx8cBEksBB6BDgHz1vBc7IvCOt0uNDyib--xeMh2OnR6_P_nfV2BKQRMqF4oF5lhpZThOgJjVj6kXZi6vX4vnxQZ2gdJ1PHpnA2GkegmiQSlefvP4phpLpAOLnt7WXRc_Qt5lkb-9q767Dtsq3AUxtQ4HRDWxQ' 
APISERVER = 'https://192.168.60.205:6443'
configuration.host = APISERVER
configuration.verify_ssl = False
configuration.api_key = {"authorization": "Bearer " + Token}
client.Configuration.set_default(configuration)
#config.kube_config.load_kube_config(config_file="config")
configuration.debug = True
watch = True
#api_instance = client.CoreV1Api(client.ApiClient(configuration))
v1 = client.CoreV1Api()
try:
    api_response = v1.delete_namespace('test')
    pprint(api_response)
except Exception as e:
    print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)


