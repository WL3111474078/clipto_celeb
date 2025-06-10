from flask import Blueprint, request, render_template, current_app, jsonify, redirect
import os
import json
import logging
from trans_web.utils import load_json

search_bp = Blueprint('search', __name__, url_prefix='/search')

# 每页显示的结果数量
ITEMS_PER_PAGE = 20

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

@search_bp.route('/')
def search():
    # 获取搜索关键词和页码
    keyword = request.args.get('keyword', '')
    page = int(request.args.get('page', 1))
    
    # 如果没有关键词，则返回空的搜索页面
    if not keyword:
        return render_template('search.html', results=[], total_results=0, 
                              current_page=page, total_pages=0, keyword=keyword)
    
    # 加载数据
    data = load_json_data()
    if not data:
        return render_template('search.html', results=[], total_results=0, 
                              current_page=page, total_pages=0, keyword=keyword,
                              error="无法加载数据库信息")
    
    # 搜索结果
    results = []
    
    # 忽略大小写的搜索
    keyword = keyword.lower()
    
    # 对每个人物进行搜索匹配
    for person in data:
        # 检查各个字段是否包含关键词
        if (
            (str(person.get('name', '')).lower().find(keyword) != -1) or
            (str(person.get('id', '')).lower().find(keyword) != -1) or
            (str(person.get('person_id', '')).lower().find(keyword) != -1) or
            (str(person.get('description', '')).lower().find(keyword) != -1) or
            (str(person.get('gender', '')).lower().find(keyword) != -1) or
            (str(person.get('title', '')).lower().find(keyword) != -1)
        ):
            # 标准化数据格式，确保所有必要字段存在
            person_data = {
                'id': person.get('id', person.get('person_id', '')),
                'name': person.get('name', ''),
                'gender': person.get('gender', ''),
                'title': person.get('title', ''),
                'description': person.get('description', ''),
                'photo_path': person.get('photo_path', ''),
                'photos': person.get('photos', []),
                'voices': person.get('voices', [])
            }
            results.append(person_data)
    
    # 计算总结果数和总页数
    total_results = len(results)
    total_pages = (total_results + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    
    # 限制页码范围
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # 获取当前页的结果
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE
    current_page_results = results[start_index:end_index]
    
    # 返回模板
    return render_template('search.html', results=current_page_results, 
                          total_results=total_results, current_page=page,
                          total_pages=total_pages, keyword=keyword)

@search_bp.route('/api')
def search_api():
    """API接口，用于AJAX搜索请求"""
    keyword = request.args.get('keyword', '')
    if not keyword:
        return jsonify({"success": True, "results": []})
    
    # 加载数据
    data = load_json_data()
    if not data:
        return jsonify({"success": False, "message": "无法加载数据库信息"})
    
    # 搜索结果
    results = []
    
    # 忽略大小写的搜索
    keyword = keyword.lower()
    
    # 对每个人物进行搜索匹配
    for person in data:
        # 检查各个字段是否包含关键词
        if (
            (str(person.get('name', '')).lower().find(keyword) != -1) or
            (str(person.get('id', '')).lower().find(keyword) != -1) or
            (str(person.get('person_id', '')).lower().find(keyword) != -1) or
            (str(person.get('description', '')).lower().find(keyword) != -1) or
            (str(person.get('gender', '')).lower().find(keyword) != -1) or
            (str(person.get('title', '')).lower().find(keyword) != -1)
        ):
            # 标准化数据格式
            person_data = {
                'id': person.get('id', person.get('person_id', '')),
                'name': person.get('name', ''),
                'gender': person.get('gender', ''),
                'title': person.get('title', ''),
                'description': person.get('description', ''),
                'photo_path': person.get('photo_path', ''),
                'photos': person.get('photos', []),
            }
            results.append(person_data)
    
    return jsonify({"success": True, "results": results})

@search_bp.route('/person/<person_id>')
def person_detail(person_id):
    # 加载数据
    data = load_json_data()
    
    # 查找指定ID的人物
    person = None
    for p in data:
        if str(p.get('id', '')) == str(person_id) or str(p.get('person_id', '')) == str(person_id):
            person = p
            break
    
    # 如果找不到人物，返回错误信息
    if not person:
        return render_template('person_detail.html', person=None)
    
    # 标准化数据格式
    person_data = {
        'id': person.get('id', person.get('person_id', '')),
        'name': person.get('name', ''),
        'gender': person.get('gender', ''),
        'title': person.get('title', ''),
        'description': person.get('description', ''),
        'photo_path': person.get('photo_path', ''),
        'photos': person.get('photos', []),
        'voices': person.get('voices', [])
    }
    
    return render_template('person_detail.html', person=person_data)

@search_bp.route('/edit/<person_id>')
def edit_person(person_id):
    """重定向到编辑页面"""
    # 直接构造URL而不使用url_for，避免循环导入
    return redirect(f"/edit?id={person_id}") 