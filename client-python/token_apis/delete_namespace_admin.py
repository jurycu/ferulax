#!/usr/bin/env python3.6
""" the monitor api restful for prometheus  """
"""this tool is designed for k8s rc monitor"""
__author__ = "gjpei"

from kubernetes import client, config
import logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='api.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

config.kube_config.load_kube_config(config_file="config")
v1 = client.CoreV1Api()
try:
    api_response = v1.delete_namespace('test')
    print(api_response)
except APIException as e:
    print("Exception when calling CoreV1Api->list_namespaced_pod: %s\n" % e)

