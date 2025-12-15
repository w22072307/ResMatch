import pytest
import json
import uuid
from datetime import datetime, date
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from app import app, db
from models import User, ResearcherProfile, ParticipantProfile, Study, StudyApplication, StudyParticipation, Message, UserRole, StudyStatus, ApplicationStatus, MessageType


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture
def test_researcher():
    """Create test researcher user"""
    researcher_id = str(uuid.uuid4())
    user = User(
        id=researcher_id,
        email='researcher@test.com',
        name='Test Researcher',
        role=UserRole.RESEARCHER
    )
    user.set_password('password123')

    researcher_profile = ResearcherProfile(
        id=str(uuid.uuid4()),
        user_id=researcher_id,
        institution='Test University',
        department='Psychology',
        title='Professor',
        bio='Researcher bio'
    )

    db.session.add(user)
    db.session.add(researcher_profile)
    db.session.commit()

    return user


@pytest.fixture
def test_participant():
    """Create test participant user"""
    participant_id = str(uuid.uuid4())
    user = User(
        id=participant_id,
        email='participant@test.com',
        name='Test Participant',
        role=UserRole.PARTICIPANT
    )
    user.set_password('password123')

    participant_profile = ParticipantProfile(
        id=str(uuid.uuid4()),
        user_id=participant_id,
        date_of_birth=date(1990, 1, 1),
        gender='Female',
        location='New York',
        bio='Participant bio',
        interests=json.dumps(['Psychology', 'Research']),
        availability=json.dumps(['Weekdays'])
    )

    db.session.add(user)
    db.session.add(participant_profile)
    db.session.commit()

    return user


@pytest.fixture
def auth_headers_participant(test_participant):
    """Get auth headers for participant"""
    access_token = create_access_token(identity=test_participant.id)
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def auth_headers_researcher(test_researcher):
    """Get auth headers for researcher"""
    access_token = create_access_token(identity={
        'user_id': test_researcher.id,
        'email': test_researcher.email,
        'role': test_researcher.role.value
    })
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def test_study(test_researcher):
    """Create test study"""
    study = Study(
        id=str(uuid.uuid4()),
        title='Test Study',
        description='A test research study',
        researcher_id=test_researcher.id,
        institution='Test University',
        category='Psychology',
        duration='3 months',
        participants_needed=10,
        status=StudyStatus.ACTIVE,
        requirements=json.dumps([{'type': 'age', 'min': 18, 'max': 65}])
    )

    db.session.add(study)
    db.session.commit()

    return study


@pytest.fixture
def test_application(test_participant, test_study):
    """Create test study application"""
    application = StudyApplication(
        id=str(uuid.uuid4()),
        study_id=test_study.id,
        user_id=test_participant.id,
        status=ApplicationStatus.PENDING,
        message='I am interested in participating'
    )

    db.session.add(application)
    db.session.commit()

    return application


@pytest.fixture
def test_participation(test_participant, test_study):
    """Create test study participation"""
    participation = StudyParticipation(
        id=str(uuid.uuid4()),
        study_id=test_study.id,
        user_id=test_participant.id,
        status='ACTIVE',
        consent_given=True
    )

    db.session.add(participation)
    db.session.commit()

    return participation


class TestParticipantProfileRoutes:
    """Test participant profile routes"""

    def test_get_participant_profile_success(self, client, test_participant, auth_headers_participant):
        """Test getting participant profile successfully"""
        response = client.get('/api/participants/profile', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'participant_profile' in data
        profile = data['participant_profile']
        assert profile['user_id'] == test_participant.id
        assert profile['gender'] == 'Female'
        assert profile['location'] == 'New York'
        assert profile['interests'] == ['Psychology', 'Research']

    def test_get_participant_profile_unauthorized(self, client):
        """Test getting participant profile without auth"""
        response = client.get('/api/participants/profile')
        assert response.status_code == 401

    def test_update_participant_profile_success(self, client, test_participant, auth_headers_participant):
        """Test updating participant profile successfully"""
        update_data = {
            'gender': 'Male',
            'location': 'Boston',
            'bio': 'Updated bio',
            'interests': ['Computer Science', 'AI'],
            'availability': ['Weekends'],
            'phone_number': '123-456-7890'
        }

        response = client.put('/api/participants/profile',
                            json=update_data,
                            headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'profile' in data
        profile = data['profile']
        assert profile['gender'] == 'Male'
        assert profile['location'] == 'Boston'
        assert profile['interests'] == ['Computer Science', 'AI']

    def test_update_participant_profile_partial(self, client, test_participant, auth_headers_participant):
        """Test partial update of participant profile"""
        update_data = {'bio': 'New bio only'}

        response = client.put('/api/participants/profile',
                            json=update_data,
                            headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        profile = data['profile']
        assert profile['bio'] == 'New bio only'
        assert profile['gender'] == 'Female'  # Should remain unchanged



class TestParticipantApplicationRoutes:
    """Test participant application routes"""

    def test_get_participant_applications_success(self, client, test_participant, test_application, auth_headers_participant):
        """Test getting participant applications successfully"""
        response = client.get('/api/participants/applications', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

        application = data[0]
        assert application['status'] == 'PENDING'
        assert application['message'] == 'I am interested in participating'
        assert 'study' in application

    def test_get_participant_applications_empty(self, client, test_participant, auth_headers_participant):
        """Test getting participant applications when none exist"""
        response = client.get('/api/participants/applications', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        # Should be empty if no applications exist for this participant

    def test_get_participant_applications_unauthorized(self, client):
        """Test getting participant applications without auth"""
        response = client.get('/api/participants/applications')
        assert response.status_code == 401


class TestParticipantParticipationRoutes:
    """Test participant participation routes"""

    def test_get_participant_participations_success(self, client, test_participant, test_participation, auth_headers_participant):
        """Test getting participant participations successfully"""
        response = client.get('/api/participants/participations', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

        participation = data[0]
        assert participation['status'] == 'ACTIVE'
        assert participation['consent_given'] == True
        assert 'study' in participation

    def test_get_participant_participations_empty(self, client, test_participant, auth_headers_participant):
        """Test getting participant participations when none exist"""
        response = client.get('/api/participants/participations', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_participant_participations_unauthorized(self, client):
        """Test getting participant participations without auth"""
        response = client.get('/api/participants/participations')
        assert response.status_code == 401


class TestStudyApplicationRoutes:
    """Test study application routes for participants"""

    def test_apply_to_study_success(self, client, test_participant, test_study, auth_headers_participant):
        """Test applying to a study successfully"""
        application_data = {
            'message': 'I would like to participate in this study'
        }

        response = client.post(f'/api/studies/{test_study.id}/apply',
                             json=application_data,
                             headers=auth_headers_participant)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'application' in data
        application = data['application']
        assert application['study_id'] == test_study.id
        assert application['status'] == 'PENDING'

    def test_apply_to_study_duplicate(self, client, test_participant, test_study, test_application, auth_headers_participant):
        """Test applying to a study when already applied"""
        application_data = {
            'message': 'Duplicate application'
        }

        response = client.post(f'/api/studies/{test_study.id}/apply',
                             json=application_data,
                             headers=auth_headers_participant)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data

    def test_apply_to_study_not_found(self, client, test_participant, auth_headers_participant):
        """Test applying to a non-existent study"""
        application_data = {
            'message': 'Study not found'
        }

        response = client.post('/api/studies/non-existent-id/apply',
                             json=application_data,
                             headers=auth_headers_participant)
        assert response.status_code == 404

    def test_apply_to_study_unauthorized(self, client, test_study):
        """Test applying to a study without authentication"""
        application_data = {
            'message': 'No auth'
        }

        response = client.post(f'/api/studies/{test_study.id}/apply',
                             json=application_data)
        assert response.status_code == 401


class TestMatchingRoutes:
    """Test matching routes for participants"""

    def test_get_matched_studies_success(self, client, test_participant, test_study, auth_headers_participant):
        """Test getting matched studies for a participant"""
        response = client.post('/api/matching/studies', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'participant_id' in data
        assert 'matches' in data
        assert 'total_matches' in data

    def test_get_matched_studies_unauthorized(self, client):
        """Test getting matched studies without auth"""
        response = client.post('/api/matching/studies')
        assert response.status_code == 401


class TestMessageRoutes:
    """Test message routes for participants"""

    def test_send_message_success(self, client, test_participant, test_researcher, auth_headers_participant):
        """Test sending a message successfully"""
        message_data = {
            'receiver_id': test_researcher.id,
            'content': 'Hello from participant'
        }

        response = client.post('/api/messages/',
                             json=message_data,
                             headers=auth_headers_participant)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'message_data' in data
        assert data['message_data']['content'] == 'Hello from participant'

    def test_send_message_to_self(self, client, test_participant, auth_headers_participant):
        """Test sending a message to oneself (should fail)"""
        message_data = {
            'receiver_id': test_participant.id,
            'content': 'Message to self'
        }

        response = client.post('/api/messages/',
                             json=message_data,
                             headers=auth_headers_participant)
        assert response.status_code == 400

    def test_send_message_missing_fields(self, client, test_participant, auth_headers_participant):
        """Test sending a message with missing fields"""
        incomplete_data = {'content': 'Missing receiver'}

        response = client.post('/api/messages/',
                             json=incomplete_data,
                             headers=auth_headers_participant)
        assert response.status_code == 400

    def test_get_messages_success(self, client, auth_headers_participant):
        """Test getting messages successfully"""
        response = client.get('/api/messages/', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_conversations_success(self, client, auth_headers_participant):
        """Test getting conversations successfully"""
        response = client.get('/api/messages/conversations', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_mark_message_as_read_success(self, client, test_participant, test_researcher, auth_headers_participant):
        """Test marking a message as read"""
        # First create a message
        message_data = {
            'receiver_id': test_participant.id,
            'content': 'Test message to mark as read'
        }

        # Send message to participant (from researcher)
        access_token = create_access_token(identity=test_researcher.id)
        researcher_headers = {'Authorization': f'Bearer {access_token}'}

        response = client.post('/api/messages/',
                             json=message_data,
                             headers=researcher_headers)
        assert response.status_code == 201

        message_id = json.loads(response.data)['message_data']['id']

        # Now mark it as read by participant
        response = client.put(f'/api/messages/{message_id}/read',
                             headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['message_data']['read'] == True

    def test_mark_message_as_read_unauthorized(self, client, test_participant, test_researcher):
        """Test marking a message as read by wrong user"""
        # First create a message
        message_data = {
            'receiver_id': test_participant.id,
            'content': 'Test message'
        }

        # Send message to participant (from researcher)
        access_token = create_access_token(identity=test_researcher.id)
        researcher_headers = {'Authorization': f'Bearer {access_token}'}

        response = client.post('/api/messages/',
                             json=message_data,
                             headers=researcher_headers)
        assert response.status_code == 201

        message_id = json.loads(response.data)['message_data']['id']

        # Try to mark as read with researcher headers (wrong user)
        response = client.put(f'/api/messages/{message_id}/read',
                             headers=researcher_headers)
        assert response.status_code == 403


class TestAuthRoutes:
    """Test authentication routes used by participants"""

    def test_register_participant_success(self, client):
        """Test registering a participant successfully"""
        participant_data = {
            'email': 'new.participant@test.com',
            'password': 'password123',
            'name': 'New Participant',
            'role': 'PARTICIPANT'
        }

        response = client.post('/api/auth/register', json=participant_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'user' in data
        assert 'token' in data
        assert data['user']['role'] == 'PARTICIPANT'

    def test_login_participant_success(self, client, test_participant):
        """Test participant login successfully"""
        login_data = {
            'email': 'participant@test.com',
            'password': 'password123'
        }

        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'user' in data
        assert 'token' in data

    def test_get_profile_participant(self, client, test_participant, auth_headers_participant):
        """Test getting participant profile"""
        response = client.get('/api/auth/profile', headers=auth_headers_participant)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['email'] == 'participant@test.com'
        assert data['role'] == 'PARTICIPANT'
        assert 'participant_profile' in data


class TestHealthCheck:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert data['version'] == '1.0.0'


if __name__ == '__main__':
    pytest.main([__file__])
