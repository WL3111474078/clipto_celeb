"""
备份调度器模块
提供定时备份功能
"""

import os
import threading
import time
from datetime import datetime

class BackupScheduler:
    """备份调度器类，用于定时备份数据库文件"""
    
    def __init__(self, app):
        """初始化备份调度器
        
        参数:
        - app: Flask应用实例
        """
        self.app = app
        self.interval = app.config.get('BACKUP_INTERVAL_HOURS', 6) * 3600  # 转换为秒
        self.running = False
        self.thread = None
        self.logger = app.logger
        
        # 自动启动
        if app.config.get('AUTO_START_BACKUP', True):
            self.start()
    
    def start(self):
        """启动备份调度器"""
        if self.running:
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._backup_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"备份调度器已启动，间隔时间: {self.interval/3600:.1f}小时")
        return True
    
    def stop(self):
        """停止备份调度器"""
        if not self.running:
            return False
        
        self.running = False
        if self.thread:
            self.thread.join(1.0)  # 等待线程结束，最多1秒
        
        self.logger.info("备份调度器已停止")
        return True
    
    def set_interval(self, hours):
        """设置备份间隔时间
        
        参数:
        - hours: 间隔小时数
        """
        if hours < 1:
            hours = 1
        
        self.interval = hours * 3600  # 转换为秒
        self.logger.info(f"备份间隔已更新为: {hours}小时")
        return True
    
    def _backup_loop(self):
        """备份循环，在单独的线程中运行"""
        while self.running:
            # 先睡眠，避免启动时立即备份
            for _ in range(self.interval):
                if not self.running:
                    return
                time.sleep(1)
            
            # 执行备份
            self.perform_backup()
    
    def perform_backup(self):
        """执行一次备份"""
        try:
            from trans_web.utils.utils import backup_main_db
            
            source_file = self.app.config['MAIN_JSON_PATH']
            backup_dir = self.app.config['DB_BACKUP_DIR']
            
            self.logger.info("开始执行数据库备份...")
            result = backup_main_db(source_file, backup_dir)
            
            if os.path.exists(result):
                self.logger.info(f"备份成功: {result}")
                return True, result
            else:
                self.logger.error(f"备份失败: {result}")
                return False, result
                
        except Exception as e:
            self.logger.error(f"备份过程中发生错误: {str(e)}", exc_info=True)
            return False, str(e) 