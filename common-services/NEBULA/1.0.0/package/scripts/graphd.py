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

import sys
from resource_management import *
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import stack_select
from resource_management.core.resources.system import Execute, File, Directory
from resource_management.core.source import InlineTemplate
from resource_management.libraries.functions.check_process_status import check_process_status

from nebula_utils import nebula_service, setup_nebula_config, generate_graphd_config
import params

class GraphdServer(Script):
    """
    Nebula Graphd服务控制类
    """

    def install(self, env):
        """
        安装Graphd组件
        """
        print("Installing Nebula Graphd...")
        self.install_packages(env)
        
        # 创建Nebula用户
        Execute(format('id {nebula_user} || useradd {nebula_user}'),
                ignore_failures=True)
        
        # 创建Nebula用户组
        Execute(format('getent group {nebula_group} || groupadd {nebula_group}'),
                ignore_failures=True)
        
        # 将用户添加到组
        Execute(format('usermod -a -G {nebula_group} {nebula_user}'),
                ignore_failures=True)

    def configure(self, env):
        """
        配置Graphd组件
        """
        import params
        env.set_params(params)
        
        print("Configuring Nebula Graphd...")
        
        # 设置基础配置
        setup_nebula_config()
        
        # 生成Graphd特定配置
        generate_graphd_config()
        
        # 确保数据和日志目录权限正确
        Directory([params.nebula_data_dir, params.nebula_log_dir, params.nebula_pid_dir],
                  owner=params.nebula_user,
                  group=params.nebula_group,
                  mode=0755,
                  create_parents=True,
                  recursive_ownership=True)

    def start(self, env, upgrade_type=None):
        """
        启动Graphd服务
        """
        import params
        env.set_params(params)
        
        print("Starting Nebula Graphd...")
        
        # 先配置
        self.configure(env)
        
        # 启动服务
        nebula_service('start', 'graphd')

    def stop(self, env, upgrade_type=None):
        """
        停止Graphd服务
        """
        import params
        env.set_params(params)
        
        print("Stopping Nebula Graphd...")
        
        # 停止服务
        nebula_service('stop', 'graphd')

    def status(self, env):
        """
        检查Graphd服务状态
        """
        import status_params
        env.set_params(status_params)
        
        # 检查服务状态
        nebula_service('status', 'graphd')

    def restart(self, env):
        """
        重启Graphd服务
        """
        print("Restarting Nebula Graphd...")
        self.stop(env)
        self.start(env)

    def get_log_folder(self):
        """
        获取日志目录
        """
        import params
        return params.nebula_log_dir

    def get_user(self):
        """
        获取运行用户
        """
        import params
        return params.nebula_user

    def get_pid_files(self):
        """
        获取PID文件列表
        """
        import params
        return [params.graphd_pid_file]

if __name__ == "__main__":
    GraphdServer().execute()