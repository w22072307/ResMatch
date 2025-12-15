# ResMatch V5 - Running & Testing Guide

This guide provides instructions for running the ResMatch V5 application and executing tests.

## Quick Start

### Development Mode (Recommended)

1. **Start Backend (Terminal 1):**
```bash
cd backend
# Activate virtual environment (Windows)
venv\Scripts\activate
# or (macOS/Linux)
source venv/bin/activate

python app.py
```

2. **Start Frontend (Terminal 2):**
```bash
# From project root
npm run dev
```

3. **Access Application:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:5000

### Production Mode

1. **Build Frontend:**
```bash
npm run build
```

2. **Start Backend:**
```bash
cd backend
python app.py
```

## Detailed Instructions

### Backend (Flask API)

#### Starting the Server

```bash
cd backend

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Run the application
python app.py
```

**Expected Output:**
```
Flask database URI: sqlite:///instance/resmatch.db
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: XXX-XXX-XXX
```

#### Available Endpoints

The API will be available at `http://localhost:5000` with the following main routes:
- `GET /api/health` - Health check
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Frontend (Next.js)

#### Development Server

```bash
# From project root
npm run dev
```

**Expected Output:**
```
- Local:        http://localhost:3000
- Environments: .env.local
- Used config:  next.config.ts

✓ Ready in 2.3s
✓ Compiled / in 452ms (247 modules)
```

## Testing

### Backend Tests (Pytest)

#### Run All Tests

```bash
cd backend

# Activate virtual environment
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html
```

#### Run Specific Test Files

```bash
# Test researcher routes only
pytest test_researcher_routes.py -v

# Test participant routes only
pytest test_participant_routes.py -v

# Run tests matching pattern
pytest -k "test_login" -v
```

#### Test Structure

**test_researcher_routes.py:**
- Authentication tests (login/register)
- Study management (create, update, delete)
- Application management (view, approve, reject)
- Messaging functionality
- Profile management

**test_participant_routes.py:**
- Authentication tests
- Profile management
- Study browsing and application
- Participations tracking
- Matching algorithms
- Messaging functionality

### Frontend Tests

## Manual Testing

### User Roles & Test Accounts

The application includes sample data with the following test accounts:

#### Researcher Accounts
- **Email:** researcher1@example.com
- **Password:** password123
- **Role:** Researcher

#### Participant Accounts
- **Email:** participant1@example.com
- **Password:** password123
- **Role:** Participant

### Testing Scenarios

#### 1. Researcher Workflow
1. Login as researcher
2. Create a new study
3. View applications
4. Approve/reject applications
5. Message participants
6. View enrolled participants

#### 2. Participant Workflow
1. Login as participant
2. Complete/update profile
3. Browse recommended studies
4. Apply to studies
5. View application status
6. Participate in approved studies

#### 3. Admin Features
1. View all users
2. Manage studies
3. Monitor applications
4. Access analytics

## API Testing

### Using Invoke-WebRequest

#### Health Check
Invoke-WebRequest http://localhost:5000/api/health

#### Login
Invoke-WebRequest -Uri "http://localhost:5000/api/auth/login" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"email":"dr.emily.rodriguez@ucla.edu","password":"password12
3"}'

#### Get Profile (requires token)
```bash
Invoke-WebRequest -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Postman/Insomnia

1. Import the API collection (if available)
2. Set base URL to `http://localhost:5000`
3. Use JWT tokens for authenticated requests

## Database Management

### Reset Database

```bash
cd backend
# Remove existing database
rm -rf instance

# Recreate and populate
python init_db.py
```

### Database Inspection

```bash
cd backend
python -c "from app import db; db.create_all(); print('Database tables created')"
```

## Debugging

### Backend Issues

#### Check Logs
```bash
# Run with debug logging
export FLASK_DEBUG=1
python app.py
```

#### Common Issues
- **Port 5000 in use:** Kill process or use different port
- **Database errors:** Reset database with `python init_db.py`
- **CORS errors:** Check Flask-CORS configuration

### Frontend Issues

#### Clear Cache
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

#### Check Console
- Open browser DevTools
- Check Network tab for API calls
- Check Console for JavaScript errors

### Environment Variables

Create `.env.local` for frontend:
```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## Performance Monitoring

### Check Application Health

```bash
# Health endpoint
curl http://localhost:5000/api/health

# Database connection test
python -c "from app import db; print('DB connected:', db.engine.url)"
```

### View Logs

- Backend: Check terminal output
- Frontend: Browser DevTools Console
- Database: SQLite browser or command line

## Deployment

### Local Production Test

1. **Build Frontend:**
```bash
npm run build
npm start
```

2. **Start Backend:**
```bash
cd backend
python app.py
```

### Environment Setup

For production deployment, set these environment variables:

```env
# Backend
FLASK_ENV=production
SECRET_KEY=your-production-secret
JWT_SECRET_KEY=your-jwt-secret

# Frontend
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Troubleshooting

### Cannot Connect to Backend
- Ensure backend is running on port 5000
- Check firewall settings
- Verify virtual environment is activated

### Database Errors
- Reset database: `python init_db.py`
- Check file permissions on `instance/` directory

### Frontend Build Errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version compatibility

### Authentication Issues
- Verify JWT token in request headers
- Check token expiration
- Ensure correct user credentials

---

**Need API documentation?** See [API_ROUTES.md](API_ROUTES.md) for detailed endpoint documentation.

**Need team information?** See [README.md](README.md) for project overview and team structure.
