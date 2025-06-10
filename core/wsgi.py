"""
WSGI应用配置
用于生产环境部署
"""

import os
import sys
import logging

# 配置日志记录器
logger = logging.getLogger('celebrity_app.wsgi')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    logger.debug(f"已添加项目根目录到Python路径: {project_root}")

# 设置环境变量（如果未设置）
if 'SCRIPT_NAME' not in os.environ:
    os.environ['SCRIPT_NAME'] = '/celeb'
if 'PYTHONPATH' not in os.environ:
    os.environ['PYTHONPATH'] = project_root

logger.debug(f"WSGI环境变量: SCRIPT_NAME={os.environ.get('SCRIPT_NAME')}, "
             f"PYTHONPATH={os.environ.get('PYTHONPATH')}")

# 创建应用工厂函数
def application(environ=None, start_response=None, config_mode='production', debug=False, no_auth=False):
    """
    WSGI应用入口
    
    参数:
    - environ: WSGI环境字典
    - start_response: WSGI回调函数
    - config_mode: 配置模式
    - debug: 是否启用调试模式
    - no_auth: 是否禁用认证
    
    返回:
    - 如果提供了environ和start_response，返回WSGI应用响应
    - 否则返回Flask应用实例
    """
    # 导入应用工厂函数
    try:
        from trans_web.core.app import create_app
        
        # 如果未明确指定，检查环境变量中的认证设置
        if environ is not None and start_response is not None:
            # WSGI调用模式，需要从环境变量获取认证设置
            no_auth = os.environ.get('DISABLE_AUTH') == 'true'
            debug = os.environ.get('FLASK_DEBUG') == '1' or config_mode == 'development'
        
        # 获取或创建应用实例
        app = create_app(
            config_mode=config_mode, 
            debug=debug, 
            no_auth=no_auth
        )
        logger.debug(f"已创建Flask应用实例，配置模式: {config_mode}, 调试模式: {debug}, 无认证模式: {no_auth}")
        
        # 确保应用配置正确
        if no_auth:
            app.config['AUTH_ENABLED'] = False
            logger.warning("认证已禁用，无需登录即可访问应用")
        else:
            app.config['AUTH_ENABLED'] = True
            logger.debug("认证已启用，需要登录才能访问应用")
            
        # 设置会话配置
        app.config.update(
            SESSION_COOKIE_PATH='/',  # 确保会话在所有路径下有效
            SESSION_COOKIE_HTTPONLY=True
        )
        
        # 检查是WSGI调用还是直接获取应用实例
        if environ and start_response:
            logger.debug("作为WSGI应用调用")
            return app(environ, start_response)
        else:
            logger.debug("返回Flask应用实例")
            return app
            
    except Exception as e:
        logger.error(f"创建应用实例失败: {e}", exc_info=True)
        
        # 如果是WSGI调用，返回错误响应
        if environ and start_response:
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [f"应用初始化错误: {str(e)}".encode('utf-8')]
        # 否则重新抛出异常
        raise

# 为兼容性提供app变量
app = application() 