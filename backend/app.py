from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')

# Use Flask's default instance folder for database
# If DATABASE_URL is not set, Flask will use instance/resmatch.db
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///resmatch.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

print(f"Flask database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# Import extensions from models
from models import db, bcrypt

# Initialize extensions with the app
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Enable CORS with proper settings
CORS(app, 
    origins=["http://localhost:3000"], 
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=True
)

# Add OPTIONS handler for CORS preflight requests
@app.before_request
def handle_options_request():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Max-Age', '86400')
        return response

# Import models
from models import User, ResearcherProfile, ParticipantProfile, Study, StudyApplication, StudyParticipation, Message

# Import routes
from routes.auth import auth_bp
from routes.studies import studies_bp
from routes.matching import matching_bp
from routes.messages import messages_bp
from routes.participants import participants_bp
from routes.researchers import researchers_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(studies_bp, url_prefix='/api/studies')
app.register_blueprint(matching_bp, url_prefix='/api/matching')
app.register_blueprint(messages_bp, url_prefix='/api/messages')
app.register_blueprint(participants_bp, url_prefix='/api/participants')
app.register_blueprint(researchers_bp, url_prefix='/api/researchers')

# Database tables will be created by init_db_standalone.py
# Commenting out automatic table creation to avoid conflicts
# with app.app_context():
#     db.create_all()

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'cors': 'enabled'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)