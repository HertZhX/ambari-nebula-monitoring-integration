# Ambari Nebula Graph监控集成

本项目实现了Nebula Graph数据库与Apache Ambari的深度集成，提供统一的集群管理和监控能力。

## 项目结构

```
ambari-nebula-monitoring-integration/
├── mpack.json                          # Mpack包配置文件
├── common-services/                     # 服务定义目录
│   └── NEBULA/                         # Nebula服务目录
│       └── 1.0.0/                      # 服务版本目录
│           ├── metainfo.xml            # 服务元信息定义
│           ├── configuration/          # 配置文件模板
│           ├── package/                # 安装包和脚本
│           ├── alerts.json             # 告警规则定义
│           └── metrics.json            # 监控指标定义
├── tests/                              # 测试脚本
├── docs/                               # 文档目录
└── README.md                           # 项目说明文档
```

## 功能特性

- 🚀 **统一管理**: 通过Ambari界面统一管理Nebula Graph集群
- 📊 **可视化监控**: 集成监控指标到Ambari Metrics System
- ⚡ **自动化运维**: 支持服务的自动部署、启动、停止和状态检查
- 🔔 **智能告警**: 内置多层次告警规则，及时发现和处理异常
- 🔧 **配置管理**: 统一的配置管理和分发机制

## 支持的组件

- **Graphd**: 查询引擎，处理客户端GraphQL请求
- **Metad**: 元数据管理服务，负责集群协调和Schema管理
- **Storaged**: 存储引擎，负责图数据的存储和管理

## 快速开始

1. 构建Mpack包
2. 在Ambari Server上安装Mpack
3. 通过Ambari Web界面添加Nebula服务
4. 配置服务参数并启动集群

详细安装和使用说明请参考docs目录下的文档。

## 版本兼容性

- Ambari: 2.6.x - 2.8.x
- Nebula Graph: 2.6.x - 3.1.x

## 贡献指南

欢迎提交Issue和Pull Request来改进本项目。

## 许可证

本项目采用Apache License 2.0许可证。