#!/usr/bin/python
# coding:utf-8
########################################################################################################################
# @Author: farmer.luo@gmail.com
# @Create Date: 2019.4.13
#
# @Desc:
# dump k8s config to yaml file
#
# @Usage:
# 1. config k8s connect config and dump dir
# 2. Installation package dependency on zabbix agent host:
#    pip install  kubernetes  argparse -i https://mirrors.aliyun.com/pypi/simple
########################################################################################################################

from __future__ import print_function
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pprint import pprint
import re
import os
import argparse
import yaml
import warnings

warnings.filterwarnings('ignore')
# urllib3.disable_warnings()

dump_path = "/tmp/k8s_backup"
# Configs can be set in Configuration class directly or using helper utility
# config.load_kube_config()
conf = client.Configuration()
# k8s-dev
conf.host = "https://127.0.0.1:8443"
conf.api_key['authorization'] = "xxxxxxxxxxx"
conf.api_key_prefix["authorization"] = "Bearer"
conf.verify_ssl = False


class DumpK8s:

    def __init__(self, use_kube_config=False):
        if use_kube_config:
            config.load_kube_config()
            self.new_client = client.ApiClient()
        else:
            self.new_client = client.ApiClient(conf)
        self.path = dump_path
        self.namespaces = []
        self.get_namespaces()

    def set_kube_config(self):
        self.new_client = client.ApiClient()

    def get_namespaces(self):
        api_instance = client.CoreV1Api(self.new_client)
        try:
            api_response = api_instance.list_namespace(watch=False)
            # pprint(api_response)
            for i in api_response.items:
                # print (i.metadata.name)
                self.namespaces.append(i.metadata.name)

        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespace: %s\n" % e)

    def dump_rolebindings(self):
        print("start dump role binding ...")
        api_instance = client.RbacAuthorizationV1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_role_binding(ns, watch=False)
                for i in api_response.items:
                    self.dump_rolebinding(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling AutoscalingV1Api->list_namespaced_role_binding: %s\n" % e)

        print("dump role binding done.\n")

    def dump_rolebinding(self, name, namespace):
        api_instance = client.RbacAuthorizationV1Api(self.new_client)
        try:
            # print("dump serviceaccount:" + name)
            api_response = api_instance.read_namespaced_role_binding(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "rolebinding", name, namespace)
        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_role_binding: %s\n" % e)

    def dump_clusterrolebindings(self):
        print("start dump cluster role binding ...")
        api_instance = client.RbacAuthorizationV1Api(self.new_client)
        try:
            api_response = api_instance.list_cluster_role_binding(watch=False)
            for i in api_response.items:
                self.dump_clusterrolebinding(i.metadata.name)

        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->list_cluster_role_binding: %s\n" % e)

        print("dump cluster role binding done.\n")

    def dump_clusterrolebinding(self, name):
        api_instance = client.RbacAuthorizationV1Api(self.new_client)
        try:
            # print("dump serviceaccount:" + name)
            api_response = api_instance.read_cluster_role_binding(name, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "clusterrolebinding", name, "cluster")
        except ApiException as e:
            print("Exception when calling RbacAuthorizationV1Api->read_cluster_role_binding: %s\n" % e)

    def dump_serviceaccounts(self):
        print("start dump service account ...")
        api_instance = client.CoreV1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_service_account(ns, watch=False)
                for i in api_response.items:
                    self.dump_serviceaccount(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling AutoscalingV1Api->list_namespaced_service_account: %s\n" % e)

        print("dump service account done.\n")

    def dump_serviceaccount(self, name, namespace):
        api_instance = client.CoreV1Api(self.new_client)
        try:
            # print("dump serviceaccount:" + name)
            api_response = api_instance.read_namespaced_service_account(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "serviceaccount", name, namespace)
        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_service_account: %s\n" % e)

    def dump_horizontalpodautoscalers(self):
        print("start dump horizontal pod autoscalers...")
        api_instance = client.AutoscalingV1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_horizontal_pod_autoscaler(ns, watch=False)
                for i in api_response.items:
                    self.dump_horizontalpodautoscaler(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling AutoscalingV1Api->list_namespaced_ingress: %s\n" % e)

        print("dump horizontal pod autoscaler done.\n")

    def dump_horizontalpodautoscaler(self, name, namespace):
        api_instance = client.AutoscalingV1Api(self.new_client)
        try:
            # print("dump secret:" + name)
            api_response = api_instance.read_namespaced_horizontal_pod_autoscaler(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "horizontal_pod_autoscaler", name, namespace)
        except ApiException as e:
            print("Exception when calling AutoscalingV1Api->read_namespaced_horizontal_pod_autoscaler: %s\n" % e)

    def dump_ingresses(self):
        print("start dump services...")
        api_instance = client.ExtensionsV1beta1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_ingress(ns, watch=False)
                for i in api_response.items:
                    self.dump_ingress(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->list_namespaced_ingress: %s\n" % e)

        print("dump services done.\n")

    def dump_ingress(self, name, namespace):
        api_instance = client.ExtensionsV1beta1Api(self.new_client)
        try:
            # print("dump secret:" + name)
            api_response = api_instance.read_namespaced_ingress(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "ingress", name, namespace)
        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->read_namespaced_ingress: %s\n" % e)

    def dump_services(self):
        print("start dump services...")
        api_instance = client.CoreV1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_service(ns, watch=False)
                for i in api_response.items:
                    # print (i.metadata.name)
                    self.dump_service(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_service: %s\n" % e)

        print("dump services done.\n")

    def dump_service(self, name, namespace):
        api_instance = client.CoreV1Api(self.new_client)
        try:
            api_response = api_instance.read_namespaced_service(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "service", name, namespace)
        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_service: %s\n" % e)

    def dump_statefulsets(self):
        print("start dump daemonsets...")
        api_instance = client.AppsV1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_stateful_set(ns, watch=False)
                for i in api_response.items:
                    self.dump_statefulset(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_stateful_set: %s\n" % e)

        print("dump daemonsets done.\n")

    def dump_statefulset(self, name, namespace):
        api_instance = client.AppsV1Api(self.new_client)
        try:
            # print("dump secret:" + name)
            api_response = api_instance.read_namespaced_stateful_set(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "statefulset", name, namespace)
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_stateful_set: %s\n" % e)

    def dump_daemonsets(self):
        print("start dump daemonsets...")
        api_instance = client.ExtensionsV1beta1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_daemon_set(ns, watch=False)
                for i in api_response.items:
                    self.dump_daemonset(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->list_namespaced_ingress: %s\n" % e)

        print("dump daemonsets done.\n")

    def dump_daemonset(self, name, namespace):
        api_instance = client.ExtensionsV1beta1Api(self.new_client)
        try:
            # print("dump secret:" + name)
            api_response = api_instance.read_namespaced_daemon_set(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "daemonset", name, namespace)
        except ApiException as e:
            print("Exception when calling ExtensionsV1beta1Api->read_namespaced_ingress: %s\n" % e)

    def dump_deployments(self):
        print("start dump deployment...")
        api_instance = client.AppsV1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_deployment(ns, watch=False)
                for i in api_response.items:
                    self.dump_deployment(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling AppsV1Api->list_namespaced_deployment: %s\n" % e)

        print("dump deployment done.\n")

    def dump_deployment(self, name, namespace):
        api_instance = client.AppsV1Api(self.new_client)
        try:
            api_response = api_instance.read_namespaced_deployment(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "deployment", name, namespace)
        except ApiException as e:
            print("Exception when calling AppsV1Api->read_namespaced_deployment: %s\n" % e)

    def dump_configmaps(self):
        print("start dump configmaps...")
        api_instance = client.CoreV1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_config_map(ns, watch=False)
                for i in api_response.items:
                    self.dump_configmap(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_config_map: %s\n" % e)

        print("dump configmaps done.\n")

    def dump_configmap(self, name, namespace):
        api_instance = client.CoreV1Api(self.new_client)
        try:
            api_response = api_instance.read_namespaced_config_map(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "configmap", name, namespace)
        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_config_map: %s\n" % e)

    def dump_secrets(self):
        print("start dump secrets...")
        api_instance = client.CoreV1Api(self.new_client)
        try:
            for ns in self.namespaces:
                api_response = api_instance.list_namespaced_secret(ns, watch=False)
                for i in api_response.items:
                    self.dump_secret(i.metadata.name, ns)

        except ApiException as e:
            print("Exception when calling CoreV1Api->list_namespaced_secret: %s\n" % e)

        print("dump secrets done.\n")

    def dump_secret(self, name, namespace):
        api_instance = client.CoreV1Api(self.new_client)
        try:
            # print("dump secret:" + name)
            api_response = api_instance.read_namespaced_secret(name, namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "secret", name, namespace)
        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced_secret: %s\n" % e)

    def dump_namespaces(self):
        print("start dump namespaces...")
        try:
            for ns in self.namespaces:
                self.dump_namespace(ns)

        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced: %s\n" % e)

        print("dump namespaces done.\n")

    def dump_namespace(self, namespace):
        api_instance = client.CoreV1Api(self.new_client)
        try:
            api_response = api_instance.read_namespace(namespace, async_req=False)
            data = filter_dict(api_response.to_dict())
            self.write_yaml_file(data, "namespace", namespace, namespace)
        except ApiException as e:
            print("Exception when calling CoreV1Api->read_namespaced: %s\n" % e)

    def write_yaml_file(self, data, res_type, name, namespace):
        type_dir = self.path + "/" + namespace + "/" + res_type
        if not os.path.exists(type_dir):
            os.makedirs(type_dir)

        if ":" in name:
            name = name.replace(":", "_")

        yaml_file = type_dir + "/" + name + ".yaml"
        print("write dump file:" + yaml_file)
        with open(yaml_file, 'w') as yaml_stream:
            yaml.safe_dump(data, yaml_stream, default_flow_style=False, encoding='utf-8', allow_unicode=True)


def filter_dict(data):
    filters = ['resource_version', 'self_link', 'uid', 'status', 'creation_timestamp', 'cluster_ip', 'deployment.kubernetes.io/revision', 'kubectl.kubernetes.io/last-applied-configuration']
    if isinstance(data, str):
        return data

    if isinstance(data, int):
        return data

    if isinstance(data, list):
        for i, el in enumerate(data):
            if el is None:
                del data[i]
                continue
            filter_dict(el)

    if isinstance(data, dict):
        for k, v in list(data.items()):
            # print("k=",k,"v=",v,"type=",type(data[k]))
            if v is None or k in filters:
                del data[k]
                continue

            if "_" in k:
                del data[k]
                data[underline2hump(k)] = filter_dict(v)

            filter_dict(v)

    return data


def hump2underline(hunp_str):
    """
    驼峰形式字符串转成下划线形式
    :param hunp_str: 驼峰形式字符串
    :return: 字母全小写的下划线形式字符串
    """
    # 匹配正则，匹配小写字母和大写字母的分界位置
    p = re.compile(r'([a-z]|\d)([A-Z])')
    # 这里第二个参数使用了正则分组的后向引用
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub


def underline2hump(underline_str):
    """
    下划线形式字符串转成驼峰形式
    :param underline_str: 下划线形式字符串
    :return: 驼峰形式字符串
    """
    # 这里re.sub()函数第二个替换参数用到了一个匿名回调函数，回调函数的参数x为一个匹配对象，返回值为一个处理后的字符串
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)
    return sub


def cmd_line_opts(arg=None):
    """
    生成命令行选项
    :return:
    """

    class ParseHelpFormat(argparse.HelpFormatter):
        def __init__(self, prog, indent_increment=5, max_help_position=50, width=200):
            super(ParseHelpFormat, self).__init__(prog, indent_increment, max_help_position, width)

    parse = argparse.ArgumentParser(description='功能：备份k8s集群用户配置，如用户namespace,deployment,configmap,hpa...')
    parse.add_argument('--version', '-v',  action='version', version="1.0", help='查看版本')
    parse.add_argument('--kube-config', action='store_true', help='使用kube config配置连接k8s,否则请编辑脚本文件配置k8s连接信息')
    parse.add_argument('--dump-dir', required=False,  help='dump目录,默认：/tmp/k8s_backup')

    return parse.parse_args(arg)


if __name__ == '__main__':
    opts = cmd_line_opts()
    k8s = DumpK8s(opts.kube_config)

    if opts.dump_dir:
        k8s.path = opts.dump_dir

    print("start dump k8s config to yaml file...\n")
    k8s.dump_namespaces()
    k8s.dump_secrets()
    k8s.dump_configmaps()
    k8s.dump_serviceaccounts()
    k8s.dump_rolebindings()
    k8s.dump_clusterrolebindings()
    k8s.dump_deployments()
    k8s.dump_daemonsets()
    k8s.dump_statefulsets()
    k8s.dump_services()
    k8s.dump_ingresses()
    k8s.dump_horizontalpodautoscalers()

    print("dump k8s config to yaml file done.\n")
