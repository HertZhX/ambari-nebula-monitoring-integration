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

from resource_management.libraries.functions import format
from resource_management.libraries.script.script import Script

# Get configuration
config = Script.get_config()

# Nebula installation directory
nebula_install_dir = config['configurations']['nebula-env']['nebula_install_dir']

# PID directory
nebula_pid_dir = config['configurations']['nebula-env']['nebula_pid_dir']

# Nebula user
nebula_user = config['configurations']['nebula-env']['nebula_user']

# PID files for each component
graphd_pid_file = format("{nebula_pid_dir}/nebula-graphd.pid")
metad_pid_file = format("{nebula_pid_dir}/nebula-metad.pid")
storaged_pid_file = format("{nebula_pid_dir}/nebula-storaged.pid")

# Log directory
nebula_log_dir = config['configurations']['nebula-env']['nebula_log_dir']

# Binary executables
nebula_graphd_bin = format("{nebula_install_dir}/bin/nebula-graphd")
nebula_metad_bin = format("{nebula_install_dir}/bin/nebula-metad")
nebula_storaged_bin = format("{nebula_install_dir}/bin/nebula-storaged")

# Configuration files
graphd_conf_file = format("{nebula_install_dir}/etc/nebula-graphd.conf")
metad_conf_file = format("{nebula_install_dir}/etc/nebula-metad.conf")
storaged_conf_file = format("{nebula_install_dir}/etc/nebula-storaged.conf")

# Service ports for status checks
graphd_port = config['configurations']['nebula-graphd-site']['port']
metad_port = config['configurations']['nebula-metad-site']['port']
storaged_port = config['configurations']['nebula-storaged-site']['port']

# HTTP management ports
graphd_http_port = config['configurations']['nebula-graphd-site']['ws_http_port']
metad_http_port = config['configurations']['nebula-metad-site']['ws_http_port']
storaged_http_port = config['configurations']['nebula-storaged-site']['ws_http_port']