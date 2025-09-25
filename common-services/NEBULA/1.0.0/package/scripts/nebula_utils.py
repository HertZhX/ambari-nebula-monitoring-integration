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
import time
import socket
from resource_management import *
from resource_management.libraries.functions import format
from resource_management.libraries.functions.check_process_status import check_process_status
from resource_management.core.exceptions import ComponentIsNotRunning
import params

def nebula_service(action, component_name):
    """
    通用的Nebula服务管理函数
    
    Args:
        action: 操作类型 ('start', 'stop', 'status')
        component_name: 组件名称 ('graphd', 'metad', 'storaged')
    """
    if component_name == 'graphd':
        pid_file = params.graphd_pid_file
        binary_path = params.nebula_graphd_bin
        conf_file = params.nebula_graphd_conf_file
        service_port = params.graphd_port
    elif component_name == 'metad':
        pid_file = params.metad_pid_file
        binary_path = params.nebula_metad_bin
        conf_file = params.metad_conf_file
        service_port = params.metad_port
    elif component_name == 'storaged':
        pid_file = params.storaged_pid_file
        binary_path = params.nebula_storaged_bin
        conf_file = params.storaged_conf_file
        service_port = params.storaged_port
    else:
        raise Exception("Unknown Nebula component: " + component_name)

    if action == 'start':
        # 确保配置文件存在
        if not os.path.exists(conf_file):
            raise Exception(format("Configuration file {conf_file} does not exist"))
        
        # 确保二进制文件存在
        if not os.path.exists(binary_path):
            raise Exception(format("Binary file {binary_path} does not exist"))
        
        # 启动服务
        cmd = format("{binary_path} --flagfile={conf_file} --daemonize --pid_file={pid_file}")
        
        Execute(cmd,
                user=params.nebula_user,
                logoutput=True,
                path=[params.bin_dir],
                environment={'JAVA_HOME': params.java64_home})
        
        # 等待服务启动
        wait_for_service_start(component_name, service_port, pid_file)

    elif action == 'stop':
        # 停止服务
        if os.path.exists(pid_file):
            Execute(format("kill -TERM `cat {pid_file}`"),
                    user=params.nebula_user,
                    ignore_failures=True)
            
            # 等待进程优雅关闭
            time.sleep(10)
            
            # 如果进程仍然存在，强制终止
            if os.path.exists(pid_file):
                Execute(format("kill -KILL `cat {pid_file}`"),
                        user=params.nebula_user,
                        ignore_failures=True)
                
                # 清理PID文件
                Execute(format("rm -f {pid_file}"),
                        user=params.nebula_user,
                        ignore_failures=True)

    elif action == 'status':
        # 检查服务状态
        check_process_status(pid_file)
        
        # 额外检查端口是否监听
        if not is_port_open(service_port):
            raise ComponentIsNotRunning(format("{component_name} process is running but port {service_port} is not open"))

def wait_for_service_start(component_name, port, pid_file, timeout=60):
    """
    等待服务启动完成
    
    Args:
        component_name: 组件名称
        port: 服务端口
        pid_file: PID文件路径
        timeout: 超时时间（秒）
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if os.path.exists(pid_file):
            if is_port_open(port):
                Logger.info(format("{component_name} service started successfully"))
                return
        time.sleep(2)
    
    raise Exception(format("Timeout waiting for {component_name} service to start"))

def is_port_open(port, host='localhost'):
    """
    检查端口是否打开
    
    Args:
        port: 端口号
        host: 主机地址，默认localhost
        
    Returns:
        bool: 端口是否打开
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, int(port)))
        sock.close()
        return result == 0
    except Exception:
        return False

def setup_nebula_config():
    """
    配置Nebula服务的通用设置
    """
    # 创建必要的目录
    Directory([params.nebula_data_dir, params.nebula_log_dir, params.nebula_pid_dir],
              owner=params.nebula_user,
              group=params.nebula_group,
              mode=0755,
              create_parents=True)
    
    # 创建配置目录
    Directory(params.config_dir,
              owner=params.nebula_user,
              group=params.nebula_group,
              mode=0755,
              create_parents=True)
    
    # 生成环境变量脚本
    File(params.nebula_env_sh_file,
         content=InlineTemplate(params.nebula_env_sh_template),
         owner=params.nebula_user,
         group=params.nebula_group,
         mode=0755)
    
    # 生成log4j配置
    File(params.nebula_log4j_file,
         content=InlineTemplate(params.log4j_props),
         owner=params.nebula_user,
         group=params.nebula_group,
         mode=0644)

def generate_graphd_config():
    """
    生成Graphd配置文件
    """
    graphd_config_content = format("""
# Nebula Graphd Configuration
# Generated by Ambari on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Network configuration
--port={graphd_port}
--ws_http_port={graphd_ws_http_port}
--ws_h2_port={graphd_ws_h2_port}

# Thread configuration
--num_netio_threads={graphd_num_netio_threads}
--num_accept_threads={graphd_num_accept_threads}
--num_worker_threads={graphd_num_worker_threads}

# Timeout configuration
--client_idle_timeout_secs={graphd_client_idle_timeout_secs}
--session_idle_timeout_secs={graphd_session_idle_timeout_secs}

# Authentication configuration
--enable_authorize={graphd_enable_authorize}
--auth_type={graphd_auth_type}

# Meta server configuration
--meta_server_addrs={metad_hosts_with_port}

# Logging configuration
--log_level={graphd_log_level}
--log_dir={nebula_log_dir}

# Connection limits
--max_allowed_connections={graphd_max_allowed_connections}

# Local configuration
--local_config={graphd_local_config}
""")
    
    File(params.nebula_graphd_conf_file,
         content=graphd_config_content,
         owner=params.nebula_user,
         group=params.nebula_group,
         mode=0644)

def generate_metad_config():
    """
    生成Metad配置文件
    """
    metad_config_content = format("""
# Nebula Metad Configuration
# Generated by Ambari on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Network configuration
--port={metad_port}
--ws_http_port={metad_ws_http_port}
--ws_meta_http_port={metad_ws_meta_http_port}

# Data configuration
--data_path={metad_data_path}

# Thread configuration
--num_io_threads={metad_num_io_threads}
--num_worker_threads={metad_num_worker_threads}

# Heartbeat configuration
--heartbeat_interval_secs={metad_heartbeat_interval_secs}
--agent_heartbeat_interval_secs={metad_agent_heartbeat_interval_secs}

# Partition management
--part_man_type={metad_part_man_type}
--default_parts_num={metad_default_parts_num}
--default_replica_factor={metad_default_replica_factor}

# Cluster configuration
--cluster_id={metad_cluster_id}

# Logging configuration
--log_level={metad_log_level}
--log_dir={nebula_log_dir}

# Local configuration
--local_config=true
""")
    
    File(params.nebula_metad_conf_file,
         content=metad_config_content,
         owner=params.nebula_user,
         group=params.nebula_group,
         mode=0644)

def generate_storaged_config():
    """
    生成Storaged配置文件
    """
    storaged_config_content = format("""
# Nebula Storaged Configuration
# Generated by Ambari on {time.strftime('%Y-%m-%d %H:%M:%S')}

# Network configuration
--port={storaged_port}
--ws_http_port={storaged_ws_http_port}
--ws_h2_port={storaged_ws_h2_port}

# Data configuration
--data_path={storaged_data_path}

# Meta server configuration
--meta_server_addrs={metad_hosts_with_port}

# Thread configuration
--num_io_threads={storaged_num_io_threads}
--num_worker_threads={storaged_num_worker_threads}

# Heartbeat configuration
--heartbeat_interval_secs={storaged_heartbeat_interval_secs}

# RocksDB configuration
--rocksdb_wal_sync={storaged_rocksdb_wal_sync}
--rocksdb_column_family_options={storaged_rocksdb_column_family_options}
--rocksdb_db_options={storaged_rocksdb_db_options}
--rocksdb_block_cache={storaged_rocksdb_block_cache}

# Compaction configuration
--enable_auto_compactions={storaged_enable_auto_compactions}
--enable_partitioning_on_compaction={storaged_enable_partitioning_on_compaction}

# Filter configuration
--custom_filter_interval_secs={storaged_custom_filter_interval_secs}

# Logging configuration
--log_level={storaged_log_level}
--log_dir={nebula_log_dir}

# Local configuration
--local_config=true
""")
    
    File(params.nebula_storaged_conf_file,
         content=storaged_config_content,
         owner=params.nebula_user,
         group=params.nebula_group,
         mode=0644)