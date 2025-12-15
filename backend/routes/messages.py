from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Message, User, Study, StudyApplication, MessageType
import uuid
from datetime import datetime

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/', methods=['GET'])
@jwt_required()
def get_messages():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        # Get query parameters
        study_id = request.args.get('study_id')
        other_user_id = request.args.get('other_user_id')
        
        # Build query
        query = Message.query.filter(
            (Message.sender_id == current_user_id) | 
            (Message.receiver_id == current_user_id)
        )
        
        if study_id:
            query = query.filter(Message.study_id == study_id)
        
        if other_user_id:
            query = query.filter(
                ((Message.sender_id == current_user_id) & (Message.receiver_id == other_user_id)) |
                ((Message.sender_id == other_user_id) & (Message.receiver_id == current_user_id))
            )
        
        messages = query.order_by(Message.created_at.asc()).all()
        
        messages_data = []
        for message in messages:
            sender = User.query.get(message.sender_id)
            receiver = User.query.get(message.receiver_id)
            if not sender or not receiver:
                continue
                
            messages_data.append({
                'id': message.id,
                'content': message.content,
                'type': message.type.value,
                'read': message.read,
                'created_at': message.created_at.isoformat(),
                'sender': {
                    'id': sender.id,
                    'name': sender.name,
                    'email': sender.email,
                    'role': sender.role.value
                },
                'receiver': {
                    'id': receiver.id,
                    'name': receiver.name,
                    'email': receiver.email,
                    'role': receiver.role.value
                },
                'study': {
                    'id': message.study.id,
                    'title': message.study.title
                } if message.study else None
            })
        
        # Mark messages as read if user is receiver
        Message.query.filter_by(
            receiver_id=current_user_id,
            read=False
        ).update({'read': True})
        
        db.session.commit()
        
        return jsonify(messages_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/', methods=['POST'])
@jwt_required()
def send_message():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        data = request.get_json()
        
        # Validate required fields
        if not data or not all(k in data for k in ['receiver_id', 'content']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if sender and receiver are different
        if current_user_id == data['receiver_id']:
            return jsonify({'error': 'Cannot send message to yourself'}), 400
        
        # Verify both users exist
        receiver = User.query.get(data['receiver_id'])
        sender = User.query.get(current_user_id)
        
        if not receiver or not sender:
            return jsonify({'error': 'One or both users not found'}), 404
        
        # If study_id is provided, verify it exists and user has access
        if 'study_id' in data and data['study_id']:
            study = Study.query.get(data['study_id'])
            if not study:
                return jsonify({'error': 'Study not found'}), 404
            
            # Verify at least one user is associated with study (researcher or participant)
            study_obj = Study.query.get(data['study_id'])
            sender_is_researcher = study_obj and study_obj.researcher_id == current_user_id
            receiver_is_researcher = study_obj and study_obj.researcher_id == data['receiver_id']
            
            sender_application = StudyApplication.query.filter_by(
                study_id=data['study_id'],
                user_id=current_user_id
            ).first()
            
            receiver_application = StudyApplication.query.filter_by(
                study_id=data['study_id'],
                user_id=data['receiver_id']
            ).first()
            
            # Allow if sender or receiver is the researcher, or if either has an application
            if not sender_is_researcher and not receiver_is_researcher and not sender_application and not receiver_application:
                return jsonify({'error': 'One or both users are not associated with this study'}), 403
        
        # Create message
        message = Message(
            id=str(uuid.uuid4()),
            sender_id=current_user_id,
            receiver_id=data['receiver_id'],
            content=data['content'],
            study_id=data.get('study_id'),
            type=MessageType(data.get('type', 'TEXT'))
        )
        
        db.session.add(message)
        db.session.commit()
        
        return jsonify({
            'message': 'Message sent successfully',
            'message_data': {
                'id': message.id,
                'content': message.content,
                'type': message.type.value,
                'read': message.read,
                'created_at': message.created_at.isoformat(),
                'sender': {
                    'id': sender.id,
                    'name': sender.name,
                    'email': sender.email
                },
                'receiver': {
                    'id': receiver.id,
                    'name': receiver.name,
                    'email': receiver.email
                }
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity

        # Get all messages involving user
        messages = Message.query.filter(
            (Message.sender_id == current_user_id) |
            (Message.receiver_id == current_user_id)
        ).order_by(Message.created_at.desc()).all()
        
        # Group messages by conversation (other user + study)
        conversations = {}
        
        for message in messages:
            other_user_id = message.sender_id if message.sender_id != current_user_id else message.receiver_id
            # Get other user from database
            other_user = User.query.get(other_user_id)
            if not other_user:
                continue
            conversation_key = f"{other_user_id}-{message.study_id or 'general'}"
            
            if conversation_key not in conversations:
                conversations[conversation_key] = {
                    'id': conversation_key,
                    'other_user': {
                        'id': other_user.id,
                        'name': other_user.name,
                        'email': other_user.email,
                        'role': other_user.role.value
                    },
                    'study': {
                        'id': message.study.id,
                        'title': message.study.title
                    } if message.study else None,
                    'last_message': None,
                    'last_message_datetime': None,  # Store datetime for comparison
                    'unread_count': 0,
                    'total_messages': 0
                }
            
            conversation = conversations[conversation_key]
            conversation['total_messages'] += 1
            
            # Count unread messages (where current user is receiver and message is unread)
            if message.receiver_id == current_user_id and not message.read:
                conversation['unread_count'] += 1
            
            # Update last message if this one is more recent
            if not conversation['last_message'] or \
               message.created_at > conversation['last_message_datetime']:
                conversation['last_message'] = {
                    'id': message.id,
                    'content': message.content,
                    'type': message.type.value,
                    'created_at': message.created_at.isoformat()
                }
                conversation['last_message_datetime'] = message.created_at
        
        # Convert to array and sort by last message time
        conversation_list = sorted(
            conversations.values(),
            key=lambda x: x['last_message_datetime'] if x['last_message_datetime'] else datetime.min,
            reverse=True
        )

        # Remove internal datetime fields before returning JSON
        for conversation in conversation_list:
            if 'last_message_datetime' in conversation:
                del conversation['last_message_datetime']

        return jsonify(conversation_list)
        
    except KeyError as e:
        print(f"KeyError in get_conversations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Invalid token format: {str(e)}'}), 422
    except Exception as e:
        print(f"Exception in get_conversations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/<message_id>/read', methods=['PUT'])
@jwt_required()
def mark_message_as_read(message_id):
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        # Verify message exists and user is receiver
        message = Message.query.get(message_id)
        
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        if message.receiver_id != current_user_id:
            return jsonify({'error': 'Only message receiver can mark as read'}), 403
        
        # Mark as read
        message.read = True
        db.session.commit()
        
        return jsonify({
            'message': 'Message marked as read',
            'message_data': {
                'id': message.id,
                'read': message.read
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500