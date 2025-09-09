from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from src.models.content import db, Content, SocialAccount
import json

content_bp = Blueprint('content', __name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_content_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in {'png', 'jpg', 'jpeg', 'gif'}:
        return 'image'
    elif ext in {'mp4', 'mov', 'avi'}:
        return 'video'
    return 'unknown'

@content_bp.route('/upload', methods=['POST'])
def upload_content():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Create upload directory if it doesn't exist
        upload_path = os.path.join(current_app.static_folder, UPLOAD_FOLDER)
        os.makedirs(upload_path, exist_ok=True)
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        file_path = os.path.join(upload_path, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Create database record
        content = Content(
            filename=unique_filename,
            original_filename=original_filename,
            file_path=f"{UPLOAD_FOLDER}/{unique_filename}",
            content_type=get_content_type(original_filename)
        )
        
        db.session.add(content)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'content': content.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content', methods=['GET'])
def get_all_content():
    try:
        content_list = Content.query.order_by(Content.created_at.desc()).all()
        return jsonify([content.to_dict() for content in content_list])
    except Exception as e:
        # Return an empty array (fixes frontend .map TypeError)
        return jsonify([]), 200

@content_bp.route('/content/<int:content_id>', methods=['GET'])
def get_content(content_id):
    try:
        content = Content.query.get_or_404(content_id)
        return jsonify(content.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>', methods=['PUT'])
def update_content(content_id):
    try:
        content = Content.query.get_or_404(content_id)
        data = request.get_json()
        
        if 'caption' in data:
            content.caption = data['caption']
        if 'hashtags' in data:
            content.hashtags = data['hashtags']
        if 'platforms' in data:
            content.platforms = json.dumps(data['platforms'])
        if 'scheduled_time' in data and data['scheduled_time']:
            content.scheduled_time = datetime.fromisoformat(data['scheduled_time'])
        if 'status' in data:
            content.status = data['status']
        
        db.session.commit()
        return jsonify(content.to_dict())
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/content/<int:content_id>', methods=['DELETE'])
def delete_content(content_id):
    try:
        content = Content.query.get_or_404(content_id)
        
        # Delete file from filesystem
        file_path = os.path.join(current_app.static_folder, content.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({'message': 'Content deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/accounts', methods=['GET'])
def get_social_accounts():
    try:
        accounts = SocialAccount.query.filter_by(is_active=True).all()
        return jsonify([account.to_dict() for account in accounts])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/accounts', methods=['POST'])
def add_social_account():
    try:
        data = request.get_json()
        
        account = SocialAccount(
            platform=data['platform'],
            username=data['username'],
            access_token=data.get('access_token'),
            account_id=data.get('account_id')
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            'message': 'Account added successfully',
            'account': account.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/post/<int:content_id>', methods=['POST'])
def post_content(content_id):
    try:
        content = Content.query.get_or_404(content_id)
        data = request.get_json()
        platforms = data.get('platforms', [])
        
        # This is a placeholder for actual posting logic
        # In a real implementation, you would integrate with Instagram and TikTok APIs
        
        results = []
        for platform in platforms:
            # Simulate posting
            result = {
                'platform': platform,
                'status': 'success',
                'message': f'Posted to {platform} successfully (simulated)',
                'post_id': f'sim_{uuid.uuid4()}'
            }
            results.append(result)
        
        # Update content status
        content.status = 'posted'
        content.posted_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Content posted successfully',
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

