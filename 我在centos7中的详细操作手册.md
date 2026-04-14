# 我在 CentOS7 中的详细操作手册（新手版）

这份手册按“可直接复制命令执行”的方式写，适合第一次在 CentOS7 跑本项目。

---

## 0. 你现在已经具备的前提

你已安装：

- CentOS 7
- Hadoop
- Hive
- HBase

本手册默认项目路径为：

```bash
/root/flask_elderly_care
```

如果你的项目不在这个路径，请把手册中的路径改成你自己的路径。

---

## 1. 第一次登录后先做这 4 件事

### 1.1 进入项目目录

```bash
cd /root/flask_elderly_care
pwd
```

看到当前路径正确后再继续。

### 1.2 检查 Python 版本

```bash
python3 --version
```

建议 Python 3.8+。

### 1.3 安装 Python 依赖

```bash
cd /root/flask_elderly_care/backend
pip3 install -r requirements.txt
```

### 1.4 回到项目根目录

```bash
cd /root/flask_elderly_care
```

---

## 2. 最推荐方式：一条命令全流程

项目已提供一键脚本：

```bash
sudo bash scripts/centos7_one_click.sh all
```

这条命令会依次执行：

1. 启动 Hadoop（HDFS + YARN）
2. 启动 Hive（metastore + hiveserver2）
3. 启动 HBase
4. 初始化 SQLite 数据
5. 导出 SQLite 到 Hive/HBase
6. 运行 Hadoop 集成验证
7. 启动后端接口（5008 端口）

看到类似输出：

```text
后端已启动: http://127.0.0.1:5008
```

说明后端已起来。

---

## 3. 分步执行方式（排错时用）

### 3.0 停止所有服务（清理环境）

如果你发现服务运行混乱，或者想彻底重启，可以先停止：

```bash
bash scripts/centos7_one_click.sh stop
```

### 3.1 只启动大数据服务

脚本会自动检查服务是否已在运行，如果已运行则会跳过启动，不会报错。

```bash
bash scripts/centos7_one_click.sh services
```

### 3.2 只初始化 SQLite 数据

```bash
bash scripts/centos7_one_click.sh init
```

### 3.3 只做数据导出（SQLite -> Hive/HBase）

```bash
bash scripts/centos7_one_click.sh export
```

### 3.4 只做集成验证

```bash
bash scripts/centos7_one_click.sh verify
```

### 3.5 只启动后端 API

```bash
bash scripts/centos7_one_click.sh api
```

---

## 4. 字段问题说明（重点）

本项目历史上存在多套表结构命名，常见有：

- `elderly / health_record / service_record`
- `seniors / health_records / service_records`
- `senior / health_record / service_log`

你不用手工改代码对字段。当前导出脚本已经做了自动识别和映射，直接运行：

```bash
bash scripts/centos7_one_click.sh export
```

如果导出失败，先看报错里是否出现 `Unsupported SQLite schema`，再检查你的 SQLite 里表名是否属于上面三套之一。

---

## 5. 新手常用检查命令

### 5.1 检查 Hadoop

```bash
hdfs dfsadmin -report
yarn node -list
```

### 5.2 检查 Hive

```bash
hive -e "SHOW DATABASES;"
hive -e "USE elderly_care; SHOW TABLES;"
```

### 5.3 检查 HBase

```bash
hbase shell -c "status"
hbase shell -c "list"
```

### 5.4 检查后端接口

```bash
curl http://127.0.0.1:5008/api/elderly/NOT_EXIST
```

返回 404 或 200 都说明接口进程是活的。

---

## 6. 日志怎么看

一键脚本会把日志写到项目下 `logs` 目录：

- `logs/hive-metastore.log`
- `logs/hive-server2.log`
- `logs/backend-api.log`

实时看日志：

```bash
tail -f /opt/bigdata/flask_elderly_care/logs/backend-api.log
```

---

## 7. 环境变量（只在你需要改默认地址时设置）

默认值已经够用；只有你的服务不在 localhost 或数据库路径不同，才设置：

```bash
export HIVE_HOST=localhost
export HBASE_HOST=localhost
export HIVE_PORT=10000
export HIVE_DATABASE=elderly_care
export SQLITE_DB_PATH=/opt/bigdata/flask_elderly_care/backend/data/database/elderly_care.db
```

设置后再执行：

```bash
bash scripts/centos7_one_click.sh all
```

---

## 8. 常见报错与处理（新手高频）

### 报错 1：`start-dfs.sh: command not found`

原因：Hadoop 环境变量没生效。  
处理：先执行 `source /etc/profile`，再重试。

### 报错 2：`hive: command not found`

原因：Hive 环境变量没生效。  
处理：先执行 `source /etc/profile`，确认 `which hive` 能找到命令。

### 报错 3：`hbase: command not found`

原因：HBase 环境变量没生效。  
处理：先执行 `source /etc/profile`，确认 `which hbase`。

### 报错 4：导出失败，提示表结构不支持

原因：SQLite 表名不是项目支持的三套结构。  
处理：先运行初始化命令重新生成标准表：

```bash
bash scripts/centos7_one_click.sh init
bash scripts/centos7_one_click.sh export
```

### 报错 5：API 起不来（5008 端口）

处理步骤：

1. 看后端日志 `logs/backend-api.log`
2. 检查 Python 依赖是否安装完整
3. 重新执行 `bash scripts/centos7_one_click.sh api`

### 报错 6：`Name node is in safe mode`

原因：HDFS 刚启动，NameNode 还在安全模式。  
处理：

```bash
hdfs dfsadmin -safemode wait
bash scripts/centos7_one_click.sh all
```

### 报错 7：`Could not connect to ... 10000` 或 `... 9090`

原因：HiveServer2 或 HBase Thrift 端口还没准备好。  
处理：

```bash
bash scripts/centos7_one_click.sh stop
bash scripts/centos7_one_click.sh services
bash scripts/centos7_one_click.sh export
```

---

## 9. 每天最简单的操作流程（建议）

每天登录虚拟机后只做：

```bash
cd /opt/bigdata/flask_elderly_care
bash scripts/centos7_one_click.sh all
```

如果只是改了业务代码、不需要重导数据，可以改为：

```bash
bash scripts/centos7_one_click.sh services
bash scripts/centos7_one_click.sh api
```

---

## 10. 给你的操作建议（新手）

1. 先用 `all` 跑通一次，再做分步操作。
2. 报错先看 `logs`，不要第一时间改字段名。
3. 尽量保持项目路径不变，减少环境变量问题。
4. 改完环境变量后，重新开一个 shell 或 `source /etc/profile`。
5. 遇到不确定问题，优先贴“完整报错 + 你执行的命令 + 日志最后 50 行”。

---

## 11. 低配电脑优化（防止 CPU 锁死/卡顿）

如果你的电脑配置较低（如 8G 内存、4核以下），运行大数据服务可能会出现 `soft lockup` 或系统卡死。请按以下步骤优化：

### 11.1 禁用 Transparent Huge Pages (THP)

这是导致 `soft lockup` 最常见的原因。在 CentOS 7 中执行：

```bash
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag
```

_注：重启后会失效，建议加入 `/etc/rc.local`。_

### 11.2 减少 JVM 内存占用

修改 Hadoop 和 HBase 的内存设置（新手建议值）：

1. **Hadoop**: 编辑 `etc/hadoop/hadoop-env.sh`，设置 `HADOOP_HEAPSIZE_MAX=512`。
2. **HBase**: 编辑 `conf/hbase-env.sh`，设置 `export HBASE_HEAPSIZE=512M`。
3. **Hive**: 执行脚本前设置 `export HIVE_OPTS="-Xmx512m"`。

### 11.3 导出脚本低资源模式

项目中的 `export_from_sqlite.py` 已调整为低资源导出策略：分批写入 Hive、连接重试、并在 HBase 导出前做端口重试，这样在低配机器上更稳定。

---

按这份手册执行，你在 CentOS7 基本可以做到“少命令、可重复、可排错”。
