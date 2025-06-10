"""
中间件定义
包含所有WSGI中间件
"""

import logging
import re
import os
from urllib.parse import urlparse

# 创建日志记录器
logger = logging.getLogger('celebrity_app.middleware')

class ReverseProxied:
    """
    中间件，用于处理反向代理情况下的URL处理
    确保应用可以在子目录中正常工作
    """
    
    def __init__(self, app, script_name=None):
        self.app = app
        self.script_name = script_name
        
        # 如果没有提供script_name，尝试从环境变量获取
        if self.script_name is None:
            self.script_name = os.environ.get('SCRIPT_NAME', '')
        
        # 确保script_name不以/结尾
        if self.script_name.endswith('/'):
            self.script_name = self.script_name[:-1]
            
        # 确保script_name以/开头（如果不为空）
        if self.script_name and not self.script_name.startswith('/'):
            self.script_name = '/' + self.script_name
            
        logger.info(f"初始化ReverseProxied中间件，script_name={self.script_name}")
    
    def __call__(self, environ, start_response):
        script_name = self.script_name
        
        # 如果环境变量中已有SCRIPT_NAME，则尊重它
        if 'SCRIPT_NAME' in environ:
            script_name = environ.get('SCRIPT_NAME', '')
            
        # 记录原始路径信息（调试用）
        original_script_name = environ.get('SCRIPT_NAME', '')
        original_path_info = environ.get('PATH_INFO', '')
        
        # 如果路径和script_name重复，修正它
        path_info = environ.get('PATH_INFO', '')
        if script_name and path_info.startswith(script_name):
            path_info = path_info[len(script_name):]
            if not path_info:
                path_info = '/'
            environ['PATH_INFO'] = path_info
            logger.debug(f"修正PATH_INFO: {original_path_info} -> {path_info} (移除重复的script_name)")
        
        # 特殊处理根路径
        if path_info == '/' and script_name:
            environ['PATH_INFO'] = '/'
            logger.debug("保留根路径PATH_INFO='/'")
            
        # 修复直接访问子目录根路径的情况
        if original_path_info == '/celeb/' and script_name == '/celeb':
            environ['PATH_INFO'] = '/'
            logger.debug("修正子目录根路径: /celeb/ -> /")
        
        # 设置SCRIPT_NAME
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            logger.debug(f"设置SCRIPT_NAME={script_name}")
        
        # 处理特殊的重定向跳转
        if environ.get('REQUEST_METHOD') == 'GET':
            query_string = environ.get('QUERY_STRING', '')
            if query_string.startswith('next='):
                import urllib.parse
                next_url = urllib.parse.unquote(query_string[5:])
                logger.debug(f"检测到重定向参数: next={next_url}")
                
                # 如果next参数包含script_name前缀，并且script_name已经设置，修正它
                if script_name and next_url.startswith(script_name):
                    next_url = next_url[len(script_name):]
                    if not next_url:
                        next_url = '/'
                    # 重新编码查询字符串
                    environ['QUERY_STRING'] = f"next={urllib.parse.quote(next_url)}"
                    logger.debug(f"修正重定向参数: next={next_url}")
        
        # 打印详细调试信息
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"请求处理: {environ.get('REQUEST_METHOD')} {original_path_info}")
            logger.debug(f"  - 原始SCRIPT_NAME: {original_script_name}")
            logger.debug(f"  - 原始PATH_INFO: {original_path_info}")
            logger.debug(f"  - 修改后SCRIPT_NAME: {environ.get('SCRIPT_NAME')}")
            logger.debug(f"  - 修改后PATH_INFO: {environ.get('PATH_INFO')}")
            logger.debug(f"  - QUERY_STRING: {environ.get('QUERY_STRING')}")
        
        # 确保错误处理正确
        try:
            return self.app(environ, start_response)
        except Exception as e:
            logger.error(f"中间件处理请求错误: {str(e)}", exc_info=True)
            # 返回错误响应
            status = '500 Internal Server Error'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return [b"Internal Server Error"] 