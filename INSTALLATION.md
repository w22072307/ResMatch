# ResMatch V5 - Installation Guide

This guide provides step-by-step instructions for setting up the ResMatch research participant recruitment platform.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 18.x or higher
- **npm**: 8.x or higher
- **Git**: Latest version
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux

### Hardware Requirements
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 500MB free space
- **Network**: Internet connection for package installation

## Installation Steps

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ResMatch
```

### 2. Backend Setup (Flask API)

#### 2.1 Create Python Virtual Environment

**Windows:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

#### 2.2 Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Required Python Packages:**
- Flask==3.0.0
- Flask-JWT-Extended==4.5.3
- Flask-SQLAlchemy==3.1.1
- Flask-Bcrypt==1.0.1
- Flask-CORS==4.0.0
- SQLAlchemy==2.0.45
- PyJWT==2.10.1
- python-dotenv==1.0.0

#### 2.3 Initialize Database

```bash
python init_db.py
```

This will:
- Create SQLite database (`instance/resmatch.db`)
- Populate with sample data
- Set up all tables and relationships

you should reinitilize the database after running a test

### 3. Frontend Setup (Next.js)

#### 3.1 Install Node.js Dependencies

```bash
# From project root directory
npm install
```

**Key Frontend Dependencies:**
- next==14.x
- react==18.x
- react-dom==18.x
- @radix-ui/react-dialog
- @radix-ui/react-tabs
- @radix-ui/react-toast
- lucide-react
- tailwindcss
- typescript

### 4. Configuration

#### 4.1 Environment Variables

Create `.env` file in backend directory:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///instance/resmatch.db
```

#### 4.2 Verify Installation

**Test Backend:**
```bash
cd backend
python -c "import flask, flask_jwt_extended, flask_sqlalchemy; print('Backend dependencies OK')"
```

**Test Frontend:**
```bash
npm run build
```

## Troubleshooting

### Common Issues

#### 1. Python Virtual Environment Issues
```bash
# If activation fails on Windows
python -m venv venv --clear
venv\Scripts\activate.ps1

# If pip install fails
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### 2. Database Initialization Errors
```bash
# Remove existing database and retry
rm -rf backend/instance
python init_db.py
```

#### 3. Node.js Installation Issues
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### 4. Port Conflicts
- Backend runs on port 5000 by default
- Frontend runs on port 3000 by default
- Ensure these ports are available

### Environment-Specific Setup

#### Windows
- Use PowerShell or Command Prompt
- Ensure execution policy allows scripts: `Set-ExecutionPolicy RemoteSigned`

#### macOS
- Use Terminal
- May need to install Xcode command line tools: `xcode-select --install`

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm
```

#### WSL (Windows Subsystem for Linux)
- Follow Linux instructions
- Ensure ports are accessible from Windows browser

## Next Steps

After successful installation:

1. **Start the application** (see RUNNING.md)
2. **Run tests** to verify functionality
3. **Access the application** at http://localhost:3000
4. **API documentation** available at http://localhost:5000 (when running)

## Support

For issues not covered in this guide:
1. Check the troubleshooting section above
2. Review the RUNNING.md guide
3. Check the main README.md for project overview
4. Ensure all prerequisites are met

---

**Installation completed successfully?** ✅ Proceed to [RUNNING.md](RUNNING.md) to start the application.
