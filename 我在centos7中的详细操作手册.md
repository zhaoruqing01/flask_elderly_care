本手册默认项目路径为：

```bash
/root/flask_elderly_care
```

---

## 1. 第一次登录后先做这 2 件事

### 1.1 进入项目目录(执行完1.1后即可直接执行步骤2)

```bash
cd /root/flask_elderly_care
pwd
```

### 1.2 安装 Python 依赖(已经执行过了)

```bash
cd /root/flask_elderly_care/backend
pip3 install -r requirements.txt
```

---

## 2. 最推荐方式：一条命令全流程(执行完1.1即可执行,'sudo bash scripts/centos7_one_click.sh all')

项目已提供一键脚本：

```bash
sudo bash scripts/centos7_one_click.sh all
```

---

## 3. 分步执行方式（排错时用,下面的不用管）

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
