#!/bin/bash

# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Nebula Ambari集成验证脚本
# 用于验证Mpack包的结构和配置文件的正确性

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MPACK_DIR="$PROJECT_ROOT"
COMMON_SERVICES_DIR="$MPACK_DIR/common-services/NEBULA/1.0.0"

# 颜色输出函数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 验证函数
check_file_exists() {
    local file_path="$1"
    local description="$2"
    
    if [[ -f "$file_path" ]]; then
        log_success "$description: $file_path"
        return 0
    else
        log_error "$description not found: $file_path"
        return 1
    fi
}

check_directory_exists() {
    local dir_path="$1"
    local description="$2"
    
    if [[ -d "$dir_path" ]]; then
        log_success "$description: $dir_path"
        return 0
    else
        log_error "$description not found: $dir_path"
        return 1
    fi
}

validate_xml_file() {
    local xml_file="$1"
    local description="$2"
    
    if command -v xmllint >/dev/null 2>&1; then
        if xmllint --noout "$xml_file" 2>/dev/null; then
            log_success "$description XML syntax is valid"
        else
            log_error "$description XML syntax is invalid"
            return 1
        fi
    else
        log_warning "xmllint not available, skipping XML validation for $description"
    fi
}

validate_json_file() {
    local json_file="$1"
    local description="$2"
    
    if command -v python >/dev/null 2>&1; then
        if python -m json.tool "$json_file" >/dev/null 2>&1; then
            log_success "$description JSON syntax is valid"
        else
            log_error "$description JSON syntax is invalid"
            return 1
        fi
    else
        log_warning "Python not available, skipping JSON validation for $description"
    fi
}

validate_python_syntax() {
    local python_file="$1"
    local description="$2"
    
    if command -v python >/dev/null 2>&1; then
        if python -m py_compile "$python_file" 2>/dev/null; then
            log_success "$description Python syntax is valid"
        else
            log_error "$description Python syntax is invalid"
            return 1
        fi
    else
        log_warning "Python not available, skipping Python syntax validation for $description"
    fi
}

# 主验证函数
main() {
    log_info "Starting Nebula Ambari Mpack validation..."
    
    local errors=0
    
    # 1. 验证基础目录结构
    log_info "=== Validating directory structure ==="
    
    check_directory_exists "$MPACK_DIR" "Mpack root directory" || ((errors++))
    check_directory_exists "$COMMON_SERVICES_DIR" "Common services directory" || ((errors++))
    check_directory_exists "$COMMON_SERVICES_DIR/configuration" "Configuration directory" || ((errors++))
    check_directory_exists "$COMMON_SERVICES_DIR/package" "Package directory" || ((errors++))
    check_directory_exists "$COMMON_SERVICES_DIR/package/scripts" "Scripts directory" || ((errors++))
    check_directory_exists "$COMMON_SERVICES_DIR/package/scripts/alerts" "Alerts directory" || ((errors++))
    
    # 2. 验证核心配置文件
    log_info "=== Validating core configuration files ==="
    
    check_file_exists "$MPACK_DIR/mpack.json" "Mpack configuration file" || ((errors++))
    check_file_exists "$COMMON_SERVICES_DIR/metainfo.xml" "Service metainfo file" || ((errors++))
    check_file_exists "$COMMON_SERVICES_DIR/metrics.json" "Metrics definition file" || ((errors++))
    check_file_exists "$COMMON_SERVICES_DIR/alerts.json" "Alerts definition file" || ((errors++))
    
    # 3. 验证配置模板文件
    log_info "=== Validating configuration template files ==="
    
    local config_files=(
        "nebula-env.xml"
        "nebula-graphd-site.xml"
        "nebula-metad-site.xml"
        "nebula-storaged-site.xml"
        "nebula-log4j.xml"
    )
    
    for config_file in "${config_files[@]}"; do
        check_file_exists "$COMMON_SERVICES_DIR/configuration/$config_file" "Configuration file $config_file" || ((errors++))
    done
    
    # 4. 验证脚本文件
    log_info "=== Validating script files ==="
    
    local script_files=(
        "params.py"
        "status_params.py"
        "nebula_utils.py"
        "graphd.py"
        "metad.py"
        "storaged.py"
        "console.py"
        "service_check.py"
    )
    
    for script_file in "${script_files[@]}"; do
        check_file_exists "$COMMON_SERVICES_DIR/package/scripts/$script_file" "Script file $script_file" || ((errors++))
    done
    
    # 5. 验证告警脚本文件
    log_info "=== Validating alert script files ==="
    
    local alert_files=(
        "alert_graphd_process.py"
        "alert_metad_process.py"
        "alert_storaged_process.py"
        "alert_cluster_health.py"
        "alert_metad_leader.py"
    )
    
    for alert_file in "${alert_files[@]}"; do
        check_file_exists "$COMMON_SERVICES_DIR/package/scripts/alerts/$alert_file" "Alert script $alert_file" || ((errors++))
    done
    
    # 6. 验证文件语法
    log_info "=== Validating file syntax ==="
    
    # 验证JSON文件
    validate_json_file "$MPACK_DIR/mpack.json" "Mpack configuration"
    validate_json_file "$COMMON_SERVICES_DIR/metrics.json" "Metrics definition"
    validate_json_file "$COMMON_SERVICES_DIR/alerts.json" "Alerts definition"
    
    # 验证XML文件
    validate_xml_file "$COMMON_SERVICES_DIR/metainfo.xml" "Service metainfo"
    for config_file in "${config_files[@]}"; do
        if [[ -f "$COMMON_SERVICES_DIR/configuration/$config_file" ]]; then
            validate_xml_file "$COMMON_SERVICES_DIR/configuration/$config_file" "Configuration $config_file"
        fi
    done
    
    # 验证Python文件
    for script_file in "${script_files[@]}"; do
        if [[ -f "$COMMON_SERVICES_DIR/package/scripts/$script_file" ]]; then
            validate_python_syntax "$COMMON_SERVICES_DIR/package/scripts/$script_file" "Script $script_file"
        fi
    done
    
    for alert_file in "${alert_files[@]}"; do
        if [[ -f "$COMMON_SERVICES_DIR/package/scripts/alerts/$alert_file" ]]; then
            validate_python_syntax "$COMMON_SERVICES_DIR/package/scripts/alerts/$alert_file" "Alert script $alert_file"
        fi
    done
    
    # 7. 验证文件权限
    log_info "=== Validating file permissions ==="
    
    # Python脚本应该是可执行的
    for script_file in "${script_files[@]}"; do
        local script_path="$COMMON_SERVICES_DIR/package/scripts/$script_file"
        if [[ -f "$script_path" ]]; then
            if [[ -x "$script_path" ]]; then
                log_success "Script $script_file is executable"
            else
                log_warning "Script $script_file is not executable (this may be expected)"
            fi
        fi
    done
    
    # 8. 检查配置文件中的关键字段
    log_info "=== Validating configuration content ==="
    
    # 检查metainfo.xml中的关键元素
    if [[ -f "$COMMON_SERVICES_DIR/metainfo.xml" ]]; then
        if grep -q "NEBULA_GRAPHD" "$COMMON_SERVICES_DIR/metainfo.xml"; then
            log_success "Graphd component found in metainfo.xml"
        else
            log_error "Graphd component not found in metainfo.xml"
            ((errors++))
        fi
        
        if grep -q "NEBULA_METAD" "$COMMON_SERVICES_DIR/metainfo.xml"; then
            log_success "Metad component found in metainfo.xml"
        else
            log_error "Metad component not found in metainfo.xml"
            ((errors++))
        fi
        
        if grep -q "NEBULA_STORAGED" "$COMMON_SERVICES_DIR/metainfo.xml"; then
            log_success "Storaged component found in metainfo.xml"
        else
            log_error "Storaged component not found in metainfo.xml"
            ((errors++))
        fi
    fi
    
    # 9. 输出验证结果
    log_info "=== Validation Summary ==="
    
    if [[ $errors -eq 0 ]]; then
        log_success "All validations passed! The Mpack structure appears to be correct."
        echo ""
        log_info "Next steps:"
        log_info "1. Build the Mpack: tar -czf nebula-ambari-mpack-1.0.0.tar.gz -C $PROJECT_ROOT ."
        log_info "2. Install on Ambari Server: ambari-server install-mpack --mpack=nebula-ambari-mpack-1.0.0.tar.gz"
        log_info "3. Restart Ambari Server: ambari-server restart"
        return 0
    else
        log_error "Validation failed with $errors error(s). Please fix the issues before proceeding."
        return 1
    fi
}

# 执行主函数
main "$@"