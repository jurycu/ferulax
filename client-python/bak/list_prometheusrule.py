from kubernetes import client, config
config.kube_config.load_kube_config(config_file="config")
v1 = client.PrometheusRuleV1Api()
#res = v1.list_api_service()
#print res
#res = v1.get_api_resources()
#print res
def creat_prometheusrule_object():
    metadata=client.V1ObjectMeta(labels={"prometheus": "k8s","role":"alert-rules"},name="test",namespace="monitoring")
    #rules=client.V1PrometheusRuleRule(record="up == 1",alert="InstanceDown",expr="up == 1",labels={"severity": "k8s_page"},annotations={"summary":` 'Instance {{ $labels.instance }} down'`})
    summary = "Instance {{ $labels.instance }} down"
    expr = "up{" + "instance!~" +' " ' + '.*8081"' + "}==0"
#    print expr
    rules=client.V1PrometheusRuleRule(alert="InstanceDown",expr=expr,ifor='1m',labels={"severity": "k8s_page","summary":summary},annotations={"test":"gjpei"})
    #rules=client.V1PrometheusRuleRule(alert="InstanceDown",expr=expr)
    spec=client.V1PrometheusRuleSpec(groups=[client.V1PrometheusRuleGroup(name="prometheus-test",rules=[rules])])
    body = client.V1PrometheusRule(
        api_version="monitoring.coreos.com/v1",
        kind="PrometheusRule",
        metadata=metadata,
        spec=spec,
        status=None
        )
#    print body
    return body
def list_prometheusrule():
    #body = creat_prometheusrule_object()
    try:
        res = v1.list_namespaced_prometheusrule()
        return 0,res
    except Exception as e:
        return -1,str(e).replace("'","").replace('"','')
#    for item in res.items:
#        print item.data
    #print 'res= ' +str(res)
a = list_prometheusrule()
#res = a[1].metadata.resource_version
print a[1]
print type(a[1])
#for ns in v1.list_api_service().items:
#    print(ns.metadata.name)
#print("Listing pods with their IPs:")
#ret = v1.list_pod_for_all_namespaces(watch=False)
#for i in ret.items:
#    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
