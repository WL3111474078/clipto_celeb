"""
生产环境配置文件
包含生产环境特定的配置参数
"""

import os
from trans_web.config.default import *

# 服务器配置
SERVER_HOST = '0.0.0.0'  # 监听所有网络接口
SERVER_PORT = 5000       # 服务端口
SERVER_THREADS = 8       # 工作线程数
APPLICATION_ROOT = '/celeb'  # 应用根目录（子目录部署路径）

# 安全配置
SECRET_KEY = 'your-very-secret-key-change-this'  # 应用密钥，请修改为复杂的随机字符串

# 日志配置
LOG_LEVEL = 'INFO'       # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_MAX_SIZE = 10485760  # 日志文件最大大小(10MB)
LOG_BACKUP_COUNT = 10    # 保留的日志文件数量

# 备份配置
BACKUP_INTERVAL_HOURS = 12  # 生产环境下备份间隔小时数
AUTO_START_BACKUP = True    # 是否自动启动备份功能 