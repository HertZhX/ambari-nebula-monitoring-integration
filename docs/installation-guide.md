# Nebula Graph Ambari集成安装指南

## 概述

本文档详细介绍了如何安装和配置Nebula Graph Ambari Management Pack (Mpack)，使您能够通过Apache Ambari统一管理Nebula Graph集群。

## 目录

1. [前置条件](#前置条件)
2. [环境准备](#环境准备)
3. [安装步骤](#安装步骤)
4. [服务配置](#服务配置)
5. [启动和验证](#启动和验证)
6. [监控和告警](#监控和告警)
7. [故障排除](#故障排除)
8. [升级和维护](#升级和维护)

## 前置条件

### 软件版本要求

| 组件 | 最低版本 | 推荐版本 | 备注 |
|------|----------|----------|------|
| Apache Ambari | 2.6.0 | 2.7.5+ | 管理平台 |
| Nebula Graph | 2.6.0 | 3.0.0+ | 图数据库 |
| Java | 1.8 | 1.8+ | 运行环境 |
| Python | 2.7 | 2.7+ | 脚本支持 |

### 硬件要求

| 组件 | 最小配置 | 推荐配置 | 备注 |
|------|----------|----------|------|
| Ambari Server | 2C4G | 4C8G | 管理节点 |
| Metad节点 | 2C4G | 4C8G | 元数据服务 |
| Graphd节点 | 4C8G | 8C16G | 查询引擎 |
| Storaged节点 | 4C8G,100G磁盘 | 8C16G,500G SSD | 存储引擎 |

### 网络要求

确保以下端口在集群节点间可以正常通信：

| 服务 | 默认端口 | 用途 | 协议 |
|------|----------|------|------|
| Graphd | 9669 | 客户端连接 | TCP |
| Graphd HTTP | 19669 | 管理接口 | HTTP |
| Metad | 9559 | 集群通信 | TCP |
| Metad HTTP | 19559 | 管理接口 | HTTP |
| Storaged | 9779 | 数据传输 | TCP |
| Storaged HTTP | 19779 | 管理接口 | HTTP |

## 环境准备

### 1. 安装Nebula Graph二进制文件

在所有集群节点上安装Nebula Graph：

```bash
# 下载Nebula Graph安装包
wget https://oss-cdn.nebula-graph.io/package/3.0.0/nebula-graph-3.0.0.el7.x86_64.rpm

# 安装
sudo rpm -ivh nebula-graph-3.0.0.el7.x86_64.rpm

# 验证安装
ls -la /usr/local/nebula/bin/
```

### 2. 创建系统用户

在所有节点创建nebula用户：

```bash
# 创建用户和组
sudo groupadd nebula
sudo useradd -g nebula -s /bin/bash nebula

# 设置目录权限
sudo mkdir -p /var/lib/nebula /var/log/nebula /var/run/nebula
sudo chown -R nebula:nebula /var/lib/nebula /var/log/nebula /var/run/nebula
sudo chmod 755 /var/lib/nebula /var/log/nebula /var/run/nebula
```

### 3. 配置系统参数

优化系统参数以支持Nebula Graph：

```bash
# 调整文件描述符限制
echo "nebula soft nofile 130000" | sudo tee -a /etc/security/limits.conf
echo "nebula hard nofile 130000" | sudo tee -a /etc/security/limits.conf

# 调整内存映射限制
echo "vm.max_map_count = 262144" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 安装步骤

### 1. 构建Mpack包

在开发机器上构建Mpack包：

```bash
# 克隆项目
git clone <项目地址>
cd ambari-nebula-monitoring-integration

# 验证Mpack结构
chmod +x tests/validate_mpack.sh
./tests/validate_mpack.sh

# 构建Mpack包
chmod +x tests/build_mpack.sh
./tests/build_mpack.sh
```

构建完成后，在`dist/`目录下会生成`nebula-ambari-mpack-1.0.0.tar.gz`文件。

### 2. 上传和安装Mpack

将Mpack包上传到Ambari Server：

```bash
# 上传到Ambari Server
scp dist/nebula-ambari-mpack-1.0.0.tar.gz ambari-server:/tmp/

# 登录Ambari Server
ssh ambari-server

# 安装Mpack
sudo ambari-server install-mpack --mpack=/tmp/nebula-ambari-mpack-1.0.0.tar.gz --verbose

# 重启Ambari Server
sudo ambari-server restart
```

### 3. 验证安装

等待Ambari Server重启完成后，验证安装：

```bash
# 检查Ambari Server状态
sudo ambari-server status

# 检查Mpack是否安装成功
sudo ambari-server list-mpacks
```

```bash
# 查看可用的堆栈版本
ls -la /var/lib/ambari-server/resources/stacks/

# 如果使用特定堆栈版本，可能需要复制到对应位置
# 例如：HDP 3.1
sudo mkdir -p /var/lib/ambari-server/resources/stacks/HDP/3.1/services/NEBULA
sudo cp -r /var/lib/ambari-server/resources/common-services/NEBULA/1.0.0/* /var/lib/ambari-server/resources/stacks/HDP/3.1/services/NEBULA/
```


登录Ambari Web界面，在"Add Service"页面应该能看到"Nebula Graph"选项。

## 服务配置

### 1. 添加Nebula服务

1. 登录Ambari Web界面（默认端口8080）
2. 点击左侧菜单的"Actions" -> "Add Service"
3. 在服务列表中选择"Nebula Graph"
4. 点击"Next"继续

### 2. 分配组件

根据集群规模分配组件：

#### 小型集群（3-5节点）
- **Metad**: 选择3个节点（奇数个节点，推荐3个）
- **Graphd**: 选择2-3个节点（可以与Metad共存）
- **Storaged**: 选择所有数据节点
- **Console**: 选择1个客户端节点

#### 大型集群（5+节点）
- **Metad**: 选择3-5个专用节点
- **Graphd**: 选择3-5个专用节点
- **Storaged**: 选择所有存储节点
- **Console**: 选择多个客户端节点

### 3. 配置参数

#### 基础配置

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| nebula_cluster_name | production_cluster | 集群名称 |
| nebula_install_dir | /usr/local/nebula | 安装目录 |
| nebula_data_dir | /var/lib/nebula | 数据目录 |
| nebula_log_dir | /var/log/nebula | 日志目录 |

#### Graphd配置

| 参数 | 小型集群 | 大型集群 | 说明 |
|------|----------|----------|------|
| port | 9669 | 9669 | 服务端口 |
| num_netio_threads | 4 | 8 | 网络IO线程 |
| num_worker_threads | 4 | 8 | 工作线程 |
| max_allowed_connections | 1000 | 5000 | 最大连接数 |

#### Metad配置

| 参数 | 小型集群 | 大型集群 | 说明 |
|------|----------|----------|------|
| port | 9559 | 9559 | 服务端口 |
| default_parts_num | 100 | 1024 | 默认分区数 |
| default_replica_factor | 1 | 3 | 副本因子 |

#### Storaged配置

| 参数 | 小型集群 | 大型集群 | 说明 |
|------|----------|----------|------|
| port | 9779 | 9779 | 服务端口 |
| rocksdb_block_cache | 512MB | 4GB | 块缓存大小 |

### 4. 高级配置

#### 性能调优

```yaml
# Graphd性能配置
graphd_num_netio_threads: 16
graphd_num_worker_threads: 32
graphd_session_idle_timeout_secs: 28800

# Storaged性能配置
storaged_rocksdb_wal_sync: true
storaged_enable_auto_compactions: true
storaged_rocksdb_block_cache: 4294967296  # 4GB
```

#### 安全配置

```yaml
# 启用认证
graphd_enable_authorize: true
graphd_auth_type: password

# 日志级别
graphd_log_level: INFO
metad_log_level: INFO
storaged_log_level: INFO
```

## 启动和验证

### 1. 启动服务

按照以下顺序启动服务：

1. **启动Metad服务**
   - 在Ambari界面中选择Nebula服务
   - 选择"Metad"组件
   - 点击"Start"

2. **启动Storaged服务**
   - 等待Metad服务完全启动
   - 启动"Storaged"组件

3. **启动Graphd服务**
   - 等待Storaged服务注册到Metad
   - 启动"Graphd"组件

### 2. 服务验证

#### 检查服务状态

```bash
# 检查进程
ps aux | grep nebula

# 检查端口
netstat -tlnp | grep -E "(9669|9559|9779)"

# 检查日志
tail -f /var/log/nebula/*.log
```

#### 功能验证

使用Nebula Console验证集群功能：

```bash
# 连接到集群
/usr/local/nebula/bin/nebula-console -addr 127.0.0.1 -port 9669 -u root -p nebula

# 查看集群状态
(root@nebula) [(none)]> SHOW HOSTS;
(root@nebula) [(none)]> SHOW SPACES;

# 创建测试空间
(root@nebula) [(none)]> CREATE SPACE test_space(vid_type=INT64);
(root@nebula) [(none)]> USE test_space;

# 创建测试数据
(root@nebula) [test_space]> CREATE TAG person(name string, age int);
(root@nebula) [test_space]> INSERT VERTEX person(name, age) VALUES 1:("Alice", 30);
(root@nebula) [test_space]> FETCH PROP ON person 1;
```

## 监控和告警

### 1. 监控指标

Ambari会自动收集以下监控指标：

#### 服务健康指标
- 进程状态
- 端口可用性
- 服务响应时间

#### 性能指标
- 查询延迟（QPS）
- 内存使用率
- CPU使用率
- 磁盘使用率

#### 集群指标
- 节点健康状态
- 数据分布情况
- 副本同步状态

### 2. 告警配置

系统内置以下告警规则：

#### 关键告警
- **服务不可用**: 进程停止或端口不可访问
- **集群异常**: 超过半数Metad节点不可用
- **无Leader**: Metad集群没有Leader节点

#### 性能告警
- **查询延迟过高**: 平均延迟超过100ms
- **连接数过多**: 活跃连接超过阈值
- **资源使用率高**: CPU/内存使用率超过80%

#### 存储告警
- **磁盘空间不足**: 使用率超过85%
- **数据同步异常**: 副本不一致

### 3. 自定义告警

您可以通过Ambari界面自定义告警规则：

1. 进入"Alerts"页面
2. 点击"Actions" -> "Manage Alert Groups"
3. 创建新的告警组
4. 配置通知方式（邮件、SNMP等）

## 故障排除

### 常见问题

#### 1. 服务启动失败

**问题**: Nebula组件无法启动

**排查步骤**:
```bash
# 检查配置文件
cat /usr/local/nebula/etc/nebula-*.conf

# 检查用户权限
ls -la /var/lib/nebula /var/log/nebula

# 检查端口占用
netstat -tlnp | grep -E "(9669|9559|9779)"

# 查看详细错误日志
tail -f /var/log/nebula/*.log
```

**解决方案**:
- 验证配置文件语法
- 确保nebula用户有正确权限
- 检查端口冲突
- 调整系统资源限制

#### 2. 集群连接问题

**问题**: 组件间无法正常通信

**排查步骤**:
```bash
# 检查网络连通性
telnet <metad_host> 9559
telnet <storaged_host> 9779

# 检查防火墙设置
sudo firewall-cmd --list-ports
sudo iptables -L

# 检查DNS解析
nslookup <hostname>
```

**解决方案**:
- 开放必要端口
- 配置正确的主机名解析
- 检查网络路由配置

#### 3. 性能问题

**问题**: 查询响应缓慢

**排查步骤**:
```bash
# 检查系统资源
top
iotop
free -h

# 检查Nebula指标
curl http://localhost:19669/stats

# 分析慢查询
grep "slow query" /var/log/nebula/graphd.log
```

**解决方案**:
- 增加硬件资源
- 优化查询语句
- 调整缓存配置
- 增加副本数量

### 日志文件位置

| 组件 | 日志文件 | 说明 |
|------|----------|------|
| Ambari Agent | /var/log/ambari-agent/ambari-agent.log | Agent日志 |
| Ambari Server | /var/log/ambari-server/ambari-server.log | Server日志 |
| Nebula Graphd | /var/log/nebula/graphd.log | 查询引擎日志 |
| Nebula Metad | /var/log/nebula/metad.log | 元数据服务日志 |
| Nebula Storaged | /var/log/nebula/storaged.log | 存储引擎日志 |

## 升级和维护

### 1. 服务升级

#### Mpack升级

```bash
# 备份当前配置
ambari-server backup-config

# 升级Mpack
ambari-server upgrade-mpack --mpack=nebula-ambari-mpack-1.1.0.tar.gz

# 重启Ambari Server
ambari-server restart
```

#### Nebula版本升级

1. 在Ambari界面停止所有Nebula服务
2. 在所有节点升级Nebula二进制文件
3. 更新配置文件（如有必要）
4. 重新启动服务

### 2. 配置管理

#### 配置备份

```bash
# 导出配置
curl -u admin:admin "http://ambari-server:8080/api/v1/clusters/cluster1/configurations" > nebula_config_backup.json
```

#### 配置恢复

通过Ambari界面的"Config History"功能可以恢复历史配置。

### 3. 数据备份

#### 备份策略

```bash
# 停止写入操作
# 创建数据快照
cp -r /var/lib/nebula/storage /backup/nebula_$(date +%Y%m%d)

# 备份元数据
cp -r /var/lib/nebula/meta /backup/meta_$(date +%Y%m%d)
```

#### 恢复数据

```bash
# 停止所有服务
# 恢复数据文件
cp -r /backup/nebula_20231201/* /var/lib/nebula/storage/
cp -r /backup/meta_20231201/* /var/lib/nebula/meta/

# 修改权限
chown -R nebula:nebula /var/lib/nebula

# 重启服务
```

## 最佳实践

### 1. 部署建议

- **高可用**: Metad节点建议部署奇数个（3或5个）
- **负载均衡**: Graphd节点建议部署多个以分散查询负载
- **存储规划**: Storaged节点建议使用SSD以提高性能
- **网络隔离**: 建议使用专用网络进行集群内部通信

### 2. 监控建议

- **设置合理的告警阈值**: 避免误报和漏报
- **定期检查集群健康状态**: 建议每日检查
- **监控磁盘空间**: 及时清理日志文件
- **性能基线**: 建立性能基线以便异常检测

### 3. 安全建议

- **启用认证**: 生产环境建议启用用户认证
- **网络安全**: 配置防火墙规则限制访问
- **日志审计**: 启用操作审计日志
- **定期更新**: 及时应用安全补丁

## 技术支持

如果遇到问题，可以通过以下渠道获取支持：

- [Nebula Graph官方文档](https://docs.nebula-graph.io/)
- [Apache Ambari文档](https://ambari.apache.org/)
- [项目GitHub Issues](https://github.com/your-org/ambari-nebula-monitoring-integration/issues)
- 社区论坛和技术群组

---

本指南涵盖了Nebula Graph Ambari集成的完整安装和配置过程。如有疑问，请参考相关技术文档或联系技术支持团队。