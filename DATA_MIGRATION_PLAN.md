# 数据迁移方案：从SQLite到HBase/HDFS

## 1. 数据结构分析

### 1.1 当前SQLite表结构

#### seniors表

| 字段名           | 数据类型 | 描述               |
| ---------------- | -------- | ------------------ |
| id               | INTEGER  | 老人ID（自增主键） |
| age              | INTEGER  | 年龄               |
| community_id     | TEXT     | 社区ID             |
| health_status    | TEXT     | 健康状态           |
| service_count    | INTEGER  | 服务次数           |
| avg_satisfaction | REAL     | 平均满意度         |

#### health_records表

| 字段名        | 数据类型 | 描述               |
| ------------- | -------- | ------------------ |
| id            | INTEGER  | 记录ID（自增主键） |
| senior_id     | INTEGER  | 老人ID（外键）     |
| date          | TEXT     | 记录日期           |
| sbp           | INTEGER  | 收缩压             |
| dbp           | INTEGER  | 舒张压             |
| blood_sugar   | REAL     | 血糖               |
| heart_rate    | INTEGER  | 心率               |
| health_status | TEXT     | 健康状态           |

#### service_records表

| 字段名       | 数据类型 | 描述               |
| ------------ | -------- | ------------------ |
| id           | INTEGER  | 记录ID（自增主键） |
| senior_id    | INTEGER  | 老人ID（外键）     |
| service_date | TEXT     | 服务日期           |
| service_type | TEXT     | 服务类型           |
| duration     | INTEGER  | 服务时长（分钟）   |
| satisfaction | INTEGER  | 满意度             |
| community_id | TEXT     | 社区ID             |

## 2. HBase表结构设计

### 2.1 表设计原则

- 利用HBase的列族特性，将相关数据组织在一起
- 设计合适的行键，确保查询效率
- 考虑数据压缩和分区策略

### 2.2 具体表设计

#### 1. seniors表

| 表名    | 列族 | 列               | 描述       |
| ------- | ---- | ---------------- | ---------- |
| seniors | info | age              | 年龄       |
|         |      | community_id     | 社区ID     |
|         |      | health_status    | 健康状态   |
|         |      | service_count    | 服务次数   |
|         |      | avg_satisfaction | 平均满意度 |

**行键设计**：`senior:{id}`

#### 2. health_records表

| 表名           | 列族   | 列            | 描述     |
| -------------- | ------ | ------------- | -------- |
| health_records | record | date          | 记录日期 |
|                |        | sbp           | 收缩压   |
|                |        | dbp           | 舒张压   |
|                |        | blood_sugar   | 血糖     |
|                |        | heart_rate    | 心率     |
|                |        | health_status | 健康状态 |

**行键设计**：`senior:{id}:{date}`

#### 3. service_records表

| 表名            | 列族   | 列           | 描述     |
| --------------- | ------ | ------------ | -------- |
| service_records | record | service_date | 服务日期 |
|                 |        | service_type | 服务类型 |
|                 |        | duration     | 服务时长 |
|                 |        | satisfaction | 满意度   |
|                 |        | community_id | 社区ID   |

**行键设计**：`senior:{id}:{service_date}:{service_type}`

## 3. HDFS存储结构设计

### 3.1 目录结构

```
/hadoop/elderly_care/
├── raw_data/               # 原始数据
│   ├── seniors/            # 老人数据
│   ├── health_records/     # 健康记录
│   └── service_records/    # 服务记录
├── processed_data/         # 处理后的数据
│   ├── health_analysis/    # 健康分析结果
│   ├── service_analysis/   # 服务分析结果
│   └── predictions/        # 预测结果
└── models/                 # 机器学习模型
```

### 3.2 数据格式

- 原始数据：CSV格式
- 处理后数据：Parquet格式（支持Hive查询）

## 4. 数据迁移方案

### 4.1 迁移步骤

1. **数据导出**：从SQLite导出数据为CSV格式
2. **数据上传**：将CSV文件上传到HDFS
3. **HBase表创建**：创建HBase表结构
4. **数据导入**：将数据导入HBase
5. **Hive表创建**：创建Hive外部表，映射HBase数据
6. **验证**：验证数据迁移是否成功

### 4.2 迁移脚本

#### 1. 数据导出脚本

```python
#!/usr/bin/env python3
"""
从SQLite导出数据为CSV格式
"""

import sqlite3
import csv
import os

# 数据库连接
db_path = 'data/database/elderly_care.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 导出目录
output_dir = 'data/export'
os.makedirs(output_dir, exist_ok=True)

# 导出seniors表
with open(os.path.join(output_dir, 'seniors.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    cursor.execute('SELECT * FROM seniors')
    # 写入表头
    writer.writerow([description[0] for description in cursor.description])
    # 写入数据
    writer.writerows(cursor.fetchall())

# 导出health_records表
with open(os.path.join(output_dir, 'health_records.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    cursor.execute('SELECT * FROM health_records')
    writer.writerow([description[0] for description in cursor.description])
    writer.writerows(cursor.fetchall())

# 导出service_records表
with open(os.path.join(output_dir, 'service_records.csv'), 'w', newline='') as f:
    writer = csv.writer(f)
    cursor.execute('SELECT * FROM service_records')
    writer.writerow([description[0] for description in cursor.description])
    writer.writerows(cursor.fetchall())

print("数据导出完成！")
conn.close()
```

#### 2. HBase表创建脚本

```bash
#!/bin/bash
"""
创建HBase表结构
"""

hbase shell << EOF
# 创建seniors表
create 'seniors', 'info'

# 创建health_records表
create 'health_records', 'record'

# 创建service_records表
create 'service_records', 'record'

# 查看表列表
list
EOF
```

#### 3. 数据导入脚本

```python
#!/usr/bin/env python3
"""
将数据导入HBase
"""

import csv
import happybase

# 连接HBase
connection = happybase.Connection('hadoop-master')

# 打开表
seniors_table = connection.table('seniors')
health_table = connection.table('health_records')
service_table = connection.table('service_records')

# 导入seniors数据
with open('data/export/seniors.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row_key = f"senior:{row['id']}"
        seniors_table.put(row_key, {
            'info:age': row['age'],
            'info:community_id': row['community_id'],
            'info:health_status': row['health_status'],
            'info:service_count': row['service_count'],
            'info:avg_satisfaction': row['avg_satisfaction']
        })

# 导入health_records数据
with open('data/export/health_records.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row_key = f"senior:{row['senior_id']}:{row['date']}"
        health_table.put(row_key, {
            'record:date': row['date'],
            'record:sbp': row['sbp'],
            'record:dbp': row['dbp'],
            'record:blood_sugar': row['blood_sugar'],
            'record:heart_rate': row['heart_rate'],
            'record:health_status': row['health_status']
        })

# 导入service_records数据
with open('data/export/service_records.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row_key = f"senior:{row['senior_id']}:{row['service_date']}:{row['service_type']}"
        service_table.put(row_key, {
            'record:service_date': row['service_date'],
            'record:service_type': row['service_type'],
            'record:duration': row['duration'],
            'record:satisfaction': row['satisfaction'],
            'record:community_id': row['community_id']
        })

print("数据导入完成！")
connection.close()
```

#### 4. Hive表创建脚本

```sql
-- 创建Hive外部表，映射HBase数据

-- 创建seniors表
CREATE EXTERNAL TABLE IF NOT EXISTS elderly_care.seniors (
    rowkey STRING,
    age INT,
    community_id STRING,
    health_status STRING,
    service_count INT,
    avg_satisfaction DOUBLE
) STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
WITH SERDEPROPERTIES (
    'hbase.columns.mapping' = ':key,info:age,info:community_id,info:health_status,info:service_count,info:avg_satisfaction'
)
TBLPROPERTIES (
    'hbase.table.name' = 'seniors'
);

-- 创建health_records表
CREATE EXTERNAL TABLE IF NOT EXISTS elderly_care.health_records (
    rowkey STRING,
    senior_id INT,
    date STRING,
    sbp INT,
    dbp INT,
    blood_sugar DOUBLE,
    heart_rate INT,
    health_status STRING
) STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
WITH SERDEPROPERTIES (
    'hbase.columns.mapping' = ':key,record:senior_id,record:date,record:sbp,record:dbp,record:blood_sugar,record:heart_rate,record:health_status'
)
TBLPROPERTIES (
    'hbase.table.name' = 'health_records'
);

-- 创建service_records表
CREATE EXTERNAL TABLE IF NOT EXISTS elderly_care.service_records (
    rowkey STRING,
    senior_id INT,
    service_date STRING,
    service_type STRING,
    duration INT,
    satisfaction INT,
    community_id STRING
) STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
WITH SERDEPROPERTIES (
    'hbase.columns.mapping' = ':key,record:senior_id,record:service_date,record:service_type,record:duration,record:satisfaction,record:community_id'
)
TBLPROPERTIES (
    'hbase.table.name' = 'service_records'
);
```

## 5. 数据访问模式设计

### 5.1 后端数据访问

1. **实时查询**：使用HBase API直接访问数据
2. **批量查询**：使用Hive SQL进行复杂查询和分析
3. **数据处理**：使用MapReduce或Spark进行大规模数据处理

### 5.2 前端数据访问

1. **API接口**：保持现有的API接口不变，内部实现从HBase/Hive获取数据
2. **数据缓存**：对频繁访问的数据进行缓存，提高响应速度
3. **分页查询**：支持大数据量的分页查询

## 6. 性能优化策略

1. **HBase优化**
   - 合理设置列族和列
   - 优化行键设计
   - 配置合适的缓存和压缩策略

2. **Hive优化**
   - 使用分区表
   - 合理设置MapReduce参数
   - 使用列式存储格式

3. **数据访问优化**
   - 实现数据缓存
   - 优化查询语句
   - 使用异步查询

## 7. 迁移风险评估

1. **数据一致性**：确保迁移过程中数据不丢失、不重复
2. **服务中断**：迁移过程中可能的服务中断
3. **性能影响**：新系统的性能可能与预期不符
4. **兼容性**：确保现有应用能够正常访问新存储系统

## 8. 回滚方案

1. **数据备份**：在迁移前备份原始SQLite数据库
2. **双系统运行**：在一段时间内保持SQLite和HBase/HDFS同时运行
3. **快速回滚**：在出现问题时能够快速切换回SQLite

## 9. 迁移时间计划

| 阶段     | 任务               | 时间估计 |
| -------- | ------------------ | -------- |
| 准备阶段 | 环境搭建、脚本开发 | 2天      |
| 测试阶段 | 测试数据迁移、验证 | 1天      |
| 迁移阶段 | 正式数据迁移       | 1天      |
| 验证阶段 | 系统验证、性能测试 | 1天      |
| 优化阶段 | 性能优化、问题修复 | 2天      |

## 10. 总结

本迁移方案设计了从SQLite到HBase/HDFS的完整数据迁移流程，包括表结构设计、数据迁移脚本和性能优化策略。通过合理的设计和实施，可以实现存储系统的平滑升级，为项目的后续发展提供更强大的数据存储和处理能力。
