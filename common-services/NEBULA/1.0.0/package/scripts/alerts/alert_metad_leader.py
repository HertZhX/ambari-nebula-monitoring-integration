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
METAD_HTTP_PORT_KEY = '{{nebula-metad-site/ws_http_port}}'

def get_tokens():
    """
    返回用于解析配置的tokens
    """
    return (METAD_HOSTS_KEY, METAD_HTTP_PORT_KEY)

def execute(configurations={}, parameters=[], host_name=None):
    """
    检查Metad集群中是否有Leader
    返回包含告警结果的元组 (result_code, [result_label])
    """
    result_code = None
    label = None
    
    if configurations is None:
        return (RESULT_CODE_UNKNOWN, ['There were no configurations supplied to the script.'])
    
    metad_hosts = None
    metad_http_port = None
    
    if METAD_HOSTS_KEY in configurations:
        metad_hosts = configurations[METAD_HOSTS_KEY]
    
    if METAD_HTTP_PORT_KEY in configurations:
        metad_http_port = int(configurations[METAD_HTTP_PORT_KEY])
    
    if metad_hosts is None or len(metad_hosts) == 0:
        return (RESULT_CODE_UNKNOWN, ['No Metad hosts are configured.'])
    
    if metad_http_port is None:
        return (RESULT_CODE_UNKNOWN, ['The Metad HTTP port could not be determined.'])
    
    # 检查每个Metad节点的Leader状态
    leaders = []
    accessible_hosts = 0
    
    for host in metad_hosts:
        try:
            if is_metad_leader(host, metad_http_port):
                leaders.append(host)
            accessible_hosts += 1
        except Exception as e:
            # 无法访问的节点不计入统计
            continue
    
    # 分析Leader状态
    leader_count = len(leaders)
    
    if leader_count == 0:
        if accessible_hosts == 0:
            result_code = RESULT_CODE_UNKNOWN
            label = 'Cannot access any Metad nodes to check leader status.'
        else:
            result_code = RESULT_CODE_CRITICAL
            label = 'No leader found in Metad cluster. This will cause service unavailability.'
    elif leader_count == 1:
        result_code = RESULT_CODE_OK
        label = 'Metad cluster has a healthy leader on {0}.'.format(leaders[0])
    else:
        result_code = RESULT_CODE_WARNING
        label = 'Metad cluster has multiple leaders: {0}. This indicates a split-brain situation.'.format(
            ', '.join(leaders))
    
    return (result_code, [label])

def is_metad_leader(host, http_port):
    """
    检查Metad节点是否为Leader
    
    Args:
        host: 主机名
        http_port: HTTP管理端口
        
    Returns:
        bool: 是否为Leader
    """
    try:
        # 尝试多个可能的API端点
        endpoints = ['/leader', '/status', '/flags']
        
        for endpoint in endpoints:
            url = 'http://{0}:{1}{2}'.format(host, http_port, endpoint)
            response = urllib2.urlopen(url, timeout=5)
            
            if response.getcode() == 200:
                data = response.read()
                
                # 尝试解析JSON响应
                try:
                    json_data = json.loads(data)
                    # 检查不同的可能字段
                    if 'is_leader' in json_data:
                        return json_data['is_leader']
                    elif 'leader' in json_data:
                        return json_data['leader']
                    elif 'role' in json_data:
                        return json_data['role'].lower() == 'leader'
                except ValueError:
                    # 如果不是JSON，检查文本响应
                    if 'leader' in data.lower():
                        return True
                
                # 如果是/status端点，默认认为能访问的就是leader
                if endpoint == '/status':
                    return True
    except Exception:
        # 访问失败，假设不是leader
        pass
    
    return False

if __name__ == '__main__':
    import sys
    print(execute())