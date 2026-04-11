#!/usr/bin/env bash

# ==================== 颜色定义 ====================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m'

# ==================== 核心配置 ====================
INSTALL_DIR="/root"
JAVA_VERSION="8u202"
HADOOP_VERSION="3.3.4"
HIVE_VERSION="3.1.3"
HBASE_VERSION="2.4.17"

# 动态获取主机名与真实IP
HOST_NAME=$(hostname)
LOCAL_IP=$(hostname -I | awk '{print $1}')

JAVA_HOME="${INSTALL_DIR}/jdk1.8.0_202"
HADOOP_HOME="${INSTALL_DIR}/hadoop-${HADOOP_VERSION}"
HIVE_HOME="${INSTALL_DIR}/apache-hive-${HIVE_VERSION}-bin"
HBASE_HOME="${INSTALL_DIR}/hbase-${HBASE_VERSION}"

# 项目与日志目录
PROJECT_ROOT="${INSTALL_DIR}/flask_elderly_care"
BACKEND_DIR="${PROJECT_ROOT}/backend"
LOG_DIR="${PROJECT_ROOT}/logs"
HIVE_LOG_DIR="/var/log/hive"

DOWNLOAD_RETRY=3
DOWNLOAD_TIMEOUT=15

# ==================== 工具函数 ====================
info() { echo -e "${GREEN}[INFO] $1${NC}"; }
warn() { echo -e "${YELLOW}[WARN] $1${NC}"; }
error() { echo -e "${RED}[ERROR] $1${NC}"; exit 1; }

check_root() {
  if [ "$(id -u)" -ne 0 ]; then
    error "请使用 root 用户执行此脚本！"
  fi
}

download_with_retry() {
  local file_name="$1"
  shift
  local mirrors=("$@")
  local success=0

  for mirror in "${mirrors[@]}"; do
    info "尝试下载: $mirror"
    if wget -c -t "${DOWNLOAD_RETRY}" -T "${DOWNLOAD_TIMEOUT}" -O "${file_name}" "${mirror}"; then
      success=1
      break
    else
      warn "镜像下载失败，自动切换下一个..."
    fi
  done

  if [ "${success}" -ne 1 ]; then
    error "所有镜像均下载失败！请检查网络后重试。"
  fi
}

wait_for_port() {
  local port=$1
  local service=$2
  local timeout=$3
  info "等待 ${service} (端口 ${port}) 启动，最大等待 ${timeout} 秒..."
  for (( i=1; i<=timeout; i++ )); do
    if netstat -tlnp 2>/dev/null | grep -q ":${port} "; then
      info "✅ ${service} (端口 ${port}) 已完全就绪！"
      return 0
    fi
    sleep 2
  done
  error "❌ ${service} 启动超时！请检查相关日志。"
}

# 彻底清理僵尸进程与锁
clean_zombie_processes() {
  info "清理残留的僵尸进程与锁文件..."
  pkill -9 -f java || true
  pkill -9 -f 'hive' || true
  pkill -9 -f 'hadoop' || true
  pkill -9 -f 'hbase' || true
  pkill -9 -f 'python3' || true
  
  rm -rf /tmp/hadoop-* /tmp/hsperfdata_* /tmp/hbase-* /tmp/hive-* /tmp/*.lck /tmp/*.csv
  
  if [ -d "${HIVE_HOME}/metastore_db" ]; then
    rm -rf ${HIVE_HOME}/metastore_db/*.lck
    rm -rf ${HIVE_HOME}/metastore_db/dbex.lck
  fi
  
  mkdir -p ${HIVE_LOG_DIR}
  info "环境清理完毕，确保干净启动！"
}

# ==================== 1. 系统前置准备 ====================
system_prepare() {
  info "开始系统环境初始化..."
  systemctl stop firewalld && systemctl disable firewalld || true
  sed -i 's/SELINUX=enforcing/SELINUX=disabled/' /etc/selinux/config || true
  setenforce 0 || true
  yum install -y wget tar openssh-server openssh-clients net-tools telnet python3 python3-pip sqlite psmisc lsof
  systemctl start sshd && systemctl enable sshd
  
  info "配置网络主机名映射..."
  sed -i "/${HOST_NAME}/d" /etc/hosts || true
  if [ -n "$LOCAL_IP" ]; then
      echo "${LOCAL_IP} ${HOST_NAME}" >> /etc/hosts
  else
      echo "127.0.0.1 ${HOST_NAME}" >> /etc/hosts
  fi
  grep -q "127.0.0.1 localhost" /etc/hosts || echo "127.0.0.1 localhost" >> /etc/hosts
  
  info "系统前置准备完成！"
}

# ==================== 2. SSH免密 ====================
config_ssh() {
  info "配置SSH免密登录..."
  if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -P "" -f ~/.ssh/id_rsa >/dev/null 2>&1
  fi
  
  grep -q "$(cat ~/.ssh/id_rsa.pub)" ~/.ssh/authorized_keys 2>/dev/null || cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
  
  ssh-keyscan -H ${HOST_NAME} >> ~/.ssh/known_hosts 2>/dev/null
  ssh-keyscan -H localhost >> ~/.ssh/known_hosts 2>/dev/null
  ssh-keyscan -H 0.0.0.0 >> ~/.ssh/known_hosts 2>/dev/null
  ssh -o StrictHostKeyChecking=no ${HOST_NAME} "echo 'SSH 免密配置成功'" >/dev/null 2>&1
  info "SSH免密配置完成！"
}

# ==================== 3. 安装JDK ====================
install_jdk() {
  info "安装 JDK 1.8.0_202..."
  mkdir -p ${INSTALL_DIR} && cd ${INSTALL_DIR}

  if [ -d "${JAVA_HOME}" ]; then
    warn "JDK 已存在，跳过安装。"
    return
  fi

  local jdk_file="jdk-${JAVA_VERSION}-linux-x64.tar.gz"
  local jdk_mirrors=(
    "https://repo.huaweicloud.com/java/jdk/${JAVA_VERSION}-b08/jdk-${JAVA_VERSION}-linux-x64.tar.gz"
    "https://mirrors.huaweicloud.com/java/jdk/${JAVA_VERSION}-b08/jdk-${JAVA_VERSION}-linux-x64.tar.gz"
  )

  download_with_retry "${jdk_file}" "${jdk_mirrors[@]}"
  tar -zxf "${jdk_file}"
  rm -f "${jdk_file}"
  info "JDK安装完成！"
}

# ==================== 4. 安装Hadoop ====================
install_hadoop() {
  info "安装 Hadoop ${HADOOP_VERSION}..."
  cd ${INSTALL_DIR}

  if [ ! -d "${HADOOP_HOME}" ]; then
    local hadoop_file="hadoop-${HADOOP_VERSION}.tar.gz"
    local hadoop_mirrors=(
      "https://mirrors.huaweicloud.com/apache/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"
      "https://mirrors.aliyun.com/apache/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"
    )
    download_with_retry "${hadoop_file}" "${hadoop_mirrors[@]}"
    tar -zxf "${hadoop_file}"
    rm -f "${hadoop_file}"
  fi

  mkdir -p ${HADOOP_HOME}/data/tmp ${HADOOP_HOME}/data/namenode ${HADOOP_HOME}/data/datanode

  cat > ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh << EOF
export JAVA_HOME=${JAVA_HOME}
export HDFS_NAMENODE_USER="root"
export HDFS_DATANODE_USER="root"
export HDFS_SECONDARYNAMENODE_USER="root"
export YARN_RESOURCEMANAGER_USER="root"
export YARN_NODEMANAGER_USER="root"
EOF

  # 【修复：root 代理用户权限】
  cat > ${HADOOP_HOME}/etc/hadoop/core-site.xml << EOF
<configuration>
    <property><name>fs.defaultFS</name><value>hdfs://${HOST_NAME}:9000</value></property>
    <property><name>hadoop.tmp.dir</name><value>${HADOOP_HOME}/data/tmp</value></property>
    <property><name>hadoop.proxyuser.root.hosts</name><value>*</value></property>
    <property><name>hadoop.proxyuser.root.groups</name><value>*</value></property>
</configuration>
EOF

  cat > ${HADOOP_HOME}/etc/hadoop/hdfs-site.xml << EOF
<configuration>
    <property><name>dfs.replication</name><value>1</value></property>
    <property><name>dfs.namenode.name.dir</name><value>${HADOOP_HOME}/data/namenode</value></property>
    <property><name>dfs.datanode.data.dir</name><value>${HADOOP_HOME}/data/datanode</value></property>
</configuration>
EOF

  cat > ${HADOOP_HOME}/etc/hadoop/mapred-site.xml << EOF
<configuration><property><name>mapreduce.framework.name</name><value>yarn</value></property></configuration>
EOF

  cat > ${HADOOP_HOME}/etc/hadoop/yarn-site.xml << EOF
<configuration><property><name>yarn.nodemanager.aux-services</name><value>mapreduce_shuffle</value></property></configuration>
EOF

  echo "${HOST_NAME}" > ${HADOOP_HOME}/etc/hadoop/workers
  info "Hadoop配置完成！"
}

# ==================== 5. 安装Hive ====================
install_hive() {
  info "安装 Hive ${HIVE_VERSION}..."
  cd ${INSTALL_DIR}

  if [ ! -d "${HIVE_HOME}" ]; then
    local hive_file="apache-hive-${HIVE_VERSION}-bin.tar.gz"
    local hive_mirrors=(
      "https://mirrors.huaweicloud.com/apache/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz"
      "https://mirrors.aliyun.com/apache/hive/hive-${HIVE_VERSION}/apache-hive-${HIVE_VERSION}-bin.tar.gz"
    )
    download_with_retry "${hive_file}" "${hive_mirrors[@]}"
    tar -zxf "${hive_file}"
    rm -f "${hive_file}"
  fi

  cat > ${HIVE_HOME}/conf/hive-env.sh << EOF
export JAVA_HOME=${JAVA_HOME}
export HADOOP_HOME=${HADOOP_HOME}
export HIVE_CONF_DIR=${HIVE_HOME}/conf
EOF

  # 【修复：强制本地模式运行】
  cat > ${HIVE_HOME}/conf/hive-site.xml << EOF
<configuration>
    <property><name>javax.jdo.option.ConnectionURL</name><value>jdbc:derby:;databaseName=${HIVE_HOME}/metastore_db;create=true</value></property>
    <property><name>javax.jdo.option.ConnectionDriverName</name><value>org.apache.derby.jdbc.EmbeddedDriver</value></property>
    <property><name>hive.metastore.warehouse.dir</name><value>/user/hive/warehouse</value></property>
    <property><name>hive.server2.thrift.port</name><value>10000</value></property>
    <property><name>hive.server2.thrift.bind.host</name><value>0.0.0.0</value></property>
    <property><name>hive.metastore.schema.verification</name><value>false</value></property>
    <property><name>datanucleus.schema.autoCreateAll</name><value>true</value></property>
    <property><name>hive.exec.mode.local.auto</name><value>true</value></property>
    <property><name>hive.exec.submitviachild</name><value>false</value></property>
    <property><name>hive.exec.submit.local.task.via.child</name><value>false</value></property>
</configuration>
EOF

  rm -f ${HIVE_HOME}/lib/guava-*.jar
  cp ${HADOOP_HOME}/share/hadoop/common/lib/guava-*.jar ${HIVE_HOME}/lib/ || true
  info "Hive配置完成！"
}

# ==================== 6. 安装HBase ====================
install_hbase() {
  info "安装 HBase ${HBASE_VERSION}..."
  cd ${INSTALL_DIR}

  if [ ! -d "${HBASE_HOME}" ]; then
    local hbase_file="hbase-${HBASE_VERSION}-bin.tar.gz"
    local hbase_mirrors=(
      "https://mirrors.huaweicloud.com/apache/hbase/${HBASE_VERSION}/hbase-${HBASE_VERSION}-bin.tar.gz"
      "https://mirrors.aliyun.com/apache/hbase/${HBASE_VERSION}/hbase-${HBASE_VERSION}-bin.tar.gz"
    )
    download_with_retry "${hbase_file}" "${hbase_mirrors[@]}"
    tar -zxf "${hbase_file}"
    rm -f "${hbase_file}"
  fi

  cat > ${HBASE_HOME}/conf/hbase-env.sh << EOF
export JAVA_HOME=${JAVA_HOME}
export HBASE_MANAGES_ZK=true
EOF

  cat > ${HBASE_HOME}/conf/hbase-site.xml << EOF
<configuration>
    <property><name>hbase.rootdir</name><value>hdfs://${HOST_NAME}:9000/hbase</value></property>
    <property><name>hbase.cluster.distributed</name><value>true</value></property>
    <property><name>hbase.zookeeper.quorum</name><value>${HOST_NAME}</value></property>
    <property><name>hbase.zookeeper.property.dataDir</name><value>${HBASE_HOME}/data/zk</value></property>
    <property><name>hbase.regionserver.thrift.port</name><value>9090</value></property>
    <property><name>hbase.regionserver.thrift.http</name><value>false</value></property>
</configuration>
EOF

  echo "${HOST_NAME}" > ${HBASE_HOME}/conf/regionservers
  mkdir -p ${HBASE_HOME}/data/zk
  rm -f ${HBASE_HOME}/lib/client-facing-thirdparty/slf4j-reload4j-*.jar || true
  info "HBase配置完成！"
}

# ==================== 7. 全局环境变量 ====================
set_global_env() {
  info "配置系统环境变量..."
  cat > /etc/profile.d/bigdata_env.sh << EOF
export JAVA_HOME=${JAVA_HOME}
export HADOOP_HOME=${HADOOP_HOME}
export HIVE_HOME=${HIVE_HOME}
export HBASE_HOME=${HBASE_HOME}
export PATH=\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$HIVE_HOME/bin:\$HBASE_HOME/bin:\$PATH
EOF

  source /etc/profile
  source /etc/profile.d/bigdata_env.sh
  info "环境变量已生效！"
}

# ==================== 8. 启动服务 (集成关键修复) ====================
start_services() {
  info "准备启动基础服务..."
  clean_zombie_processes

  if [ ! -d "${HADOOP_HOME}/data/namenode/current" ]; then
    info "正在格式化 HDFS..."
    hdfs namenode -format -force -nonInteractive >/dev/null 2>&1
  fi

  start-dfs.sh || true
  wait_for_port 9000 "HDFS NameNode" 60
  start-yarn.sh || true
  hdfs dfsadmin -safemode wait >/dev/null 2>&1 || true

  hdfs dfs -mkdir -p /user/hive/warehouse
  hdfs dfs -chmod 777 /user/hive/warehouse

  info "重新初始化Hive元数据..."
  schematool -dbType derby -initSchema -force >/dev/null 2>&1 || true
  nohup hive --service hiveserver2 > ${HIVE_LOG_DIR}/hive_server2.log 2>&1 &

  info "启动 HBase..."
  start-hbase.sh || true
  
  # 【修复：给 HBase 充分的初始化时间，防止 Thrift 超时】
  info "等待 HBase HMaster 初始化 (30秒)..."
  sleep 30
  hbase-daemon.sh start thrift || true

  wait_for_port 10000 "HiveServer2" 300
  wait_for_port 9090 "HBase Thrift" 90
  info "所有大数据基础服务启动完成！"
}

# ==================== 9. 校验 ====================
check_install() {
  info "========== 安装校验 =========="
  java -version || true
  hadoop version 2>&1 | head -1 || true
  hive --version || true
  hbase version 2>&1 | head -1 || true

  echo -e "\n${YELLOW}========== 当前运行的 Java 进程 ==========${NC}"
  jps || true

  echo -e "\n${GREEN}=============================================${NC}"
  echo -e "✅ 大数据环境 + 后端服务 部署完成！"
  echo -e "后端API：http://${LOCAL_IP}:5008"
  echo -e "测试接口：curl http://127.0.0.1:5008/api/health"
  echo -e "=============================================${NC}"
}

# ==================== 业务集成功能 ====================
prepare_python_env() {
  info "安装 Python 依赖库..."
  if [ -f "${BACKEND_DIR}/requirements.txt" ]; then
    pip3 install -r "${BACKEND_DIR}/requirements.txt" -i https://pypi.tuna.tsinghua.edu.cn/simple >/dev/null 2>&1
  fi
}

init_sqlite() {
  prepare_python_env
  info "初始化 SQLite 数据..."
  mkdir -p "${LOG_DIR}"
  export PYTHONPATH="${PROJECT_ROOT}"
  python3 "${BACKEND_DIR}/scripts/init_data.py" > "${LOG_DIR}/init_data.log" 2>&1
  info "SQLite 初始化完成！"
}

export_sqlite() {
  info "导出数据至 Hive/HBase..."
  mkdir -p "${LOG_DIR}"
  export PYTHONPATH="${PROJECT_ROOT}"
  export SQLITE_DB_PATH="${PROJECT_ROOT}/backend/data/database/elderly_care.db"
  export HIVE_HOST="${HOST_NAME}"
  export HBASE_HOST="${HOST_NAME}"

  # 第一次尝试导出
  python3 -u "${BACKEND_DIR}/scripts/export_from_sqlite.py" > "${LOG_DIR}/export.log" 2>&1
  
  # 如果失败（可能 HBase 还没准备好），则等待 15 秒后重试最后一次
  if [ $? -ne 0 ]; then
      warn "首次导出失败，HBase 可能仍在加载，15秒后进行最后一次重试..."
      sleep 15
      python3 -u "${BACKEND_DIR}/scripts/export_from_sqlite.py" >> "${LOG_DIR}/export.log" 2>&1
  fi
  info "数据导出完成！"
}

start_backend_api() {
  info "启动后端 API 服务 (5008 端口)..."
  mkdir -p "${LOG_DIR}"
  export PYTHONPATH="${PROJECT_ROOT}"
  pkill -f 'python3 .*app.py' || true
  nohup python3 "${BACKEND_DIR}/app.py" > "${LOG_DIR}/backend-api.log" 2>&1 &
  sleep 5
  
  if netstat -tlnp 2>/dev/null | grep -q ":5008 "; then
      info "✅ 后端 API 启动成功！"
  else
      error "❌ 后端 API 启动失败，请检查 ${LOG_DIR}/backend-api.log"
  fi
}

stop_all() {
  info "停止所有服务..."
  stop-dfs.sh || true
  stop-yarn.sh || true
  stop-hbase.sh || true
  pkill -9 -f 'hive' || true
  pkill -9 -f 'python3 .*app.py' || true
  clean_zombie_processes
  info "服务已彻底停止！"
}

# ==================== 入口解析 ====================
main() {
  check_root
  case "$1" in
    all|"")
      system_prepare
      config_ssh
      install_jdk
      install_hadoop
      install_hive
      install_hbase
      set_global_env
      start_services
      init_sqlite
      export_sqlite
      start_backend_api
      check_install
      ;;
    services) set_global_env; start_services ;;
    init) set_global_env; init_sqlite ;;
    export) set_global_env; export_sqlite ;;
    api) set_global_env; start_backend_api ;;
    stop) stop_all ;;
    *) echo "Usage: $0 {all|services|init|export|api|stop}" ;;
  esac
}

main "$1"