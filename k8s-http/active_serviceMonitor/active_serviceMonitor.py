import json
import requests
'''
client for prometheus to add aerviceMonitor
by gjpei@iflytek.com
2019/9/12
'''

################################
#       serviceMonitor         #
################################

token="eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJtb25pdG9yaW5nIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6Inpwcm9tZXRoZXVzLXRva2VuLTJ6bXJkIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6Inpwcm9tZXRoZXVzIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNjExNzVjN2EtZDNiNi0xMWU5LTljNTAtYjA4M2ZlM2U3MTI4Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Om1vbml0b3Jpbmc6enByb21ldGhldXMifQ.hArngOglluXsq8Zy_u5fPsv4pzAyPm1pSX1PVt_sXQx8Cf5EkSxY4bqd6zwSZAZqVgEdGHFh4aZSQJFD-shAl8TE11_TK8lMiWKvDp2Fr3HzILT8gE_4zvhX-L_XCbqwDI0IQSsnMtyLby2y9ccJGTFZ9sHO-zGpzcYpUqlbMSP_VghmFk2uSK4_-GXQynvHnGYF_1s2wNJ1UL4TPjrl8AC9K5DRBwZ3c4-h1fGOOIxp4AWjR-JtPBtRM31YS7avSfSWcL6xnJTbZzf5Ocq-07EK3IEDniFZAL_cieSxFcyfZGgFOT0zpzRs67U8D01fZZgusBxliNxkdh6q-YaVaw"
serviceMonitor_url = "https://192.168.60.205:6443/apis/monitoring.coreos.com/v1/namespaces/monitoring/servicemonitors/"
service_url = "https://192.168.60.205:6443/api/v1/namespaces/monitoring/services/"
endpoints_url = "https://192.168.60.205:6443/api/v1/namespaces/monitoring/endpoints/"
header={
    "Authorization":"Bearer "+token,
    "Content-Type": "application/json"
}
requests.packages.urllib3.disable_warnings()
#############################################
#      Below is the get function            # 
#############################################


'''get resourceversion to update serviceMonitor'''
def get_resource_version(url,name):
    resource_list = requests.get(url=url,headers=header,verify=False)
    json_resource = resource_list.json()
    json_resource_list = json_resource["items"]
    for resource_version in json_resource_list:
        if resource_version["metadata"]["name"] == name:
            resourceVersion = resource_version["metadata"]["resourceVersion"]
            return resourceVersion

'''get serviceMonitor interval'''
def get_interval(name):
    interval_body = requests.get(url=serviceMonitor_url,headers=header,verify=False)
    interval_json = interval_body.json()
    interval_list = interval_json["items"]
    for interval_s in interval_list:
        if interval_s["metadata"]["name"] == name:
            interval = interval_s["spec"]["endpoints"][0]["interval"]
            return interval

'''get ip port for servoceMonitor'''
def get_ip_port(name):
    ip_port_body = requests.get(url=endpoints_url,headers=header,verify=False)
    ip_port_json = ip_port_body.json()
    ip_port_list = ip_port_json["items"]
    for ip_port_s in ip_port_list:
        if ip_port_s["metadata"]["name"] == name:
            ip = ip_port_s["subsets"][0]["addresses"][0]["ip"]
            port = ip_port_s["subsets"][0]["ports"][0]["port"] 
            return ip,port
#############################################
#      Below is the add function             # 
#############################################

'''add only serviceMonitor'''
def add_serviceMonitor_just(name,interval):
    serviceMonitorBody ={
	"kind": "ServiceMonitor",
	"spec": {
		"jobLabel": "k8s-app",
		"endpoints": [{
			"scheme": "http",
			"port": name,
			"interval": interval
		}],
		"namespaceSelector": {
			"matchNames": ["monitoring"]
		},
		"selector": {
			"matchLabels": {
				"k8s-app": name
			}
		}
	},
	"apiVersion": "monitoring.coreos.com/v1",
	"metadata": {
		"labels": {
			"k8s-app": name
		},
		"namespace": "monitoring",
		"name": name
        	}
     }
    
    try:
        a=json.dumps(serviceMonitorBody)
        res = requests.post(url=serviceMonitor_url,data=a,headers=header,verify=False)
        res_code = res.status_code
        if res_code != 201:
            return res_code , "create serviceMonitor  failed! the errbody is: " + str(res.json())
        else:
            return 0 , "created"
    except Exception as e:
        return -2 , str(e)

'''add only service'''
def add_service(name,port):
    serviceBody ={
	"kind": "Service",
	"spec": {
		"clusterIP": "None",
		"type": "ClusterIP",
		"ports": [{
			"protocol": "TCP",
			"name": name,
			"port": port
		}]
	},
	"apiVersion": "v1",
	"metadata": {
		"labels": {
			"k8s-app": name
		},
		"namespace": "monitoring",
		"name": name
	}
     }  
    try:
        a=json.dumps(serviceBody)
        res = requests.post(url=service_url,data=a,headers=header,verify=False)
        res_code = res.status_code
        if res_code != 201:
            return res_code , "create service  failed! the errbody is: " + str(res.json())
        else:
            return 0 , "created"
    except Exception as e:
        return -2 , str(e)

'''add only endpoints'''
def add_endpoints(name,ip,port):
    endpointsBody ={
	"kind": "Endpoints",
	"apiVersion": "v1",
	"subsets": [{
		"addresses": [{
			"ip": ip
		}],
		"ports": [{
			"protocol": "TCP",
			"name": name,
			"port": port
		}]
	}],
	"metadata": {
		"labels": {
			"k8s-app": name
		},
		"namespace": "monitoring",
		"name": name
	}
    }
    try:
        a=json.dumps(endpointsBody)
        res = requests.post(url=endpoints_url,data=a,headers=header,verify=False)
        res_code = res.status_code
        if res_code != 201:
            return res_code , "create endpoints  failed! the errbody is: " + str(res.json())
        else:
            return 0 , "created"
    except Exception as e:
        return -2 , str(e)

#############################################
#      Below is the update function         # 
#############################################


'''update only serviceMonitor...'''
def update_serviceMonitor_just(name,interval):
    resourceVersion = get_resource_version(serviceMonitor_url,name)
    serviceMonitor_update_url = serviceMonitor_url +str(name)
    serviceMonitorBody ={
        "kind": "ServiceMonitor",
        "spec": {
                "jobLabel": "k8s-app",
                "endpoints": [{
                        "scheme": "http",
                        "port": name,
                        "interval": interval
                }],
                "namespaceSelector": {
                        "matchNames": ["monitoring"]
                },
                "selector": {
                        "matchLabels": {
                                "k8s-app": name
                        }
                }
        },
        "apiVersion": "monitoring.coreos.com/v1",
        "metadata": {
                "labels": {
                        "k8s-app": name
                },
                "namespace": "monitoring",
                "name": name,
                "resourceVersion":resourceVersion
                }
     }

    try:
        a=json.dumps(serviceMonitorBody)
        res = requests.put(url=serviceMonitor_update_url,data=a,headers=header,verify=False)
        res_code = res.status_code
        if res_code != 200:
            return res_code , "update serviceMonitor  failed! the errbody is: " + str(res.json())
        else:
            return 0 , "update"
    except Exception as e:
        return -2 , str(e)

'''update only service...'''
def update_service(name,port):
    resourceVersion = get_resource_version(service_url,name)
    service_update_url = service_url +str(name)
    serviceBody ={
        "kind": "Service",
        "spec": {
                "clusterIP": "None",
                "type": "ClusterIP",
                "ports": [{
                        "protocol": "TCP",
                        "name": name,
                        "port": port
                }]
        },
        "apiVersion": "v1",
        "metadata": {
                "labels": {
                        "k8s-app": name
                },
                "namespace": "monitoring",
                "name": name,
                "resourceVersion":resourceVersion
        }
     }
    try:
        a=json.dumps(serviceBody)
        res = requests.put(url=service_update_url,data=a,headers=header,verify=False)
        res_code = res.status_code
        if res_code != 200:
            return res_code , "update service  failed! the errbody is: " + str(res.json())
        else:
            return 0 , "updated"
    except Exception as e:
        return -2 , str(e)

'''update only endpoints...'''
def update_endpoints(name,ip,port):
    resourceVersion = get_resource_version(endpoints_url,name)
    endpoints_update_url = endpoints_url + str(name)
    endpointsBody ={
        "kind": "Endpoints",
        "apiVersion": "v1",
        "subsets": [{
                "addresses": [{
                        "ip": ip
                }],
                "ports": [{
                        "protocol": "TCP",
                        "name": name,
                        "port": port
                }]
        }],
        "metadata": {
                "labels": {
                        "k8s-app": name
                },
                "namespace": "monitoring",
                "name": name,
                "resourceVersion":resourceVersion
        }
    }
    try:
        a=json.dumps(endpointsBody)
        res = requests.put(url=endpoints_update_url,data=a,headers=header,verify=False)
        res_code = res.status_code
        if res_code != 200:
            return res_code , "update endpoints  failed! the errbody is: " + str(res.json())
        else:
            return 0 , "created"
    except Exception as e:
        return -2 , str(e)

#############################################
#      Below is the del function            # 
#############################################

'''del only serviceMonitor...'''
def del_serviceMonitor_just(name):
    del_url = serviceMonitor_url + str(name)
    res = requests.delete(url=del_url,headers=header,verify=False)
    res_code = res.status_code
    if res_code != 200:
            return res_code , "delete serviceMonitor  failed! the errbody is: " +str(res.json())
    else:
            return 0 , "delete serviceMionitor successsfully"

'''del service,this action will also del endpoints together...'''
def del_service(name):
    del_url = service_url + str(name)
    res = requests.delete(url=del_url,headers=header,verify=False)
    res_code = res.status_code
    if res_code != 200:
            return res_code , "delete service  failed! the errbody is: " +str(res.json())
    else:
            return 0 , "delete service successsfully"


#######################################################################################
#                      Below is acctully del update add                               #
#######################################################################################

'''del full serviceMonitor...'''
def del_serviceMonitor(name):
    ret_m,msg_m = del_serviceMonitor_just(name)
    if ret_m  == 0:
        ret_s,msg_s = del_service(name)
        if ret_s == 0:
            return 0,"del serviceMonitor successfully"
        else:
            -1 , "del service failed! the errbody is: " + str(msg_s)
    else:
        return -2 , "del serviceMonitor failed! the errbody is: " + str(msg_m)

'''create full serviceMonitor , related to service...'''
def create_serviceMonitor(name,interval,metrics_url):
    ip = metrics_url.split("/")[2].split(":")[0]
    port = int(metrics_url.split("/")[2].split(":")[1])
    ret_m,msg_m = add_serviceMonitor_just(name,interval)
    if ret_m == 0:
        ret_s ,msg_s = add_service(name,port)
        if ret_s ==0:
            ret_e , msg_e =  add_endpoints(name,ip,port)
            if ret_e == 0:
                return 0,"all created successful"
            else:
                del_service(name)
                return ret_e , msg_e
        else:
            del_serviceMonitor(name)
            return ret_s ,msg_s
    else:
        return ret_m,msg_m

'''update serviceMonitor...'''
def update_serviceMonitor(name,interval,metrics_url):
    s_interval = get_interval(name)
    ip = metrics_url.split("/")[2].split(":")[0]
    port = int(metrics_url.split("/")[2].split(":")[1])
    ret_m,msg_m = update_serviceMonitor_just(name,interval)
    if ret_m == 0:
        ret_s ,msg_s = update_service(name,port)
        if ret_s ==0:
            ret_e , msg_e =  update_endpoints(name,ip,port)
            if ret_e == 0:
                return 0,"all update successful"
            else:
                ret_e_m,msg_e_m = update_serviceMonitor_just(name,s_interval)
                if ret_e_m ==0:
                    ret_e_s,msg_e_s = update_service(name,s_port)
                    if ret_e_s == 0:
                        return 2,"update serviceMonitor and service successfully but update endpoints failed,so reverting serviceMonitor and service,it is reverting successfully. the update endpoints failed body is: " + str(msg_e)
                    else:
                        return -2,"update serviceMonitor and service successfully but update endpoints failed,so reverting serviceMonitor and service, reverting serviceMonitor successfully but service failed. the  failed body is: " + str(msg_e_s)
                else:
                    return -3,"update serviceMonitor and service successfully but update endpoints failed,so reverting serviceMonitor and service, reverting serviceMonitor failed,the service is not already to revert. the  failed body is: " + str(msg_e_m)
        else:
            ret_s_m,msg_s_m = update_serviceMonitor_just(name,s_interval)
            if ret_s_m ==0:
                return 1,"update serviceMonitor successfully but update service failed,so reverting serviceMonitor and reverting successfully. the update service failed body is: " + str(msg_s)
            else:
                return -1,"update serviceMonitor successfully but update service failed,so reverting serviceMonitor but reverting failed. the failed body is: " + str(msg_s_m)
    else:
        return ret_m,msg_m

name = "update-service"    
interval = "40s"
metrics_url = "http://172.22.104.89:10001/metrics"
#print get_resource_version("custom")
#print get_interval(name)
#print get_ip_port(name)
#print create_serviceMonitor(name,interval,metrics_url)
print update_serviceMonitor(name,interval,metrics_url)
#print update_serviceMonitor_just(name,interval)
#print add_service(name,10000)
#print del_serviceMonitor(name)
