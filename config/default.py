"""
默认配置文件
包含所有配置的默认值
"""

import os

# 基本路径配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_MAIN_DIR = os.path.join(BASE_DIR, "db_main")
DB_IMPORT_DIR = os.path.join(BASE_DIR, "db_import")
DB_EXPORT_DIR = os.path.join(BASE_DIR, "db_export")
DB_MERGE_DIR = os.path.join(BASE_DIR, "db_merge")
DB_BACKUP_DIR = os.path.join(BASE_DIR, "db_backup")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
BASE_PHOTOS_DIR = os.path.join(BASE_DIR, "base_photos")
BASE_VOICES_DIR = os.path.join(BASE_DIR, "base_voices")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
STATIC_DIR = os.path.join(BASE_DIR, "static")
STATIC_CSS_DIR = os.path.join(STATIC_DIR, "css")
STATIC_JS_DIR = os.path.join(STATIC_DIR, "js")
STATIC_IMG_DIR = os.path.join(STATIC_DIR, "img")
LOG_FILE = os.path.join(LOGS_DIR, "celebrity_app.log")
MAIN_JSON_PATH = os.path.join(DB_MAIN_DIR, "celebrity_data.json")

# 服务器配置
SERVER_HOST = '0.0.0.0'  # 监听所有网络接口
SERVER_PORT = 5000       # 服务端口
SERVER_THREADS = 4       # 工作线程数
APPLICATION_ROOT = '/celeb'  # 应用根目录（子目录部署路径）

# 安全配置
SECRET_KEY = 'dev-key-please-change-in-production'

# 日志配置
LOG_LEVEL = 'INFO'       # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_MAX_SIZE = 10485760  # 日志文件最大大小(10MB)
LOG_BACKUP_COUNT = 5     # 保留的日志文件数量

# 备份配置
BACKUP_INTERVAL_HOURS = 6  # 默认6小时备份一次
AUTO_START_BACKUP = True   # 自动启动备份功能 