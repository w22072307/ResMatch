from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Study, StudyApplication, StudyParticipation, User, StudyStatus, ApplicationStatus
import uuid
import json
from datetime import datetime, date

studies_bp = Blueprint('studies', __name__)

@studies_bp.route('/', methods=['GET'])
def get_studies():
    try:
        # Get query parameters
        category = request.args.get('category')
        status = request.args.get('status')
        researcher_id = request.args.get('researcher_id')
        
        # Build query
        query = Study.query
        
        if category:
            query = query.filter(Study.category == category)
        if status:
            query = query.filter(Study.status == StudyStatus(status))
        if researcher_id:
            query = query.filter(Study.researcher_id == researcher_id)
        
        studies = query.all()
        
        studies_data = []
        for study in studies:
            try:
                institution = study.institution
                if not institution and study.researcher and study.researcher.researcher_profile:
                    institution = study.researcher.researcher_profile.institution
                
                studies_data.append({
                    'id': study.id,
                    'title': study.title,
                    'description': study.description,
                    'institution': institution,
                    'category': study.category,
                    'duration': study.duration,
                    'compensation': study.compensation,
                    'location': study.location,
                    'participants_needed': study.participants_needed,
                    'participants_current': study.participants_current,
                    'status': study.status.value,
                    'irb_approval_number': study.irb_approval_number,
                    'requirements': json.loads(study.requirements) if study.requirements else [],
                    'start_date': study.start_date.isoformat() if study.start_date else None,
                    'end_date': study.end_date.isoformat() if study.end_date else None,
                    'application_deadline': study.application_deadline.isoformat() if study.application_deadline else None,
                    'created_at': study.created_at.isoformat(),
                    'updated_at': study.updated_at.isoformat(),
                    'researcher': {
                        'id': study.researcher.id,
                        'name': study.researcher.name,
                        'email': study.researcher.email
                    } if study.researcher else None
                })
            except Exception as e:
                print(f"Error processing study {study.id}: {e}")
                continue
        
        return jsonify(studies_data)
        
    except KeyError as e:
        print(f"KeyError in get_studies: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Invalid token format: {str(e)}'}), 422
    except Exception as e:
        print(f"Exception in get_studies: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@studies_bp.route('/', methods=['POST'])
@jwt_required()
def create_study():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'institution', 'category', 'duration', 'participants_needed']
        if not data or not all(k in data for k in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create new study
        study = Study(
            id=str(uuid.uuid4()),
            title=data['title'],
            description=data['description'],
            institution=data['institution'],
            researcher_id=current_user_id,
            category=data['category'],
            duration=data['duration'],
            compensation=data.get('compensation'),
            location=data.get('location'),
            participants_needed=data['participants_needed'],
            status=StudyStatus.DRAFT,
            irb_approval_number=data.get('irb_approval_number'),
            consent_form=data.get('consent_form'),
            requirements=json.dumps(data.get('requirements', [])),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date() if data.get('start_date') else None,
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date() if data.get('end_date') else None,
            application_deadline=datetime.strptime(data['application_deadline'], '%Y-%m-%d').date() if data.get('application_deadline') else None
        )
        
        db.session.add(study)
        db.session.commit()
        
        institution = study.institution
        if not institution and study.researcher and study.researcher.researcher_profile:
            institution = study.researcher.researcher_profile.institution
        
        return jsonify({
            'message': 'Study created successfully',
            'study': {
                'id': study.id,
                'title': study.title,
                'description': study.description,
                'institution': institution,
                'category': study.category,
                'duration': study.duration,
                'compensation': study.compensation,
                'location': study.location,
                'participants_needed': study.participants_needed,
                'participants_current': study.participants_current,
                'status': study.status.value,
                'created_at': study.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@studies_bp.route('/<study_id>', methods=['GET'])
def get_study(study_id):
    try:
        study = Study.query.get(study_id)
        
        if not study:
            return jsonify({'error': 'Study not found'}), 404
        
        # Get applications count
        applications_count = StudyApplication.query.filter_by(study_id=study_id).count()
        
        institution = study.institution
        if not institution and study.researcher and study.researcher.researcher_profile:
            institution = study.researcher.researcher_profile.institution
        
        study_data = {
            'id': study.id,
            'title': study.title,
            'description': study.description,
            'institution': institution,
            'category': study.category,
            'duration': study.duration,
            'compensation': study.compensation,
            'location': study.location,
            'participants_needed': study.participants_needed,
            'participants_current': study.participants_current,
            'status': study.status.value,
            'irb_approval_number': study.irb_approval_number,
            'consent_form': study.consent_form,
            'requirements': json.loads(study.requirements) if study.requirements else [],
            'start_date': study.start_date.isoformat() if study.start_date else None,
            'end_date': study.end_date.isoformat() if study.end_date else None,
            'application_deadline': study.application_deadline.isoformat() if study.application_deadline else None,
            'created_at': study.created_at.isoformat(),
            'updated_at': study.updated_at.isoformat(),
            'applications_count': applications_count,
            'researcher': {
                'id': study.researcher.id,
                'name': study.researcher.name,
                'email': study.researcher.email
            }
        }
        
        return jsonify(study_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@studies_bp.route('/<study_id>/apply', methods=['POST'])
@jwt_required()
def apply_to_study(study_id):
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        # Check if study exists
        study = Study.query.get(study_id)
        if not study:
            return jsonify({'error': 'Study not found'}), 404
        
        # Check if user has already applied
        existing_application = StudyApplication.query.filter_by(
            study_id=study_id,
            user_id=current_user_id
        ).first()
        
        if existing_application:
            return jsonify({'error': 'Already applied to this study'}), 400
        
        # Create application
        application = StudyApplication(
            id=str(uuid.uuid4()),
            study_id=study_id,
            user_id=current_user_id,
            status=ApplicationStatus.PENDING,
            message=request.json.get('message') if request.json else None
        )
        
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': {
                'id': application.id,
                'study_id': application.study_id,
                'status': application.status.value,
                'created_at': application.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@studies_bp.route('/<study_id>/participants', methods=['GET'])
@jwt_required()
def get_study_participants(study_id):
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity

        # Check if study exists and user is the researcher
        study = Study.query.get(study_id)
        if not study or study.researcher_id != current_user_id:
            return jsonify({'error': 'Study not found or access denied'}), 404

        # Get participants with their participation details
        participants = db.session.query(
            StudyParticipation, User
        ).join(
            User, StudyParticipation.user_id == User.id
        ).filter(
            StudyParticipation.study_id == study_id,
            StudyParticipation.status.in_(['ACTIVE', 'COMPLETED'])
        ).all()

        participants_data = []
        for participation, user in participants:
            participants_data.append({
                'id': participation.id,
                'status': participation.status.value,
                'start_date': participation.start_date.isoformat() if participation.start_date else None,
                'end_date': participation.end_date.isoformat() if participation.end_date else None,
                'consent_given': participation.consent_given,
                'notes': participation.notes,
                'created_at': participation.created_at.isoformat(),
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'participant_profile': {
                        'id': user.participant_profile.id,
                        'date_of_birth': user.participant_profile.date_of_birth.isoformat() if user.participant_profile.date_of_birth else None,
                        'gender': user.participant_profile.gender,
                        'location': user.participant_profile.location,
                        'bio': user.participant_profile.bio,
                        'interests': user.participant_profile.interests,
                        'availability': user.participant_profile.availability,
                        'phone_number': user.participant_profile.phone_number
                    } if user.participant_profile else None
                }
            })

        return jsonify(participants_data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@studies_bp.route('/<study_id>/applications', methods=['GET'])
@jwt_required()
def get_study_applications(study_id):
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        # Check if study exists and user is the researcher
        study = Study.query.get(study_id)
        if not study or study.researcher_id != current_user_id:
            return jsonify({'error': 'Study not found or access denied'}), 404
        
        # Get applications with user details
        applications = db.session.query(
            StudyApplication, User
        ).join(
            User, StudyApplication.user_id == User.id
        ).filter(
            StudyApplication.study_id == study_id
        ).all()
        
        applications_data = []
        for application, user in applications:
            applications_data.append({
                'id': application.id,
                'status': application.status.value,
                'message': application.message,
                'created_at': application.created_at.isoformat(),
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'participant_profile': {
                        'id': user.participant_profile.id,
                        'date_of_birth': user.participant_profile.date_of_birth.isoformat() if user.participant_profile.date_of_birth else None,
                        'gender': user.participant_profile.gender,
                        'location': user.participant_profile.location,
                        'bio': user.participant_profile.bio,
                        'interests': user.participant_profile.interests,
                        'availability': user.participant_profile.availability,
                        'phone_number': user.participant_profile.phone_number
                    } if user.participant_profile else None
                }
            })
        
        return jsonify(applications_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500