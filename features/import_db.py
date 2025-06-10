from flask import Blueprint, jsonify, render_template, request, current_app
import os
import json
import sqlite3
from datetime import datetime
import shutil

import_bp = Blueprint('import', __name__)

@import_bp.route('/')
def import_index():
    return render_template('import.html')

@import_bp.route('/upload', methods=['POST'])
def upload_db():
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有上传文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '未选择文件'})
        
        # 检查文件扩展名
        if not file.filename.endswith('.db'):
            return jsonify({'success': False, 'message': '请上传.db格式的SQLite数据库文件'})
        
        # 确保临时上传目录存在
        import_dir = current_app.config['DB_IMPORT_DIR']
        os.makedirs(import_dir, exist_ok=True)
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"import_{timestamp}.db"
        filepath = os.path.join(import_dir, filename)
        
        # 保存上传的文件
        file.save(filepath)
        
        # 转换数据库为JSON
        result = convert_db_to_json(filepath)
        
        if result['success']:
            return jsonify({
                'success': True, 
                'message': '数据库导入成功',
                'json_path': result['json_path'],
                'record_count': result['record_count']
            })
        else:
            return jsonify({'success': False, 'message': result['message']})
            
    except Exception as e:
        current_app.logger.error(f"导入数据库失败: {str(e)}")
        return jsonify({'success': False, 'message': f'导入失败: {str(e)}'})

def convert_db_to_json(db_path):
    try:
        main_json_path = current_app.config['MAIN_JSON_PATH']
        db_backup_dir = current_app.config['DB_BACKUP_DIR']
        
        # 创建一个到SQLite数据库的连接
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 返回字典形式的结果
        cursor = conn.cursor()
        
        # 查询所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table['name'] for table in tables]
        
        persons_table = None
        for table_name in ["persons", "characters", "celebs", "celebrities"]:
            if table_name in table_names:
                persons_table = table_name
                break
                
        if not persons_table:
            return {'success': False, 'message': '无法在数据库中找到人物表'}
        
        # 查询人物表结构
        cursor.execute(f"PRAGMA table_info({persons_table})")
        columns = [column['name'] for column in cursor.fetchall()]
        
        # 查询人物数据
        cursor.execute(f"SELECT * FROM {persons_table}")
        persons_data = []
        
        for row in cursor.fetchall():
            person = {}
            for column in columns:
                person[column] = row[column]
            
            # 确保必要的字段存在
            if 'id' not in person and 'person_id' in person:
                person['id'] = person['person_id']
            elif 'person_id' not in person and 'id' in person:
                person['person_id'] = person['id']
            
            # 查询照片数据
            if 'photos' in table_names:
                cursor.execute(f"SELECT * FROM photos WHERE person_id=?", (person.get('id'),))
                photos = []
                for photo_row in cursor.fetchall():
                    photo = {}
                    for key in photo_row.keys():
                        photo[key] = photo_row[key]
                    photos.append(photo)
                person['photos'] = photos
            
            # 查询语音数据
            if 'voices' in table_names:
                cursor.execute(f"SELECT * FROM voices WHERE person_id=?", (person.get('id'),))
                voices = []
                for voice_row in cursor.fetchall():
                    voice = {}
                    for key in voice_row.keys():
                        voice[key] = voice_row[key]
                    voices.append(voice)
                person['voices'] = voices
            
            persons_data.append(person)
        
        # 关闭数据库连接
        conn.close()
        
        # 备份现有JSON数据
        if os.path.exists(main_json_path):
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(db_backup_dir, f"backup_{backup_timestamp}.json")
            shutil.copy2(main_json_path, backup_path)
        
        # 保存新的JSON数据
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(persons_data, f, ensure_ascii=False, indent=4)
        
        return {
            'success': True, 
            'message': '数据库导入成功',
            'json_path': main_json_path,
            'record_count': len(persons_data)
        }
        
    except Exception as e:
        current_app.logger.error(f"转换数据库到JSON失败: {str(e)}")
        return {'success': False, 'message': f'转换失败: {str(e)}'} 