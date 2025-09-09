from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
import traceback
from datetime import datetime
from src.models.content import db, Content, SocialAccount
import json
import requests

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
        
        # Create uploads directory if it doesn't exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        filename = f"{file_id}.{file_extension}"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Save file
        file.save(filepath)
        
        # Get additional data from form
        caption = request.form.get('caption', '')
        scheduled_time = request.form.get('scheduled_time')
        status = request.form.get('status', 'draft')
        
        # Parse scheduled_time if provided
        scheduled_datetime = None
        if scheduled_time:
            try:
                scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
            except ValueError:
                return jsonify({'error': 'Invalid scheduled_time format'}), 400
        
        # Create content record
        content = Content(
            filename=filename,
            original_filename=original_filename,
            file_path=filepath,
            content_type=get_content_type(original_filename),
            caption=caption,
            status=status,
            scheduled_time=scheduled_datetime,
            created_at=datetime.utcnow()
        )
        
        db.session.add(content)
        db.session.commit()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'content': content.to_dict()
        }), 201
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@content_bp.route('/list', methods=['GET'])
def list_content():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status')
        
        query = Content.query
        if status:
            query = query.filter_by(status=status)
        
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'content': [content.to_dict() for content in pagination.items],
            'pagination': {
                'page': page,
                'pages': pagination.pages,
                'per_page': per_page,
                'total': pagination.total
            }
        })
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@content_bp.route('/<int:content_id>', methods=['GET'])
def get_content(content_id):
    try:
        content = Content.query.get_or_404(content_id)
        return jsonify(content.to_dict())
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@content_bp.route('/<int:content_id>', methods=['PUT'])
def update_content(content_id):
    try:
        content = Content.query.get_or_404(content_id)
        data = request.get_json()
        
        # Update allowed fields
        if 'caption' in data:
            content.caption = data['caption']
        if 'status' in data:
            content.status = data['status']
        if 'scheduled_time' in data:
            if data['scheduled_time']:
                try:
                    content.scheduled_time = datetime.fromisoformat(data['scheduled_time'].replace('Z', '+00:00'))
                except ValueError:
                    return jsonify({'error': 'Invalid scheduled_time format'}), 400
            else:
                content.scheduled_time = None
        
        db.session.commit()
        
        return jsonify({
            'message': 'Content updated successfully',
            'content': content.to_dict()
        })
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@content_bp.route('/<int:content_id>', methods=['DELETE'])
def delete_content(content_id):
    try:
        content = Content.query.get_or_404(content_id)
        
        # Delete file from filesystem
        if os.path.exists(content.file_path):
            os.remove(content.file_path)
        
        db.session.delete(content)
        db.session.commit()
        
        return jsonify({'message': 'Content deleted successfully'})
        
    except Exception as e:
        print(traceback.format_exc())
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
        print(traceback.format_exc())
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
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

# Queue endpoints for scheduling support
@content_bp.route('/api/queue', methods=['GET'])
def get_queue():
    """Get all scheduled and draft content sorted by scheduled_time ascending."""
    try:
        # Query for scheduled and draft content
        content_query = Content.query.filter(
            Content.status.in_(['scheduled', 'draft'])
        ).order_by(Content.scheduled_time.asc())
        
        content_list = content_query.all()
        
        return jsonify({
            'message': 'Queue retrieved successfully',
            'queue': [content.to_dict() for content in content_list],
            'count': len(content_list)
        })
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@content_bp.route('/api/queue/process', methods=['POST'])
def process_queue():
    """Process scheduled content and deploy to configured targets."""
    try:
        current_time = datetime.utcnow()
        
        # Find scheduled content that is due to be posted
        eligible_content = Content.query.filter(
            Content.status == 'scheduled',
            Content.scheduled_time <= current_time
        ).all()
        
        processed_items = []
        
        for content in eligible_content:
            try:
                # Mark as 'posting' status
                content.status = 'posting'
                db.session.commit()
                
                # Prepare deployment payload for n8n webhook
                deployment_payload = {
                    'content_id': content.id,
                    'filename': content.filename,
                    'file_path': content.file_path,
                    'content_type': content.content_type,
                    'caption': content.caption,
                    'original_filename': content.original_filename,
                    'scheduled_time': content.scheduled_time.isoformat() if content.scheduled_time else None
                }
                
                # POST to n8n webhook
                webhook_url = 'https://jemertai.app.n8n.cloud/webhook/deploy-content'
                response = requests.post(webhook_url, json=deployment_payload, timeout=30)
                
                if response.status_code == 200:
                    # Mark as posted and set posted_at timestamp
                    content.status = 'posted'
                    content.posted_at = datetime.utcnow()
                else:
                    # Mark as failed if webhook returns non-200 status
                    content.status = 'failed'
                
                db.session.commit()
                
                processed_items.append({
                    'id': content.id,
                    'filename': content.filename,
                    'caption': content.caption,
                    'scheduled_time': content.scheduled_time.isoformat() if content.scheduled_time else None,
                    'status': content.status,
                    'posted_at': content.posted_at.isoformat() if content.posted_at else None,
                    'webhook_status_code': response.status_code
                })
                
            except Exception as deploy_error:
                # Handle individual content deployment errors
                print(f"Error deploying content {content.id}: {str(deploy_error)}")
                content.status = 'failed'
                db.session.commit()
                
                processed_items.append({
                    'id': content.id,
                    'filename': content.filename,
                    'caption': content.caption,
                    'scheduled_time': content.scheduled_time.isoformat() if content.scheduled_time else None,
                    'status': 'failed',
                    'error': str(deploy_error)
                })
        
        return jsonify({
            'message': f'Processed {len(processed_items)} items from queue',
            'processed_items': processed_items,
            'count': len(processed_items)
        })
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
