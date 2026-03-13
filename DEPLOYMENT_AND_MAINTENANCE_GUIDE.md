# 部署和维护指南

## 1. 系统部署

### 1.1 环境准备

- **硬件要求**：
  - 主节点：至少 16GB 内存，4 核 CPU，100GB 磁盘
  - 从节点：至少 8GB 内存，2 核 CPU，50GB 磁盘
  - 网络：千兆网卡，确保节点间网络畅通

- **软件要求**：
  - CentOS 7 64位
  - Java 8 或 11
  - Hadoop 3.3.6
  - Hive 3.1.3
  - HBase 2.5.6

### 1.2 部署步骤

1. **基础环境配置**：
   - 安装 Java
   - 配置网络和主机名
   - 配置 SSH 免密登录

2. **Hadoop 部署**：
   - 下载并解压 Hadoop
   - 配置 Hadoop 环境变量
   - 修改 Hadoop 配置文件
   - 格式化 HDFS
   - 启动 Hadoop 服务

3. **Hive 部署**：
   - 下载并解压 Hive
   - 配置 Hive 环境变量
   - 修改 Hive 配置文件
   - 初始化 Hive 元数据

4. **HBase 部署**：
   - 下载并解压 HBase
   - 配置 HBase 环境变量
   - 修改 HBase 配置文件
   - 启动 HBase 服务

5. **应用部署**：
   - 复制项目代码到服务器
   - 安装项目依赖
   - 配置环境变量
   - 启动应用服务

### 1.3 配置文件

**环境变量配置**：

```bash
# /etc/profile.d/hadoop.sh
export HADOOP_HOME=/opt/hadoop/hadoop-3.3.6
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop

# /etc/profile.d/hive.sh
export HIVE_HOME=/opt/hive/apache-hive-3.1.3-bin
export PATH=$PATH:$HIVE_HOME/bin

# /etc/profile.d/hbase.sh
export HBASE_HOME=/opt/hbase/hbase-2.5.6
export PATH=$PATH:$HBASE_HOME/bin

# /etc/profile.d/elderly_care.sh
export USE_HADOOP=True
export HBASE_HOST=hadoop-master
export HIVE_HOST=hadoop-master
export HIVE_PORT=10000
export HIVE_DATABASE=elderly_care
```

## 2. 服务管理

### 2.1 启动和停止服务

**Hadoop 服务**：

```bash
# 启动 HDFS
start-dfs.sh

# 停止 HDFS
stop-dfs.sh

# 启动 YARN
start-yarn.sh

# 停止 YARN
stop-yarn.sh

# 启动所有服务
start-all.sh

# 停止所有服务
stop-all.sh
```

**HBase 服务**：

```bash
# 启动 HBase
start-hbase.sh

# 停止 HBase
stop-hbase.sh
```

**Hive 服务**：

```bash
# 启动 Hive Metastore
hive --service metastore &

# 启动 Hive Server2
hive --service hiveserver2 &
```

**应用服务**：

```bash
# 启动应用服务
cd /path/to/project
export FLASK_APP=backend/app.py
export FLASK_ENV=production
flask run --host=0.0.0.0 --port=5000 &

# 或使用 Gunicorn（推荐生产环境）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app &
```

### 2.2 服务状态检查

**Hadoop 状态**：

```bash
# 检查 HDFS 状态
hdfs dfsadmin -report

# 检查 YARN 状态
yarn node -list

# 查看 Hadoop 进程
jps
```

**HBase 状态**：

```bash
# 检查 HBase 状态
hbase shell -c 'status'

# 查看 HBase 进程
jps
```

**Hive 状态**：

```bash
# 检查 Hive 服务
telnet localhost 10000

# 测试 Hive 查询
hive -e 'SHOW TABLES;'
```

**应用状态**：

```bash
# 检查应用服务
curl http://localhost:5000/api/health

# 查看应用日志
journalctl -u elderly-care.service
```

## 3. 监控和日志管理

### 3.1 Web UI 监控

- **Hadoop HDFS Web UI**：http://hadoop-master:9870
- **YARN Web UI**：http://hadoop-master:8088
- **HBase Web UI**：http://hadoop-master:16010

### 3.2 日志管理

**Hadoop 日志**：
- HDFS 日志：`$HADOOP_HOME/logs/`
- YARN 日志：`$HADOOP_HOME/logs/`

**HBase 日志**：
- HBase 日志：`$HBASE_HOME/logs/`

**Hive 日志**：
- Hive 日志：`$HIVE_HOME/logs/`

**应用日志**：
- 应用日志：`/var/log/elderly-care/`

### 3.3 监控工具

- **Ganglia**：集群监控
- **Nagios**：服务监控
- **Prometheus + Grafana**：指标监控和可视化

## 4. 备份和恢复

### 4.1 HDFS 备份

**创建备份**：

```bash
# 创建快照
hdfs dfsadmin -createSnapshot /user/elderly_care backup_$(date +%Y%m%d)

# 复制到外部存储
hdfs dfs -get /user/elderly_care /path/to/backup/
```

**恢复数据**：

```bash
# 从快照恢复
hdfs dfsadmin -restoreSnapshot /user/elderly_care backup_20240101

# 从外部存储恢复
hdfs dfs -put /path/to/backup/elderly_care /user/
```

### 4.2 HBase 备份

**创建备份**：

```bash
# 使用 HBase Export 工具
hbase org.apache.hadoop.hbase.mapreduce.Export seniors /hbase/backup/seniors
```

**恢复数据**：

```bash
# 使用 HBase Import 工具
hbase org.apache.hadoop.hbase.mapreduce.Import seniors /hbase/backup/seniors
```

### 4.3 应用数据备份

**数据库备份**：

```bash
# 备份 SQLite 数据库
cp /path/to/elderly_care.db /path/to/backup/

# 备份模型文件
cp -r /path/to/models /path/to/backup/
```

## 5. 常见问题和解决方案

### 5.1 Hadoop 问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| NameNode 启动失败 | 元数据损坏 | 从备份恢复或重新格式化 |
| DataNode 无法启动 | 数据目录权限问题 | 检查权限并修复 |
| 资源不足 | YARN 配置不当 | 调整 YARN 资源配置 |

### 5.2 HBase 问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| RegionServer 崩溃 | 内存不足 | 增加内存或调整 JVM 配置 |
| Zookeeper 连接失败 | 网络问题或配置错误 | 检查网络和 Zookeeper 配置 |
| 表无法创建 | 权限问题 | 检查 HDFS 权限 |

### 5.3 Hive 问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| 元数据连接失败 | Metastore 服务未启动 | 启动 Metastore 服务 |
| 查询执行缓慢 | 数据量过大或查询不当 | 优化查询或增加资源 |
| 权限错误 | HDFS 权限问题 | 检查 HDFS 权限 |

### 5.4 应用问题

| 问题 | 原因 | 解决方案 |
|-----|------|---------|
| 连接 HBase 失败 | HBase 服务未启动或网络问题 | 检查 HBase 服务和网络 |
| 响应时间长 | 数据量过大或查询不当 | 优化查询或增加缓存 |
| 内存泄漏 | 应用代码问题 | 检查代码并修复 |

## 6. 升级和扩展

### 6.1 系统升级

**Hadoop 升级**：
1. 停止所有服务
2. 备份配置和数据
3. 安装新版本
4. 迁移配置
5. 启动服务并验证

**HBase 升级**：
1. 停止 HBase 服务
2. 备份数据
3. 安装新版本
4. 迁移配置
5. 启动服务并验证

**Hive 升级**：
1. 停止 Hive 服务
2. 备份元数据
3. 安装新版本
4. 迁移配置
5. 启动服务并验证

### 6.2 集群扩展

**添加新节点**：
1. 配置新节点的网络和 SSH
2. 安装必要的软件
3. 修改 Hadoop、HBase 配置
4. 启动新节点服务
5. 验证节点加入成功

**存储扩展**：
1. 添加新的存储设备
2. 挂载到 HDFS 数据目录
3. 重启 DataNode 服务
4. 验证存储扩展成功

## 7. 安全管理

### 7.1 认证和授权

- **Kerberos 认证**：配置 Kerberos 认证，增强集群安全性
- **访问控制**：使用 HDFS ACL 和 HBase 权限控制
- **网络安全**：配置防火墙，限制访问端口

### 7.2 数据安全

- **数据加密**：启用 HDFS 透明加密
- **敏感数据保护**：对敏感数据进行加密存储
- **审计日志**：启用审计日志，记录访问操作

## 8. 性能调优

### 8.1 定期维护

- **HDFS 平衡**：定期运行 `hdfs balancer` 平衡数据分布
- **HBase 压缩**：定期对 HBase 表进行压缩
- **日志清理**：定期清理过期日志

### 8.2 监控和调优

- **监控指标**：定期检查系统指标，发现性能瓶颈
- **参数调整**：根据监控结果调整系统参数
- **查询优化**：优化 Hive 查询和 HBase 操作

## 9. 故障处理

### 9.1 故障检测

- **自动监控**：使用监控工具自动检测故障
- **日志分析**：定期分析日志，发现潜在问题
- **健康检查**：定期执行健康检查脚本

### 9.2 故障恢复

- **快速响应**：建立故障响应流程
- **故障隔离**：隔离故障节点，避免影响整个集群
- **恢复策略**：制定详细的恢复策略

## 10. 最佳实践

### 10.1 部署建议

- **生产环境**：使用至少 3 个节点的集群
- **高可用性**：配置 Hadoop 和 HBase 的高可用性
- **备份策略**：制定定期备份策略

### 10.2 维护建议

- **定期检查**：每周进行一次系统检查
- **更新管理**：定期更新系统和软件
- **文档维护**：及时更新部署和维护文档

### 10.3 安全建议

- **最小权限**：遵循最小权限原则
- **定期审计**：定期进行安全审计
- **漏洞修复**：及时修复安全漏洞

## 11. 总结

本指南提供了完整的部署和维护流程，包括系统部署、服务管理、监控和日志、备份和恢复、常见问题和解决方案、升级和扩展、安全管理、性能调优、故障处理和最佳实践。通过遵循本指南，可以确保系统的稳定运行和高效维护。