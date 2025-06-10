from flask import Blueprint, request, jsonify, send_file, current_app, render_template
import os
import sqlite3
import json
import shutil
from ..utils import load_json, save_json # Assuming utils is in the parent directory
from werkzeug.utils import secure_filename # Import secure_filename
import datetime
import re
import time
import sys
import uuid

data_management_bp = Blueprint('data_management', __name__, url_prefix='/data_management')

@data_management_bp.route('/')
def index():
    return render_template('data_management.html')

@data_management_bp.route('/export_to_db', methods=['POST'])
def export_to_db():
    try:
        # 获取配置路径
        db_main_dir = current_app.config.get('DB_MAIN_DIR', 'data')
        export_dir = current_app.config.get('DB_EXPORT_DIR')  # 使用DB_EXPORT_DIR而非OUTPUTS_DIR
        os.makedirs(export_dir, exist_ok=True)
        
        # 获取主文件名（不包含路径和扩展名）
        main_json_path = current_app.config.get('MAIN_JSON_PATH')
        if not os.path.exists(main_json_path):
            main_json_path = os.path.join(db_main_dir, 'main.json')
        
        # 提取主文件名（不包含扩展名）
        main_filename = os.path.splitext(os.path.basename(main_json_path))[0]
        
        # 加载JSON数据
        data = []
        if os.path.exists(main_json_path):
            with open(main_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        
        # 检查数据，确保每个记录都有唯一ID
        fixed_data = []
        used_ids = set()
        
        for person in data:
            # 如果没有ID或ID重复，生成新ID
            if 'id' not in person or not person['id'] or person['id'] in used_ids:
                person['id'] = str(uuid.uuid4())
            
            # 记录已使用的ID
            used_ids.add(person['id'])
            fixed_data.append(person)
        
        # 创建时间戳 - 使用多种方法确保不会失败
        try:
            # 方法1：标准datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        except Exception:
            try:
                # 方法2：使用time模块
                timestamp = time.strftime("%Y%m%d_%H%M%S")
            except Exception:
                # 方法3：硬编码时间戳
                timestamp = str(int(time.time()))
        
        # 创建数据库文件路径，使用主文件名和时间戳
        db_file = os.path.join(export_dir, f"{main_filename}_{timestamp}.db")
        
        # 创建SQLite数据库
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # 创建表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id TEXT PRIMARY KEY,
            name TEXT,
            gender TEXT,
            avatar TEXT,
            photos TEXT,
            voices TEXT,
            description TEXT,
            created_time TEXT,
            updated_time TEXT
        )
        ''')
        
        # 插入数据
        for person in fixed_data:
            cursor.execute(
                "INSERT INTO persons VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    person.get('id', ''), 
                    person.get('name', ''),
                    person.get('gender', ''),
                    person.get('avatar', ''),
                    json.dumps(person.get('photos', []), ensure_ascii=False),
                    json.dumps(person.get('voices', []), ensure_ascii=False),
                    person.get('description', ''),
                    person.get('created_time', ''),
                    person.get('updated_time', '')
                )
            )
        
        # 提交并关闭
        conn.commit()
        conn.close()
        
        # 确保路径使用正斜杠
        display_path = db_file.replace('\\', '/')
        
        # 在控制台打印信息以便调试
        print(f"成功导出数据库到: {display_path}")
        
        # 如果数据被修复，保存回原文件
        if len(fixed_data) != len(data):
            with open(main_json_path, 'w', encoding='utf-8') as f:
                json.dump(fixed_data, f, ensure_ascii=False, indent=4)
        
        return jsonify({
            'success': True,
            'message': f'成功导出数据库，共{len(fixed_data)}条记录',
            'filepath': display_path
        })
        
    except Exception as e:
        # 详细记录错误信息
        error_type = type(e).__name__
        error_msg = str(e)
        error_tb = sys.exc_info()[2]
        line_no = error_tb.tb_lineno if error_tb else "未知"
        
        error_detail = f"{error_type} at line {line_no}: {error_msg}"
        print(f"导出数据库失败: {error_detail}")
        
        return jsonify({
            'success': False,
            'message': f'导出失败: {error_detail}'
        })

@data_management_bp.route("/import", methods=["GET", "POST"])
def import_database():
    if request.method == "POST":
        db_import_dir = current_app.config['DB_IMPORT_DIR']
        if 'db_file' not in request.files:
            return render_template("import.html", message="没有文件部分", success=False), 400
        file = request.files['db_file']
        if file.filename == '':
            return render_template("import.html", message="没有选择文件", success=False), 400
        if file and file.filename.endswith('.db'):
            now_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = os.path.splitext(secure_filename(file.filename))[0]
            # 去除base_name中的时间部分（如_20250602_181709等）
            base_name_clean = re.sub(r'_\d{8}_\d{6}$', '', base_name)
            db_filename = f"{base_name_clean}_{now_str}.db"
            json_filename = f"{base_name_clean}_{now_str}.json"
            db_filepath = os.path.join(db_import_dir, db_filename)
            json_filepath = os.path.join(db_import_dir, json_filename)
            try:
                file.save(db_filepath)
                conn = sqlite3.connect(db_filepath)
                cursor = conn.cursor()
                # 读取三张表
                cursor.execute('SELECT * FROM people')
                people_columns = [desc[0] for desc in cursor.description]
                people_data = [dict(zip(people_columns, row)) for row in cursor.fetchall()]
                cursor.execute('SELECT * FROM photos')
                photos_columns = [desc[0] for desc in cursor.description]
                photos_data = [dict(zip(photos_columns, row)) for row in cursor.fetchall()]
                cursor.execute('SELECT * FROM voices')
                voices_columns = [desc[0] for desc in cursor.description]
                voices_data = [dict(zip(voices_columns, row)) for row in cursor.fetchall()]
                # 按person_id组装
                result = []
                for person in people_data:
                    pid = person.get('person_id')
                    person_entry = {
                        'person_id': pid,
                        'name': person.get('name', ''),
                        'title': person.get('title', ''),
                        'description': person.get('description', ''),
                        'photos': [],
                        'voices': []
                    }
                    # 关联照片
                    for photo in photos_data:
                        if photo.get('person_id') == pid:
                            person_entry['photos'].append({
                                'photo_id': photo.get('photo_id', ''),
                                'pose': photo.get('pose', ''),
                                'file_name': photo.get('file_name', ''),
                                'uri': photo.get('uri', ''),
                                'description': photo.get('description', '')
                            })
                    # 关联音频
                    for voice in voices_data:
                        if voice.get('person_id') == pid:
                            person_entry['voices'].append({
                                'voice_id': voice.get('voice_id', ''),
                                'file_name': voice.get('file_name', ''),
                                'uri': voice.get('uri', ''),
                                'description': voice.get('description', '')
                            })
                    result.append(person_entry)
                with open(json_filepath, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                conn.close()
                return render_template("import.html", message=f"转换成功！.db和.json文件已保存至：{db_filepath} 和 {json_filepath}", success=True)
            except Exception as e:
                if os.path.exists(db_filepath):
                    os.remove(db_filepath)
                return render_template("import.html", message=f"转换失败：{str(e)}", success=False), 500
        else:
            return render_template("import.html", message="文件格式错误，请上传 .db 文件", success=False), 400
    return render_template("import.html")

@data_management_bp.route("/merge", methods=["GET", "POST"])
def merge_database():
    if request.method == "POST":
        # Use app.config to get the paths
        main_json_path = current_app.config['MAIN_JSON_PATH']
        db_merge_dir = current_app.config['DB_MERGE_DIR']
        db_main_dir = current_app.config['DB_MAIN_DIR'] # Assuming needed for save_json
        backup_dir = os.path.join(current_app.config['BASE_DIR'], 'db_backup') # Assuming backup_dir structure
        json_file_legacy = os.path.join(current_app.config['DB_MAIN_DIR'], 'output1.json') # Assuming legacy file structure
        base_photos_dir = os.path.join(current_app.config['BASE_DIR'], 'base_photos')
        base_voices_dir = os.path.join(current_app.config['BASE_DIR'], 'base_voices')

        if 'file' not in request.files:
            return jsonify({"message": "没有文件部分"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"message": "没有选择文件"}), 400

        if file and file.filename.endswith('.json'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(db_merge_dir, filename)
            file.save(filepath)

            try:
                # Load existing main data
                main_data = load_json(main_json_path)

                # Load data from the uploaded merge file
                with open(filepath, 'r', encoding='utf-8') as f:
                    merge_data = json.load(f)

                # Create dictionaries for faster lookup
                main_dict = {p.get('person_id'): p for p in main_data}
                merge_dict = {p.get('person_id'): p for p in merge_data}

                merged_data = []
                merged_ids = set()

                # Start with main data
                for person_id, person_data in main_dict.items():
                    if person_id in merge_dict:
                        # Merge existing person with imported person
                        merged_person = main_dict[person_id].copy()
                        merge_person_data = merge_dict[person_id]

                        # Merge fields, prioritize imported data if not empty
                        for field in ['name', 'title', 'description']:
                            if merge_person_data.get(field) and merge_person_data.get(field) != merged_person.get(field):
                                merged_person[field] = merge_person_data[field]

                        # Merge aliases (ensure uniqueness and list format)
                        main_aliases = set(merged_person.get('alias', []) if isinstance(merged_person.get('alias'), list) else [merged_person.get('alias')].copy() if merged_person.get('alias') else [])
                        merge_aliases = set(merge_person_data.get('alias', []) if isinstance(merge_person_data.get('alias'), list) else [merge_person_data.get('alias')].copy() if merge_person_data.get('alias') else [])
                        merged_person['alias'] = list(main_aliases.union(merge_aliases))

                        # Merge photos (ensure uniqueness by photo_id)
                        main_photos = {p.get('photo_id'): p for p in merged_person.get('photos', [])}
                        merge_photos = {p.get('photo_id'): p for p in merge_person_data.get('photos', [])}
                        merged_person['photos'] = list(main_photos.values()) + [p for id, p in merge_photos.items() if id not in main_photos]

                        # Merge voices (ensure uniqueness by voice_id)
                        main_voices = {v.get('voice_id'): v for v in merged_person.get('voices', [])}
                        merge_voices = {v.get('voice_id'): v for v in merge_person_data.get('voices', [])}
                        merged_person['voices'] = list(main_voices.values()) + [v for id, v in merge_voices.items() if id not in main_voices]

                        merged_data.append(merged_person)
                        merged_ids.add(person_id)
                    else:
                        # Keep existing person if not in merge data
                        merged_data.append(person_data)
                        merged_ids.add(person_id)

                # Add new persons from merge data
                for person_id, person_data in merge_dict.items():
                    if person_id not in merged_ids:
                        merged_data.append(person_data)

                # Save the merged data
                save_json(merged_data, main_json_path, db_main_dir, backup_dir, json_file_legacy) # Pass all required args

                return jsonify({"message": "数据库合并成功！"})

            except json.JSONDecodeError:
                return jsonify({"message": "合并文件格式错误，不是有效的JSON"}), 400
            except Exception as e:
                print(f"Error during merge: {e}")
                return jsonify({"message": f"合并失败：{str(e)}"}), 500

        else:
            return jsonify({"message": "文件格式错误，请上传 .json 文件"}), 400

    return render_template("merge.html") 