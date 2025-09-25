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
from resource_management.core.resources.system import Execute, File, Directory

from nebula_utils import setup_nebula_config
import params

class ConsoleClient(Script):
    """
    Nebula Console客户端控制类
    """

    def install(self, env):
        """
        安装Console组件
        """
        print("Installing Nebula Console...")
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
        配置Console组件
        """
        import params
        env.set_params(params)
        
        print("Configuring Nebula Console...")
        
        # 设置基础配置
        setup_nebula_config()
        
        # 确保目录权限正确
        Directory([params.nebula_log_dir],
                  owner=params.nebula_user,
                  group=params.nebula_group,
                  mode=0755,
                  create_parents=True,
                  recursive_ownership=True)

    def start(self, env, upgrade_type=None):
        """
        启动Console组件 - Console是客户端工具，无需启动服务
        """
        import params
        env.set_params(params)
        
        print("Nebula Console is a client tool, no service to start.")
        
        # 先配置
        self.configure(env)

    def stop(self, env, upgrade_type=None):
        """
        停止Console组件 - Console是客户端工具，无需停止服务
        """
        import params
        env.set_params(params)
        
        print("Nebula Console is a client tool, no service to stop.")

    def status(self, env):
        """
        检查Console组件状态 - Console是客户端工具，始终可用
        """
        import params
        env.set_params(params)
        
        # 检查Console可执行文件是否存在
        if os.path.exists(params.nebula_console_bin):
            print("Nebula Console client is available.")
        else:
            raise Exception("Nebula Console binary not found at " + params.nebula_console_bin)

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

if __name__ == "__main__":
    ConsoleClient().execute()