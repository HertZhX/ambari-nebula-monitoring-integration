#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import socket
import urllib2
import json
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.format import format
from resource_management.core.logger import Logger

RESULT_CODE_OK = 'OK'
RESULT_CODE_WARNING = 'WARNING'
RESULT_CODE_CRITICAL = 'CRITICAL'
RESULT_CODE_UNKNOWN = 'UNKNOWN'

METAD_HOSTS_KEY = '{{clusterHostInfo/nebula_metad_hosts}}'
METAD_PORT_KEY = '{{nebula-metad-site/port}}'
METAD_HTTP_PORT_KEY = '{{nebula-metad-site/ws_http_port}}'

def get_tokens():
    """
    返回用于解析配置的tokens
    """
    return (METAD_HOSTS_KEY, METAD_PORT_KEY, METAD_HTTP_PORT_KEY)

def execute(configurations={}, parameters=[], host_name=None):
    """
    检查Nebula集群健康状态
    返回包含告警结果的元组 (result_code, [result_label])
    """
    result_code = None
    label = None
    
    if configurations is None:
        return (RESULT_CODE_UNKNOWN, ['There were no configurations supplied to the script.'])
    
    metad_hosts = None
    metad_port = None
    metad_http_port = None
    
    if METAD_HOSTS_KEY in configurations:
        metad_hosts = configurations[METAD_HOSTS_KEY]
    
    if METAD_PORT_KEY in configurations:
        metad_port = int(configurations[METAD_PORT_KEY])
    
    if METAD_HTTP_PORT_KEY in configurations:
        metad_http_port = int(configurations[METAD_HTTP_PORT_KEY])
    
    if metad_hosts is None or len(metad_hosts) == 0:
        return (RESULT_CODE_UNKNOWN, ['No Metad hosts are configured.'])
    
    if metad_port is None:
        return (RESULT_CODE_UNKNOWN, ['The Metad port could not be determined.'])
    
    if metad_http_port is None:
        return (RESULT_CODE_UNKNOWN, ['The Metad HTTP port could not be determined.'])
    
    # 检查Metad节点健康状态
    healthy_metads = 0
    total_metads = len(metad_hosts)
    leaders = 0
    
    for host in metad_hosts:
        if is_metad_healthy(host, metad_port, metad_http_port):
            healthy_metads += 1
            
            # 检查是否为Leader
            if is_metad_leader(host, metad_http_port):
                leaders += 1
    
    # 计算健康状态
    health_ratio = float(healthy_metads) / float(total_metads)
    
    if health_ratio >= 0.75:  # 75%以上节点健康
        if leaders >= 1:
            result_code = RESULT_CODE_OK
            label = 'Nebula cluster is healthy. {0}/{1} Metad nodes are running with {2} leader(s).'.format(
                healthy_metads, total_metads, leaders)
        else:
            result_code = RESULT_CODE_CRITICAL
            label = 'Nebula cluster has no leader. {0}/{1} Metad nodes are running but no leader found.'.format(
                healthy_metads, total_metads)
    elif health_ratio >= 0.5:  # 50%-75%节点健康
        result_code = RESULT_CODE_WARNING
        label = 'Nebula cluster health is degraded. Only {0}/{1} Metad nodes are running.'.format(
            healthy_metads, total_metads)
    else:  # 少于50%节点健康
        result_code = RESULT_CODE_CRITICAL
        label = 'Nebula cluster health is critical. Only {0}/{1} Metad nodes are running.'.format(
            healthy_metads, total_metads)
    
    return (result_code, [label])

def is_metad_healthy(host, port, http_port):
    """
    检查Metad节点是否健康
    """
    # 检查服务端口
    if not is_port_accessible(host, port):
        return False
    
    # 检查HTTP管理端口
    if not is_port_accessible(host, http_port):
        return False
    
    # 通过HTTP接口检查状态
    try:
        url = 'http://{0}:{1}/status'.format(host, http_port)
        response = urllib2.urlopen(url, timeout=5)
        if response.getcode() == 200:
            return True
    except Exception:
        pass
    
    return False

def is_metad_leader(host, http_port):
    """
    检查Metad节点是否为Leader
    """
    try:
        url = 'http://{0}:{1}/leader'.format(host, http_port)
        response = urllib2.urlopen(url, timeout=5)
        if response.getcode() == 200:
            data = json.loads(response.read())
            return data.get('is_leader', False)
    except Exception:
        pass
    
    return False

def is_port_accessible(host, port, timeout=3):
    """
    检查端口是否可访问
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False

if __name__ == '__main__':
    import sys
    print(execute())