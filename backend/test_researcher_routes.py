import pytest
import json
import uuid
from datetime import datetime, date
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from app import app, db
from models import User, ResearcherProfile, ParticipantProfile, Study, StudyApplication, Message, UserRole, StudyStatus, ApplicationStatus, MessageType


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
def auth_headers_researcher(test_researcher):
    """Get auth headers for researcher"""
    access_token = create_access_token(identity=test_researcher.id)
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def auth_headers_participant(test_participant):
    """Get auth headers for participant"""
    access_token = create_access_token(identity=test_participant.id)
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


class TestResearcherProfileRoutes:
    """Test researcher profile routes"""

    def test_get_researcher_profile_success(self, client, test_researcher, auth_headers_researcher):
        """Test getting researcher profile successfully"""
        response = client.get('/api/researchers/profile', headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'researcher_profile' in data
        profile = data['researcher_profile']
        assert profile['user_id'] == test_researcher.id
        assert profile['institution'] == 'Test University'
        assert profile['department'] == 'Psychology'
        assert profile['title'] == 'Professor'

    def test_get_researcher_profile_unauthorized(self, client):
        """Test getting researcher profile without auth"""
        response = client.get('/api/researchers/profile')
        assert response.status_code == 401

    def test_update_researcher_profile_success(self, client, test_researcher, auth_headers_researcher):
        """Test updating researcher profile successfully"""
        update_data = {
            'institution': 'Updated University',
            'department': 'Updated Department',
            'title': 'Updated Title',
            'bio': 'Updated bio'
        }

        response = client.put('/api/researchers/profile',
                            json=update_data,
                            headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'profile' in data
        profile = data['profile']
        assert profile['institution'] == 'Updated University'
        assert profile['department'] == 'Updated Department'

    def test_update_researcher_profile_partial(self, client, test_researcher, auth_headers_researcher):
        """Test partial update of researcher profile"""
        update_data = {'bio': 'New bio only'}

        response = client.put('/api/researchers/profile',
                            json=update_data,
                            headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        profile = data['profile']
        assert profile['bio'] == 'New bio only'
        assert profile['institution'] == 'Test University'  # Should remain unchanged


class TestStudyRoutes:
    """Test study management routes"""

    def test_get_studies_public(self, client, test_study):
        """Test getting studies without authentication"""
        response = client.get('/api/studies/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) >= 1

        study = next((s for s in data if s['id'] == test_study.id), None)
        assert study is not None
        assert study['title'] == 'Test Study'

    def test_get_studies_filtered(self, client, test_study, test_researcher):
        """Test getting studies with filters"""
        response = client.get(f'/api/studies/?researcher_id={test_researcher.id}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) >= 1
        assert all(study['researcher']['id'] == test_researcher.id for study in data)

    def test_create_study_success(self, client, test_researcher, auth_headers_researcher):
        """Test creating a study successfully"""
        study_data = {
            'title': 'New Research Study',
            'description': 'A new research study for testing',
            'institution': 'Test University',
            'category': 'Psychology',
            'duration': '6 months',
            'participants_needed': 20,
            'requirements': [{'type': 'age', 'min': 21, 'max': 50}]
        }

        response = client.post('/api/studies/',
                             json=study_data,
                             headers=auth_headers_researcher)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'study' in data
        study = data['study']
        assert study['title'] == 'New Research Study'
        assert study['participants_needed'] == 20

    def test_create_study_missing_fields(self, client, test_researcher, auth_headers_researcher):
        """Test creating a study with missing required fields"""
        incomplete_data = {
            'title': 'Incomplete Study'
            # Missing required fields
        }

        response = client.post('/api/studies/',
                             json=incomplete_data,
                             headers=auth_headers_researcher)
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data

    def test_create_study_unauthorized(self, client):
        """Test creating a study without authentication"""
        study_data = {
            'title': 'Unauthorized Study',
            'description': 'Should fail',
            'institution': 'Test',
            'category': 'Test',
            'duration': '1 month',
            'participants_needed': 5
        }

        response = client.post('/api/studies/', json=study_data)
        assert response.status_code == 401

    def test_get_study_by_id(self, client, test_study):
        """Test getting a specific study by ID"""
        response = client.get(f'/api/studies/{test_study.id}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['id'] == test_study.id
        assert data['title'] == 'Test Study'

    def test_get_study_not_found(self, client):
        """Test getting a non-existent study"""
        response = client.get('/api/studies/non-existent-id')
        assert response.status_code == 404

    def test_get_study_applications_success(self, client, test_study, test_researcher, auth_headers_researcher):
        """Test getting applications for a study"""
        response = client.get(f'/api/studies/{test_study.id}/applications',
                            headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_study_applications_unauthorized(self, client, test_study, auth_headers_participant):
        """Test getting applications for a study as non-researcher"""
        response = client.get(f'/api/studies/{test_study.id}/applications',
                            headers=auth_headers_participant)
        assert response.status_code == 404  # Access denied


class TestMatchingRoutes:
    """Test matching routes"""

    def test_get_matched_participants_success(self, client, test_study, test_researcher, auth_headers_researcher):
        """Test getting matched participants for a study"""
        response = client.get(f'/api/matching/participants/{test_study.id}',
                            headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'study_id' in data
        assert 'matches' in data
        assert 'total_matches' in data

    def test_get_matched_participants_unauthorized(self, client, test_study):
        """Test getting matched participants without auth"""
        response = client.get(f'/api/matching/participants/{test_study.id}')
        assert response.status_code == 401


class TestMessageRoutes:
    """Test message routes"""

    def test_send_message_success(self, client, test_researcher, test_participant, auth_headers_researcher):
        """Test sending a message successfully"""
        message_data = {
            'receiver_id': test_participant.id,
            'content': 'Hello from researcher'
        }

        response = client.post('/api/messages/',
                             json=message_data,
                             headers=auth_headers_researcher)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'message_data' in data
        assert data['message_data']['content'] == 'Hello from researcher'

    def test_send_message_missing_fields(self, client, test_researcher, auth_headers_researcher):
        """Test sending a message with missing fields"""
        incomplete_data = {'content': 'Missing receiver'}

        response = client.post('/api/messages/',
                             json=incomplete_data,
                             headers=auth_headers_researcher)
        assert response.status_code == 400

    def test_get_messages_success(self, client, auth_headers_researcher):
        """Test getting messages successfully"""
        response = client.get('/api/messages/', headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_conversations_success(self, client, auth_headers_researcher):
        """Test getting conversations successfully"""
        response = client.get('/api/messages/conversations', headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)


class TestAuthRoutes:
    """Test authentication routes used by researchers"""

    def test_register_researcher_success(self, client):
        """Test registering a researcher successfully"""
        researcher_data = {
            'email': 'new.researcher@test.com',
            'password': 'password123',
            'name': 'New Researcher',
            'role': 'RESEARCHER'
        }

        response = client.post('/api/auth/register', json=researcher_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'user' in data
        assert 'token' in data
        assert data['user']['role'] == 'RESEARCHER'

    def test_login_researcher_success(self, client, test_researcher):
        """Test researcher login successfully"""
        login_data = {
            'email': 'researcher@test.com',
            'password': 'password123'
        }

        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'user' in data
        assert 'token' in data

    def test_get_profile_researcher(self, client, test_researcher, auth_headers_researcher):
        """Test getting researcher profile"""
        response = client.get('/api/auth/profile', headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['email'] == 'researcher@test.com'
        assert data['role'] == 'RESEARCHER'
        assert 'researcher_profile' in data


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


class TestMatchingRoutes:
    """Test matching routes"""

    def test_get_matched_participants_success(self, client, test_study, test_researcher, auth_headers_researcher):
        """Test getting matched participants for a study"""
        response = client.get(f'/api/matching/participants/{test_study.id}',
                            headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'study_id' in data
        assert 'matches' in data
        assert 'total_matches' in data

    def test_get_matched_participants_unauthorized(self, client, test_study):
        """Test getting matched participants without auth"""
        response = client.get(f'/api/matching/participants/{test_study.id}')
        assert response.status_code == 401


class TestMessageRoutes:
    """Test message routes"""

    def test_send_message_success(self, client, test_researcher, test_participant, auth_headers_researcher):
        """Test sending a message successfully"""
        message_data = {
            'receiver_id': test_participant.id,
            'content': 'Hello from researcher'
        }

        response = client.post('/api/messages/',
                             json=message_data,
                             headers=auth_headers_researcher)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'message_data' in data
        assert data['message_data']['content'] == 'Hello from researcher'

    def test_send_message_missing_fields(self, client, test_researcher, auth_headers_researcher):
        """Test sending a message with missing fields"""
        incomplete_data = {'content': 'Missing receiver'}

        response = client.post('/api/messages/',
                             json=incomplete_data,
                             headers=auth_headers_researcher)
        assert response.status_code == 400

    def test_get_messages_success(self, client, auth_headers_researcher):
        """Test getting messages successfully"""
        response = client.get('/api/messages/', headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_conversations_success(self, client, auth_headers_researcher):
        """Test getting conversations successfully"""
        response = client.get('/api/messages/conversations', headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)


class TestAuthRoutes:
    """Test authentication routes used by researchers"""

    def test_register_researcher_success(self, client):
        """Test registering a researcher successfully"""
        researcher_data = {
            'email': 'new.researcher@test.com',
            'password': 'password123',
            'name': 'New Researcher',
            'role': 'RESEARCHER'
        }

        response = client.post('/api/auth/register', json=researcher_data)
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'user' in data
        assert 'token' in data
        assert data['user']['role'] == 'RESEARCHER'

    def test_login_researcher_success(self, client, test_researcher):
        """Test researcher login successfully"""
        login_data = {
            'email': 'researcher@test.com',
            'password': 'password123'
        }

        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'user' in data
        assert 'token' in data

    def test_get_profile_researcher(self, client, test_researcher, auth_headers_researcher):
        """Test getting researcher profile"""
        response = client.get('/api/auth/profile', headers=auth_headers_researcher)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['email'] == 'researcher@test.com'
        assert data['role'] == 'RESEARCHER'
        assert 'researcher_profile' in data


if __name__ == '__main__':
    pytest.main([__file__])
