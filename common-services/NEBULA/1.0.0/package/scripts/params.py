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

from resource_management import *
from resource_management.libraries.functions import conf_select
from resource_management.libraries.functions import stack_select
from resource_management.libraries.functions import format
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.get_kinit_path import get_kinit_path
from resource_management.libraries.functions.get_not_managed_resources import get_not_managed_resources
from resource_management.libraries.script.script import Script
import status_params

# Server configurations
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

# Nebula installation directory
nebula_install_dir = config['configurations']['nebula-env']['nebula_install_dir']
nebula_data_dir = config['configurations']['nebula-env']['nebula_data_dir']
nebula_log_dir = config['configurations']['nebula-env']['nebula_log_dir']
nebula_pid_dir = config['configurations']['nebula-env']['nebula_pid_dir']

# Nebula user and group
nebula_user = config['configurations']['nebula-env']['nebula_user']
nebula_group = config['configurations']['nebula-env']['nebula_group']

# Cluster name
nebula_cluster_name = config['configurations']['nebula-env']['nebula_cluster_name']

# Java home
java64_home = config['hostLevelParams']['java_home']

# Hostname and security
hostname = config['hostname']
security_enabled = config['configurations']['cluster-env']['security_enabled']

# Common configurations that will be used by all components
if 'nebula-env' in config['configurations']:
    nebula_env_sh_template = config['configurations']['nebula-env']['content']

# Get the list of metad hosts
metad_hosts = default("/clusterHostInfo/nebula_metad_hosts", [])
metad_port = str(config['configurations']['nebula-metad-site']['port'])

# Build metad addresses string
if metad_hosts:
    metad_hosts_with_port = ','.join([host + ':' + metad_port for host in metad_hosts])
else:
    metad_hosts_with_port = hostname + ':' + metad_port

# Graphd specific configurations
if 'nebula-graphd-site' in config['configurations']:
    graphd_port = config['configurations']['nebula-graphd-site']['port']
    graphd_ws_http_port = config['configurations']['nebula-graphd-site']['ws_http_port']
    graphd_ws_h2_port = config['configurations']['nebula-graphd-site']['ws_h2_port']
    graphd_num_netio_threads = config['configurations']['nebula-graphd-site']['num_netio_threads']
    graphd_num_accept_threads = config['configurations']['nebula-graphd-site']['num_accept_threads']
    graphd_num_worker_threads = config['configurations']['nebula-graphd-site']['num_worker_threads']
    graphd_client_idle_timeout_secs = config['configurations']['nebula-graphd-site']['client_idle_timeout_secs']
    graphd_session_idle_timeout_secs = config['configurations']['nebula-graphd-site']['session_idle_timeout_secs']
    graphd_enable_authorize = config['configurations']['nebula-graphd-site']['enable_authorize']
    graphd_auth_type = config['configurations']['nebula-graphd-site']['auth_type']
    graphd_log_level = config['configurations']['nebula-graphd-site']['log_level']
    graphd_max_allowed_connections = config['configurations']['nebula-graphd-site']['max_allowed_connections']

# Metad specific configurations
if 'nebula-metad-site' in config['configurations']:
    metad_data_path = config['configurations']['nebula-metad-site']['data_path']
    metad_heartbeat_interval_secs = config['configurations']['nebula-metad-site']['heartbeat_interval_secs']
    metad_num_io_threads = config['configurations']['nebula-metad-site']['num_io_threads']
    metad_num_worker_threads = config['configurations']['nebula-metad-site']['num_worker_threads']
    metad_log_level = config['configurations']['nebula-metad-site']['log_level']
    metad_part_man_type = config['configurations']['nebula-metad-site']['part_man_type']
    metad_default_parts_num = config['configurations']['nebula-metad-site']['default_parts_num']
    metad_default_replica_factor = config['configurations']['nebula-metad-site']['default_replica_factor']
    metad_agent_heartbeat_interval_secs = config['configurations']['nebula-metad-site']['agent_heartbeat_interval_secs']
    metad_cluster_id = config['configurations']['nebula-metad-site']['cluster_id']
    metad_ws_meta_http_port = config['configurations']['nebula-metad-site']['ws_meta_http_port']

# Storaged specific configurations
if 'nebula-storaged-site' in config['configurations']:
    storaged_port = config['configurations']['nebula-storaged-site']['port']
    storaged_ws_http_port = config['configurations']['nebula-storaged-site']['ws_http_port']
    storaged_ws_h2_port = config['configurations']['nebula-storaged-site']['ws_h2_port']
    storaged_data_path = config['configurations']['nebula-storaged-site']['data_path']
    storaged_heartbeat_interval_secs = config['configurations']['nebula-storaged-site']['heartbeat_interval_secs']
    storaged_num_io_threads = config['configurations']['nebula-storaged-site']['num_io_threads']
    storaged_num_worker_threads = config['configurations']['nebula-storaged-site']['num_worker_threads']
    storaged_log_level = config['configurations']['nebula-storaged-site']['log_level']
    storaged_rocksdb_wal_sync = config['configurations']['nebula-storaged-site']['rocksdb_wal_sync']
    storaged_rocksdb_column_family_options = config['configurations']['nebula-storaged-site']['rocksdb_column_family_options']
    storaged_rocksdb_db_options = config['configurations']['nebula-storaged-site']['rocksdb_rocksdb_db_options']
    storaged_rocksdb_block_cache = config['configurations']['nebula-storaged-site']['rocksdb_block_cache']
    storaged_enable_auto_compactions = config['configurations']['nebula-storaged-site']['enable_auto_compactions']
    storaged_enable_partitioning_on_compaction = config['configurations']['nebula-storaged-site']['enable_partitioning_on_compaction']
    storaged_custom_filter_interval_secs = config['configurations']['nebula-storaged-site']['custom_filter_interval_secs']

# Log4j configurations
if 'nebula-log4j' in config['configurations']:
    log4j_props = config['configurations']['nebula-log4j']['content']

# File and directory paths
nebula_graphd_conf_file = nebula_install_dir + '/etc/nebula-graphd.conf'
nebula_metad_conf_file = nebula_install_dir + '/etc/nebula-metad.conf'
nebula_storaged_conf_file = nebula_install_dir + '/etc/nebula-storaged.conf'
nebula_env_sh_file = nebula_install_dir + '/etc/nebula-env.sh'
nebula_log4j_file = nebula_install_dir + '/etc/log4j.properties'

# PID files
graphd_pid_file = nebula_pid_dir + '/nebula-graphd.pid'
metad_pid_file = nebula_pid_dir + '/nebula-metad.pid'
storaged_pid_file = nebula_pid_dir + '/nebula-storaged.pid'

# Binary executables
nebula_graphd_bin = nebula_install_dir + '/bin/nebula-graphd'
nebula_metad_bin = nebula_install_dir + '/bin/nebula-metad'
nebula_storaged_bin = nebula_install_dir + '/bin/nebula-storaged'
nebula_console_bin = nebula_install_dir + '/bin/nebula-console'

# Import all the properties
import functools
_all_configurations = [config['configurations'][_config] for _config in config['configurations']]
all_configurations = functools.reduce(lambda a, b: dict(a.items() + b.items()), _all_configurations)

# Verify required directories exist
config_dir = nebula_install_dir + '/etc'
bin_dir = nebula_install_dir + '/bin'
lib_dir = nebula_install_dir + '/lib'