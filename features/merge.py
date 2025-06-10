from flask import Blueprint, jsonify, render_template, request, current_app
import os
import json
import shutil
from datetime import datetime

merge_bp = Blueprint('merge', __name__)

@merge_bp.route('/')
def merge_index():
    return render_template('merge.html')

@merge_bp.route('/upload', methods=['POST'])
def upload_for_merge():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'})
        
        # 检查文件扩展名
        if not file.filename.lower().endswith('.json'):
            return jsonify({'success': False, 'message': '请上传JSON格式的数据文件'})
        
        # 确保临时上传目录存在
        merge_dir = current_app.config['DB_MERGE_DIR']
        os.makedirs(merge_dir, exist_ok=True)
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"merge_{timestamp}.json"
        filepath = os.path.join(merge_dir, filename)
        
        # 保存上传的文件
        file.save(filepath)
        
        # 执行合并
        result = merge_json_files(filepath)
        
        if result['success']:
            return jsonify({
                'success': True, 
                'message': '数据合并成功',
                'main_json_path': result['main_json_path'],
                'new_records': result['new_records'],
                'updated_records': result['updated_records']
            })
        else:
            return jsonify({'success': False, 'message': result['message']})
            
    except Exception as e:
        current_app.logger.error(f"上传数据文件失败: {str(e)}")
        return jsonify({'success': False, 'message': f'上传失败: {str(e)}'})

def merge_json_files(source_path):
    try:
        # 获取主数据文件路径
        main_json_path = current_app.config['MAIN_JSON_PATH']
        backup_dir = current_app.config['DB_BACKUP_DIR']
        
        # 读取源数据
        with open(source_path, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        
        # 如果源数据不是列表，返回错误
        if not isinstance(source_data, list):
            return {'success': False, 'message': '源数据格式不正确，应为JSON数组'}
        
        # 读取主数据
        if os.path.exists(main_json_path):
            with open(main_json_path, 'r', encoding='utf-8') as f:
                main_data = json.load(f)
        else:
            main_data = []
        
        # 如果主数据不是列表，初始化为空列表
        if not isinstance(main_data, list):
            main_data = []
        
        # 备份主数据
        backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{backup_timestamp}.json")
        os.makedirs(backup_dir, exist_ok=True)
        
        if os.path.exists(main_json_path):
            shutil.copy2(main_json_path, backup_path)
        
        # 合并数据
        new_records = 0
        updated_records = 0
        
        for source_person in source_data:
            # 检查是否有ID字段
            if 'id' not in source_person and 'person_id' not in source_person:
                continue
                
            person_id = source_person.get('id') or source_person.get('person_id')
            
            # 查找是否已存在相同ID的数据
            found = False
            for i, main_person in enumerate(main_data):
                main_id = main_person.get('id') or main_person.get('person_id')
                if main_id and main_id == person_id:
                    # 更新现有记录
                    main_data[i] = {**main_person, **source_person}
                    updated_records += 1
                    found = True
                    break
            
            if not found:
                # 添加新记录
                main_data.append(source_person)
                new_records += 1
        
        # 保存合并后的数据
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(main_data, f, ensure_ascii=False, indent=4)
        
        return {
            'success': True, 
            'message': '数据合并成功',
            'main_json_path': main_json_path,
            'new_records': new_records,
            'updated_records': updated_records
        }
        
    except Exception as e:
        current_app.logger.error(f"合并JSON文件失败: {str(e)}")
        return {'success': False, 'message': f'合并失败: {str(e)}'} 