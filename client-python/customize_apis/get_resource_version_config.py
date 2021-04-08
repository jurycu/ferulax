#-*- coding: utf-8 -*-
#!/usr/bin/env python3.6
""" the monitor api restful for prometheus  """
"""this tool is designed for k8s rc monitor"""
__author__ = "gjpei"

from kubernetes import client, config
import json
config.kube_config.load_kube_config(config_file="config2")
v1 = client.PrometheusRuleV1Api()
def creat_prometheusrule_object():
    metadata=client.V1ObjectMeta(labels={"prometheus": "k8s","role":"alert-rules"},name="test",namespace="monitoring")
    summary = "Instance {{ $labels.instance }} down"
    expr = "up{" + "instance!~" +' " ' + '.*8081"' + "}==0"
    rules=client.V1PrometheusRuleRule(alert="InstanceDown",expr=expr,ifor='1m',labels={"severity": "k8s_page","summary":summary},annotations={"test":"gjpei"})
    spec=client.V1PrometheusRuleSpec(groups=[client.V1PrometheusRuleGroup(name="prometheus-test",rules=[rules])])
    body = client.V1PrometheusRule(
        api_version="monitoring.coreos.com/v1",
        kind="PrometheusRule",
        metadata=metadata,
        spec=spec,
        status=None
        )
    return body
def list_prometheusrule():
    #body = creat_prometheusrule_object()
    try:
        res = v1.list_namespaced_prometheusrule()
        return 0,res
    except Exception as e:
        return -1,str(e).replace("'","").replace('"','')
def get_res_version(name):

    a = list_prometheusrule()
    res = a[1].message
    res=json.loads(res)
    spec = res['items']
    for i in range(len(spec)):
          if spec[i]['metadata']['name'] == name:          
              resourceVersion =  spec[i]['metadata']['resourceVersion']
              return resourceVersion
