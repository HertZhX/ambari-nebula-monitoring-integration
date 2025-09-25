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

from nebula_utils import nebula_service, setup_nebula_config, generate_metad_config
import params

class MetadServer(Script):
    """
    Nebula Metad服务控制类
    """

    def install(self, env):
        """
        安装Metad组件
        """
        print("Installing Nebula Metad...")
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
        配置Metad组件
        """
        import params
        env.set_params(params)
        
        print("Configuring Nebula Metad...")
        
        # 设置基础配置
        setup_nebula_config()
        
        # 生成Metad特定配置
        generate_metad_config()
        
        # 创建Metad数据目录
        Directory(params.metad_data_path,
                  owner=params.nebula_user,
                  group=params.nebula_group,
                  mode=0755,
                  create_parents=True,
                  recursive_ownership=True)
        
        # 确保数据和日志目录权限正确
        Directory([params.nebula_data_dir, params.nebula_log_dir, params.nebula_pid_dir],
                  owner=params.nebula_user,
                  group=params.nebula_group,
                  mode=0755,
                  create_parents=True,
                  recursive_ownership=True)

    def start(self, env, upgrade_type=None):
        """
        启动Metad服务
        """
        import params
        env.set_params(params)
        
        print("Starting Nebula Metad...")
        
        # 先配置
        self.configure(env)
        
        # 启动服务
        nebula_service('start', 'metad')

    def stop(self, env, upgrade_type=None):
        """
        停止Metad服务
        """
        import params
        env.set_params(params)
        
        print("Stopping Nebula Metad...")
        
        # 停止服务
        nebula_service('stop', 'metad')

    def status(self, env):
        """
        检查Metad服务状态
        """
        import status_params
        env.set_params(status_params)
        
        # 检查服务状态
        nebula_service('status', 'metad')

    def restart(self, env):
        """
        重启Metad服务
        """
        print("Restarting Nebula Metad...")
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
        return [params.metad_pid_file]

if __name__ == "__main__":
    MetadServer().execute()