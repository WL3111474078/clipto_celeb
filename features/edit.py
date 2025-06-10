from flask import Blueprint, request, jsonify, render_template, current_app, flash, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename
from ..utils import load_json, save_json # Assuming utils is in the parent directory
from datetime import datetime
import shutil
import uuid
import time
import re

edit_bp = Blueprint('edit', __name__, url_prefix='/edit')

# 新增函数：重新编号照片和音频
def renumber_media_files(person, media_type, base_dir):
    """
    重新编号人物的照片或音频文件，确保编号连续
    
    参数:
    - person: 人物数据字典
    - media_type: 'photos' 或 'voices'
    - base_dir: 基础目录路径
    
    返回:
    - 重命名操作是否成功
    """
    try:
        if media_type not in person or not person[media_type]:
            return True
            
        items = person[media_type]
        sanitized_name = person.get('name', '').replace(" ", "_").replace("/", "_")
        numeric_id_part = person.get("person_id", "").split('_')[0] if person.get("person_id", "") else "unknown"
        
        # 确定文件类型标识
        type_id = "photo" if media_type == "photos" else "voice"
        
        # 按顺序重新编号
        for idx, item in enumerate(items):
            old_filename = item.get('file_name')
            if not old_filename:
                continue
                
            # 获取原始文件扩展名
            original_extension = os.path.splitext(old_filename)[1]
            
            # 生成新的文件名和ID（不带时间戳）
            new_filename = f"{numeric_id_part}_{sanitized_name}_{type_id}_{idx+1}{original_extension}"
            new_id = f"{numeric_id_part}_{sanitized_name}_{type_id}_{idx+1}"
            
            # 如果文件名相同，不需要重命名
            if old_filename == new_filename:
                continue
                
            # 重命名物理文件
            old_path = os.path.join(base_dir, old_filename)
            new_path = os.path.join(base_dir, new_filename)
            
            if os.path.exists(old_path):
                # 如果目标文件已存在，先删除
                if os.path.exists(new_path):
                    os.remove(new_path)
                shutil.move(old_path, new_path)
            
            # 更新JSON中的记录
            item['file_name'] = new_filename
            item[f'{type_id}_id'] = new_id
        
        return True
    except Exception as e:
        print(f"重新编号{media_type}出错: {e}")
        import traceback
        print(traceback.format_exc())
        return False

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
    # 首先尝试获取配置的主数据文件路径
    main_json_path = current_app.config.get('MAIN_JSON_PATH')
    
    # 确保目录存在
    os.makedirs(os.path.dirname(main_json_path), exist_ok=True)
    
    try:
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        current_app.logger.error(f"保存JSON数据失败: {str(e)}")
        return False

@edit_bp.route('/')
def edit_index():
    """显示编辑页面"""
    person_id = request.args.get('id')
    if not person_id:
        # 如果没有指定ID，返回人物列表页面
        return render_template('edit.html', person=None)
    
    # 加载数据
    data = load_json_data()
    
    # 查找指定ID的人物
    person = None
    for p in data:
        if str(p.get('id', '')) == str(person_id) or str(p.get('person_id', '')) == str(person_id):
            person = p
            break
    
    # 标准化数据格式
    if person:
        # 确保所有必要的字段都存在
        person_data = {
            'id': person.get('id') or person.get('person_id', ''),
            'name': person.get('name', ''),
            'gender': person.get('gender', ''),
            'title': person.get('title', ''),
            'description': person.get('description', ''),
            'photo_path': person.get('photo_path', ''),
            'audio_path': person.get('audio_path', ''),
            'photos': person.get('photos', []),
            'voices': person.get('voices', [])
        }
        return render_template('edit.html', person=person_data)
    else:
        return render_template('edit.html', person=None, error="未找到指定ID的人物")

@edit_bp.route('/update', methods=['POST'])
def update_person():
    """更新人物基本信息"""
    person_id = request.form.get('id')
    if not person_id:
        return jsonify({"success": False, "message": "未提供人物ID"})
    
    # 加载数据
    data = load_json_data()
    
    # 查找指定ID的人物
    person_index = -1
    for i, p in enumerate(data):
        if str(p.get('id', '')) == str(person_id) or str(p.get('person_id', '')) == str(person_id):
            person_index = i
            break
    
    if person_index == -1:
        return jsonify({"success": False, "message": "未找到指定ID的人物"})
    
    # 更新基本信息
    data[person_index]['name'] = request.form.get('name', data[person_index].get('name', ''))
    data[person_index]['gender'] = request.form.get('gender', data[person_index].get('gender', ''))
    data[person_index]['description'] = request.form.get('description', data[person_index].get('description', ''))
    data[person_index]['title'] = request.form.get('title', data[person_index].get('title', ''))
    
    # 新增：保存别名字段
    if 'alias' in request.form:
        data[person_index]['alias'] = request.form.get('alias', '')
    
    # 处理照片上传
    photo = request.files.get('photo')
    if photo and photo.filename:
        photo_dir = current_app.config.get('PHOTO_DIR')
        if not os.path.exists(photo_dir):
            os.makedirs(photo_dir)
        
        filename = secure_filename(f"{person_id}_{photo.filename}")
        photo_path = os.path.join(photo_dir, filename)
        photo.save(photo_path)
        
        # 相对路径存储，以便前端访问
        relative_path = os.path.join('/photos', filename)
        data[person_index]['photo_path'] = relative_path
    
    # 处理音频上传
    audio = request.files.get('audio')
    if audio and audio.filename:
        audio_dir = current_app.config.get('AUDIO_DIR')
        if not os.path.exists(audio_dir):
            os.makedirs(audio_dir)
        
        filename = secure_filename(f"{person_id}_{audio.filename}")
        audio_path = os.path.join(audio_dir, filename)
        audio.save(audio_path)
        
        # 相对路径存储，以便前端访问
        relative_path = os.path.join('/audios', filename)
        data[person_index]['audio_path'] = relative_path
    
    # 保存更新后的数据
    if save_json_data(data):
        return jsonify({"success": True, "message": "人物信息已成功更新"})
    else:
        return jsonify({"success": False, "message": "保存数据失败"})

@edit_bp.route('/delete_photo/<person_id>', methods=['DELETE'])
def delete_photo(person_id):
    """删除人物照片"""
    if not person_id:
        return jsonify({"success": False, "message": "未提供人物ID"})
    
    # 加载数据
    data = load_json_data()
    
    # 查找指定ID的人物
    person_index = -1
    for i, p in enumerate(data):
        if str(p.get('id', '')) == str(person_id) or str(p.get('person_id', '')) == str(person_id):
            person_index = i
            break
    
    if person_index == -1:
        return jsonify({"success": False, "message": "未找到指定ID的人物"})
    
    # 删除文件系统中的照片
    photo_path = data[person_index].get('photo_path', '')
    if photo_path:
        try:
            # 从相对路径获取完整路径
            if photo_path.startswith('/photos/'):
                photo_filename = os.path.basename(photo_path)
                full_path = os.path.join(current_app.config.get('PHOTO_DIR'), photo_filename)
                if os.path.exists(full_path):
                    os.remove(full_path)
        except Exception as e:
            current_app.logger.error(f"删除照片文件失败: {str(e)}")
            # 即使文件删除失败，也继续删除记录
    
    # 更新数据
    data[person_index]['photo_path'] = ''
    
    # 保存更新后的数据
    if save_json_data(data):
        return jsonify({"success": True, "message": "照片已成功删除"})
    else:
        return jsonify({"success": False, "message": "保存数据失败"})

@edit_bp.route('/delete_audio/<person_id>', methods=['DELETE'])
def delete_audio(person_id):
    """删除人物音频"""
    if not person_id:
        return jsonify({"success": False, "message": "未提供人物ID"})
    
    # 加载数据
    data = load_json_data()
    
    # 查找指定ID的人物
    person_index = -1
    for i, p in enumerate(data):
        if str(p.get('id', '')) == str(person_id) or str(p.get('person_id', '')) == str(person_id):
            person_index = i
            break
    
    if person_index == -1:
        return jsonify({"success": False, "message": "未找到指定ID的人物"})
    
    # 删除文件系统中的音频
    audio_path = data[person_index].get('audio_path', '')
    if audio_path:
        try:
            # 从相对路径获取完整路径
            if audio_path.startswith('/audios/'):
                audio_filename = os.path.basename(audio_path)
                full_path = os.path.join(current_app.config.get('AUDIO_DIR'), audio_filename)
                if os.path.exists(full_path):
                    os.remove(full_path)
        except Exception as e:
            current_app.logger.error(f"删除音频文件失败: {str(e)}")
            # 即使文件删除失败，也继续删除记录
    
    # 更新数据
    data[person_index]['audio_path'] = ''
    
    # 保存更新后的数据
    if save_json_data(data):
        return jsonify({"success": True, "message": "音频已成功删除"})
    else:
        return jsonify({"success": False, "message": "保存数据失败"})

@edit_bp.route('/person/<person_id>/edit_pose', methods=['POST'])
def edit_person_pose(person_id):
    """编辑人物照片姿势"""
    try:
        pose_changes = request.json.get('pose_changes', {})
        if not pose_changes:
            return jsonify({'success': False, 'message': '未提供姿势更改数据'})
        
        # 加载主数据
        data = load_json_data()
        
        # 查找人物
        found = False
        for person in data:
            if str(person.get('id', '')) == str(person_id) or str(person.get('person_id', '')) == str(person_id):
                found = True
                
                # 检查照片并更新姿势
                if 'photos' in person:
                    for photo in person['photos']:
                        photo_id = str(photo.get('photo_id', ''))
                        if photo_id in pose_changes:
                            # 保存数字类型的姿势值(0,1,2)
                            photo['pose'] = int(pose_changes[photo_id])
                
                break
        
        if not found:
            return jsonify({'success': False, 'message': '未找到指定人物'})
        
        # 保存更改
        main_json_path = current_app.config.get('MAIN_JSON_PATH')
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return jsonify({'success': True, 'message': '姿势更改已保存'})
    
    except Exception as e:
        current_app.logger.error(f"编辑人物姿势时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'})

@edit_bp.route('/person/<person_id>/delete_photo', methods=['POST'])
def delete_person_photo(person_id):
    """删除人物照片集合中的指定照片"""
    try:
        data = request.get_json()
        photo_id = data.get('photo_id')
        if not photo_id:
            return jsonify({'success': False, 'message': '缺少照片ID'}), 400
        
        base_photos_dir = current_app.config['BASE_PHOTOS_DIR']
        data = load_json_data()
        person_found = next((p for p in data if p.get('person_id') == person_id), None)
        
        if not person_found:
            return jsonify({'success': False, 'message': '未找到指定人物'}), 404
        
        photo_to_delete = next((photo for photo in person_found.get('photos', []) if photo.get('photo_id') == photo_id), None)
        if not photo_to_delete:
            return jsonify({'success': False, 'message': '未找到指定照片'}), 404
        
        photo_filename = photo_to_delete.get('file_name')
        person_found['photos'].remove(photo_to_delete)
        
        if photo_filename:
            photo_path = os.path.join(base_photos_dir, photo_filename)
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except Exception as e:
                    current_app.logger.error(f"删除照片文件出错: {e}")
        
        renumber_media_files(person_found, 'photos', base_photos_dir)
        save_json_data(data)
        return jsonify({'success': True, 'message': '照片删除成功'})
    except Exception as e:
        current_app.logger.error(f"删除照片失败: {e}")
        return jsonify({'success': False, 'message': f'删除照片失败: {str(e)}'}), 500

@edit_bp.route('/person/<person_id>/delete_voice', methods=['POST'])
def delete_person_voice(person_id):
    """删除人物音频集合中的指定音频"""
    try:
        data = request.get_json()
        voice_id = data.get('voice_id')
        if not voice_id:
            return jsonify({'success': False, 'message': '缺少音频ID'}), 400
        
        base_voices_dir = current_app.config['BASE_VOICES_DIR']
        data = load_json_data()
        person_found = next((p for p in data if p.get('person_id') == person_id), None)
        
        if not person_found:
            return jsonify({'success': False, 'message': '未找到指定人物'}), 404
        
        voice_to_delete = next((voice for voice in person_found.get('voices', []) if voice.get('voice_id') == voice_id), None)
        if not voice_to_delete:
            return jsonify({'success': False, 'message': '未找到指定音频'}), 404
        
        voice_filename = voice_to_delete.get('file_name')
        person_found['voices'].remove(voice_to_delete)
        
        if voice_filename:
            voice_path = os.path.join(base_voices_dir, voice_filename)
            if os.path.exists(voice_path):
                try:
                    os.remove(voice_path)
                except Exception as e:
                    current_app.logger.error(f"删除音频文件出错: {e}")
        
        renumber_media_files(person_found, 'voices', base_voices_dir)
        save_json_data(data)
        return jsonify({'success': True, 'message': '音频删除成功'})
    except Exception as e:
        current_app.logger.error(f"删除音频失败: {e}")
        return jsonify({'success': False, 'message': f'删除音频失败: {str(e)}'}), 500

@edit_bp.route('/person/<person_id>/upload_photo', methods=['POST'])
def upload_person_photo(person_id):
    """上传人物照片"""
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'message': '未包含照片文件'})
        
        photos = request.files.getlist('photo')
        if not photos or photos[0].filename == '':
            return jsonify({'success': False, 'message': '未选择照片'})
        
        # 获取姿势值(0,1,2)
        pose = int(request.form.get('pose', 0))  # 默认为0(正面)
        
        # 加载主数据
        data = load_json_data()
        
        # 查找人物
        person = None
        person_index = -1
        for i, p in enumerate(data):
            if str(p.get('id', '')) == str(person_id) or str(p.get('person_id', '')) == str(person_id):
                person = p
                person_index = i
                break
        
        if not person:
            return jsonify({'success': False, 'message': '未找到指定人物'})
        
        # 确保照片目录存在
        photos_dir = current_app.config.get('BASE_PHOTOS_DIR')
        os.makedirs(photos_dir, exist_ok=True)
        
        # 确保人物有photos字段
        if 'photos' not in person:
            person['photos'] = []
        
        # 上传照片
        uploaded_files = []
        for photo in photos:
            # 安全的文件名
            filename = secure_filename(photo.filename)
            if not filename:
                continue
            
            # 生成唯一文件名
            unique_filename = f"{person.get('id', person_id)}_{int(time.time())}_{filename}"
            file_path = os.path.join(photos_dir, unique_filename)
            
            # 保存文件
            photo.save(file_path)
            
            # 生成照片ID
            photo_id = str(uuid.uuid4())
            
            # 添加到照片列表
            person['photos'].append({
                'photo_id': photo_id,
                'file_name': unique_filename,
                'pose': pose  # 使用数字姿势值
            })
            
            uploaded_files.append(unique_filename)
        
        # 更新数据
        data[person_index] = person
        
        # 保存数据
        main_json_path = current_app.config.get('MAIN_JSON_PATH')
        with open(main_json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        return jsonify({
            'success': True, 
            'message': f'成功上传 {len(uploaded_files)} 张照片',
            'files': uploaded_files
        })
    
    except Exception as e:
        current_app.logger.error(f"上传照片时出错: {str(e)}")
        return jsonify({'success': False, 'message': f'服务器错误: {str(e)}'})

@edit_bp.route('/person/<person_id>/upload_voice', methods=['POST'])
def upload_person_voice(person_id):
    """上传人物音频"""
    try:
        base_voices_dir = current_app.config['BASE_VOICES_DIR']
        
        files = request.files.getlist('voice')
        if not files or len(files) == 0:
            return jsonify({'success': False, 'message': '没有音频文件'}), 400

        data = load_json_data()
        person_found = next((p for p in data if p.get('person_id') == person_id), None)

        if not person_found:
            return jsonify({'success': False, 'message': '未找到指定人物'}), 404

        sanitized_name = person_found.get('name', '').replace(" ", "_").replace("/", "_")
        numeric_id_part = person_found.get("person_id", "").split('_')[0] if person_found.get("person_id", "") else "unknown"
        voice_count = len(person_found.get('voices', []))
        new_voices = []

        for file in files:
            if not file or file.filename == '':
                continue
                
            # 生成文件名，不使用时间戳
            original_extension = os.path.splitext(file.filename)[1]
            filename = f"{numeric_id_part}_{sanitized_name}_voice_{voice_count + 1}{original_extension}"
            
            # 确保目录存在
            os.makedirs(base_voices_dir, exist_ok=True)
            
            filepath = os.path.join(base_voices_dir, filename)
            file.save(filepath)
            
            voice_dict = {
                "voice_id": f"{numeric_id_part}_{sanitized_name}_voice_{voice_count + 1}",
                "file_name": filename,
                "uri": "",
                "description": ""
            }
            
            if "voices" not in person_found:
                person_found["voices"] = []
                
            person_found["voices"].append(voice_dict)
            new_voices.append(voice_dict)
            voice_count += 1

        save_json_data(data)
        return jsonify({'success': True, 'new_voices': new_voices})
        
    except Exception as e:
        current_app.logger.error(f"上传音频失败: {str(e)}")
        return jsonify({'success': False, 'message': f'音频上传失败: {str(e)}'}), 500

@edit_bp.route('/person/<person_id>/save_edit', methods=['POST'])
def save_all_edits(person_id):
    """处理所有编辑操作，包括照片pose编辑、照片/音频删除和上传"""
    try:
        # 获取配置路径
        base_photos_dir = current_app.config['BASE_PHOTOS_DIR']
        base_voices_dir = current_app.config['BASE_VOICES_DIR']
        
        # 加载数据
        data = load_json_data()
        
        # 查找person
        person_found = next((p for p in data if p.get('id') == person_id or p.get('person_id') == person_id), None)
        
        if not person_found:
            return jsonify({'success': False, 'message': '未找到指定人物'}), 404
        
        # 处理照片pose更改
        if 'pose_changes' in request.form:
            pose_changes = json.loads(request.form.get('pose_changes', '{}'))
            for photo_id, new_pose in pose_changes.items():
                for photo in person_found.get('photos', []):
                    if photo.get('photo_id') == photo_id:
                        photo['pose'] = new_pose
                        break
        
        # 处理照片删除
        if 'photos_to_delete' in request.form:
            photos_to_delete = json.loads(request.form.get('photos_to_delete', '[]'))
            for photo_info in photos_to_delete:
                photo_id = photo_info.get('photoId')
                file_name = photo_info.get('fileName')
                
                # 从列表中移除照片
                person_found['photos'] = [p for p in person_found.get('photos', []) if p.get('photo_id') != photo_id]
                
                # 删除物理文件
                photo_path = os.path.join(base_photos_dir, file_name)
                if os.path.exists(photo_path):
                    try:
                        os.remove(photo_path)
                    except Exception as e:
                        current_app.logger.error(f"删除照片文件出错: {e}")
            
            # 重新编号照片
            renumber_media_files(person_found, 'photos', base_photos_dir)
        
        # 处理音频删除
        if 'voices_to_delete' in request.form:
            voices_to_delete = json.loads(request.form.get('voices_to_delete', '[]'))
            for voice_info in voices_to_delete:
                voice_id = voice_info.get('voiceId')
                file_name = voice_info.get('fileName')
                
                # 从列表中移除音频
                person_found['voices'] = [v for v in person_found.get('voices', []) if v.get('voice_id') != voice_id]
                
                # 删除物理文件
                voice_path = os.path.join(base_voices_dir, file_name)
                if os.path.exists(voice_path):
                    try:
                        os.remove(voice_path)
                    except Exception as e:
                        current_app.logger.error(f"删除音频文件出错: {e}")
            
            # 重新编号音频
            renumber_media_files(person_found, 'voices', base_voices_dir)
        
        # 处理上传的新照片和音频 - 复用已有的上传接口
        
        # 保存所有更改到JSON文件
        save_json_data(data)
        
        return jsonify({'success': True, 'message': '主库信息更新成功'})
    
    except Exception as e:
        current_app.logger.error(f"保存更改出错: {e}")
        return jsonify({'success': False, 'message': f'保存失败: {str(e)}'}), 500

@edit_bp.route('/edit/batch', methods=['POST'], endpoint='batch_edit_person')
def batch_edit_person():
    # Implementation of batch_edit_person method
    pass

    # Placeholder return
    return jsonify({'success': True, 'message': 'Batch edit method not implemented yet'}) 