import yaml
import requests
import json

'''
client for prometheus to add prometheusrule
by gjpei@iflytek.com
2019/9/12
'''

################################
#       prometheusrule         #
################################

requests.packages.urllib3.disable_warnings()
token="eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJtb25pdG9yaW5nIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Inpwcm9tZXRoZXVzLXRva2VuLTJ6bXJkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Inpwcm9tZXRoZXVzIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNjExNzVjN2EtZDNiNi0xMWU5LTljNTAtYjA4M2ZlM2U3MTI4Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Om1vbml0b3Jpbmc6enByb21ldGhldXMifQ.hArngOglluXsq8Zy_u5fPsv4pzAyPm1pSX1PVt_sXQx8Cf5EkSxY4bqd6zwSZAZqVgEdGHFh4aZSQJFD-shAl8TE11_TK8lMiWKvDp2Fr3HzILT8gE_4zvhX-L_XCbqwDI0IQSsnMtyLby2y9ccJGTFZ9sHO-zGpzcYpUqlbMSP_VghmFk2uSK4_-GXQynvHnGYF_1s2wNJ1UL4TPjrl8AC9K5DRBwZ3c4-h1fGOOIxp4AWjR-JtPBtRM31YS7avSfSWcL6xnJTbZzf5Ocq-07EK3IEDniFZAL_cieSxFcyfZGgFOT0zpzRs67U8D01fZZgusBxliNxkdh6q-YaVaw"
url="https://192.168.60.205:6443/apis/monitoring.coreos.com/v1/namespaces/monitoring/prometheusrules/"
header={
    "Authorization":"Bearer "+token,
    "Content-Type": "application/json"
}

#############################################
#      Below is the api function            # 
#############################################

'''get resourceversion to update prometheusrule'''
def get_resource_version(alert_name):
    rule_list = requests.get(url=url,headers=header,verify=False)
    json_rule = rule_list.json()
    json_rule_list = json_rule["items"]
    for rule in json_rule_list:
        if rule["metadata"]["name"] == alert_name:
            resourceVersion = rule["metadata"]["resourceVersion"]
            return resourceVersion

'''delete prometheusrule'''
def delete_prometheusrule(alert_name):
    delete_url = url + str(alert_name)
    res = requests.delete(url=delete_url,headers=header,verify=False)
    res_code = res.status_code 
    if res_code != 200:
            return res_code , "delete prometheusrule  failed! the errbody is: " +str(res.json())
    else:
            return 0 , "delete prometheusrule successful"

'''create prometheusrule...'''
def create_prometheusrule(alertname,summary,rule,durtime,severity,is_sms,is_mail,is_wechat):

    rule_json = {
	'apiVersion': 'monitoring.coreos.com/v1',
	'kind': 'PrometheusRule',
	'metadata': {
		'labels': {
			'prometheus': 'k8s',
			'role': 'alert-rules'
		},
		'name': alertname,
		'namespace': 'monitoring',
	},
	'spec': {
		'groups': [{
			'name': alertname,
			'rules': [{
				'alert': alertname,
				'annotations': {
					'summary': summary 
				},
				'expr': rule,
				'for': durtime,
				'labels': {
					'severity': severity,
					'is_sms': is_sms,
					'is_mail': is_mail,
					'is_wechat': is_wechat
				}
			}]
		}]
        	}
    }
    try:
        a=json.dumps(rule_json)
        res = requests.post(url=url,data=a,headers=header,verify=False)
        res_code = res.status_code
        if res_code != 201:
            return res_code , "create prometheusrule  failed! the errbody is: " + str(res.json())
        else:
            return 0 , "created"
    except Exception as e:
        return -2 , str(e)

'''update prometheusrule...'''
def update_prometheusrule(alertname,summary,rule,durtime,severity,is_sms,is_mail,is_wechat):
    header={
    "Authorization":"Bearer "+token,
    "Content-Type": "application/json"
}
 
    resourceVersion = get_resource_version(alertname) 
    rule_json = {
        'apiVersion': 'monitoring.coreos.com/v1',
        'kind': 'PrometheusRule',
        'metadata': {
                'labels': {
                        'prometheus': 'k8s',
                        'role': 'alert-rules'
                },
                'name': alertname,
                'namespace': 'monitoring',
                'resourceVersion': resourceVersion
        },
        'spec': {
                'groups': [{
                        'name': alertname,
                        'rules': [{
                                'alert': alertname,
                                'annotations': {
                                        'summary': summary
                                },
                                'expr': rule,
                                'for': durtime,
                                'labels': {
                                        'severity': severity,
                                        'is_sms': is_sms,
                                        'is_mail': is_mail,
                                        'is_wechat': is_wechat
                                }
                        }]
                }]
                }
    }
    try:
        a=json.dumps(rule_json)
        url_put = url +str(alertname)
        res = requests.put(url=url_put,data=a,headers=header,verify=False)
        res_code = res.status_code
        if res_code != 200:
            return res_code , "update prometheusrule  failed! errbody is: " + str(res.json())
        else:
            return 0 , "update prometheusrule successful"  
    except Exception as e:
        return -2 , str(e)
    
alertname = "json1-test4"
summary = "test"
rule = 'changes(kube_pod_container_status_restarts_total{pod!~".*kube-apiserver.*|.*kube-scheduler.*|.*etcd-1.*|.*kube-controller-manager.*"}[3m]) *  on (pod )  group_left(node) kube_pod_info >0'
#rule = 'count(up{job="etcd"}>0'
durtime = "3m"
severity = "severity"
is_sms = "1"
is_mail = "1"
is_wechat = "1"
print create_prometheusrule(alertname,summary,rule,durtime,severity,is_sms,is_mail,is_wechat)
#print update_prometheusrule(alertname,summary,rule,durtime,severity,is_sms,is_mail,is_wechat)
#print delete_prometheusrule("json-test2") 
