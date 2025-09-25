# Nebula Graph Ambari集成API参考文档

## 概述

本文档描述了Nebula Graph Ambari集成中提供的各种API接口，包括监控指标API、管理接口以及扩展接口。

## 目录

1. [监控指标API](#监控指标api)
2. [管理接口API](#管理接口api)
3. [告警接口API](#告警接口api)
4. [配置管理API](#配置管理api)
5. [服务控制API](#服务控制api)
6. [扩展开发API](#扩展开发api)

## 监控指标API

### Graphd监控指标

#### 获取服务状态
```http
GET http://{graphd_host}:{graphd_http_port}/status
```

**响应示例**:
```json
{
  "status": "running",
  "version": "3.0.0",
  "uptime": 3600,
  "git_info_sha": "abc123"
}
```

#### 获取性能指标
```http
GET http://{graphd_host}:{graphd_http_port}/stats
```

**响应示例**:
```json
{
  "num_active_sessions": 25,
  "query_latency_us": 1500,
  "qps": 100,
  "memory_usage_bytes": 2147483648,
  "cpu_usage_percent": 45.5,
  "slow_query_count": 2,
  "error_query_count": 0
}
```

#### 获取连接信息
```http
GET http://{graphd_host}:{graphd_http_port}/connections
```

**响应示例**:
```json
{
  "total_connections": 50,
  "active_connections": 25,
  "idle_connections": 25,
  "connection_pool_size": 100
}
```

### Metad监控指标

#### 获取集群状态
```http
GET http://{metad_host}:{metad_http_port}/status
```

**响应示例**:
```json
{
  "status": "running",
  "role": "leader",
  "cluster_id": 1,
  "peers": [
    "192.168.1.1:9559",
    "192.168.1.2:9559",
    "192.168.1.3:9559"
  ]
}
```

#### 获取元数据统计
```http
GET http://{metad_host}:{metad_http_port}/stats
```

**响应示例**:
```json
{
  "num_spaces": 5,
  "num_tags": 20,
  "num_edges": 15,
  "num_hosts": 10,
  "heartbeat_latency_us": 2000,
  "is_leader": true,
  "memory_usage_bytes": 1073741824,
  "cpu_usage_percent": 30.2
}
```

#### 获取Leader信息
```http
GET http://{metad_host}:{metad_http_port}/leader
```

**响应示例**:
```json
{
  "leader_addr": "192.168.1.1:9559",
  "is_leader": true,
  "term": 100
}
```

### Storaged监控指标

#### 获取存储状态
```http
GET http://{storaged_host}:{storaged_http_port}/status
```

**响应示例**:
```json
{
  "status": "running",
  "data_path": "/var/lib/nebula/storage",
  "disk_usage_bytes": 10737418240,
  "disk_total_bytes": 107374182400
}
```

#### 获取存储统计
```http
GET http://{storaged_host}:{storaged_http_port}/stats
```

**响应示例**:
```json
{
  "num_vertices": 1000000,
  "num_edges_stored": 5000000,
  "get_latency_us": 500,
  "put_latency_us": 800,
  "memory_usage_bytes": 4294967296,
  "cpu_usage_percent": 60.8,
  "rocksdb_block_cache_hit_rate": 0.95,
  "rocksdb_compaction_pending": 2
}
```

#### 获取RocksDB指标
```http
GET http://{storaged_host}:{storaged_http_port}/rocksdb_stats
```

**响应示例**:
```json
{
  "block_cache_usage": 1073741824,
  "block_cache_capacity": 4294967296,
  "compaction_pending": 2,
  "memtable_flush_pending": 0,
  "num_immutable_mem_table": 0,
  "num_running_compactions": 1,
  "num_running_flushes": 0
}
```

## 管理接口API

### 配置管理

#### 获取配置
```http
GET http://{host}:{http_port}/flags
```

**响应示例**:
```json
{
  "port": 9669,
  "ws_http_port": 19669,
  "num_netio_threads": 4,
  "num_worker_threads": 4,
  "log_level": "INFO"
}
```

#### 动态更新配置
```http
PUT http://{host}:{http_port}/flags
Content-Type: application/json

{
  "log_level": "DEBUG",
  "num_worker_threads": 8
}
```

### 服务控制

#### 健康检查
```http
GET http://{host}:{http_port}/health
```

**响应示例**:
```json
{
  "healthy": true,
  "components": {
    "process": "healthy",
    "disk": "healthy",
    "memory": "healthy",
    "network": "healthy"
  }
}
```

#### 版本信息
```http
GET http://{host}:{http_port}/version
```

**响应示例**:
```json
{
  "version": "3.0.0",
  "git_sha": "abc123def456",
  "build_time": "2023-12-01T10:30:00Z",
  "go_version": "go1.18.5"
}
```

## 告警接口API

### 告警规则管理

#### 获取告警规则
```http
GET http://ambari-server:8080/api/v1/clusters/{cluster_name}/alert_definitions
```

#### 创建自定义告警
```http
POST http://ambari-server:8080/api/v1/clusters/{cluster_name}/alert_definitions
Content-Type: application/json

{
  "AlertDefinition": {
    "name": "custom_nebula_alert",
    "service_name": "NEBULA",
    "component_name": "NEBULA_GRAPHD",
    "enabled": true,
    "scope": "ANY",
    "source": {
      "type": "METRIC",
      "reporting": {
        "ok": {"text": "Normal"},
        "warning": {"text": "Warning", "value": 80},
        "critical": {"text": "Critical", "value": 90}
      }
    }
  }
}
```

### 告警历史

#### 获取告警历史
```http
GET http://ambari-server:8080/api/v1/clusters/{cluster_name}/alerts?fields=*
```

#### 获取特定服务告警
```http
GET http://ambari-server:8080/api/v1/clusters/{cluster_name}/alerts?Alert/service_name=NEBULA
```

## 配置管理API

### 服务配置

#### 获取服务配置
```http
GET http://ambari-server:8080/api/v1/clusters/{cluster_name}/configurations?type=nebula-graphd-site
```

#### 更新服务配置
```http
PUT http://ambari-server:8080/api/v1/clusters/{cluster_name}/configurations
Content-Type: application/json

{
  "Clusters": {
    "desired_config": {
      "type": "nebula-graphd-site",
      "tag": "version_$(date +%s)",
      "properties": {
        "port": "9669",
        "num_worker_threads": "8"
      }
    }
  }
}
```

### 配置版本管理

#### 获取配置历史
```http
GET http://ambari-server:8080/api/v1/clusters/{cluster_name}/configurations?type=nebula-graphd-site&fields=*
```

#### 回滚配置
```http
PUT http://ambari-server:8080/api/v1/clusters/{cluster_name}/configurations
Content-Type: application/json

{
  "Clusters": {
    "desired_config": {
      "type": "nebula-graphd-site",
      "tag": "previous_version_tag"
    }
  }
}
```

## 服务控制API

### 服务生命周期

#### 启动服务
```http
POST http://ambari-server:8080/api/v1/clusters/{cluster_name}/services/NEBULA
Content-Type: application/json

{
  "RequestInfo": {
    "context": "Start Nebula Service"
  },
  "Body": {
    "ServiceInfo": {
      "state": "STARTED"
    }
  }
}
```

#### 停止服务
```http
POST http://ambari-server:8080/api/v1/clusters/{cluster_name}/services/NEBULA
Content-Type: application/json

{
  "RequestInfo": {
    "context": "Stop Nebula Service"
  },
  "Body": {
    "ServiceInfo": {
      "state": "INSTALLED"
    }
  }
}
```

#### 重启服务
```http
POST http://ambari-server:8080/api/v1/clusters/{cluster_name}/services/NEBULA/actions/RESTART
Content-Type: application/json

{
  "RequestInfo": {
    "context": "Restart Nebula Service"
  }
}
```

### 组件控制

#### 启动特定组件
```http
POST http://ambari-server:8080/api/v1/clusters/{cluster_name}/hosts/{host_name}/host_components/NEBULA_GRAPHD
Content-Type: application/json

{
  "RequestInfo": {
    "context": "Start Graphd Component"
  },
  "Body": {
    "HostRoles": {
      "state": "STARTED"
    }
  }
}
```

#### 获取组件状态
```http
GET http://ambari-server:8080/api/v1/clusters/{cluster_name}/services/NEBULA/components/NEBULA_GRAPHD
```

## 扩展开发API

### 自定义指标接口

#### 注册自定义指标
```python
from resource_management.libraries.functions import format
from resource_management.core.resources.system import Execute

class CustomMetricCollector:
    def collect_custom_metrics(self):
        """收集自定义指标"""
        metrics = {}
        
        # 执行自定义指标收集逻辑
        cmd = format("curl -s http://localhost:19669/custom_stats")
        result = Execute(cmd, user="nebula")
        
        # 解析结果并返回指标
        metrics['custom_metric_1'] = result.get('value1', 0)
        metrics['custom_metric_2'] = result.get('value2', 0)
        
        return metrics
```

#### 自定义告警脚本
```python
def execute(configurations={}, parameters=[], host_name=None):
    """自定义告警检查逻辑"""
    
    # 获取配置参数
    threshold = float(parameters[0]) if parameters else 80.0
    
    # 执行检查逻辑
    try:
        # 获取指标值
        metric_value = get_custom_metric_value()
        
        if metric_value > threshold:
            return ('CRITICAL', [f'Custom metric value {metric_value} exceeds threshold {threshold}'])
        else:
            return ('OK', [f'Custom metric value {metric_value} is normal'])
            
    except Exception as e:
        return ('UNKNOWN', [f'Failed to check custom metric: {str(e)}'])
```

### 配置模板扩展

#### 添加自定义配置项
```xml
<!-- 在configuration/nebula-custom-site.xml中添加 -->
<configuration>
  <property>
    <name>custom_parameter</name>
    <display-name>Custom Parameter</display-name>
    <value>default_value</value>
    <description>Custom configuration parameter</description>
    <value-attributes>
      <type>string</type>
    </value-attributes>
  </property>
</configuration>
```

#### 在脚本中使用自定义配置
```python
# 在params.py中添加
if 'nebula-custom-site' in config['configurations']:
    custom_parameter = config['configurations']['nebula-custom-site']['custom_parameter']

# 在组件脚本中使用
def configure(self, env):
    import params
    env.set_params(params)
    
    # 使用自定义参数
    custom_config = format("custom_setting={custom_parameter}")
    
    File(format("{nebula_install_dir}/etc/custom.conf"),
         content=custom_config,
         owner=params.nebula_user,
         group=params.nebula_group)
```

## 错误代码参考

### HTTP状态码

| 状态码 | 含义 | 描述 |
|--------|------|------|
| 200 | OK | 请求成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 认证失败 |
| 403 | Forbidden | 权限不足 |
| 404 | Not Found | 资源不存在 |
| 500 | Internal Server Error | 服务器内部错误 |
| 503 | Service Unavailable | 服务不可用 |

### 应用错误码

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| NE001 | 服务未运行 | 检查服务状态并启动 |
| NE002 | 配置文件错误 | 验证配置文件语法 |
| NE003 | 端口被占用 | 检查端口使用情况 |
| NE004 | 权限不足 | 检查用户权限设置 |
| NE005 | 磁盘空间不足 | 清理磁盘空间 |

## API使用示例

### Python示例

```python
import requests
import json

class NebulaAmbariClient:
    def __init__(self, ambari_url, username, password):
        self.ambari_url = ambari_url
        self.auth = (username, password)
    
    def get_service_status(self, cluster_name):
        """获取Nebula服务状态"""
        url = f"{self.ambari_url}/api/v1/clusters/{cluster_name}/services/NEBULA"
        response = requests.get(url, auth=self.auth)
        return response.json()
    
    def start_service(self, cluster_name):
        """启动Nebula服务"""
        url = f"{self.ambari_url}/api/v1/clusters/{cluster_name}/services/NEBULA"
        data = {
            "RequestInfo": {"context": "Start Nebula Service"},
            "Body": {"ServiceInfo": {"state": "STARTED"}}
        }
        response = requests.post(url, json=data, auth=self.auth)
        return response.json()
    
    def get_metrics(self, graphd_host, graphd_port):
        """获取Graphd指标"""
        url = f"http://{graphd_host}:{graphd_port}/stats"
        response = requests.get(url)
        return response.json()

# 使用示例
client = NebulaAmbariClient("http://ambari-server:8080", "admin", "admin")
status = client.get_service_status("cluster1")
metrics = client.get_metrics("graphd-host", 19669)
```

### Shell脚本示例

```bash
#!/bin/bash

AMBARI_URL="http://ambari-server:8080"
CLUSTER_NAME="cluster1"
USERNAME="admin"
PASSWORD="admin"

# 获取服务状态
get_service_status() {
    curl -u $USERNAME:$PASSWORD \
         -H "X-Requested-By: ambari" \
         "$AMBARI_URL/api/v1/clusters/$CLUSTER_NAME/services/NEBULA"
}

# 启动服务
start_service() {
    curl -u $USERNAME:$PASSWORD \
         -H "X-Requested-By: ambari" \
         -X POST \
         -d '{"RequestInfo":{"context":"Start Nebula"},"Body":{"ServiceInfo":{"state":"STARTED"}}}' \
         "$AMBARI_URL/api/v1/clusters/$CLUSTER_NAME/services/NEBULA"
}

# 获取组件指标
get_component_metrics() {
    local host=$1
    local port=$2
    curl -s "http://$host:$port/stats" | jq .
}

# 使用示例
echo "Service Status:"
get_service_status | jq .

echo "Starting service..."
start_service

echo "Graphd Metrics:"
get_component_metrics "graphd-host" "19669"
```

## 最佳实践

### API调用优化

1. **批量操作**: 尽可能使用批量API减少请求次数
2. **缓存结果**: 对不频繁变化的数据进行缓存
3. **错误处理**: 实现完善的错误处理和重试机制
4. **认证管理**: 安全地管理认证凭据

### 监控集成

1. **指标收集频率**: 根据需要设置合适的收集频率
2. **告警阈值**: 设置合理的告警阈值避免误报
3. **数据保留**: 配置适当的数据保留策略
4. **性能影响**: 监控API调用对系统性能的影响

### 安全考虑

1. **认证**: 使用强密码和安全的认证方式
2. **授权**: 实施细粒度的权限控制
3. **加密**: 对敏感数据进行加密传输
4. **审计**: 记录API调用日志用于安全审计

---

本API文档提供了Nebula Graph Ambari集成的完整API接口说明。