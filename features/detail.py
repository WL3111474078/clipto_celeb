from flask import Blueprint, request, render_template, current_app
import os
import json
from ..utils import load_json

detail_bp = Blueprint('detail', __name__, url_prefix='/detail')

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

@detail_bp.route('', methods=['GET'])
def person_detail():
    """处理/detail?id=xxx路由，显示人物详情页面"""
    person_id = request.args.get('id')
    if not person_id:
        return render_template('detail.html', error="未提供人物ID")
    
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
        return render_template('detail.html', error=f'未找到ID为{person_id}的人物')
    
    # 标准化数据格式，确保所有必要字段存在
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
    
    return render_template('detail.html', person=person_data) 