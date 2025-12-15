# ResMatch V5 - Research Participant Recruitment Platform

A modern, AI-powered platform connecting researchers with qualified participants for academic studies. Built with Flask backend and Next.js frontend.

## 🌟 Features

- **Dual User Roles**: Separate dashboards for researchers and participants
- **Intelligent Matching**: AI-powered participant-study compatibility scoring
- **Real-time Messaging**: Built-in communication system between researchers and participants
- **Study Management**: Complete CRUD operations for study lifecycle management
- **Application Workflow**: Streamlined application and approval process
- **Profile Management**: Comprehensive user profiles with demographics and preferences
- **Responsive Design**: Mobile-first design with modern UI components

## 🚀 Quick Start

1. **Install dependencies**: See [INSTALLATION.md](INSTALLATION.md)
2. **Run the application**: See [RUNNING.md](RUNNING.md)
3. **Access the app**: Open http://localhost:3000

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask 3.0.0 with SQLAlchemy ORM
- **Authentication**: JWT-based with role-based access control
- **Database**: SQLite with proper relationships and constraints
- **API**: RESTful endpoints with comprehensive error handling

### Frontend (Next.js)
- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS with shadcn/ui component library
- **State Management**: React hooks with TypeScript
- **UI/UX**: Responsive design with accessibility features

### Project Structure
```
ResMatchV5/
├── backend/                    # Flask API backend
│   ├── app.py                 # Main application
│   ├── models.py              # Database models
│   ├── init_db.py             # Database initialization
│   ├── requirements.txt       # Python dependencies
│   ├── test_*.py             # Comprehensive test suites
│   └── routes/                # API endpoints
├── src/                       # Next.js frontend
│   ├── app/                  # App router pages
│   ├── components/ui/        # Reusable UI components
│   └── lib/                  # Utilities and API client
├── INSTALLATION.md           # Setup guide
├── RUNNING.md               # Running and testing guide
├── API_ROUTES.md            # Complete API documentation
└── TEAM_TASKS.md            # Team implementation details
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+ and pip
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd resmatch
```

### 2. Start Backend

```bash
cd backend
./run.sh
```

This will:
- Create Python virtual environment
- Install dependencies
- Initialize database with mock data
- Start Flask server on port 5000

### 3. Start Frontend

```bash
# In a new terminal
npm install
npm run dev
```

This will start Next.js on port 3000.

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000/api
- **Health Check**: http://localhost:5000/api/health

## 🔑 Test Accounts

### Researchers
- **Email**: dr.sarah.johnson@stanford.edu
- **Password**: password123
- **Name**: Dr. Sarah Johnson

### Participants
- **Email**: sarah.johnson@email.com
- **Password**: password123
- **Name**: Sarah Johnson

## 📊 Features

### For Researchers
- ✅ Study creation and management
- ✅ Participant recruitment and screening
- ✅ AI-powered matching algorithm
- ✅ Application management
- ✅ Real-time messaging
- ✅ Analytics dashboard
- ✅ IRB compliance tracking

### For Participants
- ✅ Personalized study recommendations
- ✅ Easy application process
- ✅ Profile management
- ✅ Participation tracking
- ✅ Secure messaging with researchers
- ✅ Achievement system

### Platform Features
- ✅ JWT-based authentication
- ✅ Role-based access control
- ✅ Real-time notifications
- ✅ GDPR compliance
- ✅ Responsive design
- ✅ Mobile-friendly interface

## 🧠 AI Matching Algorithm

The platform uses a sophisticated rule-based matching algorithm that considers:

- **Age Compatibility** (20 points)
- **Location Matching** (15 points)
- **Gender Requirements** (10 points)
- **Interest Alignment** (25 points)
- **Availability** (20 points)
- **Study History** (10 points)

Participants with 50%+ match score are recommended for studies.

## 🔧 Technology Stack

### Backend
- **Framework**: Flask 3.0.0
- **Database**: SQLite with SQLAlchemy 2.0.45
- **Authentication**: Flask-JWT-Extended 4.5.3
- **Security**: Flask-Bcrypt 1.0.1 for password hashing
- **CORS**: Flask-CORS 4.0.0
- **Testing**: pytest with comprehensive test coverage

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript with full type safety
- **Styling**: Tailwind CSS with shadcn/ui components
- **UI Library**: Radix UI primitives with custom styling
- **Icons**: Lucide React
- **State Management**: React hooks and context

### Development Tools
- **Package Management**: npm (frontend), pip (backend)
- **Version Control**: Git
- **Code Quality**: ESLint, TypeScript strict mode

## 🔗 API Overview

The platform provides a comprehensive REST API with 21+ endpoints covering:

- **Authentication**: JWT-based login/registration with role management
- **Studies**: Full CRUD operations with application management
- **Matching**: AI-powered participant-study compatibility scoring
- **Messages**: Real-time messaging between researchers and participants
- **Profiles**: Comprehensive user profile management

For complete API documentation including request/response formats, see [API_ROUTES.md](API_ROUTES.md).

## 👥 Development Team

This project was developed by a team of 6 specialists:

- **MESFER** - Project Manager + Design (Admin)
- **YAMI** - Frontend Researcher (Researcher APIs)
- **ALI** - Backend Researcher (API Management)
- **Ghazi** - Frontend Recruiter (Participant APIs)
- **Saud** - Backend Recruiter (Matching Algorithms)
- **Sultan** - Database + Tester (Admin Tools)

For detailed information about each team member's contributions and implemented features, see [TEAM_TASKS.md](TEAM_TASKS.md).

## 🛡️ Security & Quality

- **Authentication**: JWT-based with secure password hashing
- **Authorization**: Role-based access control (Researcher/Participant)
- **Data Protection**: SQL injection prevention through ORM
- **Input Validation**: Comprehensive request validation and sanitization
- **Testing**: Complete test coverage with pytest for backend functionality
- **Responsive**: Mobile-first design with accessibility features
## 📚 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Complete setup and installation guide
- **[RUNNING.md](RUNNING.md)** - Running, testing, and development instructions
- **[API_ROUTES.md](API_ROUTES.md)** - Comprehensive API documentation
- **[TEAM_TASKS.md](TEAM_TASKS.md)** - Team contributions and implementation details



## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the API documentation

---
