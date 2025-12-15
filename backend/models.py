from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from enum import Enum

# These will be initialized in app.py
db = SQLAlchemy()
bcrypt = Bcrypt()

# Enums
class UserRole(Enum):
    RESEARCHER = "RESEARCHER"
    PARTICIPANT = "PARTICIPANT"
    ADMIN = "ADMIN"

class StudyStatus(Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ApplicationStatus(Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class ParticipationStatus(Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    WITHDRAWN = "WITHDRAWN"
    TERMINATED = "TERMINATED"

class MessageType(Enum):
    TEXT = "TEXT"
    CONSENT_FORM = "CONSENT_FORM"
    NOTIFICATION = "NOTIFICATION"

# Models
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.PARTICIPANT, nullable=False)
    avatar = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    researcher_profile = db.relationship('ResearcherProfile', backref='user', uselist=False)
    participant_profile = db.relationship('ParticipantProfile', backref='user', uselist=False)
    studies = db.relationship('Study', backref='researcher')
    applications = db.relationship('StudyApplication', backref='user')
    participations = db.relationship('StudyParticipation', backref='user')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class ResearcherProfile(db.Model):
    __tablename__ = 'researcher_profiles'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), unique=True, nullable=False)
    institution = db.Column(db.String(200))
    department = db.Column(db.String(200))
    title = db.Column(db.String(100))
    bio = db.Column(db.Text)
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ParticipantProfile(db.Model):
    __tablename__ = 'participant_profiles'

    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    location = db.Column(db.String(200))
    bio = db.Column(db.Text)
    interests = db.Column(db.Text)  # JSON string
    availability = db.Column(db.Text)  # JSON string
    phone_number = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Study(db.Model):
    __tablename__ = 'studies'
    
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    researcher_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    institution = db.Column(db.String(200))
    category = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    compensation = db.Column(db.Float)
    location = db.Column(db.String(200))
    participants_needed = db.Column(db.Integer, nullable=False)
    participants_current = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum(StudyStatus), default=StudyStatus.ACTIVE)
    irb_approval_number = db.Column(db.String(100))
    consent_form = db.Column(db.Text)
    requirements = db.Column(db.Text)  # JSON string
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    application_deadline = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    applications = db.relationship('StudyApplication', backref='study')
    participations = db.relationship('StudyParticipation', backref='study')
    messages = db.relationship('Message', backref='study')

class StudyApplication(db.Model):
    __tablename__ = 'study_applications'
    
    id = db.Column(db.String, primary_key=True)
    study_id = db.Column(db.String, db.ForeignKey('studies.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.PENDING)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudyParticipation(db.Model):
    __tablename__ = 'study_participations'
    
    id = db.Column(db.String, primary_key=True)
    study_id = db.Column(db.String, db.ForeignKey('studies.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.Enum(ParticipationStatus), default=ParticipationStatus.ACTIVE)
    consent_given = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.String, primary_key=True)
    study_id = db.Column(db.String, db.ForeignKey('studies.id'))
    sender_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.Enum(MessageType), default=MessageType.TEXT)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)

