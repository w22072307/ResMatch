from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Study, User, ParticipantProfile, StudyApplication, StudyParticipation, UserRole
import json

matching_bp = Blueprint('matching', __name__)

def calculate_match_score(participant, study):
    """Simple rule-based matching algorithm"""
    score = 0
    max_score = 0
    
    try:
        profile = participant.participant_profile
        if not profile:
            return 0
        
        requirements = json.loads(study.requirements) if study.requirements else []
        
        # Age matching (20 points)
        if profile.date_of_birth:
            max_score += 20
            from datetime import datetime
            age = (datetime.now().date() - profile.date_of_birth).days // 365
            
            age_req = next((req for req in requirements if req.get('type') == 'age'), None)
            if age_req:
                min_age, max_age = age_req.get('min', 0), age_req.get('max', 100)
                if min_age <= age <= max_age:
                    score += 20
            else:
                score += 10  # Partial points if no age requirement
        
        # Location matching (15 points)
        if study.location and profile.location:
            max_score += 15
            if 'remote' in study.location.lower() or \
               profile.location.lower() in study.location.lower() or \
               study.location.lower() in profile.location.lower():
                score += 15
        
        # Gender matching (10 points)
        if profile.gender:
            max_score += 10
            gender_req = next((req for req in requirements if req.get('type') == 'gender'), None)
            if not gender_req or gender_req.get('value') == profile.gender:
                score += 10
        
        # Interests matching (25 points)
        if profile.interests and study.category:
            max_score += 25
            interests = json.loads(profile.interests) if profile.interests else []
            if any(study.category.lower() in interest.lower() for interest in interests):
                score += 25
            elif interests:
                score += 10  # Partial points for having interests
        
        # Availability matching (20 points)
        if profile.availability:
            max_score += 20
            # Simple availability check
            score += 15
        
        # Study history matching (10 points)
        max_score += 10
        completed_studies = StudyParticipation.query.filter_by(
            user_id=participant.id,
            status='COMPLETED'
        ).count()
        if completed_studies > 0:
            score += 10
        
        # Convert to percentage
        final_score = (score / max_score * 100) if max_score > 0 else 0
        return min(final_score, 100)
        
    except Exception as e:
        print(f"Error calculating match score: {e}")
        return 0

@matching_bp.route('/participants/<study_id>', methods=['GET'])
@jwt_required()
def get_matched_participants(study_id):
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        # Check if study exists and user is the researcher
        study = Study.query.get(study_id)
        if not study:
            return jsonify({'error': 'Study not found'}), 404
        
        # Get all participants
        participants = User.query.filter_by(role=UserRole.PARTICIPANT).all()
        
        # Filter out already applied participants
        applied_participant_ids = [app.user_id for app in StudyApplication.query.filter_by(study_id=study_id).all()]
        participating_participant_ids = [part.user_id for part in StudyParticipation.query.filter_by(study_id=study_id).all()]
        
        available_participants = [
            p for p in participants 
            if p.id not in applied_participant_ids and p.id not in participating_participant_ids
        ]
        
        # Calculate match scores
        matched_participants = []
        for participant in available_participants:
            match_score = calculate_match_score(participant, study)
            if match_score >= 50:  # Only show matches with 50% or higher
                matched_participants.append({
                    'id': participant.id,
                    'name': participant.name,
                    'email': participant.email,
                    'participant_profile': participant.participant_profile,
                    'match_score': match_score
                })
        
        # Sort by match score (highest first)
        matched_participants.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify({
            'study_id': study_id,
            'total_matches': len(matched_participants),
            'matches': matched_participants[:20]  # Limit to top 20 matches
        })
        
    except Exception as e:
        print(f"Exception in get_matched_participants: {e}")
        return jsonify({'error': str(e)}), 500

@matching_bp.route('/studies', methods=['POST'])
@jwt_required()
def get_matched_studies():
    try:
        identity = get_jwt_identity()
        if isinstance(identity, dict):
            current_user_id = identity['user_id']
        else:
            current_user_id = identity
        
        # Check if user exists and is a participant
        participant = User.query.get(current_user_id)
        if not participant or participant.role != UserRole.PARTICIPANT:
            return jsonify({'error': 'Participant not found'}), 404
        
        # Get all active studies
        studies = Study.query.filter_by(status='ACTIVE').all()
        
        # Filter out already applied studies
        applied_study_ids = [app.study_id for app in StudyApplication.query.filter_by(user_id=current_user_id).all()]
        participating_study_ids = [part.study_id for part in StudyParticipation.query.filter_by(user_id=current_user_id).all()]
        
        available_studies = [
            study for study in studies
            if study.id not in applied_study_ids and \
               study.id not in participating_study_ids and \
               study.participants_current < study.participants_needed
        ]
        
        # Calculate match scores
        matched_studies = []
        for study in available_studies:
            match_score = calculate_match_score(participant, study)
            if match_score >= 50:  # Only show matches with 50% or higher
                # Format requirements for display
                requirements = []
                if study.requirements:
                    reqs = json.loads(study.requirements)
                    for req in reqs:
                        if req['type'] == 'age':
                            requirements.append(f"Age: {req['min']}-{req['max']}")
                        elif req['type'] == 'gender':
                            requirements.append(f"Gender: {req['value']}")
                        elif req['type'] == 'interest':
                            requirements.append(f"Interest: {req['value']}")
                        elif req['type'] == 'language':
                            requirements.append(f"Language: {req['value']}")
                        elif req['type'] == 'status':
                            requirements.append(f"Status: {req['value']}")
                        elif req['type'] == 'device':
                            requirements.append(f"Device: {req['value']}")
                        elif req['type'] == 'fitness':
                            requirements.append(f"Fitness: {req['value']}")
                        elif req['type'] == 'bmi':
                            requirements.append(f"BMI: {req['min']}-{req['max']}")
                        else:
                            requirements.append(f"{req['type']}: {req.get('value', 'N/A')}")

                matched_studies.append({
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
                    'requirements': requirements,
                    'researcher': {
                        'id': study.researcher.id,
                        'name': study.researcher.name,
                        'email': study.researcher.email
                    } if study.researcher else None,
                    'matchScore': int(match_score),  # Frontend expects matchScore with capital S
                    'created_at': study.created_at.isoformat()
                })
        
        # Sort by match score (highest first)
        matched_studies.sort(key=lambda x: x['matchScore'], reverse=True)
        
        return jsonify({
            'participant_id': current_user_id,
            'total_matches': len(matched_studies),
            'matches': matched_studies[:20]  # Limit to top 20 matches
        })
        
    except Exception as e:
        print(f"Exception in get_matched_studies: {e}")
        return jsonify({'error': str(e)}), 500