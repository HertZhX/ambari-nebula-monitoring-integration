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

# Nebula Ambari Mpack构建脚本

set -e

# 脚本配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"

# 从mpack.json读取版本信息
MPACK_NAME="nebula-ambari-mpack"
MPACK_VERSION="1.0.0"

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

# 清理函数
cleanup() {
    log_info "Cleaning up build directory..."
    if [[ -d "$BUILD_DIR" ]]; then
        rm -rf "$BUILD_DIR"
    fi
}

# 准备构建环境
prepare_build() {
    log_info "Preparing build environment..."
    
    # 创建构建目录
    mkdir -p "$BUILD_DIR"
    mkdir -p "$DIST_DIR"
    
    # 复制源文件到构建目录
    log_info "Copying source files..."
    
    # 复制核心文件
    cp "$PROJECT_ROOT/mpack.json" "$BUILD_DIR/"
    cp -r "$PROJECT_ROOT/common-services" "$BUILD_DIR/"
    
    # 复制文档文件
    if [[ -f "$PROJECT_ROOT/README.md" ]]; then
        cp "$PROJECT_ROOT/README.md" "$BUILD_DIR/"
    fi
    
    # 复制许可证文件
    if [[ -f "$PROJECT_ROOT/LICENSE" ]]; then
        cp "$PROJECT_ROOT/LICENSE" "$BUILD_DIR/"
    fi
}

# 验证构建内容
validate_build() {
    log_info "Validating build content..."
    
    # 检查必需文件
    local required_files=(
        "mpack.json"
        "common-services/NEBULA/1.0.0/metainfo.xml"
        "common-services/NEBULA/1.0.0/metrics.json"
        "common-services/NEBULA/1.0.0/alerts.json"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$BUILD_DIR/$file" ]]; then
            log_error "Required file missing: $file"
            return 1
        fi
    done
    
    # 检查Python脚本语法
    if command -v python >/dev/null 2>&1; then
        log_info "Validating Python script syntax..."
        find "$BUILD_DIR/common-services/NEBULA/1.0.0/package/scripts" -name "*.py" -exec python -m py_compile {} \; 2>/dev/null || {
            log_error "Python syntax validation failed"
            return 1
        }
        log_success "Python syntax validation passed"
    else
        log_warning "Python not available, skipping syntax validation"
    fi
    
    # 检查JSON文件语法
    if command -v python >/dev/null 2>&1; then
        log_info "Validating JSON file syntax..."
        find "$BUILD_DIR" -name "*.json" -exec python -m json.tool {} \; >/dev/null 2>&1 || {
            log_error "JSON syntax validation failed"
            return 1
        }
        log_success "JSON syntax validation passed"
    fi
    
    log_success "Build validation completed successfully"
}

# 设置文件权限
set_permissions() {
    log_info "Setting file permissions..."
    
    # 设置脚本文件为可执行
    find "$BUILD_DIR/common-services/NEBULA/1.0.0/package/scripts" -name "*.py" -exec chmod +x {} \;
    
    # 设置配置文件为只读
    find "$BUILD_DIR/common-services/NEBULA/1.0.0/configuration" -name "*.xml" -exec chmod 644 {} \;
    
    log_success "File permissions set successfully"
}

# 构建Mpack包
build_mpack() {
    log_info "Building Mpack package..."
    
    local mpack_filename="${MPACK_NAME}-${MPACK_VERSION}.tar.gz"
    local mpack_path="$DIST_DIR/$mpack_filename"
    
    # 使用更简单的打包方式，创建一个临时目录并将内容正确组织
    local temp_dir="$(mktemp -d)"
    local mpack_root="$temp_dir/root"
    
    # 创建root目录
    mkdir -p "$mpack_root"
    
    # 复制所有文件到root目录
    cp -r "$BUILD_DIR"/* "$mpack_root/"
    
    # 创建tar包 - 从临时目录的父目录打包，确保有正确的根目录结构
    cd "$temp_dir"
    tar -czf "$mpack_path" "root"
    cd "$PROJECT_ROOT"
    
    # 清理临时目录
    rm -rf "$temp_dir"
    
    if [[ -f "$mpack_path" ]]; then
        log_success "Mpack package created: $mpack_path"
        
        # 显示包信息
        local file_size=$(du -h "$mpack_path" | cut -f1)
        log_info "Package size: $file_size"
        
        # 验证tar包内容
        log_info "Package contents:"
        tar -tzf "$mpack_path" | head -20
        if [[ $(tar -tzf "$mpack_path" | wc -l) -gt 20 ]]; then
            echo "... and $(($(tar -tzf "$mpack_path" | wc -l) - 20)) more files"
        fi
        
        return 0
    else
        log_error "Failed to create Mpack package"
        return 1
    fi
}

# 生成安装说明
generate_install_instructions() {
    local mpack_filename="${MPACK_NAME}-${MPACK_VERSION}.tar.gz"
    local instructions_file="$DIST_DIR/INSTALL.md"
    
    cat > "$instructions_file" << EOF
# Nebula Graph Ambari Mpack安装说明

## 概述

本文档描述如何安装和使用Nebula Graph Ambari Management Pack (Mpack)。

## 前置条件

- Apache Ambari 2.6.0+
- Nebula Graph 2.6.0+
- 集群节点已安装Nebula Graph二进制文件

## 安装步骤

### 1. 上传Mpack包

将${mpack_filename}文件上传到Ambari Server所在的服务器。

### 2. 安装Mpack

在Ambari Server上执行以下命令：

\`\`\`bash
# 安装Mpack
ambari-server install-mpack --mpack=${mpack_filename} --verbose

# 重启Ambari Server
ambari-server restart
\`\`\`

### 3. 验证安装

重启完成后，登录Ambari Web界面，在"Add Service"页面应该能看到"Nebula Graph"服务选项。

### 4. 添加Nebula服务

1. 在Ambari Web界面中，点击"Actions" -> "Add Service"
2. 选择"Nebula Graph"服务
3. 按照向导配置服务参数：
   - 选择安装Graphd、Metad、Storaged组件的节点
   - 配置服务端口、数据目录等参数
   - 设置集群名称和相关配置
4. 完成配置并启动服务

## 配置说明

### 关键配置参数

- **nebula_install_dir**: Nebula Graph安装目录
- **nebula_data_dir**: 数据存储目录
- **nebula_log_dir**: 日志文件目录
- **nebula_cluster_name**: 集群名称

### 组件配置

- **Graphd**: 查询引擎配置，包括端口、线程数、连接限制等
- **Metad**: 元数据服务配置，包括数据路径、心跳间隔、分区设置等
- **Storaged**: 存储引擎配置，包括数据路径、RocksDB参数等

## 监控和告警

安装完成后，Ambari会自动收集以下监控指标：

- 服务健康状态
- 查询性能指标
- 资源使用情况
- 集群连通性

告警规则包括：

- 进程状态检查
- 端口可用性检查
- 性能阈值告警
- 集群健康检查

## 故障排除

### 常见问题

1. **服务启动失败**
   - 检查Nebula二进制文件是否存在
   - 验证配置文件语法
   - 查看日志文件获取详细错误信息

2. **端口冲突**
   - 检查配置的端口是否被其他服务占用
   - 修改端口配置并重启服务

3. **权限问题**
   - 确认nebula用户具有正确的目录权限
   - 检查数据和日志目录的权限设置

### 日志文件位置

- Ambari日志: /var/log/ambari-server/
- Nebula服务日志: /var/log/nebula/
- 组件特定日志: 
  - Graphd: /var/log/nebula/graphd.log
  - Metad: /var/log/nebula/metad.log
  - Storaged: /var/log/nebula/storaged.log

## 卸载

如需卸载Mpack，执行以下命令：

\`\`\`bash
# 卸载Mpack
ambari-server uninstall-mpack --mpack-name=${MPACK_NAME}

# 重启Ambari Server
ambari-server restart
\`\`\`

## 支持

如遇到问题，请查看：

- [Nebula Graph官方文档](https://docs.nebula-graph.io/)
- [Apache Ambari文档](https://ambari.apache.org/)
- 项目GitHub仓库的Issues页面

EOF

    log_success "Installation instructions generated: $instructions_file"
}

# 生成构建信息
generate_build_info() {
    local build_info_file="$DIST_DIR/build-info.txt"
    
    cat > "$build_info_file" << EOF
Nebula Graph Ambari Mpack Build Information
==========================================

Build Date: $(date)
Build Host: $(hostname)
Build User: $(whoami)
Mpack Name: ${MPACK_NAME}
Mpack Version: ${MPACK_VERSION}

Package Contents:
$(tar -tzf "$DIST_DIR/${MPACK_NAME}-${MPACK_VERSION}.tar.gz" | wc -l) files

Git Information:
$(cd "$PROJECT_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo "N/A")

EOF

    log_success "Build information generated: $build_info_file"
}

# 主函数
main() {
    log_info "Starting Nebula Ambari Mpack build process..."
    
    # 检查是否在正确的目录
    if [[ ! -f "$PROJECT_ROOT/mpack.json" ]]; then
        log_error "mpack.json not found. Please run this script from the project root."
        exit 1
    fi
    
    # 清理之前的构建
    cleanup
    
    # 执行构建步骤
    prepare_build
    validate_build
    set_permissions
    build_mpack
    generate_install_instructions
    generate_build_info
    
    # 清理构建目录
    cleanup
    
    log_success "Mpack build completed successfully!"
    log_info "Output files:"
    log_info "- Mpack package: $DIST_DIR/${MPACK_NAME}-${MPACK_VERSION}.tar.gz"
    log_info "- Installation guide: $DIST_DIR/INSTALL.md"
    log_info "- Build information: $DIST_DIR/build-info.txt"
    
    echo ""
    log_info "Next steps:"
    log_info "1. Copy the Mpack package to your Ambari Server"
    log_info "2. Install using: ambari-server install-mpack --mpack=${MPACK_NAME}-${MPACK_VERSION}.tar.gz"
    log_info "3. Restart Ambari Server: ambari-server restart"
}

# 执行主函数
main "$@"