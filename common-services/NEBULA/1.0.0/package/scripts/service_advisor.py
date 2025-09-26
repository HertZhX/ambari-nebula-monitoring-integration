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
import re
import socket
from math import ceil, floor

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
            
            # 端口配置推荐
            self._recommend_port_configurations(configurations)
            
            # 性能配置推荐
            self._recommend_performance_configurations(configurations, hosts)
            
            # 路径配置推荐
            self._recommend_path_configurations(configurations)
            
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
    
    def _recommend_port_configurations(self, configurations):
        """
        推荐端口配置
        """
        # Metad端口配置
        metad_site = self._get_configuration(configurations, 'nebula-metad-site', {})
        if 'port' not in metad_site:
            metad_site['port'] = '9559'
        if 'ws_http_port' not in metad_site:
            metad_site['ws_http_port'] = '19559'
        if 'ws_h2_port' not in metad_site:
            metad_site['ws_h2_port'] = '19560'
        self._put_configuration(configurations, 'nebula-metad-site', metad_site)
        
        # Graphd端口配置
        graphd_site = self._get_configuration(configurations, 'nebula-graphd-site', {})
        if 'port' not in graphd_site:
            graphd_site['port'] = '9669'
        if 'ws_http_port' not in graphd_site:
            graphd_site['ws_http_port'] = '19669'
        if 'ws_h2_port' not in graphd_site:
            graphd_site['ws_h2_port'] = '19670'
        self._put_configuration(configurations, 'nebula-graphd-site', graphd_site)
        
        # Storaged端口配置
        storaged_site = self._get_configuration(configurations, 'nebula-storaged-site', {})
        if 'port' not in storaged_site:
            storaged_site['port'] = '9779'
        if 'ws_http_port' not in storaged_site:
            storaged_site['ws_http_port'] = '19779'
        if 'ws_h2_port' not in storaged_site:
            storaged_site['ws_h2_port'] = '19780'
        if 'heartbeat_interval_secs' not in storaged_site:
            storaged_site['heartbeat_interval_secs'] = '10'
        self._put_configuration(configurations, 'nebula-storaged-site', storaged_site)
    
    def _recommend_performance_configurations(self, configurations, hosts):
        """
        根据主机资源推荐性能配置
        """
        if not hosts:
            return
            
        # 获取典型主机的资源信息
        host_info = hosts[0] if hosts else {}
        memory_mb = int(host_info.get('memory', 8192))  # 默认8GB
        cpu_cores = int(host_info.get('cpu', 4))  # 默认4核
        
        # Metad性能配置
        metad_site = self._get_configuration(configurations, 'nebula-metad-site', {})
        if 'num_io_threads' not in metad_site:
            metad_site['num_io_threads'] = str(min(16, max(4, cpu_cores)))
        if 'num_worker_threads' not in metad_site:
            metad_site['num_worker_threads'] = str(min(32, max(8, cpu_cores * 2)))
        self._put_configuration(configurations, 'nebula-metad-site', metad_site)
        
        # Graphd性能配置
        graphd_site = self._get_configuration(configurations, 'nebula-graphd-site', {})
        if 'num_io_threads' not in graphd_site:
            graphd_site['num_io_threads'] = str(min(16, max(4, cpu_cores)))
        if 'num_worker_threads' not in graphd_site:
            graphd_site['num_worker_threads'] = str(min(32, max(8, cpu_cores * 2)))
        if 'max_allowed_connections' not in graphd_site:
            graphd_site['max_allowed_connections'] = str(min(1000, max(100, memory_mb // 10)))
        self._put_configuration(configurations, 'nebula-graphd-site', graphd_site)
        
        # Storaged性能配置
        storaged_site = self._get_configuration(configurations, 'nebula-storaged-site', {})
        if 'num_io_threads' not in storaged_site:
            storaged_site['num_io_threads'] = str(min(16, max(4, cpu_cores)))
        if 'num_worker_threads' not in storaged_site:
            storaged_site['num_worker_threads'] = str(min(32, max(8, cpu_cores * 2)))
        self._put_configuration(configurations, 'nebula-storaged-site', storaged_site)
    
    def _recommend_path_configurations(self, configurations):
        """
        推荐路径配置
        """
        nebula_env = self._get_configuration(configurations, 'nebula-env', {})
        nebula_data_dir = nebula_env.get('nebula_data_dir', '/var/lib/nebula')
        
        # Metad路径配置
        metad_site = self._get_configuration(configurations, 'nebula-metad-site', {})
        if 'data_path' not in metad_site:
            metad_site['data_path'] = nebula_data_dir + '/meta'
        self._put_configuration(configurations, 'nebula-metad-site', metad_site)
        
        # Storaged路径配置
        storaged_site = self._get_configuration(configurations, 'nebula-storaged-site', {})
        if 'data_path' not in storaged_site:
            storaged_site['data_path'] = nebula_data_dir + '/storage'
        self._put_configuration(configurations, 'nebula-storaged-site', storaged_site)
    
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
                graphd_site['meta_server_addrs'] = metad_server_list
                self._put_configuration(configurations, 'nebula-graphd-site', graphd_site)
                
                # 更新Storaged配置
                storaged_site = self._get_configuration(configurations, 'nebula-storaged-site', {})
                storaged_site['meta_server_addrs'] = metad_server_list
                self._put_configuration(configurations, 'nebula-storaged-site', storaged_site)
            
            # 推荐副本因子配置
            storaged_hosts = self.component_hosts_map.get('NEBULA_STORAGED', [])
            if len(storaged_hosts) >= 3:
                # 根据Storaged节点数量推荐副本因子
                recommended_replica_factor = min(3, len(storaged_hosts))
                
                metad_site = self._get_configuration(configurations, 'nebula-metad-site', {})
                if 'default_replica_factor' not in metad_site:
                    metad_site['default_replica_factor'] = str(recommended_replica_factor)
                self._put_configuration(configurations, 'nebula-metad-site', metad_site)
                
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
        validations = []
        
        # 获取组件分布情况
        component_hosts = self._get_component_host_mapping(services)
        
        # 验证METAD组件
        metad_hosts = component_hosts.get('NEBULA_METAD', [])
        if len(metad_hosts) == 0:
            validations.append({
                "type": "configuration",
                "level": "ERROR",
                "message": "至少需要部署一个Metad组件",
                "config-type": "nebula-metad-site",
                "config-name": "port"
            })
        elif len(metad_hosts) % 2 == 0 and len(metad_hosts) > 1:
            validations.append({
                "type": "configuration",
                "level": "WARN",
                "message": "建议Metad组件部署奇数个实例以确保选举正常",
                "config-type": "nebula-metad-site",
                "config-name": "port"
            })
        
        # 验证STORAGED组件
        storaged_hosts = component_hosts.get('NEBULA_STORAGED', [])
        if len(storaged_hosts) < 3:
            validations.append({
                "type": "configuration",
                "level": "WARN",
                "message": "建议至少部署3个Storaged组件以确保数据冗余和高可用性",
                "config-type": "nebula-storaged-site",
                "config-name": "port"
            })
        
        # 验证GRAPHD组件
        graphd_hosts = component_hosts.get('NEBULA_GRAPHD', [])
        if len(graphd_hosts) == 0:
            validations.append({
                "type": "configuration",
                "level": "ERROR",
                "message": "至少需要部署一个Graphd组件",
                "config-type": "nebula-graphd-site",
                "config-name": "port"
            })
        
        return validations
    
    def _get_component_host_mapping(self, services):
        """
        获取组件与主机的映射关系
        """
        component_hosts = {}
        
        for service in services.get('services', []):
            if service.get('StackServices', {}).get('service_name') == 'NEBULA':
                for component in service.get('components', []):
                    component_name = component.get('StackServiceComponents', {}).get('component_name')
                    if component_name:
                        component_hosts[component_name] = [
                            host.get('HostRoles', {}).get('host_name')
                            for host in component.get('host_components', [])
                        ]
        
        return component_hosts


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
    return service_advisor.validate_configurations(services, hosts)