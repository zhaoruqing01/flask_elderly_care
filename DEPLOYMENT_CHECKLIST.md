# CentOS 7 一键部署兼容性检查清单

## ✅ 已完成的修复与优化

### 1. 数据库层面

#### 1.1 表结构完整性

- [x] `community` 表使用统一字段名: `total_population`, `elderly_population`
- [x] `prediction_result` 表使用统一字段名: `prediction_date`
- [x] `service_record` 表已添加 `caregiver_id` 字段
- [x] `caregiver` 表定义完整 (护工信息)
- [x] `schedule` 表定义完整 (排班信息)

#### 1.2 后端兼容性

- [x] `data_service.py` 添加字段名自动兼容逻辑
- [x] 支持新旧字段名自动切换 (try-except)
- [x] `db_init.py` 包含所有表的创建语句
- [x] SQLite 初始化脚本正确创建所有表

### 2. 前端优化

#### 2.1 表单验证

- [x] 6个弹窗全部添加表单验证规则
- [x] ID格式校验 (正则表达式)
- [x] 必填项检查
- [x] 数值范围限制
- [x] 日期格式验证

#### 2.2 用户体验

- [x] 弹窗宽度统一为 550px
- [x] 防误触关闭 (`:close-on-click-modal="false"`)
- [x] 提交按钮加载状态 (`:loading="submitting"`)
- [x] 输入框占位提示 (`placeholder`)
- [x] 下拉框支持搜索 (`filterable`)
- [x] 双列布局优化 (健康记录、服务记录)

### 3. 接口调用

- [x] 所有19个接口调用添加 `role` 参数
- [x] 错误处理完善 (`e.response?.data?.error`)
- [x] 分页函数完整 (6个)
- [x] 筛选条件监听器 (2个 watch)

## 🚀 CentOS 7 部署流程

### 前置要求

```bash
# 确保系统是 CentOS 7
cat /etc/redhat-release

# 确保有 root 权限
whoami  # 应该是 root
```

### 一键部署

```bash
cd /root/flask_elderly_care/scripts
chmod +x centos7_one_click.sh
./centos7_one_click.sh all
```

### 部署步骤说明

#### 1. 系统准备 (system_prepare)

- 关闭防火墙
- 禁用 SELinux
- 安装必要软件包 (wget, tar, python3, sqlite, etc.)

#### 2. SSH配置 (config_ssh)

- 生成 SSH 密钥
- 配置免密登录

#### 3. 安装 JDK (install_jdk)

- 下载并安装 JDK 1.8.0_202
- 配置 JAVA_HOME

#### 4. 安装 Hadoop (install_hadoop)

- 下载 Hadoop 3.3.4
- 配置 HDFS、YARN
- 格式化 NameNode

#### 5. 安装 Hive (install_hive)

- 下载 Hive 3.1.3
- 配置 Derby 元数据存储
- 强制本地模式运行

#### 6. 安装 HBase (install_hbase)

- 下载 HBase 2.4.17
- 配置 ZooKeeper
- 启动 Thrift 服务

#### 7. 启动服务 (start_services)

- 启动 HDFS
- 启动 YARN
- 初始化 Hive 元数据
- 启动 HiveServer2
- 启动 HBase + Thrift

#### 8. 初始化数据 (init_sqlite) ⭐ **已优化**

```bash
# 新的初始化流程
1. 执行 db_init.py - 创建所有表结构
2. 执行 data_generator.py - 生成测试数据
```

#### 9. 导出到大数据平台 (export_sqlite)

- 从 SQLite 导出数据到 Hive
- 从 SQLite 导出数据到 HBase
- 自动重试机制

#### 10. 启动后端 API (start_backend_api)

```bash
# 自动化三步走
1. 修复数据库表/字段 (db_init.py)
2. 生成测试数据 (data_generator.py)
3. 启动 Flask API (app.py on port 5008)
```

## 🔍 验证部署成功

### 1. 检查服务状态

```bash
# 检查 Java 进程
jps

# 应该看到以下进程:
# - NameNode
# - DataNode
# - SecondaryNameNode
# - ResourceManager
# - NodeManager
# - HMaster
# - HRegionServer
# - RunJar (Hive)
# - ThriftServer (HBase)
```

### 2. 检查端口

```bash
# 检查关键端口
netstat -tlnp | grep -E '5008|9000|10000|9090'

# 期望输出:
# :5008  - Flask API
# :9000  - HDFS NameNode
# :10000 - HiveServer2
# :9090  - HBase Thrift
```

### 3. 测试 API

```bash
# 测试健康检查接口
curl http://127.0.0.1:5008/api/health

# 测试数据统计接口
curl http://127.0.0.1:5008/api/data/stats

# 测试社区列表
curl http://127.0.0.1:5008/api/data/communities
```

### 4. 检查数据库

```bash
# 进入 SQLite 数据库
sqlite3 /root/flask_elderly_care/backend/data/database/elderly_care.db

# 检查表是否存在
.tables

# 应该看到:
# community, elderly, caregiver, schedule
# health_record, service_record, prediction_result
# users

# 检查数据
SELECT COUNT(*) FROM community;
SELECT COUNT(*) FROM elderly;
SELECT COUNT(*) FROM caregiver;
SELECT COUNT(*) FROM schedule;
```

### 5. 访问前端

```
浏览器打开: http://<服务器IP>:5173

默认账号:
- admin / 123456 (机构管理员)
- caregiver1 / 123456 (护工)
- gov / 123456 (监管部门)
```

## ⚠️ 常见问题与解决方案

### 问题1: HBase Thrift 启动失败

**症状**: 端口 9090 未监听
**解决**:

```bash
# 等待 HBase 完全启动后再启动 Thrift
sleep 30
hbase-daemon.sh start thrift
```

### 问题2: Hive 元数据初始化失败

**症状**: schematool 报错
**解决**:

```bash
# 删除旧的元数据目录
rm -rf $HIVE_HOME/metastore_db
# 重新初始化
schematool -dbType derby -initSchema -force
```

### 问题3: 后端 API 启动失败

**症状**: 端口 5008 未监听
**解决**:

```bash
# 查看日志
cat /root/flask_elderly_care/logs/backend-api.log

# 检查 Python 依赖
pip3 install -r /root/flask_elderly_care/backend/requirements.txt

# 手动启动测试
cd /root/flask_elderly_care/backend
python3 app.py
```

### 问题4: 前端页面数据为空

**症状**: DataView.vue 显示空白
**解决**:

```bash
# 1. 检查数据库是否有数据
sqlite3 /root/flask_elderly_care/backend/data/database/elderly_care.db "SELECT COUNT(*) FROM elderly;"

# 2. 如果没有数据,重新生成
cd /root/flask_elderly_care/backend
python3 data_generator.py

# 3. 重启后端
pkill -f 'python3 .*app.py'
nohup python3 app.py > logs/backend-api.log 2>&1 &
```

### 问题5: 字段名不匹配错误

**症状**: API 返回 500 错误
**解决**:

```bash
# 后端已添加兼容层,自动适配新旧字段名
# 如果仍有问题,检查日志
tail -f /root/flask_elderly_care/logs/backend-api.log
```

## 📋 部署后检查清单

- [ ] 所有 Java 进程正常运行 (jps)
- [ ] 所有端口正常监听 (netstat)
- [ ] SQLite 数据库包含所有表
- [ ] 数据库中有初始数据
- [ ] 后端 API 可以正常访问
- [ ] 前端页面可以正常加载
- [ ] 所有 CRUD 操作正常工作
- [ ] 表单验证功能正常
- [ ] 分页和筛选功能正常
- [ ] 不同角色权限控制正常

## 🔧 维护命令

### 停止所有服务

```bash
./centos7_one_click.sh stop
```

### 重启后端 API

```bash
./centos7_one_click.sh api
```

### 重新初始化数据

```bash
./centos7_one_click.sh init
```

### 重新导出数据到大数据平台

```bash
./centos7_one_click.sh export
```

## 📝 更新日志

### 2026-04-30

- ✅ 修复 community 表字段名不匹配问题
- ✅ 修复 prediction_result 表字段名不匹配问题
- ✅ 添加 caregiver 和 schedule 表定义
- ✅ 在 service_record 表中添加 caregiver_id 字段
- ✅ 后端添加字段名自动兼容逻辑
- ✅ 前端添加完整的表单验证
- ✅ 优化弹窗用户体验
- ✅ 更新部署脚本初始化流程
- ✅ 所有接口调用添加 role 参数
- ✅ 修复分页和筛选功能

---

**最后更新**: 2026-04-30
**维护人员**: 开发团队
