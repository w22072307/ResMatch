from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, ParticipantProfile, Study, StudyApplication, StudyParticipation, UserRole
import json
import uuid

participants_bp = Blueprint('participants', __name__)

@participants_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_participant_profile():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        user = User.query.get(current_user_id)
        if not user or user.role != UserRole.PARTICIPANT:
            return jsonify({'error': 'Participant not found'}), 404
        
        profile = user.participant_profile
        if not profile:
            return jsonify({'error': 'Profile not found'}), 404
        
        profile_data = {
            'id': profile.id,
            'user_id': profile.user_id,
            'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
            'gender': profile.gender,
            'location': profile.location,
            'bio': profile.bio,
            'interests': json.loads(profile.interests) if profile.interests else [],
            'availability': json.loads(profile.availability) if profile.availability else [],
            'phone_number': profile.phone_number,
            'created_at': profile.created_at.isoformat(),
            'updated_at': profile.updated_at.isoformat()
        }
        
        return jsonify({
            'participant_profile': profile_data
        })
        
    except KeyError as e:
        return jsonify({'error': 'Invalid token format'}), 422
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@participants_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_participant_profile():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        user = User.query.get(current_user_id)
        if not user or user.role != UserRole.PARTICIPANT:
            return jsonify({'error': 'Participant not found'}), 404
        
        profile = user.participant_profile
        if not profile:
            # Create profile if it doesn't exist
            profile = ParticipantProfile(
                id=str(uuid.uuid4()),
                user_id=current_user_id
            )
            db.session.add(profile)
            db.session.flush()
        
        data = request.get_json()
        
        # Update profile fields
        if 'date_of_birth' in data:
            from datetime import datetime
            profile.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
        
        if 'gender' in data:
            profile.gender = data['gender']
        
        if 'location' in data:
            profile.location = data['location']
        
        if 'bio' in data:
            profile.bio = data['bio']
        
        if 'interests' in data:
            profile.interests = json.dumps(data['interests'])
        
        if 'availability' in data:
            profile.availability = json.dumps(data['availability'])
        
        if 'phone_number' in data:
            profile.phone_number = data['phone_number']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': {
                'id': profile.id,
                'date_of_birth': profile.date_of_birth.isoformat() if profile.date_of_birth else None,
                'gender': profile.gender,
                'location': profile.location,
                'bio': profile.bio,
                'interests': json.loads(profile.interests) if profile.interests else [],
                'availability': json.loads(profile.availability) if profile.availability else [],
                'phone_number': profile.phone_number,
                'updated_at': profile.updated_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@participants_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_participant_applications():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        user = User.query.get(current_user_id)
        if not user or user.role != UserRole.PARTICIPANT:
            return jsonify({'error': 'Participant not found'}), 404
        
        # Get applications with study details
        applications = db.session.query(
            StudyApplication, Study, User
        ).join(
            Study, StudyApplication.study_id == Study.id
        ).join(
            User, Study.researcher_id == User.id
        ).filter(
            StudyApplication.user_id == current_user_id
        ).order_by(
            StudyApplication.created_at.desc()
        ).all()
        
        applications_data = []
        for application, study, researcher in applications:
            applications_data.append({
                'id': application.id,
                'status': application.status.value,
                'message': application.message,
                'created_at': application.created_at.isoformat(),
                'updated_at': application.updated_at.isoformat(),
                'study': {
                    'id': study.id,
                    'title': study.title,
                    'description': study.description,
                    'institution': study.institution,
                    'category': study.category,
                    'duration': study.duration,
                    'compensation': study.compensation,
                    'location': study.location,
                    'participants_needed': study.participants_needed,
                    'participants_current': study.participants_current,
                    'status': study.status.value,
                    'application_deadline': study.application_deadline.isoformat() if study.application_deadline else None,
                    'researcher': {
                        'id': researcher.id,
                        'name': researcher.name,
                        'email': researcher.email
                    }
                }
            })
        
        return jsonify(applications_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@participants_bp.route('/participations', methods=['GET'])
@jwt_required()
def get_participant_participations():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        user = User.query.get(current_user_id)
        if not user or user.role != UserRole.PARTICIPANT:
            return jsonify({'error': 'Participant not found'}), 404
        
        # Get participations with study details
        participations = db.session.query(
            StudyParticipation, Study, User
        ).join(
            Study, StudyParticipation.study_id == Study.id
        ).join(
            User, Study.researcher_id == User.id
        ).filter(
            StudyParticipation.user_id == current_user_id
        ).order_by(
            StudyParticipation.created_at.desc()
        ).all()
        
        participations_data = []
        for participation, study, researcher in participations:
            participations_data.append({
                'id': participation.id,
                'status': participation.status.value,
                'consent_given': participation.consent_given,
                'start_date': participation.start_date.isoformat(),
                'end_date': participation.end_date.isoformat() if participation.end_date else None,
                'notes': participation.notes,
                'created_at': participation.created_at.isoformat(),
                'updated_at': participation.updated_at.isoformat(),
                'study': {
                    'id': study.id,
                    'title': study.title,
                    'description': study.description,
                    'institution': study.institution,
                    'category': study.category,
                    'duration': study.duration,
                    'compensation': study.compensation,
                    'location': study.location,
                    'researcher': {
                        'id': researcher.id,
                        'name': researcher.name,
                        'email': researcher.email
                    }
                }
            })
        
        return jsonify(participations_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500