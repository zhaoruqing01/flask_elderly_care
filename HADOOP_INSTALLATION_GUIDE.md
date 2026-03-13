# Hadoop、Hive、HBase 安装配置指南（CentOS 7）

## 系统准备

### 1. 系统要求

- CentOS 7 64位
- 至少 8GB 内存（推荐 16GB+）
- 至少 50GB 磁盘空间
- Java 8 或 11

### 2. 安装 Java

```bash
# 安装 Java 8
yum install java-1.8.0-openjdk-devel -y

# 验证安装
java -version
```

### 3. 配置网络和主机名

```bash
# 编辑主机名
hostnamectl set-hostname hadoop-master

# 编辑 hosts 文件
vi /etc/hosts
# 添加以下内容（根据实际IP修改）
192.168.1.100 hadoop-master
192.168.1.101 hadoop-slave1
192.168.1.102 hadoop-slave2
```

### 4. 配置 SSH 免密登录

```bash
# 生成密钥对
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa

# 复制公钥到所有节点
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# 测试免密登录
ssh hadoop-master
```

## Hadoop 安装配置

### 1. 下载 Hadoop

```bash
# 下载 Hadoop 3.3.6
wget https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz

# 解压
mkdir -p /opt/hadoop
tar -xzf hadoop-3.3.6.tar.gz -C /opt/hadoop/
```

### 2. 配置环境变量

```bash
vi /etc/profile.d/hadoop.sh
```

添加以下内容：

```bash
export HADOOP_HOME=/opt/hadoop/hadoop-3.3.6
export PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin
export HADOOP_CONF_DIR=$HADOOP_HOME/etc/hadoop
export HADOOP_MAPRED_HOME=$HADOOP_HOME
export HADOOP_COMMON_HOME=$HADOOP_HOME
export HADOOP_HDFS_HOME=$HADOOP_HOME
export YARN_HOME=$HADOOP_HOME
```

```bash
# 生效环境变量
source /etc/profile
```

### 3. 配置 Hadoop

#### core-site.xml

```bash
vi $HADOOP_HOME/etc/hadoop/core-site.xml
```

```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://hadoop-master:9000</value>
    </property>
    <property>
        <name>hadoop.tmp.dir</name>
        <value>/opt/hadoop/tmp</value>
    </property>
</configuration>
```

#### hdfs-site.xml

```bash
vi $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```

```xml
<configuration>
    <property>
        <name>dfs.replication</name>
        <value>3</value>
    </property>
    <property>
        <name>dfs.namenode.name.dir</name>
        <value>/opt/hadoop/hdfs/namenode</value>
    </property>
    <property>
        <name>dfs.datanode.data.dir</name>
        <value>/opt/hadoop/hdfs/datanode</value>
    </property>
</configuration>
```

#### yarn-site.xml

```bash
vi $HADOOP_HOME/etc/hadoop/yarn-site.xml
```

```xml
<configuration>
    <property>
        <name>yarn.nodemanager.aux-services</name>
        <value>mapreduce_shuffle</value>
    </property>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>hadoop-master</value>
    </property>
</configuration>
```

#### mapred-site.xml

```bash
cp $HADOOP_HOME/etc/hadoop/mapred-site.xml.template $HADOOP_HOME/etc/hadoop/mapred-site.xml
vi $HADOOP_HOME/etc/hadoop/mapred-site.xml
```

```xml
<configuration>
    <property>
        <name>mapreduce.framework.name</name>
        <value>yarn</value>
    </property>
</configuration>
```

### 4. 格式化 HDFS

```bash
# 创建必要的目录
mkdir -p /opt/hadoop/tmp /opt/hadoop/hdfs/namenode /opt/hadoop/hdfs/datanode

# 格式化 namenode
hdfs namenode -format
```

### 5. 启动 Hadoop

```bash
# 启动 HDFS
start-dfs.sh

# 启动 YARN
start-yarn.sh

# 查看进程
jps
```

## Hive 安装配置

### 1. 下载 Hive

```bash
# 下载 Hive 3.1.3
wget https://archive.apache.org/dist/hive/hive-3.1.3/apache-hive-3.1.3-bin.tar.gz

# 解压
mkdir -p /opt/hive
tar -xzf apache-hive-3.1.3-bin.tar.gz -C /opt/hive/
```

### 2. 配置环境变量

```bash
vi /etc/profile.d/hive.sh
```

添加以下内容：

```bash
export HIVE_HOME=/opt/hive/apache-hive-3.1.3-bin
export PATH=$PATH:$HIVE_HOME/bin
```

```bash
# 生效环境变量
source /etc/profile
```

### 3. 配置 Hive

#### hive-site.xml

```bash
cp $HIVE_HOME/conf/hive-default.xml.template $HIVE_HOME/conf/hive-site.xml
vi $HIVE_HOME/conf/hive-site.xml
```

修改以下配置：

```xml
<configuration>
    <property>
        <name>javax.jdo.option.ConnectionURL</name>
        <value>jdbc:derby:;databaseName=/opt/hive/metastore_db;create=true</value>
    </property>
    <property>
        <name>hive.metastore.warehouse.dir</name>
        <value>/user/hive/warehouse</value>
    </property>
    <property>
        <name>hive.server2.thrift.port</name>
        <value>10000</value>
    </property>
    <property>
        <name>hive.server2.thrift.bind.host</name>
        <value>0.0.0.0</value>
    </property>
</configuration>
```

### 4. 初始化 Hive 元数据

```bash
# 初始化元数据
hive --service metastore &
sleep 5
hive -e "CREATE DATABASE IF NOT EXISTS elderly_care;
```

## HBase 安装配置

### 1. 下载 HBase

```bash
# 下载 HBase 2.5.6
wget https://archive.apache.org/dist/hbase/2.5.6/hbase-2.5.6-bin.tar.gz

# 解压
mkdir -p /opt/hbase
tar -xzf hbase-2.5.6-bin.tar.gz -C /opt/hbase/
```

### 2. 配置环境变量

```bash
vi /etc/profile.d/hbase.sh
```

添加以下内容：

```bash
export HBASE_HOME=/opt/hbase/hbase-2.5.6
export PATH=$PATH:$HBASE_HOME/bin
```

```bash
# 生效环境变量
source /etc/profile
```

### 3. 配置 HBase

#### hbase-site.xml

```bash
vi $HBASE_HOME/conf/hbase-site.xml
```

```xml
<configuration>
    <property>
        <name>hbase.rootdir</name>
        <value>hdfs://hadoop-master:9000/hbase</value>
    </property>
    <property>
        <name>hbase.cluster.distributed</name>
        <value>true</value>
    </property>
    <property>
        <name>hbase.zookeeper.quorum</name>
        <value>hadoop-master</value>
    </property>
    <property>
        <name>hbase.zookeeper.property.dataDir</name>
        <value>/opt/hbase/zookeeper</value>
    </property>
</configuration>
```

#### regionservers

```bash
vi $HBASE_HOME/conf/regionservers
```

添加以下内容：

```
hadoop-master
hadoop-slave1
hadoop-slave2
```

### 4. 启动 HBase

```bash
# 启动 HBase
start-hbase.sh

# 查看进程
jps
```

## 测试和验证

### 1. 测试 Hadoop

```bash
# 创建测试目录
hdfs dfs -mkdir -p /user/test

# 上传测试文件
echo "Hello Hadoop" > test.txt
hdfs dfs -put test.txt /user/test/

# 查看文件
hdfs dfs -ls /user/test/
hdfs dfs -cat /user/test/test.txt
```

### 2. 测试 Hive

```bash
# 启动 Hive 命令行
hive

# 创建测试表
CREATE TABLE test_table (id INT, name STRING);
INSERT INTO test_table VALUES (1, 'test');
SELECT * FROM test_table;
```

### 3. 测试 HBase

```bash
# 启动 HBase Shell
hbase shell

# 创建测试表
create 'test_table', 'cf'
put 'test_table', 'row1', 'cf:col1', 'value1'
get 'test_table', 'row1'
```

## 常见问题及解决方案

1. **Hadoop 启动失败**
   - 检查 Java 版本是否正确
   - 检查 SSH 免密登录是否配置成功
   - 检查配置文件中的主机名是否正确

2. **Hive 元数据初始化失败**
   - 检查 Hadoop 是否正常运行
   - 检查 Hive 配置文件中的路径是否正确

3. **HBase 启动失败**
   - 检查 Hadoop 是否正常运行
   - 检查 Zookeeper 服务是否正常
   - 检查 HBase 配置文件中的路径是否正确

## 监控和管理

- **Hadoop Web UI**: http://hadoop-master:9870
- **YARN Web UI**: http://hadoop-master:8088
- **HBase Web UI**: http://hadoop-master:16010
