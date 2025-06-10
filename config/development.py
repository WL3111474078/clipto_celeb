"""
开发环境配置文件
包含开发环境特定的配置参数
"""

import os
from trans_web.config.default import *

# 服务器配置 - 开发环境使用本地IP
SERVER_HOST = '127.0.0.1'  
SERVER_PORT = 5000       
SERVER_THREADS = 1       # 开发环境只需要单线程
APPLICATION_ROOT = '/celeb'  

# 安全配置
SECRET_KEY = 'dev-key-not-secure'  # 开发环境密钥

# 日志配置
LOG_LEVEL = 'DEBUG'      # 开发环境使用DEBUG级别
LOG_MAX_SIZE = 5242880   # 5MB
LOG_BACKUP_COUNT = 3     

# 备份配置
BACKUP_INTERVAL_HOURS = 24  # 开发环境下延长备份间隔
AUTO_START_BACKUP = False   # 开发环境可选关闭自动备份 