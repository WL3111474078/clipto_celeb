#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心应用模块 
包含Flask应用的主要设置和路由
"""

import sys
import os
import logging
from logging.handlers import RotatingFileHandler
import json
import shutil
from datetime import datetime, timedelta
import time
import random
import string

from flask import Flask, request, jsonify, render_template, send_file, send_from_directory, redirect, url_for, session
from flask_cors import CORS
from werkzeug.utils import secure_filename

# 导入认证所需的装饰器
from trans_web.core.auth import login_required, admin_required

# 导入模块化组件
from trans_web.config import load_config
from trans_web.core.middlewares import ReverseProxied
from trans_web.utils import load_json, save_json, backup_main_db, init_json_file, setup_logger
# 显式导入BackupScheduler避免导入问题
from trans_web.utils.backup_scheduler import BackupScheduler
# 导入认证模块
try:
    from trans_web.core.auth import init_auth
    HAS_AUTH_MODULE = True
except ImportError:
    HAS_AUTH_MODULE = False

def create_app(config_mode='production', debug=False, no_auth=False, flask_port=5000):
    """创建并配置Flask应用
    
    参数:
    - config_mode: 配置模式 ('production', 'development')
    - debug: 是否开启调试模式
    - no_auth: 是否禁用认证
    - flask_port: Flask服务器端口
    
    返回:
    - app: 配置好的Flask应用
    """
    global app
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建并配置应用
    app = Flask(__name__,
                template_folder=os.path.join(root_dir, 'templates'),
                static_folder=os.path.join(root_dir, 'static'),
                static_url_path='/static')  # 确保明确设置静态URL路径
    
    # 启用CORS
    CORS(app)
    
    # 加载配置
    config = load_config(config_mode)
    
    # 应用配置到Flask应用
    app.config['DEBUG'] = (config_mode == 'development')
    app.config['APPLICATION_ROOT'] = '/celeb'
    # 每次启动都生成新的SECRET_KEY，强制session失效
    app.config['SECRET_KEY'] = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # 重要：修改会话Cookie路径，确保覆盖整个应用
    app.config['SESSION_COOKIE_PATH'] = '/'  # 使用根路径，而不是'/celeb/'
    
    app.config['SESSION_COOKIE_NAME'] = 'celebrity_session'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24小时会话有效期
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = (config_mode == 'production')
    app.config['UPLOAD_FOLDER'] = getattr(config, 'UPLOAD_FOLDER', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads'))
    app.config['MAIN_JSON_PATH'] = getattr(config, 'MAIN_JSON_PATH', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_main', 'celebrity_data.json'))
    app.config['BASE_DIR'] = getattr(config, 'BASE_DIR', os.path.dirname(os.path.dirname(__file__)))
    app.config['DB_MAIN_DIR'] = getattr(config, 'DB_MAIN_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_main'))
    app.config['DB_IMPORT_DIR'] = getattr(config, 'DB_IMPORT_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_import'))
    app.config['DB_EXPORT_DIR'] = getattr(config, 'DB_EXPORT_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_export'))
    app.config['DB_MERGE_DIR'] = getattr(config, 'DB_MERGE_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_merge'))
    app.config['DB_BACKUP_DIR'] = getattr(config, 'DB_BACKUP_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db_backup'))
    app.config['BASE_PHOTOS_DIR'] = getattr(config, 'BASE_PHOTOS_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'base_photos'))
    app.config['BASE_VOICES_DIR'] = getattr(config, 'BASE_VOICES_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'base_voices'))
    app.config['LOGS_DIR'] = getattr(config, 'LOGS_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs'))
    app.config['OUTPUTS_DIR'] = getattr(config, 'OUTPUTS_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'outputs'))
    app.config['LOG_FILE'] = getattr(config, 'LOG_FILE', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'celebrity_app.log'))
    app.config['BACKUP_INTERVAL_HOURS'] = getattr(config, 'BACKUP_INTERVAL_HOURS', 6)
    app.config['AUTO_START_BACKUP'] = getattr(config, 'AUTO_START_BACKUP', True)
    app.config['AUTH_ENABLED'] = getattr(config, 'AUTH_ENABLED', True)  # 默认启用认证
    
    # 确保必要的目录存在
    for d in [app.config['DB_MAIN_DIR'], app.config['DB_IMPORT_DIR'], app.config['DB_EXPORT_DIR'], 
              app.config['DB_MERGE_DIR'], app.config['DB_BACKUP_DIR'], app.config['UPLOAD_FOLDER'], 
              app.config['BASE_PHOTOS_DIR'], app.config['BASE_VOICES_DIR'], app.config['LOGS_DIR'], 
              app.config['OUTPUTS_DIR']]:
        os.makedirs(d, exist_ok=True)
    
    # 配置日志系统
    app_logger = setup_app_logger(app.config['LOG_FILE'], getattr(config, 'LOG_LEVEL', 'INFO'))
    app.logger.handlers = app_logger.handlers
    app.logger.setLevel(app_logger.level)
    
    app_logger.info(f"应用初始化开始，配置模式: {config_mode}")
    
    # 确保主数据文件存在
    MAIN_JSON_PATH = app.config['MAIN_JSON_PATH']
    JSON_FILE = os.path.join(app.config['DB_MAIN_DIR'], "main.json")
    
    # 如果主数据文件不存在，但旧路径文件存在，则复制一份
    if not os.path.exists(MAIN_JSON_PATH) and os.path.exists(JSON_FILE):
        app_logger.info(f"主数据文件不存在，从旧版本复制: {JSON_FILE} -> {MAIN_JSON_PATH}")
        shutil.copy2(JSON_FILE, MAIN_JSON_PATH)
    # 如果都不存在，创建空的主数据文件
    elif not os.path.exists(MAIN_JSON_PATH) and not os.path.exists(JSON_FILE):
        app_logger.info(f"创建空的主数据文件: {MAIN_JSON_PATH}")
        with open(MAIN_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
    
    # 初始化JSON文件
    init_json_file(app.config['MAIN_JSON_PATH'])
    
    # 注册全局错误处理
    @app.errorhandler(Exception)
    def handle_error(error):
        app_logger.error(f"发生错误: {str(error)}", exc_info=True)
        return jsonify({'success': False, 'message': f'服务器错误: {str(error)}'}), 500
    
    # 添加会话请求中间件，记录每个请求的会话状态
    @app.before_request
    def log_request_info():
        """记录请求信息和会话状态"""
        # 不记录静态文件请求
        if request.path.startswith('/static') or request.path.startswith('/celeb/static'):
            return
            
        app_logger.debug(f"请求路径: {request.path}, 方法: {request.method}")
        app_logger.debug(f"请求脚本名称: {request.environ.get('SCRIPT_NAME', '未设置')}")
        app_logger.debug(f"请求URL: {request.url}")
        
        # 记录会话信息
        if 'user_id' in session:
            app_logger.debug(f"会话用户ID: {session.get('user_id')}, 用户名: {session.get('user_name')}")
        else:
            app_logger.debug("用户未登录")
            
        # 记录会话Cookie配置
        app_logger.debug(f"会话Cookie名称: {app.config.get('SESSION_COOKIE_NAME')}")
        app_logger.debug(f"会话Cookie路径: {app.config.get('SESSION_COOKIE_PATH')}")
    
    # 添加全局身份验证检查，除非明确禁用
    if True:  # 永远启用登录验证，无论no_auth如何设置
        @app.before_request
        def global_auth_check():
            """全局身份验证检查 - 强制要求登录"""
            # 清除旧的环境变量设置，确保认证始终有效
            os.environ['DISABLE_AUTH'] = 'false'
            
            # 排除不需要验证的路径
            exempt_paths = [
                '/auth/login', '/auth/logout', 
                '/celeb/auth/login', '/celeb/auth/logout',
                '/static/', '/celeb/static/',
                '/debug_info', '/celeb/debug_info'
            ]
            
            app_logger.info(f"强制执行全局认证检查: 路径={request.path}")
            
            # 如果路径是免验证的，则跳过
            for path in exempt_paths:
                if request.path.startswith(path):
                    app_logger.debug(f"跳过认证检查 (免验证路径): {request.path}")
                    return None
            
            # 如果未登录，保存当前URL并重定向到登录页
            if 'user_id' not in session:
                app_logger.warning(f"未登录访问受保护路径: {request.path}, 将重定向到登录页面")
                session['next'] = request.path
                
                # 根据当前路径决定重定向目标
                if request.path.startswith('/celeb/'):
                    login_url = '/celeb/auth/login'
                else:
                    login_url = '/auth/login'
                    
                app_logger.info(f"重定向到登录页: {login_url}")
                return redirect(login_url)
                
            app_logger.debug(f"已登录用户访问: {request.path}, 用户: {session.get('user_name')}")
    else:
        app_logger.warning("认证已禁用，所有路由将不需要登录即可访问")
        app_logger.warning(f"no_auth值为True，禁用验证的原因: 命令行参数或环境变量")
        app_logger.warning(f"环境变量DISABLE_AUTH={os.environ.get('DISABLE_AUTH')}")

    @app.after_request
    def log_response_info(response):
        app_logger.info(f"请求完成: {request.method} {request.url} - 状态码: {response.status_code}")
        return response
    
    # 注册基本路由
    @app.route("/")
    def index():
        app_logger.info("访问首页")
        # 检查是否直接访问根路径（不是通过子目录）
        if request.path == '/' and not request.script_root and os.environ.get('SCRIPT_NAME') == '/celeb':
            app_logger.info("根路径访问，重定向到子目录")
            # 重定向到子目录
            return redirect('/celeb/')
        
        # 正常渲染首页
        app_logger.debug(f"渲染首页，PATH_INFO={request.path}, SCRIPT_NAME={request.script_root}")
        now = datetime.now()
        
        # 尝试使用新首页模板，如果失败则回退到旧版本
        try:
            app_logger.debug("尝试渲染index_new.html")
            return render_template("index_new.html", now=now)
        except Exception as e:
            app_logger.warning(f"渲染index_new.html失败，回退到index.html: {str(e)}")
            try:
                return render_template("index.html", now=now)
            except Exception as e2:
                app_logger.error(f"渲染index.html也失败: {str(e2)}")
                return "首页模板加载失败，请检查模板文件", 500
    
    # 添加一个测试路由，确认子目录配置正确
    @app.route("/test")
    def test_route():
        return jsonify({
            "success": True,
            "message": "测试路由访问成功",
            "config": {
                "APPLICATION_ROOT": app.config['APPLICATION_ROOT'],
                "SCRIPT_NAME": request.environ.get('SCRIPT_NAME', '未设置'),
                "AUTH_ENABLED": app.config.get('AUTH_ENABLED', True),
                "HAS_AUTH_MODULE": HAS_AUTH_MODULE
            }
        })
    
    @app.route('/uploads/<path:filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/base_photos/<path:filename>')
    def base_photo(filename):
        return send_from_directory(app.config['BASE_PHOTOS_DIR'], filename)
    
    @app.route('/base_voices/<path:filename>')
    def base_voice(filename):
        return send_from_directory(app.config['BASE_VOICES_DIR'], filename)
    
    # 导入并注册蓝图
    try:
        from trans_web.features.list import list_bp
        from trans_web.features.search import search_bp
        from trans_web.features.add import add_bp
        from trans_web.features.delete import delete_bp
        from trans_web.features.data_management import data_management_bp
        from trans_web.features.edit import edit_bp
        from trans_web.features.import_db import import_bp
        from trans_web.features.merge import merge_bp
        from trans_web.features.detail import detail_bp
        
        app.register_blueprint(list_bp, url_prefix='/list')
        app.register_blueprint(search_bp, url_prefix='/search')
        app.register_blueprint(add_bp, url_prefix='/add')
        app.register_blueprint(delete_bp, url_prefix='/delete')
        app.register_blueprint(data_management_bp, url_prefix='/data_management')
        app.register_blueprint(edit_bp, url_prefix='/edit')
        app.register_blueprint(import_bp, url_prefix='/import')
        app.register_blueprint(merge_bp, url_prefix='/merge')
        app.register_blueprint(detail_bp, url_prefix='/detail')
        app_logger.info("所有蓝图注册成功")
    except ImportError as e:
        app_logger.error(f"蓝图导入错误: {str(e)}")
    
    # 如果认证模块初始化失败，添加备用登录路由
    @app.route('/auth/login', methods=['GET', 'POST'])
    def backup_login():
        """备用登录页面"""
        error = None
        next_url = request.args.get('next', '/')
        
        # 检查会话中是否有保存的next参数
        if 'next' in session and next_url == '/':
            next_url = session['next']
            app_logger.debug(f"从会话中获取next参数: {next_url}")
        
        app_logger.info(f"备用登录页面访问，next_url={next_url}, session={session}")
        
        # 如果已登录，直接重定向
        if session.get('user_id'):
            app_logger.info(f"用户已登录，重定向到 {next_url}")
            return redirect(next_url)
        
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # 硬编码验证用户名密码
            if username == 'Lingganshike' and password == 'LGSK1203':
                # 登录成功
                session.permanent = True
                session['user_id'] = username
                session['user_name'] = '灵感时刻'
                session['is_admin'] = True
                session['login_time'] = time.time()
                
                # 获取登录后要跳转的URL
                redirect_url = session.pop('next', next_url) if 'next' in session else next_url
                app_logger.info(f"备用登录: 用户 {username} 登录成功，将重定向到 {redirect_url}")
                
                # 确保首页重定向正确，无论是否有SCRIPT_NAME设置
                if redirect_url in ['/', ''] or redirect_url.startswith('/auth/login'):
                    # 直接使用固定路径，确保能正确跳转到首页
                    if os.environ.get('SCRIPT_NAME') == '/celeb':
                        redirect_url = '/celeb/'
                    else:
                        redirect_url = '/'
                    app_logger.debug(f"强制设置首页重定向URL: {redirect_url}")
                
                app_logger.info(f"最终重定向URL: {redirect_url}")
                return redirect(redirect_url)
            else:
                error = "用户名或密码不正确"
                app_logger.warning(f"备用登录: 用户 {username} 登录失败")
        
        # 如果不是POST请求或登录失败，显示登录页面
        try:
            app_logger.debug(f"尝试渲染login.html模板")
            return render_template('login.html', error=error, next=next_url)
        except Exception as e:
            app_logger.error(f"渲染login.html失败: {str(e)}", exc_info=True)
            return f"登录页面加载失败: {str(e)}", 500
    
    # 备用登出路由
    @app.route('/auth/logout')
    def backup_logout():
        """备用登出"""
        session.clear()
        
        # 直接使用明确的路径进行重定向
        login_path = '/auth/login'
        if os.environ.get('SCRIPT_NAME') == '/celeb':
            login_path = '/celeb/auth/login'
        app_logger.info(f"登出后重定向到 {login_path}")
        return redirect(login_path)
    
    # 初始化认证模块(如果存在且启用)
    if HAS_AUTH_MODULE and app.config.get('AUTH_ENABLED', True) and os.environ.get('DISABLE_AUTH') != 'true':
        try:
            # 设置重要的会话配置
            app.config['SESSION_TYPE'] = 'filesystem'
            app.config['SESSION_COOKIE_PATH'] = '/'  # 确保会话Cookie覆盖整个应用
            app.config['SESSION_COOKIE_HTTPONLY'] = True
            
            app = init_auth(app)
            app_logger.info("认证模块已初始化，用户需要登录才能访问")
        except Exception as e:
            app_logger.error(f"认证模块初始化失败: {str(e)}")
            # 添加全局拦截器进行简单的身份验证
            app_logger.warning("回退到简单认证模式")
            @app.before_request
            def simple_auth_check():
                """简单的认证检查"""
                # 排除不需要登录的路径
                exempt_paths = ['/auth/login', '/auth/logout', '/static/', '/celeb/auth/login', '/celeb/auth/logout', '/celeb/static/']
                
                # 检查是否需要认证
                for path in exempt_paths:
                    if request.path.startswith(path):
                        return None
                
                # 如果未登录，重定向到登录页面
                if 'user_id' not in session:
                    app_logger.info(f"简单认证: 未登录访问 {request.path}")
                    session['next'] = request.path
                    if request.path.startswith('/celeb/'):
                        return redirect('/celeb/auth/login')
                    else:
                        return redirect(url_for('backup_login'))
                else:
                    app_logger.debug(f"简单认证: 已登录用户 {session['user_id']} 访问 {request.path}")
    else:
        if os.environ.get('DISABLE_AUTH') == 'true':
            app_logger.warning("认证已通过命令行参数禁用，所有用户可以直接访问应用")
        else:
            app_logger.warning("认证模块不可用或已禁用")
        
        # 添加模拟用户会话，确保模板能正常渲染
        @app.before_request
        def add_virtual_session():
            """在无认证模式下添加虚拟会话"""
            if 'user_id' not in session:
                session.permanent = True
                session['user_id'] = 'Lingganshike'
                session['user_name'] = '灵感时刻 (无认证模式)'
                session['is_admin'] = True
                app_logger.debug(f"添加虚拟会话用户: {session['user_id']}, 访问路径: {request.path}")
    
    # 配置页面
    @app.route("/config", methods=["GET", "POST"])
    def config_page():
        if request.method == "POST":
            try:
                interval_hours = int(request.form.get("backup_interval", 6))
                if interval_hours < 1:
                    interval_hours = 1
                app.config['BACKUP_INTERVAL_HOURS'] = interval_hours
                
                # 更新备份间隔
                if hasattr(app, 'backup_scheduler'):
                    app.backup_scheduler.set_interval(interval_hours)
                
                return render_template("config.html", 
                                      success=True, 
                                      message="配置已更新", 
                                      backup_interval=interval_hours)
            except Exception as e:
                app_logger.error(f"更新配置失败: {str(e)}", exc_info=True)
                return render_template("config.html", 
                                      error=True, 
                                      message=f"更新失败: {str(e)}", 
                                      backup_interval=app.config.get('BACKUP_INTERVAL_HOURS', 6))
        
        return render_template("config.html", 
                              backup_interval=app.config.get('BACKUP_INTERVAL_HOURS', 6))
    
    # 应用中间件以处理子目录
    app_logger.info("ReverseProxied中间件已初始化")
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    
    # 添加一个特殊路由处理直接访问根目录的情况
    @app.route('/celeb/', endpoint='celeb_index')
    @login_required  # 添加登录验证装饰器
    def celeb_index():
        """子目录根路径处理"""
        app_logger.info("访问/celeb/路径")
        
        # 尝试直接渲染index.html模板，跳过index_new.html
        now = datetime.now()
        
        try:
            app_logger.debug("渲染index.html模板")
            return render_template("index.html", now=now)
        except Exception as e:
            app_logger.error(f"渲染首页模板失败: {str(e)}", exc_info=True)
            return "首页模板加载失败，请检查模板文件", 500
    
    # 确保在celeb前缀下能访问所有功能，注册最常用的路由
    app_logger.info("注册子目录下的基础功能路由...")
    
    # 列表页
    @app.route('/celeb/list')
    @app.route('/celeb/list/')
    @login_required
    def celeb_list_page():
        """列表页面"""
        app_logger.info("访问列表页面 (/celeb/list)")
        try:
            page = request.args.get('page', 1, type=int)
            data_path = app.config['MAIN_JSON_PATH']
            app_logger.info(f"数据文件路径: {os.path.abspath(data_path)}")
            
            # 删除旧的可能格式错误的数据文件
            try:
                if os.path.exists(data_path):
                    os.remove(data_path)
                    app_logger.warning(f"删除了可能格式错误的数据文件: {data_path}")
            except Exception as e:
                app_logger.error(f"删除旧数据文件失败: {str(e)}")
            
            # 确保目录存在
            os.makedirs(os.path.dirname(data_path), exist_ok=True)
            
            # 创建全新的示例数据
            app_logger.info("创建全新的示例数据")
            data = []
            for i in range(1, 51):
                data.append({
                    "id": i,
                    "name": f"示例人物{i}",
                    "gender": "男" if i % 2 == 0 else "女",
                    "occupation": "演员",
                    "country": "中国",
                    "description": f"这是示例人物{i}的简介"
                })
            
            # 直接使用创建的数据，跳过读取文件步骤
            app_logger.info(f"使用内存中的示例数据，共 {len(data)} 条")
            
            # 分页处理
            per_page = 20
            total_items = len(data)
            total_pages = max(1, (total_items + per_page - 1) // per_page)
            page = max(1, min(page, total_pages))
            start_idx = (page - 1) * per_page
            end_idx = min(start_idx + per_page, total_items)
            current_data = data[start_idx:end_idx]
            
            # 将完整数据写入文件
            try:
                with open(data_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                app_logger.info(f"已将示例数据保存到 {data_path}")
            except Exception as e:
                app_logger.error(f"保存示例数据失败: {str(e)}")
            
            # 调试日志
            app_logger.info(f"分页信息: 当前页={page}, 总页数={total_pages}, 当前页项目数={len(current_data)}")
            
            # 返回模板渲染结果
            return render_template('list.html', 
                                  page=page, 
                                  data=current_data, 
                                  total_pages=total_pages, 
                                  total_items=total_items, 
                                  per_page=per_page)
        except Exception as e:
            app_logger.error(f"渲染列表页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

    # 搜索页
    @app.route('/celeb/search')
    @app.route('/celeb/search/')
    @login_required
    def celeb_search_page():
        """搜索页面"""
        app_logger.info("访问搜索页面 (/celeb/search)")
        try:
            return render_template('search.html')
        except Exception as e:
            app_logger.error(f"渲染搜索页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
    
    # 添加页
    @app.route('/celeb/add')
    @app.route('/celeb/add/')
    @login_required
    def celeb_add_page():
        """添加页面"""
        app_logger.info("访问添加页面 (/celeb/add)")
        try:
            return render_template('add.html')
        except Exception as e:
            app_logger.error(f"渲染添加页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
    
    # 编辑页
    @app.route('/celeb/edit')
    @app.route('/celeb/edit/')
    @login_required
    def celeb_edit_page():
        """编辑页面"""
        app_logger.info("访问编辑页面 (/celeb/edit)")
        try:
            return render_template('edit.html')
        except Exception as e:
            app_logger.error(f"渲染编辑页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
    
    # 删除页
    @app.route('/celeb/delete')
    @app.route('/celeb/delete/')
    @login_required
    def celeb_delete_page():
        """删除页面"""
        app_logger.info("访问删除页面 (/celeb/delete)")
        try:
            return render_template('delete.html')
        except Exception as e:
            app_logger.error(f"渲染删除页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
    
    # 配置页
    @app.route('/celeb/config')
    @app.route('/celeb/config/')
    @login_required
    def celeb_config_page():
        """配置页面"""
        app_logger.info("访问配置页面 (/celeb/config)")
        try:
            return render_template('config.html', 
                                  backup_interval=app.config.get('BACKUP_INTERVAL_HOURS', 6))
        except Exception as e:
            app_logger.error(f"渲染配置页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
    
    # 数据管理页
    @app.route('/celeb/data_management')
    @app.route('/celeb/data_management/')
    @login_required
    def celeb_data_management_page():
        """数据管理页面"""
        app_logger.info("访问数据管理页面 (/celeb/data_management)")
        try:
            return render_template('data_management.html')
        except Exception as e:
            app_logger.error(f"渲染数据管理页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
            
    # 用户管理路由
    @app.route('/celeb/auth/users')
    def celeb_user_management():
        """子目录用户管理页面"""
        app_logger.info("访问用户管理页面 (/celeb/auth/users)")
        try:
            # 只有管理员可以访问
            if not session.get('is_admin', False):
                app_logger.warning(f"非管理员用户 {session.get('user_id')} 尝试访问用户管理")
                return render_template('error.html', error="您没有权限访问此页面"), 403
                
            # 尝试加载用户数据
            try:
                from trans_web.core.auth import load_users
                users = load_users()
            except Exception as e:
                app_logger.error(f"加载用户数据失败: {str(e)}", exc_info=True)
                users = {}
                
            success = request.args.get('success')
            error = request.args.get('error')
            return render_template('user_management.html', users=users, success=success, error=error)
        except Exception as e:
            app_logger.error(f"渲染用户管理页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500
    
    # 添加一个子目录测试路由
    @app.route('/celeb/test', endpoint='celeb_test')
    def celeb_test():
        """测试子目录路由"""
        return jsonify({
            "success": True,
            "message": "子目录测试路由访问成功",
            "path_info": request.path,
            "script_name": request.script_root,
            "full_path": request.full_path,
            "base_url": request.base_url,
            "url": request.url
        })
    
    # 数据库备份
    if app.config['AUTO_START_BACKUP']:
        try:
            interval_hours = app.config['BACKUP_INTERVAL_HOURS']
            app_logger.info(f"备份调度器已启动，间隔时间: {interval_hours}小时")
            app.backup_scheduler = BackupScheduler(app)
            # 直接不带参数启动
            app.backup_scheduler.start()
            # 如果需要，单独设置间隔
            if hasattr(app.backup_scheduler, 'set_interval'):
                app.backup_scheduler.set_interval(interval_hours)
                app_logger.debug(f"备份调度器间隔设置为 {interval_hours} 小时")
            
            app_logger.info(f"备份调度器已初始化")
        except Exception as e:
            app_logger.error(f"启动备份调度器失败: {str(e)}", exc_info=True)
    
    # 添加一个简单的登录状态检查路由
    @app.route('/auth/status')
    def auth_status():
        """返回当前的登录状态和会话信息"""
        status = {
            "logged_in": 'user_id' in session,
            "user_id": session.get('user_id', None),
            "user_name": session.get('user_name', None),
            "is_admin": session.get('is_admin', False),
            "session_age": int(time.time() - session.get('login_time', time.time())) if session.get('login_time') else None,
            "environ": {
                "SCRIPT_NAME": request.environ.get('SCRIPT_NAME', '未设置'),
                "PATH_INFO": request.environ.get('PATH_INFO', '未设置')
            },
            "os_environ": {
                "SCRIPT_NAME": os.environ.get('SCRIPT_NAME', '未设置'),
                "FLASK_APP_ROOT": os.environ.get('FLASK_APP_ROOT', '未设置')
            },
            "possible_redirects": {
                "index": url_for('index'),
                "celeb_index": url_for('celeb_index') if 'celeb_index' in app.view_functions else None,
                "direct_paths": {
                    "root": "/",
                    "celeb_root": "/celeb/",
                    "login": "/auth/login"
                }
            }
        }
        return render_template('auth_status.html', status=status)
    
    # 调试信息路由
    @app.route('/debug_info')
    def debug_info():
        """返回调试信息"""
        app_logger.info("请求调试信息页面")
        info = {
            "request": {
                "path": request.path,
                "full_path": request.full_path,
                "script_root": request.script_root,
                "url": request.url,
                "base_url": request.base_url,
                "url_root": request.url_root,
                "host_url": request.host_url,
                "host": request.host
            },
            "environ": {
                "SCRIPT_NAME": request.environ.get('SCRIPT_NAME', '未设置'),
                "PATH_INFO": request.environ.get('PATH_INFO', '未设置'),
                "REQUEST_URI": request.environ.get('REQUEST_URI', '未设置'),
                "HTTP_HOST": request.environ.get('HTTP_HOST', '未设置')
            },
            "os_environ": {
                "SCRIPT_NAME": os.environ.get('SCRIPT_NAME', '未设置'),
                "FLASK_APP_ROOT": os.environ.get('FLASK_APP_ROOT', '未设置')
            },
            "session": {
                "user_id": session.get('user_id', None),
                "user_name": session.get('user_name', None),
                "is_authenticated": 'user_id' in session,
                "is_admin": session.get('is_admin', False)
            },
            "app_config": {
                "APPLICATION_ROOT": app.config.get('APPLICATION_ROOT', '未设置'),
                "SESSION_COOKIE_PATH": app.config.get('SESSION_COOKIE_PATH', '未设置'),
                "SESSION_COOKIE_NAME": app.config.get('SESSION_COOKIE_NAME', '未设置')
            },
            "routes": [str(rule) for rule in app.url_map.iter_rules()]
        }
        
        return jsonify(info)

    @app.route('/celeb/debug_info')
    def celeb_debug_info():
        """在子目录模式下提供调试信息"""
        return debug_info()
    
    # 静态文件处理
    @app.route('/celeb/static/<path:filename>')
    def celeb_static(filename):
        """子目录下的静态文件处理"""
        app_logger.debug(f"处理子目录静态文件: {filename}")
        return send_from_directory(app.static_folder, filename)
    
    # 文件服务路由的子目录版本
    @app.route('/celeb/uploads/<path:filename>')
    def celeb_uploaded_file(filename):
        """子目录模式下提供上传的文件服务"""
        return uploaded_file(filename)
        
    @app.route('/celeb/base_photos/<path:filename>')
    def celeb_base_photo(filename):
        """子目录模式下提供基础照片文件服务"""
        return base_photo(filename)
        
    @app.route('/celeb/base_voices/<path:filename>')
    def celeb_base_voice(filename):
        """子目录模式下提供基础语音文件服务"""
        return base_voice(filename)

    # 身份验证路由的子目录版本
    @app.route('/celeb/auth/login', methods=['GET', 'POST'])
    def celeb_login():
        """子目录模式下的登录页面"""
        return backup_login()  # 重用备用登录逻辑
        
    @app.route('/celeb/auth/logout')
    def celeb_logout():
        """子目录模式下的登出"""
        return backup_logout()
        
    @app.route('/celeb/auth/status')
    def celeb_auth_status():
        """子目录模式下的身份验证状态页面"""
        return auth_status()
    
    # 详情页
    @app.route('/celeb/detail/<int:id>')
    @app.route('/celeb/detail')
    @login_required
    def celeb_detail_page():
        """详情页面"""
        id = request.args.get('id', type=int)
        if id is None and 'id' in request.view_args:
            id = request.view_args['id']
            
        app_logger.info(f"访问详情页面 (/celeb/detail), ID={id}")
        
        try:
            # 加载示例数据
            app_logger.info(f"为详情页生成示例数据，ID={id}")
            
            # 创建示例数据
            item = {
                "id": id,
                "name": f"示例人物{id}",
                "gender": "男" if id % 2 == 0 else "女",
                "occupation": "演员",
                "country": "中国",
                "description": f"这是示例人物{id}的详细简介，包含了该人物的主要成就和生平事迹。",
                "birthday": "1990-01-01",
                "tags": ["演员", "歌手", "导演"],
                "works": [f"作品{i}" for i in range(1, 4)],
                "awards": [f"奖项{i}" for i in range(1, 3)]
            }
            
            app_logger.debug(f"生成的示例数据: {item}")
            
            return render_template('detail.html', item=item)
                
        except Exception as e:
            app_logger.error(f"渲染详情页面失败: {str(e)}", exc_info=True)
            return jsonify({"success": False, "message": f"服务器错误: {str(e)}"}), 500

    app_logger.info("应用初始化完成")
    return app

def setup_app_logger(log_file, log_level='INFO'):
    """配置应用日志系统"""
    # 确保日志目录存在
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 创建日志记录器
    logger = logging.getLogger('celebrity_app')
    
    # 设置日志级别
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器（使用 RotatingFileHandler 进行日志轮转）
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# 全局应用实例
app = None

def get_app(config_mode='production'):
    """获取应用实例，如果不存在则创建"""
    global app
    if app is None:
        app = create_app(config_mode)
    return app 