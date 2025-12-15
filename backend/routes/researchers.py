from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, ResearcherProfile, UserRole
import uuid

researchers_bp = Blueprint('researchers', __name__)

@researchers_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_researcher_profile():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        user = User.query.get(current_user_id)
        if not user or user.role != UserRole.RESEARCHER:
            return jsonify({'error': 'Researcher not found'}), 404
        
        profile = user.researcher_profile
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile_data = {
            'id': profile.id,
            'user_id': profile.user_id,
            'institution': profile.institution,
            'department': profile.department,
            'title': profile.title,
            'bio': profile.bio,
            'verified': profile.verified,
            'created_at': profile.created_at.isoformat(),
            'updated_at': profile.updated_at.isoformat()
        }
        
        return jsonify({
            'researcher_profile': profile_data
        })
        
    except KeyError as e:
        print(f"KeyError in get_researcher_profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Invalid token format: {str(e)}'}), 422
    except Exception as e:
        print(f"Exception in get_researcher_profile: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@researchers_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_researcher_profile():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        user = User.query.get(current_user_id)
        if not user or user.role != UserRole.RESEARCHER:
            return jsonify({'error': 'Researcher not found'}), 404
        
        profile = user.researcher_profile
        if not profile:
            # Create profile if it doesn't exist
            profile = ResearcherProfile(
                id=str(uuid.uuid4()),
                user_id=current_user_id
            )
            db.session.add(profile)
            db.session.flush()
        
        data = request.get_json()
        
        # Update profile fields
        if 'institution' in data:
            profile.institution = data['institution']
        
        if 'department' in data:
            profile.department = data['department']
        
        if 'title' in data:
            profile.title = data['title']
        
        if 'bio' in data:
            profile.bio = data['bio']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': {
                'id': profile.id,
                'institution': profile.institution,
                'department': profile.department,
                'title': profile.title,
                'bio': profile.bio,
                'verified': profile.verified,
                'updated_at': profile.updated_at.isoformat()
            }
        })
        
    except KeyError as e:
        print(f"KeyError in update_researcher_profile: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': f'Invalid token format: {str(e)}'}), 422
    except Exception as e:
        print(f"Exception in update_researcher_profile: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

