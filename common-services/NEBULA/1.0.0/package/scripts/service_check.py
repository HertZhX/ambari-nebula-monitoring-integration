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
from resource_management import *
from resource_management.libraries.script.script import Script
from resource_management.core.resources.system import Execute

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
        
        # 简单检查：确保必要的目录存在
        self.check_directories()
        
        # 检查配置文件是否存在
        self.check_config_files()
        
        print("Nebula service check completed successfully!")

    def check_directories(self):
        """
        检查必要的目录是否存在
        """
        import params
        
        print("Checking Nebula directories...")
        
        directories = [
            params.nebula_data_dir,
            params.nebula_log_dir,
            params.nebula_pid_dir,
            params.config_dir
        ]
        
        for directory in directories:
            if not os.path.exists(directory):
                raise Exception("Required directory does not exist: %s" % directory)
        
        print("All required directories exist")

    def check_config_files(self):
        """
        检查配置文件是否存在
        """
        import params
        
        print("Checking Nebula configuration files...")
        
        config_files = [
            params.nebula_graphd_conf_file,
            params.nebula_metad_conf_file,
            params.nebula_storaged_conf_file
        ]
        
        for config_file in config_files:
            if not os.path.exists(config_file):
                print("Warning: Configuration file does not exist: %s" % config_file)
        
        print("Configuration file check completed")

if __name__ == "__main__":
    NebulaServiceCheck().execute()