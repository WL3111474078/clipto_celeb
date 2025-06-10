from flask import Blueprint, request, jsonify, render_template, current_app
import os
import json
import shutil
from datetime import datetime
from ..utils import load_json, save_json

delete_bp = Blueprint('delete', __name__)

def load_data():
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

def save_data(data):
    # 使用配置的主数据文件路径
    main_json_path = current_app.config.get('MAIN_JSON_PATH')
    
    # 备份原始文件
    backup_dir = current_app.config.get('DB_BACKUP_DIR')
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"backup_{timestamp}.json")
    
    try:
        if os.path.exists(main_json_path):
            shutil.copy2(main_json_path, backup_path)
    except Exception as e:
        current_app.logger.error(f"备份数据文件失败: {str(e)}")
        
    # 保存数据
    try:
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        current_app.logger.error(f"保存数据文件失败: {str(e)}")
        return False

@delete_bp.route('/')
def delete_index():
    return render_template('delete.html')

@delete_bp.route('/search', methods=['GET'])
def search_person():
    keyword = request.args.get('keyword', '').lower().strip()
    if not keyword:
        return jsonify({'success': False, 'message': '请输入搜索关键词'})
    
    data = load_data()
    results = []
    
    for person in data:
        # 检查姓名、ID或描述是否匹配关键字
        name = str(person.get('name', '')).lower()
        person_id = str(person.get('id', '') or person.get('person_id', '')).lower()
        description = str(person.get('description', '')).lower()
        
        # 获取照片信息
        avatar = None
        if 'photos' in person and person['photos']:
            avatar = person['photos'][0].get('file_name')
            
        # 检查关键字是否匹配
        if keyword in name or keyword in person_id or keyword in description:
            results.append({
                'id': person.get('id') or person.get('person_id', ''),
                'name': person.get('name', '未命名'),
                'gender': person.get('gender', '未知'),
                'avatar': avatar
            })
    
    return jsonify({'success': True, 'results': results})

@delete_bp.route('/delete', methods=['POST'])
def delete_person():
    person_id = request.form.get('id')
    if not person_id:
        return jsonify({'success': False, 'message': '缺少人物ID'})
    
    data = load_data()
    person_to_delete = None
    person_index = -1
    
    # 查找要删除的人物
    for idx, person in enumerate(data):
        if person.get('id') == person_id or person.get('person_id') == person_id:
            person_to_delete = person
            person_index = idx
            break
    
    if person_to_delete is None:
        return jsonify({'success': False, 'message': '未找到指定人物'})
    
    # 删除相关文件
    try:
        # 删除照片
        photos_dir = current_app.config.get('BASE_PHOTOS_DIR')
        if 'photos' in person_to_delete:
            for photo in person_to_delete['photos']:
                filename = photo.get('file_name')
                if filename:
                    file_path = os.path.join(photos_dir, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        # 删除语音
        voices_dir = current_app.config.get('BASE_VOICES_DIR')
        if 'voices' in person_to_delete:
            for voice in person_to_delete['voices']:
                filename = voice.get('file_name')
                if filename:
                    file_path = os.path.join(voices_dir, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        # 从JSON中删除
        data.pop(person_index)
        
        # 保存更新后的数据
        save_result = save_data(data)
        
        if save_result:
            return jsonify({'success': True, 'message': '人物已成功删除'})
        else:
            return jsonify({'success': False, 'message': '保存更新后的数据失败'})
            
    except Exception as e:
        current_app.logger.error(f"删除人物失败: {str(e)}")
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})

@delete_bp.route("/delete_photo", methods=["POST"])
def delete_photo():
    # Logic needs to be adapted to work with the main JSON and the specific person/photo
    # This route might be redundant if photo deletion is handled via edit or person_detail page
    # Assuming this is a separate route for photo deletion
    data = request.get_json()
    person_id = data.get('person_id')
    photo_filename = data.get('photo_filename')

    if not person_id or not photo_filename:
        return jsonify({'success': False, 'message': '缺少人物ID或照片文件名'}), 400

    # Use app.config to get the paths
    main_json_path = current_app.config['MAIN_JSON_PATH']
    db_main_dir = current_app.config['DB_MAIN_DIR'] # Assuming needed for save_json
    backup_dir = os.path.join(current_app.config['BASE_DIR'], 'db_backup') # Assuming backup_dir structure
    json_file_legacy = os.path.join(current_app.config['DB_MAIN_DIR'], 'output1.json') # Assuming legacy file structure
    base_photos_dir = os.path.join(current_app.config['BASE_DIR'], 'base_photos')


    # Pass db_main_dir to load_json
    data = load_json(db_main_dir)

    person_found = None
    for p in data:
        if p.get('person_id') == person_id:
            person_found = p
            break

    if not person_found:
        return jsonify({'success': False, 'message': '未找到指定人物'}), 404

    # Find and remove the photo from the person's photo list
    initial_photo_count = len(person_found.get('photos', []))
    person_found['photos'] = [photo for photo in person_found.get('photos', []) if photo.get('file_name') != photo_filename]

    if len(person_found['photos']) == initial_photo_count:
         return jsonify({'success': False, 'message': '未找到指定照片'}), 404

    # Delete the physical file
    photo_path = os.path.join(base_photos_dir, photo_filename)
    if os.path.exists(photo_path):
        try:
            os.remove(photo_path)
        except Exception as e:
            print(f"Error deleting photo file {photo_path}: {e}")
            # Continue even if file deletion fails, as the JSON is updated

    save_json(data, main_json_path, db_main_dir, backup_dir, json_file_legacy) # Pass all required args

    return jsonify({'success': True, 'message': '照片删除成功'})

@delete_bp.route("/delete_voice", methods=["POST"])
def delete_voice():
    # Logic needs to be adapted similarly for voice deletion
     data = request.get_json()
     person_id = data.get('person_id')
     voice_filename = data.get('voice_filename')

     if not person_id or not voice_filename:
         return jsonify({'success': False, 'message': '缺少人物ID或音频文件名'}), 400

     # Use app.config to get the paths
     main_json_path = current_app.config['MAIN_JSON_PATH']
     db_main_dir = current_app.config['DB_MAIN_DIR'] # Assuming needed for save_json
     backup_dir = os.path.join(current_app.config['BASE_DIR'], 'db_backup') # Assuming backup_dir structure
     json_file_legacy = os.path.join(current_app.config['DB_MAIN_DIR'], 'output1.json') # Assuming legacy file structure
     base_voices_dir = os.path.join(current_app.config['BASE_DIR'], 'base_voices')

     # Pass db_main_dir to load_json
     data = load_json(db_main_dir)

     person_found = None
     for p in data:
         if p.get('person_id') == person_id:
             person_found = p
             break

     if not person_found:
         return jsonify({'success': False, 'message': '未找到指定人物'}), 404

     # Find and remove the voice from the person's voice list
     initial_voice_count = len(person_found.get('voices', []))
     person_found['voices'] = [voice for voice in person_found.get('voices', []) if voice.get('file_name') != voice_filename]

     if len(person_found['voices']) == initial_voice_count:
         return jsonify({'success': False, 'message': '未找到指定音频'}), 404

     # Delete the physical file
     voice_path = os.path.join(base_voices_dir, voice_filename)
     if os.path.exists(voice_path):
         try:
             os.remove(voice_path)
         except Exception as e:
             print(f"Error deleting voice file {voice_path}: {e}")
             # Continue even if file deletion fails, as the JSON is updated

     save_json(data, main_json_path, db_main_dir, backup_dir, json_file_legacy) # Pass all required args

     return jsonify({'success': True, 'message': '音频删除成功'}) 