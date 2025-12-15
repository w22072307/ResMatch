#!/usr/bin/env python3
"""
Complete database initialization for ResMatch with all required columns
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
import json
from datetime import datetime, timedelta, date
import uuid
import bcrypt

def init_database():
    """Initialize database with tables and mock data"""
    print("Initializing ResMatch Database...")
    
    # Database file path - use Flask instance folder
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(backend_dir, 'instance')
    
    # Create instance directory if it doesn't exist
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"Created instance directory: {instance_dir}")

    # Database file path
    db_path = os.path.join(instance_dir, 'resmatch.db')
    print(f"Creating database at: {db_path}")

    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print("Removed existing database file.")

    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create tables
    create_tables(cursor)

    # Create mock data
    create_mock_data(conn, cursor)

    # Close connection
    conn.close()

    print(f"Database successfully created at: {db_path}")
    print("Database initialization complete!")

    # Create .env file for Flask
    env_path = os.path.join(backend_dir, '.env')
    with open(env_path, 'w') as f:
        f.write(f'DATABASE_URL=sqlite:///{db_path}\n')

    print(f"Created .env file for Flask")
    return db_path

def create_tables(cursor):
    """Create database tables"""
    print("Creating database tables...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('RESEARCHER', 'PARTICIPANT', 'ADMIN')),
            password_hash TEXT NOT NULL,
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Researcher profiles table
    cursor.execute('''
        CREATE TABLE researcher_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            institution TEXT,
            department TEXT,
            title TEXT,
            bio TEXT,
            verified BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Participant profiles table
    cursor.execute('''
        CREATE TABLE participant_profiles (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            date_of_birth DATE,
            gender TEXT,
            location TEXT,
            bio TEXT,
            interests TEXT,
            availability TEXT,
            phone_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Studies table
    cursor.execute('''
        CREATE TABLE studies (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            researcher_id TEXT NOT NULL,
            institution TEXT,
            category TEXT,
            duration TEXT,
            compensation REAL,
            location TEXT,
            participants_needed INTEGER,
            participants_current INTEGER DEFAULT 0,
            status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'COMPLETED', 'CANCELLED', 'DRAFT')),
            irb_approval_number TEXT,
            consent_form TEXT,  -- Added consent_form column
            requirements TEXT,
            start_date DATE,
            end_date DATE,
            application_deadline DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (researcher_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # Study applications table
    cursor.execute('''
        CREATE TABLE study_applications (
            id TEXT PRIMARY KEY,
            study_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'WITHDRAWN')),
            message TEXT,
            consent_form TEXT,  -- Added consent_form column
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (study_id) REFERENCES studies (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(study_id, user_id)
        )
    ''')
    
    # Study participations table
    cursor.execute('''
        CREATE TABLE study_participations (
            id TEXT PRIMARY KEY,
            study_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            status TEXT DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'COMPLETED', 'WITHDRAWN', 'PAUSED')),
            consent_given BOOLEAN DEFAULT FALSE,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (study_id) REFERENCES studies (id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            UNIQUE(study_id, user_id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE messages (
            id TEXT PRIMARY KEY,
            study_id TEXT,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT DEFAULT 'TEXT' CHECK (type IN ('TEXT', 'FILE', 'SYSTEM')),
            read BOOLEAN DEFAULT FALSE,
            read_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (study_id) REFERENCES studies (id) ON DELETE SET NULL,
            FOREIGN KEY (sender_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    print("Database tables created successfully!")

def create_mock_data(conn, cursor):
    """Create mock data for testing"""
    print("Creating mock data...")
    
    # Create mock researchers
    researchers_data = [
        {
            'id': str(uuid.uuid4()),
            'email': 'dr.sarah.johnson@stanford.edu',
            'name': 'Dr. Sarah Johnson',
            'role': 'RESEARCHER'
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'dr.michael.chen@mit.edu',
            'name': 'Dr. Michael Chen',
            'role': 'RESEARCHER'
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'dr.emily.rodriguez@ucla.edu',
            'name': 'Dr. Emily Rodriguez',
            'role': 'RESEARCHER'
        }
    ]
    
    # Insert researchers with proper bcrypt hashes
    for researcher_data in researchers_data:
        password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        researcher_data['password_hash'] = password_hash
    
    cursor.executemany('''
        INSERT INTO users (id, email, name, role, password_hash)
        VALUES (:id, :email, :name, :role, :password_hash)
    ''', researchers_data)
    
    # Create researcher profiles
    researcher_profiles_data = [
        {
            'id': str(uuid.uuid4()),
            'user_id': researchers_data[0]['id'],
            'institution': 'Stanford University',
            'department': 'Psychology',
            'title': 'Assistant Professor',
            'bio': 'Expert in cognitive psychology and behavioral research',
            'verified': 1
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': researchers_data[1]['id'],
            'institution': 'MIT',
            'department': 'Neuroscience',
            'title': 'Research Scientist',
            'bio': 'Specialist in sleep research and brain function',
            'verified': 1
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': researchers_data[2]['id'],
            'institution': 'UCLA',
            'department': 'Health Sciences',
            'title': 'Principal Investigator',
            'bio': 'Leading researcher in exercise and cognition studies',
            'verified': 1
        }
    ]
    
    cursor.executemany('''
        INSERT INTO researcher_profiles (id, user_id, institution, department, title, bio, verified)
        VALUES (:id, :user_id, :institution, :department, :title, :bio, :verified)
    ''', researcher_profiles_data)
    
    # Create mock participants
    participants_data = [
        {
            'id': str(uuid.uuid4()),
            'email': 'sarah.johnson@email.com',
            'name': 'Sarah Johnson',
            'role': 'PARTICIPANT'
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'michael.chen@email.com',
            'name': 'Michael Chen',
            'role': 'PARTICIPANT'
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'emily.rodriguez@email.com',
            'name': 'Emily Rodriguez',
            'role': 'PARTICIPANT'
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'david.park@email.com',
            'name': 'David Park',
            'role': 'PARTICIPANT'
        },
        {
            'id': str(uuid.uuid4()),
            'email': 'jessica.taylor@email.com',
            'name': 'Jessica Taylor',
            'role': 'PARTICIPANT'
        }
    ]
    
    # Insert participants with proper bcrypt hashes
    for participant_data in participants_data:
        password_hash = bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        participant_data['password_hash'] = password_hash
    
    cursor.executemany('''
        INSERT INTO users (id, email, name, role, password_hash)
        VALUES (:id, :email, :name, :role, :password_hash)
    ''', participants_data)
    
    # Create participant profiles
    participant_profiles_data = [
        {
            'id': str(uuid.uuid4()),
            'user_id': participants_data[0]['id'],
            'date_of_birth': '1999-05-15',  # 24 years old
            'gender': 'Female',
            'location': 'San Francisco, CA',
            'bio': 'Graduate student interested in psychology and neuroscience research',
            'interests': json.dumps(['Psychology', 'Health', 'Technology', 'Education']),
            'availability': json.dumps(['Weekdays', 'Evenings', 'Weekends']),
            'phone_number': '+1-555-0101'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': participants_data[1]['id'],
            'date_of_birth': '1997-03-22',  # 27 years old
            'gender': 'Male',
            'location': 'Los Angeles, CA',
            'bio': 'Software developer interested in cognitive science and sleep research',
            'interests': json.dumps(['Technology', 'Health', 'Neuroscience', 'Data Science']),
            'availability': json.dumps(['Flexible', 'Weekdays', 'Evenings']),
            'phone_number': '+1-555-0102'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': participants_data[2]['id'],
            'date_of_birth': '2002-08-10',  # 22 years old
            'gender': 'Female',
            'location': 'Remote',
            'bio': 'Undergraduate student passionate about mental health research',
            'interests': json.dumps(['Psychology', 'Health', 'Education', 'Social Media']),
            'availability': json.dumps(['Weekends', 'Flexible hours']),
            'phone_number': '+1-555-0103'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': participants_data[3]['id'],
            'date_of_birth': '1995-11-08',  # 29 years old
            'gender': 'Male',
            'location': 'Seattle, WA',
            'bio': 'Data analyst interested in sleep patterns and cognitive research',
            'interests': json.dumps(['Data Science', 'Health', 'Neuroscience', 'Statistics']),
            'availability': json.dumps(['Weekdays', 'Evenings']),
            'phone_number': '+1-555-0104'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': participants_data[4]['id'],
            'date_of_birth': '1999-02-14',  # 25 years old
            'gender': 'Female',
            'location': 'New York, NY',
            'bio': 'Marketing student interested in social media and behavior research',
            'interests': json.dumps(['Social Media', 'Psychology', 'Marketing', 'Communication']),
            'availability': json.dumps(['Evenings', 'Weekends']),
            'phone_number': '+1-555-0105'
        }
    ]
    
    cursor.executemany('''
        INSERT INTO participant_profiles (id, user_id, date_of_birth, gender, location, bio, interests, availability, phone_number)
        VALUES (:id, :user_id, :date_of_birth, :gender, :location, :bio, :interests, :availability, :phone_number)
    ''', participant_profiles_data)
    
    # Create mock studies
    studies_data = [
        {
            'id': str(uuid.uuid4()),
            'title': 'Social Media Usage and Mental Health',
            'description': 'A longitudinal study examining the relationship between social media use and well-being in young adults',
            'researcher_id': researchers_data[0]['id'],
            'institution': 'Stanford University',
            'category': 'Psychology',
            'duration': '4 weeks',
            'compensation': 50.0,
            'location': 'Remote',
            'participants_needed': 100,
            'participants_current': 45,
            'status': 'ACTIVE',
            'irb_approval_number': 'IRB-2025-123456',
            'consent_form': 'Standard consent form for social media research',
            'requirements': json.dumps([
                {'type': 'age', 'min': 18, 'max': 30},
                {'type': 'interest', 'value': 'Social Media'},
                {'type': 'interest', 'value': 'Psychology'},
                {'type': 'gender', 'value': 'Any'},
                {'type': 'language', 'value': 'English'}
            ]),
            'start_date': '2025-01-15',
            'end_date': '2025-03-15',
            'application_deadline': '2025-02-01'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Sleep Patterns in College Students',
            'description': 'Understanding sleep quality and academic performance correlation through wearable tracking',
            'researcher_id': researchers_data[1]['id'],
            'institution': 'MIT',
            'category': 'Neuroscience',
            'duration': '2 weeks',
            'compensation': 30.0,
            'location': 'Remote',
            'participants_needed': 80,
            'participants_current': 78,
            'status': 'ACTIVE',
            'irb_approval_number': 'IRB-2025-234567',
            'consent_form': 'Sleep study consent with wearable device tracking',
            'requirements': json.dumps([
                {'type': 'age', 'min': 18, 'max': 25},
                {'type': 'status', 'value': 'Student'},
                {'type': 'device', 'value': 'Smartphone'},
                {'type': 'language', 'value': 'English'}
            ]),
            'start_date': '2025-02-01',
            'end_date': '2025-02-15',
            'application_deadline': '2025-01-25'
        },
        {
            'id': str(uuid.uuid4()),
            'title': 'Cognitive Effects of Exercise',
            'description': 'Investigating how different exercise routines affect cognitive function and memory',
            'researcher_id': researchers_data[2]['id'],
            'institution': 'UCLA',
            'category': 'Health',
            'duration': '6 weeks',
            'compensation': 75.0,
            'location': 'Los Angeles, CA',
            'participants_needed': 60,
            'participants_current': 25,
            'status': 'ACTIVE',
            'irb_approval_number': 'IRB-2025-345678',
            'consent_form': 'Exercise study consent with cognitive testing',
            'requirements': json.dumps([
                {'type': 'age', 'min': 20, 'max': 40},
                {'type': 'fitness', 'value': 'No regular exercise'},
                {'type': 'bmi', 'min': 18.5, 'max': 24.9},
                {'type': 'language', 'value': 'English'}
            ]),
            'start_date': '2025-03-01',
            'end_date': '2025-04-15',
            'application_deadline': '2025-02-20'
        }
    ]
    
    cursor.executemany('''
        INSERT INTO studies (id, title, description, researcher_id, institution, category, duration, compensation, location, participants_needed, participants_current, status, irb_approval_number, consent_form, requirements, start_date, end_date, application_deadline)
        VALUES (:id, :title, :description, :researcher_id, :institution, :category, :duration, :compensation, :location, :participants_needed, :participants_current, :status, :irb_approval_number, :consent_form, :requirements, :start_date, :end_date, :application_deadline)
    ''', studies_data)
    
    # Create some study applications
    applications_data = [
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'user_id': participants_data[0]['id'],  # Sarah Johnson
            'status': 'APPROVED',
            'message': 'I am very interested in this study as it aligns with my research interests.',
            'consent_form': 'Social media consent form signed'
        },
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'user_id': participants_data[1]['id'],  # Michael Chen
            'status': 'PENDING',
            'message': 'I would like to participate in this study about social media effects.',
            'consent_form': None
        },
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'user_id': participants_data[2]['id'],  # Emily Rodriguez
            'status': 'PENDING',
            'message': 'This study sounds very interesting and relevant to my studies.',
            'consent_form': None
        },
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[1]['id'],  # Sleep Patterns study
            'user_id': participants_data[1]['id'],  # Michael Chen
            'status': 'PENDING',
            'message': 'As a student interested in sleep research, I would like to participate.',
            'consent_form': None
        }
    ]
    
    cursor.executemany('''
        INSERT INTO study_applications (id, study_id, user_id, status, message, consent_form)
        VALUES (:id, :study_id, :user_id, :status, :message, :consent_form)
    ''', applications_data)
    
    # Create some study participations
    participations_data = [
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'user_id': participants_data[0]['id'],  # Sarah Johnson
            'status': 'ACTIVE',
            'consent_given': 1,
            'start_date': (datetime.utcnow() - timedelta(days=14)).isoformat(),
            'notes': 'Participant is very engaged and providing detailed responses.'
        },
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[1]['id'],  # Sleep Patterns study
            'user_id': participants_data[1]['id'],  # Michael Chen
            'status': 'ACTIVE',
            'consent_given': 1,
            'start_date': (datetime.utcnow() - timedelta(days=7)).isoformat(),
            'notes': 'Consistently submitting sleep tracking data on time.'
        }
    ]
    
    cursor.executemany('''
        INSERT INTO study_participations (id, study_id, user_id, status, consent_given, start_date, notes)
        VALUES (:id, :study_id, :user_id, :status, :consent_given, :start_date, :notes)
    ''', participations_data)
    
    # Create some messages
    messages_data = [
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'sender_id': researchers_data[0]['id'],  # Dr. Sarah Johnson
            'receiver_id': participants_data[0]['id'],  # Sarah Johnson
            'content': 'Hello! Thank you for enrolling in our study. I wanted to reach out to confirm your availability for first session.',
            'type': 'TEXT',
            'read': 1  # Read by participant
        },
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'sender_id': participants_data[0]['id'],  # Sarah Johnson
            'receiver_id': researchers_data[0]['id'],  # Dr. Sarah Johnson
            'content': 'Hi Dr. Johnson! Yes, I am available this week.',
            'type': 'TEXT',
            'read': 1  # Read by researcher
        },
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'sender_id': researchers_data[0]['id'],  # Dr. Sarah Johnson
            'receiver_id': participants_data[0]['id'],  # Sarah Johnson
            'content': 'Perfect! How about Thursday at 2 PM?',
            'type': 'TEXT',
            'read': 1  # Read by participant
        },
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'sender_id': participants_data[0]['id'],  # Sarah Johnson
            'receiver_id': researchers_data[0]['id'],  # Dr. Sarah Johnson
            'content': 'Thursday at 2 PM works great for me.',
            'type': 'TEXT',
            'read': 1  # Read by researcher
        },
        {
            'id': str(uuid.uuid4()),
            'study_id': studies_data[0]['id'],  # Social Media study
            'sender_id': researchers_data[0]['id'],  # Dr. Sarah Johnson
            'receiver_id': participants_data[0]['id'],  # Sarah Johnson
            'content': 'Excellent! I will send you a calendar invite. Looking forward to working with you.',
            'type': 'TEXT',
            'read': 0  # Unread by participant
        }
    ]
    
    cursor.executemany('''
        INSERT INTO messages (id, study_id, sender_id, receiver_id, content, type, read)
        VALUES (:id, :study_id, :sender_id, :receiver_id, :content, :type, :read)
    ''', messages_data)
    
    # Commit all changes
    conn.commit()
    print("Mock data created successfully!")
    
    # Print summary
    print(f"Created {len(researchers_data)} researchers")
    print(f"Created {len(participants_data)} participants")
    print(f"Created {len(studies_data)} studies")
    print(f"Created {len(applications_data)} applications")
    print(f"Created {len(participations_data)} participations")
    print(f"Created {len(messages_data)} messages")

def recreate_database():
    """Recreate database schema without mock data"""
    print("Recreating database schema...")

    # Database file path - use Flask instance folder
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    instance_dir = os.path.join(backend_dir, 'instance')

    # Create instance directory if it doesn't exist
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

    # Database file path
    db_path = os.path.join(instance_dir, 'resmatch.db')

    # Create database connection
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # Create tables
    create_tables(cursor)
    conn.commit()
    conn.close()

    print(f"Database schema recreated at: {db_path}")
    return db_path

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'recreate':
        recreate_database()
    else:
        init_database()