-- =====================================================
-- 养老系统数据库 SQL 语句整理
-- 文件: elderly_care.sql
-- 说明: 包含所有表结构、初始数据、查询语句（MySQL兼容）
-- =====================================================


-- =====================================================
-- 第一部分：表结构创建 (CREATE TABLE)
-- =====================================================

-- -----------------------------------------------------
-- 1.1 社区表 (community)
-- 用途: 存储社区基本信息
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `community` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `community_id` VARCHAR(50) UNIQUE COMMENT '社区ID',
    `name` VARCHAR(100) COMMENT '社区名称',
    `population` INT DEFAULT 0 COMMENT '总人口',
    `elderly_count` INT DEFAULT 0 COMMENT '老年人口数量',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_community_id` (`community_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='社区信息表';

-- -----------------------------------------------------
-- 1.2 老人表 (elderly) - 主表
-- 用途: 存储老人详细信息，主表
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `elderly` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `elderly_id` VARCHAR(36) UNIQUE COMMENT '老人唯一ID',
    `name` VARCHAR(50) COMMENT '姓名',
    `age` INT COMMENT '年龄',
    `gender` VARCHAR(10) COMMENT '性别（男/女）',
    `community_id` VARCHAR(50) COMMENT '所属社区',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_elderly_id` (`elderly_id`),
    KEY `idx_community_id` (`community_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='老人信息主表';

-- -----------------------------------------------------
-- 1.3 健康记录表 (health_record)
-- 用途: 存储老人健康监测数据，主表
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `health_record` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `elderly_id` VARCHAR(36) COMMENT '关联老人ID',
    `record_date` VARCHAR(20) COMMENT '记录日期',
    `sbp` INT COMMENT '收缩压（高压）',
    `dbp` INT COMMENT '舒张压（低压）',
    `blood_sugar` DECIMAL(5,2) COMMENT '血糖值',
    `heart_rate` INT COMMENT '心率',
    `health_status` VARCHAR(20) COMMENT '健康状态',
    PRIMARY KEY (`id`),
    KEY `idx_elderly_id` (`elderly_id`),
    KEY `idx_record_date` (`record_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='健康记录主表';

-- -----------------------------------------------------
-- 1.4 服务记录表 (service_record)
-- 用途: 存储老人接受服务记录，主表
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `service_record` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `elderly_id` VARCHAR(36) COMMENT '关联老人ID',
    `community_id` VARCHAR(50) COMMENT '所属社区',
    `service_type` VARCHAR(20) COMMENT '服务类型',
    `service_date` VARCHAR(20) COMMENT '服务日期',
    `duration` INT COMMENT '服务时长（分钟）',
    `satisfaction` INT COMMENT '满意度评分（1-5）',
    PRIMARY KEY (`id`),
    KEY `idx_elderly_id` (`elderly_id`),
    KEY `idx_service_date` (`service_date`),
    KEY `idx_service_type` (`service_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='服务记录主表';

-- -----------------------------------------------------
-- 1.5 预测结果表 (prediction_result)
-- 用途: 存储服务需求预测结果
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `prediction_result` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `community_id` VARCHAR(50) COMMENT '社区ID',
    `service_type` VARCHAR(20) COMMENT '服务类型',
    `predict_date` VARCHAR(20) COMMENT '预测日期',
    `predicted_demand` DECIMAL(10,2) COMMENT '预测需求量',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`),
    KEY `idx_community_id` (`community_id`),
    KEY `idx_service_type` (`service_type`),
    KEY `idx_predict_date` (`predict_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='服务需求预测结果表';

-- =====================================================
-- 第二部分：初始数据插入 (INSERT INTO)
-- =====================================================

-- -----------------------------------------------------
-- 2.1 插入社区数据
-- 用途: 系统初始化时填充基础社区数据
-- -----------------------------------------------------
INSERT INTO `community` (`community_id`, `name`, `population`, `elderly_count`) VALUES
('C001', '社区A', 5000, 800),
('C002', '社区B', 8000, 1200),
('C003', '社区C', 6000, 950),
('C004', '社区D', 4500, 700),
('C005', '社区E', 7000, 1100);

-- -----------------------------------------------------
-- 2.2 插入老人数据 (elderly)
-- 用途: 系统初始化时填充基础老人数据
-- -----------------------------------------------------
INSERT INTO `elderly` (`elderly_id`, `name`, `age`, `gender`, `community_id`) VALUES
('E00001', '张三', 65, '男', 'C001'),
('E00002', '李四', 72, '男', 'C001'),
('E00003', '王五', 68, '女', 'C002'),
('E00004', '赵六', 75, '男', 'C002'),
('E00005', '钱七', 70, '女', 'C003'),
('E00006', '孙八', 69, '男', 'C003'),
('E00007', '周九', 71, '女', 'C004'),
('E00008', '吴十', 73, '男', 'C004'),
('E00009', '郑十一', 67, '女', 'C005'),
('E00010', '王十二', 74, '男', 'C005');

-- -----------------------------------------------------
-- 2.3 插入健康记录数据 (health_record)
-- 用途: 系统初始化时填充基础健康数据
-- -----------------------------------------------------
INSERT INTO `health_record` (`elderly_id`, `record_date`, `sbp`, `dbp`, `blood_sugar`, `heart_rate`, `health_status`) VALUES
('E00001', '2024-01-01', 120, 80, 5.6, 72, '良好'),
('E00001', '2024-01-08', 118, 78, 5.5, 70, '良好'),
('E00002', '2024-01-02', 130, 85, 6.1, 75, '临界'),
('E00002', '2024-01-09', 132, 86, 6.2, 76, '临界'),
('E00003', '2024-01-03', 115, 75, 5.4, 68, '良好'),
('E00003', '2024-01-10', 116, 76, 5.3, 69, '良好'),
('E00004', '2024-01-04', 145, 90, 7.2, 80, '高危'),
('E00004', '2024-01-11', 148, 92, 7.3, 82, '高危'),
('E00005', '2024-01-05', 118, 78, 5.5, 71, '良好'),
('E00005', '2024-01-12', 119, 79, 5.6, 72, '良好');

-- -----------------------------------------------------
-- 2.4 插入服务记录数据 (service_record)
-- 用途: 系统初始化时填充基础服务数据
-- -----------------------------------------------------
INSERT INTO `service_record` (`elderly_id`, `community_id`, `service_type`, `service_date`, `duration`, `satisfaction`) VALUES
('E00001', 'C001', '助餐', '2024-01-01', 60, 5),
('E00001', 'C001', '助医', '2024-01-08', 45, 4),
('E00002', 'C001', '保洁', '2024-01-02', 90, 4),
('E00002', 'C001', '陪护', '2024-01-09', 120, 5),
('E00003', 'C002', '助餐', '2024-01-03', 60, 5),
('E00003', 'C002', '康复', '2024-01-10', 60, 5),
('E00004', 'C002', '助医', '2024-01-04', 45, 4),
('E00004', 'C002', '陪护', '2024-01-11', 120, 4),
('E00005', 'C003', '助餐', '2024-01-05', 60, 5),
('E00005', 'C003', '保洁', '2024-01-12', 90, 5);

-- -----------------------------------------------------
-- 2.5 插入预测结果数据 (prediction_result)
-- 用途: 系统初始化时填充预测数据
-- -----------------------------------------------------
INSERT INTO `prediction_result` (`community_id`, `service_type`, `predict_date`, `predicted_demand`) VALUES
('C001', '助餐', '2024-02-01', 120.00),
('C001', '助医', '2024-02-01', 45.00),
('C002', '助餐', '2024-02-01', 150.00),
('C002', '保洁', '2024-02-01', 80.00),
('C003', '陪护', '2024-02-01', 60.00);


-- =====================================================
-- 第三部分：数据查询 (SELECT) - 常用查询模板
-- =====================================================

-- -----------------------------------------------------
-- 3.1 统计查询
-- -----------------------------------------------------

-- 统计老人总数
SELECT COUNT(*) AS total FROM `elderly`;

-- 统计健康记录数
SELECT COUNT(*) AS total FROM `health_record`;

-- 统计服务记录数
SELECT COUNT(*) AS total FROM `service_record`;

-- 统计社区数量
SELECT COUNT(DISTINCT community_id) AS total FROM `elderly`;

-- 获取所有社区列表
SELECT DISTINCT community_id FROM `elderly`;

-- -----------------------------------------------------
-- 3.2 老人数据查询
-- -----------------------------------------------------

-- 分页查询老人基本信息
SELECT `id`, `elderly_id`, `name`, `age`, `community_id` 
FROM `elderly`
LIMIT 20 OFFSET 0;

-- 按社区筛选老人
SELECT `id`, `elderly_id`, `name`, `age`, `community_id` 
FROM `elderly`
WHERE `community_id` = 'C001';

-- 查询老人最新健康状态
SELECT `health_status` 
FROM `health_record` 
WHERE `elderly_id` = 'E00001' 
ORDER BY `record_date` DESC 
LIMIT 1;

-- 查询老人服务次数
SELECT COUNT(*) AS service_count
FROM `service_record` 
WHERE `elderly_id` = 'E00001';

-- 查询老人平均满意度
SELECT AVG(satisfaction) AS avg_satisfaction
FROM `service_record` 
WHERE `elderly_id` = 'E00001';

-- -----------------------------------------------------
-- 3.3 健康记录查询
-- -----------------------------------------------------

-- 分页查询健康记录
SELECT `id`, `elderly_id`, `record_date`, `sbp`, `dbp`, `blood_sugar`, `heart_rate`, `health_status`
FROM `health_record`
ORDER BY `record_date` DESC 
LIMIT 20 OFFSET 0;

-- 按日期范围查询健康记录
SELECT `id`, `elderly_id`, `record_date`, `sbp`, `dbp`, `blood_sugar`, `heart_rate`, `health_status`
FROM `health_record`
WHERE `record_date` >= '2024-01-01' 
  AND `record_date` <= '2024-12-31'
ORDER BY `record_date` DESC;

-- 查询健康状态分布
SELECT `health_status`, COUNT(*) AS count
FROM `health_record`
WHERE `record_date` = (
    SELECT MAX(`record_date`) FROM `health_record` hr2 
    WHERE hr2.elderly_id = `health_record`.elderly_id
)
GROUP BY `health_status`;

-- -----------------------------------------------------
-- 3.4 服务记录查询
-- -----------------------------------------------------

-- 分页查询服务记录
SELECT `id`, `elderly_id`, `service_date`, `service_type`, `satisfaction`, `community_id`
FROM `service_record`
ORDER BY `service_date` DESC 
LIMIT 20 OFFSET 0;

-- 按服务类型筛选服务记录
SELECT `id`, `elderly_id`, `service_date`, `service_type`, `satisfaction`, `community_id`
FROM `service_record`
WHERE `service_type` = '助餐'
ORDER BY `service_date` DESC;

-- -----------------------------------------------------
-- 3.5 社区数据查询
-- -----------------------------------------------------

-- 查询所有社区及其老人数量
SELECT c.`community_id`, c.`name`, c.`population`, c.`elderly_count`,
       (SELECT COUNT(*) FROM `elderly` e WHERE e.`community_id` = c.`community_id`) AS actual_elderly_count
FROM `community` c;

-- -----------------------------------------------------
-- 3.6 预测结果查询
-- -----------------------------------------------------

-- 查询预测结果
SELECT `community_id`, `service_type`, `predict_date`, `predicted_demand`
FROM `prediction_result`
ORDER BY `predict_date` DESC;

-- 按社区查询预测结果
SELECT `community_id`, `service_type`, `predict_date`, `predicted_demand`
FROM `prediction_result`
WHERE `community_id` = 'C001'
ORDER BY `predict_date` DESC;


-- =====================================================
-- 第四部分：数据删除 (DELETE)
-- =====================================================

-- 清空健康记录表
DELETE FROM `health_record`;

-- 清空服务记录表
DELETE FROM `service_record`;


-- =====================================================
-- 附录：数据字典
-- =====================================================

-- 健康状态判断标准
-- 高危: sbp >= 180 OR dbp >= 110 OR blood_sugar >= 11.1 OR heart_rate > 140
-- 临界: (sbp >= 140 OR dbp >= 90) OR (blood_sugar >= 7.0) OR (heart_rate > 100)
-- 良好: 其他情况

-- 服务类型说明
-- 助餐: 餐饮配送服务
-- 助医: 医疗陪护服务
-- 保洁: 居家清洁服务
-- 陪护: 专人陪护服务
-- 康复: 康复训练服务

-- 满意度评分标准
-- 5: 非常满意
-- 4: 满意
-- 3: 一般
-- 2: 不满意
-- 1: 非常不满意

-- 表关系说明
-- community (主表) 1:N elderly
-- elderly (主表) 1:N health_record
-- elderly (主表) 1:N service_record

-- 主表与兼容表对应关系
-- elderly -> seniors (老人信息)
-- health_record -> health_records (健康记录)
-- service_record -> service_records (服务记录)