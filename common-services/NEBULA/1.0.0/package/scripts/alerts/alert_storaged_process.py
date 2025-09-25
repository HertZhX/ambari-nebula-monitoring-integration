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
from resource_management.libraries.script.script import Script
from resource_management.libraries.functions.format import format
from resource_management.core.logger import Logger

RESULT_CODE_OK = 'OK'
RESULT_CODE_CRITICAL = 'CRITICAL'
RESULT_CODE_UNKNOWN = 'UNKNOWN'

STORAGED_PID_FILE_KEY = '{{nebula-env/nebula_pid_dir}}/nebula-storaged.pid'
STORAGED_PORT_KEY = '{{nebula-storaged-site/port}}'

def get_tokens():
    """
    返回用于解析配置的tokens
    """
    return (STORAGED_PID_FILE_KEY, STORAGED_PORT_KEY)

def execute(configurations={}, parameters=[], host_name=None):
    """
    返回包含告警结果的元组 (result_code, [result_label])
    """
    result_code = None
    label = None
    
    if configurations is None:
        return (RESULT_CODE_UNKNOWN, ['There were no configurations supplied to the script.'])
    
    pid_file = None
    port = None
    
    if STORAGED_PID_FILE_KEY in configurations:
        pid_file = configurations[STORAGED_PID_FILE_KEY]
    
    if STORAGED_PORT_KEY in configurations:
        port = int(configurations[STORAGED_PORT_KEY])
    
    if pid_file is None:
        return (RESULT_CODE_UNKNOWN, ['The Nebula Storaged PID file could not be determined.'])
    
    if port is None:
        return (RESULT_CODE_UNKNOWN, ['The Nebula Storaged port could not be determined.'])
    
    # 检查进程是否运行
    process_running = is_process_running(pid_file)
    
    if not process_running:
        result_code = RESULT_CODE_CRITICAL
        label = 'Nebula Storaged process is not running'
    else:
        # 检查端口是否监听
        port_accessible = is_port_accessible(port)
        
        if port_accessible:
            result_code = RESULT_CODE_OK
            label = 'Nebula Storaged process is running and port {0} is accessible'.format(port)
        else:
            result_code = RESULT_CODE_CRITICAL
            label = 'Nebula Storaged process is running but port {0} is not accessible'.format(port)
    
    return (result_code, [label])

def is_process_running(pid_file):
    """
    检查进程是否运行
    """
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

def is_port_accessible(port, host='localhost', timeout=3):
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