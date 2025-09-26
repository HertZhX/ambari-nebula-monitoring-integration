#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Nebula Graph Service Advisor for Ambari
提供Nebula Graph服务的配置推荐和验证
"""

import os
import traceback


class NebulaServiceAdvisor(object):
    """
    Nebula Graph服务配置建议器
    """
    
    def __init__(self):
        self.component_hosts_map = {}
        self.services = []
        self.hosts = []
        
    def get_service_configuration_recommendations(self, configurations, cluster_data, hosts, services):
        """
        获取服务配置推荐
        """
        try:
            self.component_hosts_map = cluster_data.get('componentHostsMap', {})
            self.services = services
            self.hosts = hosts
            
            # 基础配置推荐
            self._recommend_nebula_configurations(configurations, cluster_data, hosts, services)
            
        except Exception as e:
            print("Error in get_service_configuration_recommendations: %s" % str(e))
            traceback.print_exc()
    
    def _recommend_nebula_configurations(self, configurations, cluster_data, hosts, services):
        """
        推荐Nebula基础配置
        """
        # nebula-env配置推荐
        nebula_env = self._get_configuration(configurations, 'nebula-env', {})
        
        # 设置默认用户和组
        if 'nebula_user' not in nebula_env:
            nebula_env['nebula_user'] = 'nebula'
        if 'nebula_group' not in nebula_env:
            nebula_env['nebula_group'] = 'nebula'
            
        # 设置默认安装目录
        if 'nebula_install_dir' not in nebula_env:
            nebula_env['nebula_install_dir'] = '/usr/local/nebula'
            
        # 设置默认数据目录
        if 'nebula_data_dir' not in nebula_env:
            nebula_env['nebula_data_dir'] = '/var/lib/nebula'
            
        # 设置默认日志目录
        if 'nebula_log_dir' not in nebula_env:
            nebula_env['nebula_log_dir'] = '/var/log/nebula'
            
        # 设置默认PID目录
        if 'nebula_pid_dir' not in nebula_env:
            nebula_env['nebula_pid_dir'] = '/var/run/nebula'
            
        # 设置默认集群名称
        if 'nebula_cluster_name' not in nebula_env:
            nebula_env['nebula_cluster_name'] = 'nebula_cluster'
            
        self._put_configuration(configurations, 'nebula-env', nebula_env)
        
        # 推荐基于集群拓扑的配置
        self._recommend_cluster_topology_configs(configurations, cluster_data, hosts, services)
    
    def _recommend_cluster_topology_configs(self, configurations, cluster_data, hosts, services):
        """
        根据集群拓扑推荐配置
        """
        try:
            # 获取Metad主机列表
            metad_hosts = self.component_hosts_map.get('NEBULA_METAD', [])
            if metad_hosts:
                # 构建 metad 服务器地址列表
                metad_addrs = []
                for host in metad_hosts:
                    metad_addrs.append('{}:9559'.format(host))
                metad_server_list = ','.join(metad_addrs)
                
                # 更新Graphd配置
                graphd_site = self._get_configuration(configurations, 'nebula-graphd-site', {})
                if 'meta_server_addrs' not in graphd_site or not graphd_site['meta_server_addrs']:
                    graphd_site['meta_server_addrs'] = metad_server_list
                self._put_configuration(configurations, 'nebula-graphd-site', graphd_site)
                
                # 更新Storaged配置  
                storaged_site = self._get_configuration(configurations, 'nebula-storaged-site', {})
                if 'meta_server_addrs' not in storaged_site or not storaged_site['meta_server_addrs']:
                    storaged_site['meta_server_addrs'] = metad_server_list
                self._put_configuration(configurations, 'nebula-storaged-site', storaged_site)
                
        except Exception as e:
            print("Error in _recommend_cluster_topology_configs: %s" % str(e))
    
    def _get_configuration(self, configurations, config_type, default_value=None):
        """
        获取配置
        """
        if config_type in configurations:
            return configurations[config_type].get('properties', default_value or {})
        return default_value or {}
    
    def _put_configuration(self, configurations, config_type, config_properties):
        """
        设置配置
        """
        if config_type not in configurations:
            configurations[config_type] = {}
        if 'properties' not in configurations[config_type]:
            configurations[config_type]['properties'] = {}
        configurations[config_type]['properties'].update(config_properties)
    
    def get_service_configuration_validators(self):
        """
        获取配置验证器
        """
        return []
    
    def get_service_component_layout_validations(self, services, hosts):
        """
        获取组件布局验证规则
        """
        return []


# 导出服务建议器实例
service_advisor = NebulaServiceAdvisor()

def get_service_configuration_recommendations(configurations, cluster_data, hosts, services):
    """
    获取服务配置推荐的全局函数
    """
    return service_advisor.get_service_configuration_recommendations(configurations, cluster_data, hosts, services)

def get_service_configuration_validators():
    """
    获取配置验证器的全局函数
    """
    return service_advisor.get_service_configuration_validators()

def get_service_component_layout_validations(services, hosts):
    """
    获取组件布局验证的全局函数
    """
    return service_advisor.get_service_component_layout_validations(services, hosts)

def validate_configurations(services, hosts):
    """
    验证配置的全局函数
    """
    try:
        return service_advisor.get_service_component_layout_validations(services, hosts)
    except Exception as e:
        print("Error in validate_configurations: %s" % str(e))
        return []