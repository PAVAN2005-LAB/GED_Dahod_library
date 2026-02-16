# 📚 GECDahod Library System

A modern, smart library management system for **GEC Dahod**, featuring automated student tracking, camera-based barcode scanning, and detailed reporting.

## ✨ Features

- **🚀 Smart Kiosk**: Fast check-in/check-out for students using real-time barcode scanning.
- **📷 Camera Scanning**: Built-in camera scanner (HTML5-QRCode) - no external hardware needed!
- **📊 Admin Dashboard**: Real-time view of students currently in the library.
- **📜 Detailed Reports**: Export entry/exit logs and book issue records to Excel.
- **📧 Automated Notifications**: Email reminders for overdue books (via APScheduler).
- **🔒 Secure Admin**: Advanced admin panel with custom branding and user management.
- **🌐 REST API**: JWT-authenticated API for mobile app integration.

## � File Structure

```text
library_mangement/
├── config/                 # Project configuration (settings, urls, wsgi)
├── management/             # Main application logic
│   ├── management/         # Custom management commands (initadmin)
│   ├── migrations/         # Database migrations
│   ├── models.py           # Database schema (Student, Book, Log, Transaction)
│   ├── views.py            # Kiosk and Dashboard logic
│   ├── report_views.py     # Excel/PDF report generation
│   ├── scheduler.py        # Background task configuration
│   └── api_views.py        # REST API endpoints
├── static/                 # Static assets
│   └── css/
│       └── style.css       # Custom premium styling
├── templates/              # HTML Templates
│   ├── admin/              # Custom admin & report templates
│   ├── management/         # Kiosk & Dashboard templates
│   └── base.html           # Master layout
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── .env.example            # Template for environment variables
```

## �🛠️ Tech Stack

- **Backend**: Django (Python)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Frontend**: Bootstrap 5, Font Awesome, Vanilla JS
- **Scanning**: HTML5-QRCode Library
- **Tasks**: Django APScheduler

## 🚀 Quick Start

### 1. Clone & Setup
```bash
# Clone the repository
git clone https://github.com/PAVAN2005-LAB/GED_Dahod_library.git
cd library_mangement

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```ini
DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Admin Setup
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=your_secure_password
DJANGO_SUPERUSER_EMAIL=admin@gecdahod.ac.in

# Email Client (Gmail example)
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### 3. Initialize Database
```bash
python manage.py migrate
python manage.py initadmin  # Custom command to sync .env admin to DB
```

### 4. Run Server
```bash
python manage.py runserver
```

## 🌍 Hosting Recommendations

To make this system live, you can host it on:

1. **PythonAnywhere** (Recommended for Beginners):
   - Very easy Django setup.
   - Provides a free tier (low traffic).
   - Good for small college projects.

2. **Railway / Render**:
   - Modern "Infrastructure as Code" platforms.
   - Fast deployments from GitHub.

3. **DigitalOcean / Linode**:
   - For high performance (VPS).
   - Requires setting up Nginx and Gunicorn.

## 🛠️ Developer & Support
Developed for **GECDahod Library System**. For technical support or contribution, contact the lead developer.

**Email:** pavan.yadav.sde@gmail.com | 230180107045@gecdahod.ac.in
