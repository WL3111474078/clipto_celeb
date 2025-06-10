from flask import Blueprint, request, render_template, current_app, redirect, url_for, jsonify
import math
import ijson
import os
from ..utils import load_json # Assuming utils is in the parent directory
import json

list_bp = Blueprint('list', __name__, url_prefix='/list')

def load_main_json_page(page=1, page_size=20):
    """
    分页加载主数据库JSON
    """
    # 首先尝试获取配置的主数据文件路径
    main_json_path = current_app.config.get('MAIN_JSON_PATH')
    
    # 如果配置路径的文件不存在，回退到兼容旧版本的路径
    if not os.path.exists(main_json_path):
        db_main_dir = current_app.config.get('DB_MAIN_DIR')
        main_json_path = os.path.join(db_main_dir, 'main.json')
    
    # 检查文件是否存在
    if not os.path.exists(main_json_path):
        current_app.logger.error(f"主数据文件不存在: {main_json_path}")
        return [], 0, 0
    
    try:
        # 读取整个JSON文件
        with open(main_json_path, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        # 计算总页数
        total_items = len(all_data)
        total_pages = math.ceil(total_items / page_size)
        
        # 分页
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = all_data[start_idx:end_idx]
        
        return page_data, total_items, total_pages
    except Exception as e:
        current_app.logger.error(f"加载JSON数据失败: {str(e)}")
        return [], 0, 0

def load_json_data():
    """加载所有人物数据"""
    # 使用配置的主数据文件路径
    main_json_path = current_app.config.get('MAIN_JSON_PATH')
    
    try:
        if os.path.exists(main_json_path):
            current_app.logger.info(f"正在加载主数据文件: {main_json_path}")
            with open(main_json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            current_app.logger.error(f"主数据文件不存在: {main_json_path}")
            return []
    except Exception as e:
        current_app.logger.error(f"加载JSON数据失败: {str(e)}")
        return []

@list_bp.route('/')
def index():
    """显示人物列表，支持精确搜索，按ID排序"""
    page = int(request.args.get('page', 1))
    page_size = 20
    search_name = request.args.get('search_name', '').strip()
    
    # 加载所有数据
    all_data = load_json_data()
    
    # 按ID排序（优先使用person_id，如果不存在则使用id）
    all_data.sort(key=lambda x: str(x.get('person_id', x.get('id', ''))).lower())
    
    # 如果有搜索条件，过滤数据
    if search_name:
        # 精确匹配名称
        filtered_data = [p for p in all_data if p.get('name', '') == search_name]
    else:
        filtered_data = all_data
    
    # 计算总页数
    total_items = len(filtered_data)
    total_pages = max(1, math.ceil(total_items / page_size))
    
    # 确保页码有效
    page = min(max(1, page), total_pages)
    
    # 分页
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    persons = filtered_data[start_idx:end_idx]
    
    return render_template('list.html', persons=persons, page=page, total_pages=total_pages)

@list_bp.route('/person/<person_id>')
def person_detail(person_id):
    """查看单个人物的详细信息"""
    # 加载所有人物数据
    persons = load_json_data()
    
    # 查找指定ID的人物
    person = None
    for p in persons:
        if p.get('id') == person_id or p.get('person_id') == person_id:
            person = p
            break
    
    if person is None:
        return render_template('detail.html', person=None, error=f'未找到ID为{person_id}的人物')
    
    # 确保所有必要字段存在
    person_data = {
        'id': person.get('id') or person.get('person_id', ''),
        'name': person.get('name', ''),
        'gender': person.get('gender', ''),
        'title': person.get('title', ''),
        'description': person.get('description', ''),
        'photo_path': person.get('photo_path', ''),
        'audio_path': person.get('audio_path', ''),
        'photos': person.get('photos', []),
        'voices': person.get('voices', []),
        'alias': person.get('alias', '')
    }
    
    # 渲染详情页面
    return render_template('detail.html', person=person_data)

@list_bp.route('/api/list')
def list_api():
    """返回所有人物的JSON数据"""
    persons = load_json_data()
    
    # 简化数据，只返回必要的字段
    simplified_persons = []
    for p in persons:
        has_photos = 'photos' in p and len(p['photos']) > 0
        has_voices = 'voices' in p and len(p['voices']) > 0
        
        person_data = {
            'id': p.get('id') or p.get('person_id', ''),
            'name': p.get('name', '未命名'),
            'gender': p.get('gender', '未知'),
            'title': p.get('title', ''),
            'has_photos': has_photos,
            'has_voices': has_voices,
            'photo_count': len(p.get('photos', [])),
            'voice_count': len(p.get('voices', []))
        }
        
        # 添加第一张照片作为预览
        if has_photos:
            person_data['avatar'] = p['photos'][0].get('file_name', '')
        
        simplified_persons.append(person_data)
    
    # 按ID排序
    simplified_persons.sort(key=lambda x: str(x.get('id', '')).lower())
    
    return jsonify({'success': True, 'data': simplified_persons})

@list_bp.route('/person/<person_id>/edit', methods=['GET'])
def edit_person_page(person_id):
    db_main_dir = current_app.config['DB_MAIN_DIR']
    data = load_json(db_main_dir)
    person = next((p for p in data if p.get('person_id') == person_id), None)
    if not person:
        return "未找到该人物", 404
    return render_template('edit.html', person=person) 