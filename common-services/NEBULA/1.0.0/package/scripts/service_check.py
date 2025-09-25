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
import time
import socket
from resource_management import *
from resource_management.libraries.script.script import Script
from resource_management.core.resources.system import Execute
from resource_management.libraries.functions.format import format

class NebulaServiceCheck(Script):
    """
    Nebula服务健康检查类
    """

    def service_check(self, env):
        """
        执行Nebula服务的健康检查
        """
        import params
        env.set_params(params)
        
        print("Performing Nebula service health check...")
        
        # 检查Metad服务
        self.check_metad_service()
        
        # 检查Graphd服务
        self.check_graphd_service()
        
        # 检查Storaged服务
        self.check_storaged_service()
        
        print("All Nebula services are healthy!")

    def check_metad_service(self):
        """
        检查Metad服务健康状态
        """
        import params
        
        print("Checking Metad service...")
        
        # 检查进程是否运行
        if not self.is_process_running(params.metad_pid_file):
            raise Exception("Metad process is not running")
        
        # 检查端口是否监听
        if not self.is_port_open(params.metad_port):
            raise Exception(format("Metad port {metad_port} is not accessible"))
        
        # 检查HTTP管理接口
        if not self.check_http_endpoint(params.metad_http_port, '/status'):
            raise Exception("Metad HTTP management interface is not responding")
        
        print("Metad service is healthy")

    def check_graphd_service(self):
        """
        检查Graphd服务健康状态
        """
        import params
        
        print("Checking Graphd service...")
        
        # 检查进程是否运行
        if not self.is_process_running(params.graphd_pid_file):
            raise Exception("Graphd process is not running")
        
        # 检查端口是否监听
        if not self.is_port_open(params.graphd_port):
            raise Exception(format("Graphd port {graphd_port} is not accessible"))
        
        # 检查HTTP管理接口
        if not self.check_http_endpoint(params.graphd_http_port, '/status'):
            raise Exception("Graphd HTTP management interface is not responding")
        
        print("Graphd service is healthy")

    def check_storaged_service(self):
        """
        检查Storaged服务健康状态
        """
        import params
        
        print("Checking Storaged service...")
        
        # 检查进程是否运行
        if not self.is_process_running(params.storaged_pid_file):
            raise Exception("Storaged process is not running")
        
        # 检查端口是否监听
        if not self.is_port_open(params.storaged_port):
            raise Exception(format("Storaged port {storaged_port} is not accessible"))
        
        # 检查HTTP管理接口
        if not self.check_http_endpoint(params.storaged_http_port, '/status'):
            raise Exception("Storaged HTTP management interface is not responding")
        
        print("Storaged service is healthy")

    def is_process_running(self, pid_file):
        """
        检查进程是否运行
        
        Args:
            pid_file: PID文件路径
            
        Returns:
            bool: 进程是否运行
        """
        import os
        
        if not os.path.exists(pid_file):
            return False
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # 检查进程是否存在
            os.kill(pid, 0)
            return True
        except (OSError, ValueError):
            return False

    def is_port_open(self, port, host='localhost', timeout=5):
        """
        检查端口是否打开
        
        Args:
            port: 端口号
            host: 主机地址，默认localhost
            timeout: 超时时间（秒）
            
        Returns:
            bool: 端口是否打开
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            return result == 0
        except Exception:
            return False

    def check_http_endpoint(self, port, path='/status', host='localhost', timeout=10):
        """
        检查HTTP端点是否响应
        
        Args:
            port: HTTP端口
            path: 请求路径
            host: 主机地址
            timeout: 超时时间（秒）
            
        Returns:
            bool: 端点是否正常响应
        """
        try:
            url = format("http://{host}:{port}{path}")
            req = urllib2.Request(url)
            response = urllib2.urlopen(req, timeout=timeout)
            
            if response.getcode() == 200:
                return True
            else:
                return False
        except Exception as e:
            print(format("HTTP endpoint check failed: {e}"))
            return False

    def perform_simple_query_test(self):
        """
        执行简单的查询测试
        """
        import params
        
        try:
            # 通过console执行简单的查询来验证服务可用性
            graphd_host = params.hostname
            test_cmd = format("{nebula_console_bin} -addr {graphd_host} -port {graphd_port} -u root -p nebula -e 'SHOW HOSTS'")
            
            Execute(test_cmd,
                    user=params.nebula_user,
                    timeout=30,
                    logoutput=True)
            
            print("Simple query test passed")
            return True
        except Exception as e:
            print(format("Simple query test failed: {e}"))
            return False

    def check_cluster_connectivity(self):
        """
        检查集群组件间的连通性
        """
        import params
        
        print("Checking cluster connectivity...")
        
        # 检查Graphd到Metad的连接
        metad_hosts = params.metad_hosts
        for metad_host in metad_hosts:
            if not self.is_port_open(params.metad_port, metad_host):
                raise Exception(format("Cannot connect to Metad on {metad_host}:{metad_port}"))
        
        print("Cluster connectivity check passed")

if __name__ == "__main__":
    NebulaServiceCheck().execute()