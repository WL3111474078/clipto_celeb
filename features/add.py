from flask import Blueprint, jsonify, request, render_template, current_app, flash, redirect, url_for
import os
import json
import uuid
import time
from werkzeug.utils import secure_filename
from datetime import datetime
import shutil

add_bp = Blueprint('add', __name__)

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

def save_json_data(data):
    """保存人物数据到主数据库文件"""
    # 使用配置的主数据文件路径
    main_json_path = current_app.config.get('MAIN_JSON_PATH')
    
    # 确保目录存在
    os.makedirs(os.path.dirname(main_json_path), exist_ok=True)
    
    # 备份原始文件
    if os.path.exists(main_json_path):
        backup_dir = current_app.config.get('DB_BACKUP_DIR')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}.json")
        
        try:
            shutil.copy2(main_json_path, backup_path)
        except Exception as e:
            current_app.logger.error(f"备份数据文件失败: {str(e)}")
    
    try:
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        current_app.logger.error(f"保存JSON数据失败: {str(e)}")
        return False

@add_bp.route('/')
def index():
    # 为模板传入空的person对象，防止undefined错误
    empty_person = {
        'id': '',
        'name': '',
        'gender': '',
        'title': '',
        'description': '',
        'alias': [],
        'photos': [],
        'voices': []
    }
    return render_template('add.html', person=empty_person)

@add_bp.route('/add_person', methods=['POST'])
def add_person():
    try:
        # 获取基本信息
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '男').strip()
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        alias_str = request.form.get('alias', '').strip()
        
        # 处理别名
        alias = [a.strip() for a in alias_str.split(',') if a.strip()]
        
        # 生成唯一ID
        timestamp = int(time.time())
        unique_id = f"{timestamp}_{str(uuid.uuid4())[:8]}"
        
        # 创建新人物记录
        new_person = {
            'id': unique_id,
            'person_id': unique_id,  # 兼容旧字段
            'name': name,
            'gender': gender,
            'title': title,
            'description': description,
            'alias': alias,
            'photos': [],
            'voices': []
        }
        
        # 处理照片上传
        photo_file = request.files.get('photo')
        photo_path = None
        
        if photo_file and photo_file.filename:
            photos_dir = current_app.config['BASE_PHOTOS_DIR']
            os.makedirs(photos_dir, exist_ok=True)
            
            # 生成安全的文件名
            original_filename = secure_filename(photo_file.filename)
            filename = f"{unique_id}_{name.replace(' ', '_')}_photo_1{os.path.splitext(original_filename)[1]}"
            file_path = os.path.join(photos_dir, filename)
            
            # 保存文件
            photo_file.save(file_path)
            photo_path = f"/base_photos/{filename}"
            
            # 添加到人物记录
            new_person['photos'].append({
                'photo_id': f"{unique_id}_{name.replace(' ', '_')}_photo_1",
                'pose': '正面',
                'file_name': filename,
                'uri': '',
                'description': ''
            })
        
        # 处理音频上传
        voice_file = request.files.get('voice')
        voice_path = None
        
        if voice_file and voice_file.filename:
            voices_dir = current_app.config['BASE_VOICES_DIR']
            os.makedirs(voices_dir, exist_ok=True)
            
            # 生成安全的文件名
            original_filename = secure_filename(voice_file.filename)
            filename = f"{unique_id}_{name.replace(' ', '_')}_voice_1{os.path.splitext(original_filename)[1]}"
            file_path = os.path.join(voices_dir, filename)
            
            # 保存文件
            voice_file.save(file_path)
            voice_path = f"/base_voices/{filename}"
            
            # 添加到人物记录
            new_person['voices'].append({
                'voice_id': f"{unique_id}_{name.replace(' ', '_')}_voice_1",
                'file_name': filename,
                'uri': '',
                'description': ''
            })
        
        # 加载现有数据并添加新人物
        data = load_json_data()
        data.append(new_person)
        
        # 保存更新后的数据
        if save_json_data(data):
            # 获取文件保存路径
            main_json_path = current_app.config.get('MAIN_JSON_PATH')
            base_photos_dir = current_app.config.get('BASE_PHOTOS_DIR')
            base_voices_dir = current_app.config.get('BASE_VOICES_DIR')
            
            return jsonify({
                'success': True, 
                'message': '人物添加成功', 
                'id': unique_id,
                'main_data_path': main_json_path,
                'photo_path': photo_path,
                'voice_path': voice_path,
                'photo_dir': base_photos_dir,
                'voice_dir': base_voices_dir
            })
        else:
            return jsonify({'success': False, 'message': '保存数据失败'})
    
    except Exception as e:
        current_app.logger.error(f"添加人物失败: {str(e)}")
        return jsonify({'success': False, 'message': f'添加失败: {str(e)}'}) 