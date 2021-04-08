#!/usr/bin/env python3.6
# coding=utf-8
import json

#from common.zabbixapi import HostApi, ItemApi, ItemprototypeApi, TriggerApi, ApplicationApi, LldApi
from common.zbxapi.zabbix_api import ZabbixAPI

from pypinyin import lazy_pinyin
import sys
import time

from port.models import port
from common.add_info import AddInfo

class TesPort(object):
    def __init__(self, get_string):
        print(get_string)
        print(11)
    def tea(self):
        print(22)

class CreatePortZabApi(object):
    def __init__(self, data_list):
        self.zbxapi = ZabbixAPI()
        self.name = data_list["name"]
        self.group_ip = data_list["group_ip"]
        self.port = data_list["port"]
        self.productline = data_list["productline"]
        self.alarm_group = data_list["alarm_group"]
        self.ops = data_list["ops"]
        self.dev = data_list["dev"]
        self.trigger_rank = data_list["trigger_rank"]
        self.addinfo = AddInfo()
        self.status = data_list["status"]

        get_pinyin_tempate = lazy_pinyin(self.name)
        self.tem_name_key = "-".join(i.strip() for i in get_pinyin_tempate)
        self.group_name = "端口监控"
        self.appli_name = "monitor-port"

    def now_time(self):
        now_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        return now_time

    def get_group_appid(self):
        try:
            get_data = self.zbxapi.hostgroup.get(output=['groupid'], filter={"name": [self.group_name]})
            groupid = get_data[0]['groupid']
        except:
            raise Exception("获取监控组group:%s 失败!" % self.group_name)
        return groupid

    def get_hosts_id(self):
        get_data = self.zbxapi.hostinterface.get(output=["hostid", "ip"], filter={"ip": self.group_ip, "type": 1})
        ip_list = []
        for data in get_data:
            ip_list.append(data['ip'])
        for ip in self.group_ip:
            if ip not in ip_list:
                raise Exception("获取%s失败，可能原因：没装zabbix-agent客户端！" % ip)
        hostid = []
        for i in get_data:
             hostid.append(i['hostid'])
        return hostid

    def create_appli(self):
        tem_id = self.get_template_id()
        try:
            self.zbxapi.application.create(name=self.appli_name, hostid=tem_id)
        except:
            self.delete_port_item()
            raise Exception("创建application:%s 失败!" % self.appli_name)

    def get_appli_id(self):
        tem_id = self.get_template_id()
        try:
            get_id = self.zbxapi.application.get(output=["applicationid"], hostids=tem_id, filter={"name": [self.appli_name]})
            get_id = get_id[0]["applicationid"]
        except:
            raise Exception("获取application-id: %s 失败！" % self.appli_name)
        return get_id

    def create_template(self):
        groupid = self.get_group_appid()
        hosts_id = self.get_hosts_id()
        hosts_list = []
        for i in hosts_id:
            host_dic = {}
            get_h = host_dic["hostid"] = i
            hosts_list.append(get_h)
        try:
            self.zbxapi.template.create(host=self.tem_name_key, groups={"groupid": groupid}, hosts=hosts_list, name=self.name)
        except:
            raise Exception("创建template: %s模板失败！" % self.tem_name_key)

    def get_template_id(self):
        try:
            get_id = self.zbxapi.template.get(output=["hostid"], filter={"host": [self.tem_name_key]})
            get_id = get_id[0]['templateid']
        except:
            raise Exception("获取template-id: %s 失败！" % self.tem_name_key)
        return get_id

    def create_item_trigger(self):
        self.create_template()
        self.create_appli()
        tem_id = self.get_template_id()
        get_appli_id = self.get_appli_id()
        for i in self.port:
            item_name_des = self.name + '-' + i + '-端口'
            key = "net.tcp.listen[%s]" % i
            try:
                self.zbxapi.item.create(name=item_name_des, key_=key, hostid=tem_id, type="7", value_type="3", delay=30, valuemapid="3", applications=[get_appli_id])
            except:
                self.delete_port_item()
                raise Exception("创建item失败，key: %s！" % key)
            self.create_trigger(item_name_des, key)

    def create_trigger(self, trigger_name, key):

        priority = self.trigger_rank
        if priority == 'information':
            priority_num = 1
        elif priority == 'warning':
            priority_num = 2
        elif priority == 'average':
            priority_num = 3
        elif priority == 'high':
            priority_num = 4
        elif priority == 'disaster':
            priority_num = 5
        else:
            priority_num = 3

        trigger_expres = "{%s:%s.max(#2)}<1" % (self.tem_name_key, key)
        recovery_expres = "{%s:%s.min(#2)}>0" % (self.tem_name_key, key)

        tag_list = []
        alarm_group = {"tag": "alarm_group",  "value": self.alarm_group}
        ops_list = {"tag": "运维", "value": self.ops}
        dev_list = {"tag": "开发", "value": self.dev}
        sub_list = {"tag": "产品线", "value": self.productline}
        tag_list.append(alarm_group)
        tag_list.append(ops_list)
        tag_list.append(dev_list)
        tag_list.append(sub_list)
        try:
            self.zbxapi.trigger.create(description=trigger_name, expression=trigger_expres, recovery_mode=1,
                                                    recovery_expression=recovery_expres, priority=priority_num, tags=tag_list, manual_close=1)
        except:
            self.delete_port_item()
            raise Exception("创建trigger: %s失败！" % trigger_name)


    def delete_port_item(self):
        # raise Exception("删除trigger：失败！")
        tempate_id = self.get_template_id()
        try:
            self.zbxapi.template.delete(tempate_id)
        except:
            raise Exception("删除trigger：%s失败！" % tempate_id)

class UpdatePortZabApi(object):
    def __init__(self, old_data_list, new_data_list):

        self.zbxapi = ZabbixAPI()
        self.old_name = old_data_list["name"]
        self.old_group_ip = old_data_list["group_ip"]
        self.old_port = old_data_list["port"]
        self.old_productline = old_data_list["productline"]
        self.old_alarm_group = old_data_list["alarm_group"]
        self.old_ops = old_data_list["ops"]
        self.old_dev = old_data_list["dev"]
        self.old_trigger_rank = old_data_list["trigger_rank"]
        self.old_status = old_data_list["status"]

        self.new_name = new_data_list["name"]
        self.new_group_ip = new_data_list["group_ip"]
        self.new_port = new_data_list["port"]
        self.new_productline = new_data_list["productline"]
        self.new_alarm_group = new_data_list["alarm_group"]
        self.new_ops = new_data_list["ops"]
        self.new_dev = new_data_list["dev"]
        self.new_trigger_rank = new_data_list["trigger_rank"]
        self.new_status = new_data_list["status"]

        get_old_pinyin_tempate = lazy_pinyin(self.old_name)
        self.old_tem_name_key = "-".join(i.strip() for i in get_old_pinyin_tempate)
        get_new_pinyin_tempate = lazy_pinyin(self.new_name)
        self.new_tem_name_key = "-".join(i.strip() for i in get_new_pinyin_tempate)
        self.group_name = "端口监控"
        self.appli_name = "monitor-port"

        # self.addinfo = AddInfo()
        # self.port_info = port.objects.get(name=self.new_name)
        #
        # self.port_info.port_status = 1

    def get_template_id(self):
        try:
            get_id = self.zbxapi.template.get(output=["hostid"], filter={"host": [self.new_tem_name_key]})
            get_id = get_id[0]['templateid']
        except:
            raise Exception("获取template-id失败！")
        return get_id

    def update_template(self):
            try:
                template_result = self.zbxapi.template.get(output=["hostid"], filter={"host": [self.old_tem_name_key]})
                template_id = template_result[0]['templateid']
            except:
                raise Exception("获取old-template-id失败！")
            hosts_id = self.get_hosts_id()
            hosts_list = []
            for i in hosts_id:
                host_dic = {}
                host_dic["hostid"] = i
                hosts_list.append(host_dic)
            try:
                self.zbxapi.template.update(templateid=template_id, hosts=hosts_list, name=self.new_name, host=self.new_tem_name_key)
            except:
                raise Exception("更新template失败！")


    def update_item(self):
        self.update_template()
        tem_id = self.get_template_id()
        get_appli_id = self.get_appli_id()
        for new_port in self.new_port:
            if new_port not in self.old_port:
                item_name_des = self.new_name + '-' + new_port + '-端口'
                key = "net.tcp.listen[%s]" % new_port
                try:
                    self.zbxapi.item.create(name=item_name_des, key_=key, hostid=tem_id, type="7", value_type="3", delay=30, valuemapid="3", applications=[get_appli_id])
                except:
                    raise Exception("创建item失败！")
                self.create_trigger(item_name_des, key)
            else:
                item_name_des = self.new_name + '-' + new_port + '-端口'
                key = "net.tcp.listen[%s]" % new_port
                try:
                    get_item_result = self.zbxapi.item.get(output=["itemid"], filter={"key_": key}, hostids=tem_id)
                    get_item_id = get_item_result[0]["itemid"]
                    self.zbxapi.item.update(itemid=get_item_id, name=item_name_des)
                except:
                    raise Exception("更新item: %s失败！" % item_name_des)
        for old_port in self.old_port:
            if old_port not in self.new_port:
                key = "net.tcp.listen[%s]" % old_port
                try:
                    get_item_result = self.zbxapi.item.get(output=["itemid"], filter={"key_": key}, hostids=tem_id)
                    get_item_id = get_item_result[0]["itemid"]
                    self.zbxapi.item.delete(get_item_id)
                except:
                    raise Exception("del item: %s 失败！" % key)

        self.update_trigger()

    def get_group_appid(self):
        try:
            get_data = self.zbxapi.hostgroup.get(output=['groupid'], filter={"name": [self.group_name]})
            groupid = get_data[0]['groupid']
        except:
            raise Exception("获取组: %s 失败！" % self.group_name)
        return groupid

    def get_hosts_id(self):
        try:
            get_data = self.zbxapi.hostinterface.get(output=["hostid", "ip"], filter={"ip": self.new_group_ip})
        except:
            raise Exception("获取ip地址: %s 失败！" % self.group_name)
        ip_list = []
        for data in get_data:
            ip_list.append(data['ip'])
        print(ip_list)
        print(self.new_group_ip)
        for ip in self.new_group_ip:
            if ip not in ip_list:
                raise Exception("获取ip失败，原因： %s 可能没装agent客户端！" % ip)
        hostid = []
        for i in get_data:
            hostid.append(i['hostid'])
        return hostid

    def get_appli_id(self):
        tem_id = self.get_template_id()
        get_id = self.zbxapi.application.get(output=["applicationid"], hostids=tem_id, filter={"name": [self.appli_name]})
        get_id = get_id[0]["applicationid"]
        return get_id

    def update_trigger(self):
        for new_port in self.new_port:
            if new_port in self.old_port:
                old_trigger_name = self.old_name + '-' + new_port + '-端口'
                trigger_name = self.new_name + '-' + new_port + '-端口'
                tem_id = self.get_template_id()
                get_trigger_result = self.zbxapi.trigger.get(output=["triggerid"], hostids=tem_id, filter={"description": old_trigger_name})
                get_trigger_id = get_trigger_result[0]['triggerid']
                priority = self.new_trigger_rank
                if priority == 'information':
                    priority_num = 1
                elif priority == 'warning':
                    priority_num = 2
                elif priority == 'average':
                    priority_num = 3
                elif priority == 'high':
                    priority_num = 4
                elif priority == 'disaster':
                    priority_num = 5
                else:
                    priority_num = 3

                tag_list = []
                alarm_group = {"tag": "alarm_group",  "value": self.new_alarm_group}
                ops_list = {"tag": "运维", "value": self.new_ops}
                dev_list = {"tag": "开发", "value": self.new_dev}
                sub_list = {"tag": "产品线", "value": self.new_productline}
                tag_list.append(alarm_group)
                tag_list.append(ops_list)
                tag_list.append(dev_list)
                tag_list.append(sub_list)
                try:
                    self.zbxapi.trigger.update(triggerid=get_trigger_id, description=trigger_name, priority=priority_num, tags=tag_list, manual_close=1, status=self.old_status)
                except:
                    raise Exception("更新trigger: %s 失败！" % trigger_name)

    def create_trigger(self, trigger_name, key):

        priority = self.new_trigger_rank
        if priority == 'information':
            priority_num = 1
        elif priority == 'warning':
            priority_num = 2
        elif priority == 'average':
            priority_num = 3
        elif priority == 'high':
            priority_num = 4
        elif priority == 'disaster':
            priority_num = 5
        else:
            priority_num = 3

        trigger_expres = "{%s:%s.max(#2)}<1" % (self.new_tem_name_key, key)
        recovery_expres = "{%s:%s.min(#2)}>0" % (self.new_tem_name_key, key)

        tag_list = []
        alarm_group = {"tag": "alarm_group",  "value": self.new_alarm_group}
        ops_list = {"tag": "运维", "value": self.new_ops}
        dev_list = {"tag": "开发", "value": self.new_dev}
        sub_list = {"tag": "产品线", "value": self.new_productline}
        tag_list.append(alarm_group)
        tag_list.append(ops_list)
        tag_list.append(dev_list)
        tag_list.append(sub_list)

        try:
            self.zbxapi.trigger.create(description=trigger_name, expression=trigger_expres, recovery_mode=1,
                                                    recovery_expression=recovery_expres, priority=priority_num ,tags=tag_list, manual_close=1, status=self.old_status)
        except:
            raise Exception("创建trigger: %s失败！" % trigger_name)


class UpdatePortTriggerStatusZabApi(object):
    def __init__(self, data_list):
        self.zbxapi = ZabbixAPI()
        self.name = data_list["name"]
        self.group_ip = data_list["group_ip"]
        self.ports = data_list["port"]
        self.productline = data_list["productline"]
        self.alarm_group = data_list["alarm_group"]
        self.ops = data_list["ops"]
        self.dev = data_list["dev"]
        self.trigger_rank = data_list["trigger_rank"]
        self.addinfo = AddInfo()
        self.status = data_list["status"]

        get_pinyin_tempate = lazy_pinyin(self.name)
        self.tem_name_key = "-".join(i.strip() for i in get_pinyin_tempate)
        self.group_name = "端口监控"
        self.appli_name = "monitor-port"
        self.port_info = port.objects.get(name=self.name)

    def get_group_appid(self):
        try:
            get_data = self.zbxapi.hostgroup.get(output=['groupid'], filter={"name": [self.group_name]})
            groupid = get_data[0]['groupid']
        except:
            # self.port_info.info += self.addinfo.add_info('get-group-id', 'danger', '%s失败' % self.group_name)
            # self.port_info.port_status = 0
            # self.port_info.save()
            raise Exception("获取组：%s 失败！" % self.group_name)
        return groupid

    def update_trigger_status(self):
        group_id = self.get_group_appid()
        try:
            get_keys = self.zbxapi.item.get(output=["itemid"], filter={"host": [self.tem_name_key]},
                                        selectTriggers=['triggerid'], groupids=group_id)
        except:
            raise Exception("获取item-id：%s 失败！" % self.name)

        trigger_id = []
        for item in get_keys:
            trigger_ids = item['triggers']
            if trigger_ids:
                for trigger in trigger_ids:
                    trigger_id.append(trigger['triggerid'])

        if str(self.status) == '0':
            status = 1
        else:
            status = 0
        if trigger_id:
            for i in trigger_id:
                try:
                    self.zbxapi.trigger.update(triggerid=i, status=status)
                except:
                    # self.port_info.info += self.addinfo.add_info('update-trigger', 'danger', '%s失败' % self.name)
                    self.port_info.trigger_enable = self.status
                    self.port_info.port_status = 0
                    self.port_info.save()
                    raise Exception("获取item-id：%s 失败！")
            self.port_info.trigger_enable = status
            self.port_info.save()
        # else:
            # self.port_info.info += self.addinfo.add_info('update-trigger', 'danger', '%s失败' % self.name)
            # self.port_info.save()

name = {'name': 'testbb4', 'group_ip': ['10.101.2.10', '172.22.104.89'], 'port': ['1022', '1321', '10521'], 'productline': '新版本听写', 'alarm_group': 'jianshen2', 'ops': '李德辉', 'dev': '刘健', 'trigger_rank': 'high', 'status': 0}
# name = {'name': 'test2-端口', 'group_ip': ['10.101.2.10', '172.22.104.89'], 'port': ['1022', '1322', '520', '521'], 'productline': '新版本听写', 'alarm_group': 'jianshen2', 'ops': '李辉', 'dev': '刘健', 'trigger_rank': 'high', 'status': 0}
# name = {'name': 'test2-端口', 'group_ip': ['10.101.2.10', '172.22.104.89'], 'port': ['1022', '1322', '520', '521'], 'productline': '新版本听写', 'alarm_group': 'jianshen2', 'ops': '李辉', 'dev': '刘健', 'trigger_rank': 'high', 'status': 0}
# name_new = {'name': 'test5-端口', 'group_ip': ['172.22.104.89'], 'port': ['1022', '1322', '522'], 'productline': '新版本听写', 'alarm_group': 'jianshen2', 'ops': '李辉', 'dev': '刘', 'trigger_rank': 'high', 'status': 0}

# get_data = UpdatePortStatusZabApi(name)
# get_data.get_exits_items()

# get_data = CreatePortZabApi(name)
# get_data.create_item_trigger()
# get_data_new = UpdateZabApi(name, name_new)
# get_data_new.update_item()
# get_data_new.update_trigger()
# get_data.delete_port_item()
# get_data.get_template_id('tts端口监控')
# get_data.create_template('端口监控', 'tts端口监控', ['172.16.59.210', '172.22.104.89'])
# get_data.get_hosts_id(['172.16.59.210', '172.22.104.89'])
# get_data.get_appli_id('tts端口监控', 'monitor-port')
# get_data.create_appli('tts端口监控', 'monitor-port')