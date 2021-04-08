#!/usr/bin/env python3.6
#-*- coding: utf-8 -*-
""" the monitor api restful for prometheus  """
"""this tool is designed for k8s rc monitor"""
__author__ = "gjpei"

import urllib3
from kubernetes import client, config
from get_resource_version import get_res_version
import logging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='api.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)

configuration = client.Configuration()
Token = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJtb25pdG9yaW5nIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Inpwcm9tZXRoZXVzLXRva2VuLXd2N3Y3Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Inpwcm9tZXRoZXVzIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiYzZjNmQzN2ItYTE2MS0xMWU5LTljNTAtYjA4M2ZlM2U3MTI4Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Om1vbml0b3Jpbmc6enByb21ldGhldXMifQ.CPoiVID3uKrckCnsxYf2XeV91x-_l18-P5RZz4XpZXWjX5l67UGYPV0cHfrIh_yc0HLDuctrQj8nyaDcFiw1EihKLug2__iYKvERLJjoZRzt8qaIRiJ0Ja1Y7qPT3RKEIqknVck4VaTsRyvoKE560gccR8xQFdyuuJAwbubqn1I08MckCK3VhEvACx8cBEksBB6BDgHz1vBc7IvCOt0uNDyib--xeMh2OnR6_P_nfV2BKQRMqF4oF5lhpZThOgJjVj6kXZi6vX4vnxQZ2gdJ1PHpnA2GkegmiQSlefvP4phpLpAOLnt7WXRc_Qt5lkb-9q767Dtsq3AUxtQ4HRDWxQ'
APISERVER = 'https://172.16.59.32:6443'
configuration.host = APISERVER
configuration.verify_ssl = False
configuration.api_key = {"authorization": "Bearer " + Token}
client.Configuration.set_default(configuration)
#config.kube_config.load_kube_config(config_file="config")
configuration.debug = False
watch = False
#api_instance = client.CoreV1Api(client.ApiClient(configuration))
v1 = client.PrometheusRuleV1Api()

class CreateRcPrometheusrule(object):
    def __init__(self,data_list):
        self.name = data_list["name"]  #告警名
        self.times = data_list["times"] #阈值
        self.productline = data_list["productline"] #产品线
        self.alert_group = data_list["alarm_group"] #告警组   
        self.ops = data_list["ops"]   #运维负责人
        self.dev = data_list["dev"]   #开发负责人
        self.ifor = data_list["ifor"] #持续多长时间告警
        self.rc_name = data_list["rc_name"] #rc名
    #构建告警规则的body体，以POST传给api后端
    def creat_prometheusrule_object(self):
        metadata=client.V1ObjectMeta(labels={"prometheus": "k8s","role":"alert-rules"},name=self.name,namespace="monitoring")
        summary = "rc {{$labels.replicationcontroller}} 副本数未达到期望值!比期望少{{ $value }}个,已持续" + str(self.ifor)
        expr = 'kube_replicationcontroller_status_replicas{' + 'replicationcontroller=~'+ '".*' + str(self.rc_name) + '.*"} - ' + 'kube_replicationcontroller_status_available_replicas{' + 'replicationcontroller=~'+ '".*' + str(self.rc_name) + '.*"} > ' + str(self.times) 
        rules=client.V1PrometheusRuleRule(alert=str(self.name) + "_Rc_Erro",expr=expr,ifor=self.ifor,labels={"alert_group":self.alert_group,"productline":self.productline},annotations={"summary":summary})
        spec=client.V1PrometheusRuleSpec(groups=[client.V1PrometheusRuleGroup(name="prometheus",rules=[rules])])
        body = client.V1PrometheusRule(
            api_version="monitoring.coreos.com/v1",
            kind="PrometheusRule",
            metadata=metadata,
            spec=spec,
            status=None
            )
        return body
    #更新告警规则的body体
    def put_prometheusrule_object(self):
        resource_version = get_res_version(self.name)        
        metadata=client.V1ObjectMeta(labels={"prometheus": "k8s","role":"alert-rules"},name=self.name,namespace="monitoring",resource_version=resource_version)
        summary = "rc {{$labels.replicationcontroller}} 副本数未达到期望值!比期望少{{ $value }}个,已持续" + str(self.ifor) 
        expr = 'kube_replicationcontroller_status_replicas{' + 'replicationcontroller=~'+ '".*' + str(self.rc_name) + '.*"} - ' + 'kube_replicationcontroller_status_available_replicas{' + 'replicationcontroller=~'+ '".*' + str(self.rc_name) + '.*"} > ' +str(self.times)
        rules=client.V1PrometheusRuleRule(alert=str(self.name) + "_Rc_Erro",expr=expr,ifor=self.ifor,labels={"alert_group":self.alert_group,"productline":self.productline},annotations={"summary":summary})
        spec=client.V1PrometheusRuleSpec(groups=[client.V1PrometheusRuleGroup(name="prometheus",rules=[rules])])
        body = client.V1PrometheusRule(
            api_version="monitoring.coreos.com/v1",
            kind="PrometheusRule",
            metadata=metadata,
            spec=spec,
            status=None
            )
        return body
    #关闭告警规则的body体，直接修改labels的role达到目的
    def close_prometheusrule_object(self):
        resource_version = get_res_version(self.name)
        metadata=client.V1ObjectMeta(labels={"prometheus": "k8s","role":"ban"},name=self.name,namespace="monitoring",resource_version=resource_version)
        summary = "rc {{$labels.replicationcontroller}} 副本数未达到期望值!比期望少{{ $value }}个,已持续" + str(self.ifor) 
        expr = 'kube_replicationcontroller_status_replicas{' + 'replicationcontroller=~'+ '".*' + str(self.rc_name) + '.*"} - ' + 'kube_replicationcontroller_status_available_replicas{' + 'replicationcontroller=~'+ '".*' + str(self.rc_name) + '.*"} > ' +str(self.times)
        rules=client.V1PrometheusRuleRule(alert=str(self.name) + "_Rc_Erro",expr=expr,ifor=self.ifor,labels={"alert_group":self.alert_group,"productline":self.productline},annotations={"summary":summary})
        spec=client.V1PrometheusRuleSpec(groups=[client.V1PrometheusRuleGroup(name="prometheus",rules=[rules])])
        body = client.V1PrometheusRule(
            api_version="monitoring.coreos.com/v1",
            kind="PrometheusRule",
            metadata=metadata,
            spec=spec,
            status=None
            )
        return body
    #调用自定义的prometheusrule api，请求k8s接口，往prometheus operator 增加告警规则
    def create_prometheusrule(self):
        body = self.creat_prometheusrule_object()
        try:
            res = v1.create_namespaced_prometheusrule(namespace="monitoring",body=body)
            return 0,res
        except Exception as e:
            raise Exception("创建告警规则失败:%s 失败!" % self.name)
            logging.debug(str(e))
    #调用自定义的prometheusrule api，请求k8s接口，直接删除告警规则
    def delete_prometheusrule(self):
        try:
            res = v1.delete_namespaced_prometheusrule(namespace='monitoring',name=self.name)
            return 0,res
        except:
            raise Exception("删除告警规则失败:%s 失败!" % self.name) 
    #调用自定义的prometheusrule api，请求k8s接口，prometheus operator 会自动更新告警规则   
    def put_prometheusrule(self):
        body = self.put_prometheusrule_object()
        try:
            res = v1.patch_namespaced_prometheusrule(namespace='monitoring',name=self.name,body=body)
            return 0,res
        except Exception as e:
            raise Exception("更新告警规则失败:%s 失败!" % self.name)
            logging.debug(str(e))
    #调用自定义的prometheusrule api，请求k8s接口，返回所有告警规则
    def list_prometheusrule(self):
        try:
            res = v1.list_namespaced_prometheusrule()
            return 0,res
        except Exception as e:
            raise Exception("获取告警规则失败:%s 失败!" % self.name) 
            logging.debug(str(e))
    #调用自定义的prometheusrule api，请求k8s接口，prometheus operator 自动更新告警规则，关闭告警
    def close_prometheusrule(self):
        body = self.close_prometheusrule_object()
        try:
            res = v1.patch_namespaced_prometheusrule(namespace='monitoring',name=self.name,body=body)
        except Exception as e:
            raise Exception("关闭告警规则失败:%s 失败!" % self.name)
            logging.debug(str(e))
    #调用自定义的prometheusrule api，请求k8s接口，重新打开告警规则
    def open_prometheusrule(self):
       body = self.put_prometheusrule_object()
       try:
           res = v1.patch_namespaced_prometheusrule(namespace='monitoring',name=self.name,body=body)
       except Exception as e:
           raise Exception("开启告警规则失败:%s 失败!" % self.name)
           logging.debug(str(e))

if __name__ == '__main__':
    name = {'name': 'test3', 'times':0, 'productline': 'iat', 'alarm_group': 'jianshen2', 'ops': 'dhli', 'dev': 'jianliu', 'ifor': '1m','rc_name': 'xits-cnen.xits-cnen.1006'}
    #get_data = CreateRcPrometheusrule(name)
    #get_data.delete_prometheusrule()
   # print (a)
    #b = get_data.create_prometheusrule()
   #print (b)
    #get_data.put_prometheusrule()
    print (get_data.list_prometheusrule())
    #get_data.close_prometheusrule()
    #get_data.open_prometheusrule()
