# 智慧养老服务大数据分析系统

基于 Flask + Vue 3 的养老护理数据分析平台，提供健康分析、服务监控、需求预测和 AI 智能问答等功能。

## 项目简介

本系统是一个面向养老机构、护工和监管部门的多角色协作平台，采用前后端分离架构，集成了数据管理、健康分析、服务监控、需求预测和 AI 智能问答等核心功能。

### 主要特性

- **多角色权限体系**：支持机构管理员、护工、监管部门三种角色，完整的 RBAC 权限控制
- **健康分析**：老人健康状态分布、趋势分析、健康指标监测
- **服务分析**：服务频次统计、满意度分析、社区服务对比
- **需求预测**：基于机器学习的多模型服务需求预测（Random Forest、XGBoost、Ensemble）
- **AI 智能助手**：基于意图识别的养老咨询聊天机器人，支持 16 种预定义意图
- **数据管理**：社区、老人、护工、排班、健康记录、服务记录的完整 CRUD 操作
- **数据可视化**：ECharts 丰富的图表展示
- **大数据扩展**：可选的 Hadoop/HBase/Hive 集成支持

## 技术栈

### 后端

- **框架**: Flask + Flask-CORS
- **数据库**: SQLite3 (支持 Hadoop/HBase/Hive 扩展)
- **机器学习**: scikit-learn, XGBoost, joblib
- **数据处理**: pandas, numpy, Faker
- **大数据集成**: happybase (HBase), pyhive (Hive), thrift

### 前端

- **框架**: Vue 3.5+ (Composition API)
- **UI 组件库**: Element Plus 2.8+
- **路由**: Vue Router 4.4+
- **HTTP 客户端**: Axios 1.7+
- **图表库**: ECharts 5.4+
- **构建工具**: Vite 7.3+
- **语言**: TypeScript 5.9+

## 项目结构

```
flask_elderly_care/
├── backend/                    # 后端 Flask 应用
│   ├── app.py                  # 应用启动入口（端口 5008）
│   ├── app/
│   │   ├── __init__.py         # Flask 应用初始化和蓝图注册
│   │   ├── db_init.py          # 数据库初始化脚本
│   │   ├── config/
│   │   │   └── config.py       # 应用配置管理
│   │   ├── routes/             # API 路由模块
│   │   │   ├── health.py       # 健康分析 API
│   │   │   ├── service.py      # 服务分析 API
│   │   │   ├── prediction.py   # 需求预测 API
│   │   │   ├── admin.py        # 系统管理 API
│   │   │   ├── indicator.py    # 关键指标 API
│   │   │   ├── data_routes.py  # 数据管理 API
│   │   │   ├── chat_routes.py  # AI 聊天 API
│   │   │   └── common_questions.py  # 常见问题 API
│   │   ├── services/           # 业务逻辑层
│   │   │   ├── health_service.py
│   │   │   ├── service_service.py
│   │   │   ├── prediction_service.py
│   │   │   ├── admin_service.py
│   │   │   └── data_service.py
│   │   └── utils/              # 工具模块
│   │       ├── database.py     # SQLite/Hadoop 数据库封装
│   │       ├── hadoop_database.py
│   │       └── logger.py
│   ├── requirements.txt        # Python 依赖
│   ├── predictor.py            # 预测模型实现
│   ├── data_generator.py       # 模拟数据生成器
│   ├── data_cleaner.py         # 数据清洗工具
│   └── data_processor.py       # 数据处理工具
├── frontend/                   # 前端 Vue3 应用
│   ├── src/
│   │   ├── App.vue             # 主应用组件
│   │   ├── main.ts             # 应用入口
│   │   ├── router/index.ts     # 路由配置
│   │   ├── views/              # 页面视图
│   │   │   ├── LoginView.vue   # 登录页
│   │   │   ├── HomeView.vue    # 首页仪表盘
│   │   │   ├── HealthView.vue  # 健康分析页
│   │   │   ├── ServiceView.vue # 服务分析页
│   │   │   ├── PredictionView.vue  # 需求预测页
│   │   │   ├── DataView.vue    # 数据管理页
│   │   │   ├── ChatView.vue    # AI 聊天页
│   │   │   └── AdminView.vue   # 系统管理页
│   │   └── utils/
│   │       ├── auth.ts         # 认证工具
│   │       └── http.ts         # HTTP 客户端配置
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── elderly_care.sql            # MySQL 数据库 SQL 脚本
├── models/                     # 机器学习模型存储目录
└── scripts/                    # 部署脚本
    └── centos7_one_click.sh    # CentOS 一键部署脚本
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 18+
- pnpm (推荐) 或 npm

### 后端安装

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python app/db_init.py

# 启动服务（默认端口 5008）
python app.py
```

### 前端安装

```bash
cd frontend

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev
```

### 默认账户

| 用户名     | 密码   | 角色        | 说明       |
| ---------- | ------ | ----------- | ---------- |
| admin      | 123456 | institution | 机构管理员 |
| caregiver1 | 123456 | caregiver   | 护工       |
| gov        | 123456 | regulatory  | 监管部门   |

## 功能模块

### 1. 首页仪表盘

展示关键指标卡片：老人总数、服务次数、平均满意度、高危人数。

### 2. 健康分析

- 健康状态分布（良好/临界/高危）
- 按年龄段分析健康分布
- 健康状态趋势
- 健康照护建议

### 3. 服务分析

- 服务使用频次统计
- 按社区分析服务频次
- 服务满意度分析
- 服务使用趋势

### 4. 需求预测

- 多模型预测趋势（Random Forest / Gradient Boosting / XGBoost / Ensemble）
- 资源配置建议
- 模型评估指标与对比
- 异常检测
- 预测数据导出

### 5. 数据管理

- **社区管理**: 增删改查（仅机构管理员）
- **老人管理**: 分页查询、增删改（护工可新增/更新，仅机构可删除）
- **护工管理**: CRUD 操作（仅机构管理员）
- **排班管理**: 排班 CRUD（仅机构管理员）
- **健康记录**: 分页查询、上报/更新/删除（护工权限）
- **服务记录**: 分页查询、提交/更新/删除（护工权限）
- **预测结果**: 分页查询（所有角色）
- **社区报表**: 全景统计数据（机构和监管）

### 6. AI 智能聊天

支持 16 种预定义意图：

- 问候、感谢、帮助
- 最大需求查询、满意度查询
- 社区需求分析、健康状况查询
- 老人数量、服务类型、社区数量
- 平均年龄、服务次数查询
- 服务详情、健康建议、服务流程

特点：

- 基于关键词匹配的意图识别
- 实体抽取（社区名、服务类型）
- 上下文记忆支持多轮对话
- 直接查询数据库获取实时数据

### 7. 系统管理

- 数据清洗
- 模型训练
- 重新生成模拟数据
- 操作日志查看
- 数据质量检查

## API 接口

### 健康分析 API (`/api/health`)

| 方法 | 路径                | 说明         |
| ---- | ------------------- | ------------ |
| GET  | `/distribution`     | 健康状态分布 |
| GET  | `/distribution/age` | 按年龄段分布 |
| GET  | `/trend`            | 健康趋势     |
| GET  | `/recommendations`  | 健康建议     |

### 服务分析 API (`/api/service`)

| 方法 | 路径                   | 说明       |
| ---- | ---------------------- | ---------- |
| GET  | `/frequency`           | 服务频次   |
| GET  | `/frequency/community` | 按社区频次 |
| GET  | `/satisfaction`        | 满意度     |
| GET  | `/trend`               | 服务趋势   |

### 需求预测 API (`/api/prediction`)

| 方法 | 路径                        | 说明     |
| ---- | --------------------------- | -------- |
| GET  | `/trend`                    | 预测趋势 |
| GET  | `/resource/recommendations` | 资源建议 |
| GET  | `/model/metrics`            | 模型指标 |
| GET  | `/model/comparison`         | 模型对比 |
| POST | `/model/train`              | 训练模型 |
| GET  | `/anomalies`                | 异常检测 |
| GET  | `/export`                   | 导出数据 |

### 数据管理 API (`/api/data`)

| 方法       | 路径                    | 说明              |
| ---------- | ----------------------- | ----------------- |
| GET        | `/stats`                | 数据统计概览      |
| GET/POST   | `/communities`          | 社区列表/新增     |
| PUT/DELETE | `/communities/<id>`     | 社区更新/删除     |
| GET/POST   | `/seniors`              | 老人列表/新增     |
| PUT/DELETE | `/seniors/<id>`         | 老人更新/删除     |
| GET/POST   | `/caregivers`           | 护工列表/新增     |
| PUT/DELETE | `/caregivers/<id>`      | 护工更新/删除     |
| GET/POST   | `/schedules`            | 排班列表/新增     |
| PUT/DELETE | `/schedules/<id>`       | 排班更新/删除     |
| GET/POST   | `/health-records`       | 健康记录列表/上报 |
| PUT/DELETE | `/health-records/<id>`  | 健康记录更新/删除 |
| GET/POST   | `/service-records`      | 服务记录列表/提交 |
| PUT/DELETE | `/service-records/<id>` | 服务记录更新/删除 |
| GET        | `/services`             | 服务类型列表      |
| GET        | `/predictions`          | 预测结果          |
| GET        | `/reports/community`    | 社区报表          |

### AI 聊天 API (`/api/chat`)

| 方法 | 路径                | 说明     |
| ---- | ------------------- | -------- |
| POST | `/`                 | 发送消息 |
| GET  | `/initial`          | 初始消息 |
| GET  | `/common-questions` | 常见问题 |
| POST | `/emergency`        | 紧急预警 |

### 系统管理 API (`/api`)

| 方法 | 路径            | 说明     |
| ---- | --------------- | -------- |
| POST | `/clean`        | 数据清洗 |
| POST | `/train`        | 模型训练 |
| POST | `/generate`     | 生成数据 |
| GET  | `/logs`         | 操作日志 |
| GET  | `/data-quality` | 数据质量 |

## 角色权限

| 功能模块   | 机构管理员 | 护工 | 监管部门 |
| ---------- | ---------- | ---- | -------- |
| 首页仪表盘 | ✓          | ✓    | ✓        |
| 健康分析   | ✓          | ✓    | ✓        |
| 服务分析   | ✓          | ✓    | ✓        |
| 需求预测   | ✓          | ✗    | ✓        |
| 数据管理   | ✓          | ✓    | ✓        |
| AI 聊天    | ✓          | ✓    | ✗        |
| 系统管理   | ✓          | ✗    | ✗        |

## 数据库设计

### 主要数据表

| 表名                | 说明          |
| ------------------- | ------------- |
| `users`             | 用户表 (RBAC) |
| `community`         | 社区表        |
| `elderly`           | 老人表        |
| `caregiver`         | 护工表        |
| `schedule`          | 排班表        |
| `health_record`     | 健康记录表    |
| `service_record`    | 服务记录表    |
| `prediction_result` | 预测结果表    |

详细表结构请参考 `elderly_care.sql` 文件。

## 环境变量配置

### 后端配置

在 `backend/app/config/config.py` 中配置：

```python
SECRET_KEY = 'dev-secret-key'  # 可通过环境变量设置
DEBUG = True
DATABASE_PATH = 'backend/data/database/elderly_care.db'
MODEL_PATH = 'backend/models/'
API_PREFIX = '/api'
LOG_LEVEL = 'INFO'
```

### 前端配置

创建 `frontend/.env` 文件：

```
VITE_API_BASE=http://localhost:5008  # API 基础 URL
```

### 可选环境变量

| 变量名       | 说明        | 默认值           |
| ------------ | ----------- | ---------------- |
| `SECRET_KEY` | Flask 密钥  | `dev-secret-key` |
| `DEBUG`      | 调试模式    | `True`           |
| `FLASK_ENV`  | 运行环境    | `development`    |
| `LOG_LEVEL`  | 日志级别    | `INFO`           |
| `USE_HADOOP` | 启用 Hadoop | `False`          |

## 部署

### 本地开发

参考 [快速开始](#快速开始) 章节。

### CentOS 一键部署

```bash
chmod +x scripts/centos7_one_click.sh
./scripts/centos7_one_click.sh
```

## 常见问题

### 1. 数据库初始化失败

确保 `backend/data/database/` 目录存在且有写入权限：

```bash
mkdir -p backend/data/database
```

### 2. 前端无法连接后端

检查 `frontend/.env` 中的 `VITE_API_BASE` 是否配置正确，确保后端服务已启动。

### 3. 模型训练失败

确保 `backend/models/` 目录存在：

```bash
mkdir -p backend/models
```

### 4. DataView 页面数据未加载

检查浏览器控制台是否有 API 请求错误，确认后端服务正常运行且 API 路径正确。

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'Add some feature'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

## 许可证

本项目仅供学习和研究使用。

## 联系方式

如有问题或建议，请通过 Gitee Issue 反馈。
