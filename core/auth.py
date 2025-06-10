#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
认证模块
提供基本的用户登录验证功能
"""

import os
import json
import time
import logging
from functools import wraps
from flask import session, redirect, url_for, request, flash, Blueprint, render_template, jsonify

# 配置日志
logger = logging.getLogger('celebrity_app.auth')

# 创建认证蓝图
auth_bp = Blueprint('auth', __name__)

# 用户数据文件路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
USERS_FILE = os.path.join(PARENT_DIR, 'config', 'users.json')

# 确保用户配置文件存在
def ensure_users_file():
    """确保用户配置文件存在"""
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)
    if not os.path.exists(USERS_FILE):
        # 创建默认用户
        default_users = {
            "admin": {"name": "管理员", "password": "admin123"},
            "user": {"name": "普通用户", "password": "user123"}
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=2)
        logger.info(f"已创建默认用户配置文件: {USERS_FILE}")

# 加载用户数据
def load_users():
    """加载用户数据"""
    ensure_users_file()
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载用户数据失败: {str(e)}")
        return {}

# 保存用户数据
def save_users(users):
    """保存用户数据"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"保存用户数据失败: {str(e)}")
        return False

# 登录验证装饰器
def login_required(f):
    """确保用户已经登录的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"未授权访问: {request.path} - 用户未登录")
            # 保存请求的URL以便登录后重定向
            if request.path.startswith('/celeb/'):
                session['next'] = request.path
                login_url = '/celeb/auth/login'
            else:
                session['next'] = request.path
                login_url = url_for('auth.login')
                
            return redirect(login_url)
        return f(*args, **kwargs)
    return decorated_function

# 管理员权限验证装饰器
def admin_required(f):
    """确保用户是管理员的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning(f"未授权访问: {request.path} - 用户未登录")
            # 保存请求的URL以便登录后重定向
            if request.path.startswith('/celeb/'):
                session['next'] = request.path
                login_url = '/celeb/auth/login'
            else:
                session['next'] = request.path
                login_url = url_for('auth.login')
                
            return redirect(login_url)
        if not session.get('is_admin', False):
            logger.warning(f"未授权访问: {request.path} - 用户 {session.get('user_name')} 不是管理员")
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated_function

# 路由: 登录页面
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    error = None
    next_url = request.args.get('next', '/')
    
    # 调试日志
    logger.info(f"登录尝试，next_url={next_url}, session={session}")
    
    # 如果已登录，直接重定向
    if 'user_id' in session:
        logger.info(f"用户已登录，重定向到 {next_url}")
        return redirect(next_url)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # 硬编码固定的用户名和密码
        if username == 'Lingganshike' and password == 'LGSK1203':
            # 登录成功，设置会话
            session.permanent = True
            session['user_id'] = username
            session['user_name'] = '灵感时刻'
            session['login_time'] = time.time()
            session['is_admin'] = True  # 设置为管理员权限
            
            # 获取登录后要跳转的URL，确保不会跳回登录页
            redirect_url = session.pop('next_url', next_url)
            logger.info(f"用户 {username} 登录成功，将重定向到 {redirect_url}")
            
            # 确保首页重定向正确，无论是否有SCRIPT_NAME设置
            if redirect_url in ['/', ''] or redirect_url.startswith('/auth/login'):
                # 直接使用固定路径，确保能正确跳转到首页
                if os.environ.get('SCRIPT_NAME') == '/celeb':
                    redirect_url = '/celeb/'
                else:
                    redirect_url = '/'
                logger.debug(f"强制设置首页重定向URL: {redirect_url}")
            
            # 确保显式地返回重定向，不进行其他处理
            logger.info(f"最终重定向URL: {redirect_url}")
            return redirect(redirect_url)
        else:
            # 登录失败
            error = "用户名或密码不正确"
            logger.warning(f"用户 {username} 登录失败")
    
    try:
        logger.debug(f"尝试渲染login.html模板，提交路径: {request.path}, 模板文件: {os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates', 'login.html')}")
        return render_template('login.html', error=error, next=next_url)
    except Exception as e:
        logger.error(f"渲染login.html失败: {str(e)}", exc_info=True)
        return f"登录页面加载失败: {str(e)}", 500

# 路由: 登出
@auth_bp.route('/logout')
def logout():
    """登出"""
    user_id = session.pop('user_id', None)
    user_name = session.pop('user_name', None)
    if user_id:
        logger.info(f"用户 {user_id} ({user_name}) 已登出")
    
    # 确保完全清除会话
    session.clear()
    
    # 直接使用明确的路径进行重定向，并考虑子目录
    login_path = '/auth/login'
    if os.environ.get('SCRIPT_NAME') == '/celeb':
        login_path = '/celeb/auth/login'
    logger.info(f"登出后重定向到 {login_path}")
    return redirect(login_path)

# 路由: 用户管理页面
@auth_bp.route('/users', methods=['GET'])
@admin_required
def manage_users():
    """用户管理页面"""
    users = load_users()
    success = request.args.get('success')
    error = request.args.get('error')
    return render_template('user_management.html', users=users, success=success, error=error)

# 路由: 添加用户
@auth_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    """添加用户"""
    username = request.form.get('username')
    display_name = request.form.get('display_name')
    password = request.form.get('password')
    
    if not username or not display_name or not password:
        return redirect(url_for('auth.manage_users', error='用户名、显示名称和密码不能为空'))
    
    users = load_users()
    
    if username in users:
        return redirect(url_for('auth.manage_users', error=f'用户 {username} 已存在'))
    
    # 添加新用户
    users[username] = {
        'name': display_name,
        'password': password
    }
    
    if save_users(users):
        logger.info(f"管理员 {session.get('user_id')} 添加了新用户: {username} ({display_name})")
        return redirect(url_for('auth.manage_users', success=f'用户 {username} 添加成功'))
    else:
        return redirect(url_for('auth.manage_users', error='保存用户数据失败'))

# 路由: 编辑用户
@auth_bp.route('/users/edit', methods=['POST'])
@admin_required
def edit_user():
    """编辑用户"""
    username = request.form.get('username')
    display_name = request.form.get('display_name')
    password = request.form.get('password')
    
    if not username or not display_name:
        return redirect(url_for('auth.manage_users', error='用户名和显示名称不能为空'))
    
    users = load_users()
    
    if username not in users:
        return redirect(url_for('auth.manage_users', error=f'用户 {username} 不存在'))
    
    # 更新用户信息
    users[username]['name'] = display_name
    
    # 如果提供了新密码，则更新密码
    if password:
        users[username]['password'] = password
    
    if save_users(users):
        logger.info(f"管理员 {session.get('user_id')} 编辑了用户: {username}")
        return redirect(url_for('auth.manage_users', success=f'用户 {username} 更新成功'))
    else:
        return redirect(url_for('auth.manage_users', error='保存用户数据失败'))

# 路由: 删除用户
@auth_bp.route('/users/delete', methods=['POST'])
@admin_required
def delete_user():
    """删除用户"""
    username = request.form.get('username')
    
    if not username:
        return redirect(url_for('auth.manage_users', error='用户名不能为空'))
    
    if username == 'admin':
        return redirect(url_for('auth.manage_users', error='不能删除管理员账号'))
    
    users = load_users()
    
    if username not in users:
        return redirect(url_for('auth.manage_users', error=f'用户 {username} 不存在'))
    
    # 删除用户
    deleted_user_name = users[username]['name']
    del users[username]
    
    if save_users(users):
        logger.info(f"管理员 {session.get('user_id')} 删除了用户: {username} ({deleted_user_name})")
        return redirect(url_for('auth.manage_users', success=f'用户 {username} 删除成功'))
    else:
        return redirect(url_for('auth.manage_users', error='保存用户数据失败'))

# 初始化认证模块
def init_auth(app):
    """初始化认证模块"""
    # 确保用户配置文件存在
    ensure_users_file()
    
    # 设置会话密钥和配置
    if not app.config.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'celebrity_default_secret_key')
    
    # 设置会话有效期（12小时）和安全配置
    app.config['PERMANENT_SESSION_LIFETIME'] = 43200
    app.config['SESSION_TYPE'] = 'filesystem'
    # 不要设置SESSION_COOKIE_PATH，让Flask根据SCRIPT_NAME自动处理
    app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境设为False
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止XSS攻击
    
    # 注册蓝图
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # 添加全局变量
    @app.context_processor
    def inject_user():
        return dict(
            user_id=session.get('user_id', None),
            user_name=session.get('user_name', None),
            is_authenticated='user_id' in session,
            is_admin=session.get('is_admin', False) or session.get('user_id') == 'Lingganshike'
        )
    
    # 添加全局拦截器
    @app.before_request
    def check_auth():
        """检查认证状态"""
        # 排除不需要登录的路径
        exempt_paths = [
            '/auth/login', 
            '/auth/logout',
            '/static/'
        ]
        
        # 调试日志
        logger.debug(f"验证请求: path={request.path}, session={session}")
        
        # 如果请求路径是排除路径，则不检查登录状态
        path = request.path
        for exempt in exempt_paths:
            if path.startswith(exempt):
                return None
        
        # 如果未登录，重定向到登录页面
        if 'user_id' not in session:
            logger.info(f"未登录访问: {path}, 重定向到登录页")
            session['next_url'] = request.path
            return redirect(url_for('auth.login', next=request.path))
        else:
            logger.debug(f"已登录用户访问: {path}, user_id={session.get('user_id')}")
    
    logger.info("认证模块初始化完成")
    return app 