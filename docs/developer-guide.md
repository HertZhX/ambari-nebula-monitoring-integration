# Nebula Graph Ambari集成开发者指南

## 概述

本文档为Nebula Graph Ambari集成项目的开发者指南，包含架构说明、开发流程和最佳实践。

## 快速开始

### 开发环境要求

- Python 2.7+
- Java 1.8+
- Apache Ambari 2.6+
- Git, Maven

### 项目结构

```
ambari-nebula-monitoring-integration/
├── mpack.json                     # Mpack包配置
├── common-services/NEBULA/1.0.0/  # 服务定义
│   ├── metainfo.xml               # 服务元信息
│   ├── configuration/             # 配置模板
│   ├── package/scripts/           # 控制脚本
│   ├── metrics.json               # 监控指标
│   └── alerts.json                # 告警规则
├── tests/                         # 测试脚本
└── docs/                          # 文档
```

## 核心开发任务

### 1. 添加新组件

在`metainfo.xml`中定义组件：

```xml
<component>
  <name>NEBULA_NEWSERVICE</name>
  <displayName>New Service</displayName>
  <category>MASTER</category>
  <cardinality>1+</cardinality>
  <commandScript>
    <script>scripts/newservice.py</script>
    <scriptType>PYTHON</scriptType>
  </commandScript>
</component>
```

创建控制脚本`newservice.py`：

```python
from resource_management.libraries.script.script import Script
from nebula_utils import nebula_service, setup_nebula_config

class NewService(Script):
    def install(self, env):
        print("Installing New Service...")
        
    def configure(self, env):
        setup_nebula_config()
        
    def start(self, env, upgrade_type=None):
        self.configure(env)
        nebula_service('start', 'newservice')
        
    def stop(self, env, upgrade_type=None):
        nebula_service('stop', 'newservice')
        
    def status(self, env):
        nebula_service('status', 'newservice')

if __name__ == "__main__":
    NewService().execute()
```

### 2. 添加配置参数

在`configuration/`目录下创建配置文件：

```xml
<configuration>
  <property>
    <name>new_parameter</name>
    <display-name>New Parameter</display-name>
    <value>default_value</value>
    <description>Parameter description</description>
    <value-attributes>
      <type>string</type>
    </value-attributes>
  </property>
</configuration>
```

在`params.py`中引用：

```python
if 'nebula-newservice-site' in config['configurations']:
    new_parameter = config['configurations']['nebula-newservice-site']['new_parameter']
```

### 3. 添加监控指标

在`metrics.json`中定义指标：

```json
{
  "metrics/nebula/newservice/custom_metric": {
    "metric": "nebula.newservice.custom_metric",
    "pointInTime": true,
    "temporal": true
  }
}
```

### 4. 添加告警规则

在`alerts.json`中定义告警：

```json
{
  "name": "newservice_alert",
  "label": "New Service Alert", 
  "description": "Alert for new service",
  "interval": 5,
  "scope": "ANY",
  "enabled": true,
  "source": {
    "type": "SCRIPT",
    "path": "NEBULA/1.0.0/package/scripts/alerts/alert_newservice.py"
  }
}
```

创建告警脚本：

```python
def execute(configurations={}, parameters=[], host_name=None):
    # 检查逻辑
    if check_condition():
        return ('OK', ['Service is healthy'])
    else:
        return ('CRITICAL', ['Service has issues'])

def get_tokens():
    return ('{{config_parameter}}',)
```

## 测试开发

### 单元测试

```python
import unittest
from unittest.mock import Mock, patch

class TestNewService(unittest.TestCase):
    def test_service_start(self):
        with patch('newservice.nebula_service') as mock_service:
            from newservice import NewService
            service = NewService()
            service.start(Mock())
            mock_service.assert_called_with('start', 'newservice')

if __name__ == '__main__':
    unittest.main()
```

### 验证和构建

```bash
# 验证Mpack结构
./tests/validate_mpack.sh

# 运行单元测试  
python -m unittest discover tests/

# 构建Mpack包
./tests/build_mpack.sh
```

## 部署流程

### 本地测试

1. 构建Mpack包
2. 在测试环境安装
3. 验证功能

### 发布流程

1. 代码审查
2. 测试验证
3. 版本标记
4. 构建发布包
5. 部署到生产环境

## 最佳实践

### 代码规范

- 遵循Python PEP8规范
- 使用有意义的变量名
- 添加必要的注释和文档

### 错误处理

- 捕获和处理异常
- 提供清晰的错误信息
- 记录详细的日志

### 性能优化

- 避免阻塞操作
- 合理设置超时时间
- 优化资源使用

### 安全考虑

- 验证输入参数
- 使用最小权限原则
- 保护敏感信息

## 常见问题

### Q: 如何调试脚本？
A: 在脚本中添加日志输出，查看`/var/log/ambari-agent/`下的日志文件。

### Q: 配置不生效怎么办？
A: 检查配置文件语法，重启Ambari服务。

### Q: 告警不触发怎么办？
A: 检查告警脚本逻辑，验证配置参数。

## 参考资源

- [Apache Ambari开发指南](https://ambari.apache.org/)
- [Nebula Graph官方文档](https://docs.nebula-graph.io/)
- 项目GitHub仓库

---

本指南涵盖了开发Nebula Graph Ambari集成的核心内容。