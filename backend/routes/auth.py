from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User, ResearcherProfile, ParticipantProfile, UserRole
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validate required fields
        if not data or not all(k in data for k in ['email', 'password', 'name', 'role']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400

        # Validate role
        if data['role'] not in [role.value for role in UserRole]:
            return jsonify({'error': 'Invalid role'}), 400

        # Create new user
        user = User(
            id=str(uuid.uuid4()),
            email=data['email'],
            name=data['name'],
            role=UserRole(data['role'])
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create profile based on role
        if user.role == UserRole.RESEARCHER:
            researcher_profile = ResearcherProfile(
                id=str(uuid.uuid4()),
                user_id=user.id
            )
            db.session.add(researcher_profile)
        else:
            participant_profile = ParticipantProfile(
                id=str(uuid.uuid4()),
                user_id=user.id
            )
            db.session.add(participant_profile)

        db.session.commit()

        # Create access token
        access_token = create_access_token(
            identity=user.id
        )

        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role.value,
                'created_at': user.created_at.isoformat()
            },
            'token': access_token
        }), 201
        
    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data or not all(k in data for k in ['email', 'password']):
            return jsonify({'error': 'Missing email or password'}), 400

        # Find user
        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        # Create access token
        access_token = create_access_token(
            identity=user.id
        )

        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'role': user.role.value,
                'created_at': user.created_at.isoformat()
            },
            'token': access_token
        })
        
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        identity = get_jwt_identity()
        print(f"DEBUG: get_jwt_identity() returned: {identity}, type: {type(identity)}")

        if identity is None:
            return jsonify({'error': 'No identity in token'}), 422

        if isinstance(identity, dict):
            current_user_id = identity.get('user_id')
            if not current_user_id:
                return jsonify({'error': 'No user_id in token identity'}), 422
        else:
            current_user_id = identity
        
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile_data = {
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'role': user.role.value,
            'avatar': user.avatar,
            'created_at': user.created_at.isoformat(),
            'updated_at': user.updated_at.isoformat()
        }
        
        # Add profile-specific data
        if user.role == UserRole.RESEARCHER and user.researcher_profile:
            profile_data['researcher_profile'] = {
                'id': user.researcher_profile.id,
                'institution': user.researcher_profile.institution,
                'department': user.researcher_profile.department,
                'title': user.researcher_profile.title,
                'bio': user.researcher_profile.bio,
                'verified': user.researcher_profile.verified
            }
        elif user.role == UserRole.PARTICIPANT and user.participant_profile:
            profile_data['participant_profile'] = {
                'id': user.participant_profile.id,
                'date_of_birth': user.participant_profile.date_of_birth.isoformat() if user.participant_profile.date_of_birth else None,
                'gender': user.participant_profile.gender,
                'location': user.participant_profile.location,
                'bio': user.participant_profile.bio,
                'interests': user.participant_profile.interests,
                'availability': user.participant_profile.availability,
                'phone_number': user.participant_profile.phone_number
            }
        
        return jsonify(profile_data)
        
    except KeyError as e:
        print(f"KeyError in get_profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Invalid token format: {str(e)}'}), 422
    except Exception as e:
        print(f"Exception in get_profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500