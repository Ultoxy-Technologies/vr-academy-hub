# 📘 VR ACADEMY HUB — Developer Handover & System Reference Guide

> **Official Repository**: `https://github.com/Ultoxy-Technologies/vr-academy-hub.git`  
> **Production Server IP**: `72.60.96.41`  
> **Production Domains**: https://vracademyhub.com | https://www.vracademyhub.com  
> **Primary Timezone**: `Asia/Kolkata` (IST - UTC+5:30)  
> **Target Python Version**: `Python 3.12+ / 3.14` | **Django Version**: `6.0.1`  
> **Target Flutter Version**: `Flutter 3.x / Dart 3.x`

---

## 📑 Table of Contents
1. [System Architecture & Monorepo Structure](#1-system-architecture--monorepo-structure)
2. [Server & Network Configuration](#2-server--network-configuration)
3. [Credentials & Integrations Reference](#3-credentials--integrations-reference)
4. [Backend Applications & Model Architecture](#4-backend-applications--model-architecture)
5. [Frontend (Flutter CRM Mobile & Desktop)](#5-frontend-flutter-crm-mobile--desktop)
6. [Security, Auth & Anti-Bot Systems](#6-security-auth--anti-bot-systems)
7. [Developer Command Cheat Sheet](#7-developer-command-cheat-sheet)
8. [Production Deployment, Nginx & Gunicorn Guide](#8-production-deployment-nginx--gunicorn-guide)
9. [Important Development Directives & Rules](#9-important-development-directives--rules)

---

## 1. System Architecture & Monorepo Structure

The repository is organized into a full-stack monorepo containing the Django Backend web ecosystem and the Flutter Mobile/Desktop CRM application:

```
vr-academy-hub/
├── BackEnd/                             # Django Backend Platform
│   ├── AdminApp/                        # Core User, Authentication, Course & Enquiry Models
│   ├── SoftwareApp/                     # CRM Leads, Pipeline, Batches, Enrollment & Receipts
│   ├── StudentApp/                      # Student Dashboard, Course Access & Progress
│   ├── WebApp/                          # Public Website, Event Registration, OTP & Enquiry Form
│   ├── VRACADEMYHUB/                    # Project Settings & Root Routing
│   │   ├── settings/
│   │   │   ├── base.py                  # Shared settings (Apps, Middleware, Jazzmin, JWT, CORS)
│   │   │   ├── development.py           # Local debug settings
│   │   │   └── production.py            # Live server settings (SSL, Host headers, Logging)
│   │   ├── urls.py                      # Master URL dispatcher with i18n support
│   │   ├── wsgi.py                      # WSGI configuration for Gunicorn
│   │   └── asgi.py                      # ASGI configuration
│   ├── locale/                          # Internationalization translations (en, hi, mr)
│   ├── media/                           # User-uploaded content (thumbnails, certificates, videos)
│   ├── static/                          # Compiled stylesheets, branding, scripts, vendors
│   ├── db.sqlite3                       # Primary Database (Live Production Data)
│   ├── info.log                         # Centralized Application Error Logger
│   ├── manage.py                        # Django CLI utility
│   └── requirements.txt                 # Backend Python package dependencies
│
├── Front End/
│   └── vr_academy_crm/                  # Flutter CRM Cross-Platform Application
│       ├── lib/
│       │   ├── core/                    # API clients, Theme, Design System, Constants, Storage
│       │   ├── data/                    # Models & Repositories (Auth, Followups, Stats, Users)
│       │   ├── providers/               # State Management (AuthProvider, FollowupProvider)
│       │   ├── ui/                      # Material 3 Screens (Auth, Pipeline, Enquiries, Profile)
│       │   └── main.dart                # App Entry Point
│       └── pubspec.yaml                 # Flutter dependencies & assets
│
└── DEVELOPER_HANDOVER.md                # Handover reference file
```

---

## 2. Server & Network Configuration

### 🌐 IP Addresses & Host Names

| Environment | Host / IP Address | Base URL | Port |
| :--- | :--- | :--- | :--- |
| **Production Server** | `72.60.96.41` | `https://vracademyhub.com` | `80 / 443` |
| **Production Alternative** | `72.60.96.41` | `https://www.vracademyhub.com` | `80 / 443` |
| **Local Development** | `127.0.0.1` / `localhost` | `http://127.0.0.1:8000/` | `8000` |
| **Local Network / Dev** | `0.0.0.0` | `http://<YOUR_LOCAL_IP>:8000/` | `8000` |
| **Android Emulator Loopback** | `10.0.2.2` | `http://10.0.2.2:8000/api/` | `8000` |

### 📂 Server Filesystem Paths (Ubuntu / Linux)

| Resource | Path on Server |
| :--- | :--- |
| **Project Root** | `/var/www/vracademyhub` (or deployment directory) |
| **Static Root (`STATIC_ROOT`)** | `/var/www/vracademyhub_static` |
| **Media Root (`MEDIA_ROOT`)** | `/var/www/vracademyhub_media` |
| **Error Log File** | `<PROJECT_DIR>/BackEnd/info.log` |
| **Database File** | `<PROJECT_DIR>/BackEnd/db.sqlite3` |

---

## 3. Credentials & Integrations Reference

### 📧 SMTP Email Configuration (Google Workspace / Gmail)

The backend sends password reset OTPs, registration receipts, and enquiry notifications through Gmail SMTP:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'prameshwar4378@gmail.com'
EMAIL_HOST_PASSWORD = 'rxfv klps utdv tiro'   # Google 16-character App Password
DEFAULT_FROM_EMAIL = 'VR Academy Hub <prameshwar4378@gmail.com>'
SERVER_EMAIL = 'prameshwar4378@gmail.com'
```

### 💳 Razorpay Payment Gateway

Used for event registrations and course fee collections:

```python
# Live Production Credentials
RAZORPAY_KEY_ID = 'rzp_live_S0GtEF2P4Jr7SY'
RAZORPAY_KEY_SECRET = 'RLFz6G1j9CgStlwKDFyBIqPK'
```

### 🏢 Academy Contact & Branch Directory

- **Primary Support / Contact**: `+91 99703 60424` | `+91 98606 59538` | `+91 90224 25739`
- **Official Email**: `vrtrainingacademy1123@gmail.com`
- **Branch 1 (Shirdi)**: Airport Rd, near Kimaya Garden, Shirdi, Maharashtra 423109
- **Branch 2 (Chakan)**: The Grand Center, UG-18, Pune Nashik Highway, Chakan
- **Branch 3 (Puntambe)**: Kopargaon Shrirampur Road, Puntambe, Maharashtra 413723

---

## 4. Backend Applications & Model Architecture

### 🔑 Authentication (`AdminApp.CustomUser`)
- **Important**: The custom user model uses `mobile_number` as the `USERNAME_FIELD` (not standard username).
- **Required Fields**: `name`, `email`, `mobile_number`.
- **Roles (`role` field)**:
  - `is_crm_manager`: Access to CRM Lead Pipeline and Follow-up modules.
  - `is_enrollment`: Access to Student Enrollment, Receipts, and Batches.
  - `is_crm_and_enrollment`: Combined access across CRM & Enrollment software.
  - `is_student`: Student Learning Portal & Dashboard.
  - `is_superuser`: Full Django administration.

### 📋 CRM & Leads (`SoftwareApp.CRMFollowup`)
- Tracks leads with status (`interested`, `planning`, `under_review`, `on_hold`, `class_joined`, `class_completed`, `not_interested`), priority (`high`, `medium`, `low`), and call responses.
- Supports debounced AJAX auto-suggestions via `/software/followups/suggestions/?q=`.

### 🛡️ Website Inquiries (`AdminApp.Enquiry`)
- Captures inquiries from the public website with full anti-bot protection.
- Includes `is_added_in_CRMFollowup_model` flag allowing one-click transfer into the CRM pipeline.

### 🎓 Courses & Events
- `Basic_to_Advance_Cource` & `Advance_to_Pro_Cource`: Main training course offerings.
- `FreeCourse` & `FreeCourseProgress`: Free modular courses with video tracking and certificates.
- `Event` & `EventRegistration`: Webinars, live workshops, and paid event admissions.

---

## 5. Frontend (Flutter CRM Mobile & Desktop)

The `Front End/vr_academy_crm` application provides a cross-platform Flutter experience for sales and management staff:

- **State Management**: Provider-based architecture (`AuthProvider`, `FollowupProvider`).
- **Dynamic Endpoints**: Supports on-the-fly Base URL switching in settings (`Production 72.60.96.41`, `Localhost 127.0.0.1`, `Emulator 10.0.2.2`).
- **Security**: Access and refresh tokens stored via secure storage / shared preferences.
- **Dynamic Choices**: Automatically fetches and caches backend choices for status, priority, and source fields without hardcoding.

---

## 6. Security, Auth & Anti-Bot Systems

### 1. Dynamic Arithmetic CAPTCHA on Inquiries
- **Implementation**: Located in `WebApp/views.py` (`generate_captcha`, `refresh_enquiry_captcha`).
- **Mechanism**: The backend dynamically generates random arithmetic challenges (`+`, `-`, `×`), stores the expected answer in `request.session['enquiry_captcha_answer']`, and verifies it on POST.
- **AJAX Refresh**: Users can click the **Refresh (🔄)** button to call `/captcha/refresh/` for a new question without page reloads.
- **Form Data Preservation**: If an invalid answer is provided, previous field values (`name`, `phone`, `email`, `message`) are preserved so the user does not re-type.

### 2. Honeypot Bot Trap
- **Implementation**: A hidden input `<input type="text" name="hp_check" style="display:none !important;" tabindex="-1">` is rendered on public forms.
- **Mechanism**: Automated spam bots fill all form fields indiscriminately; if `hp_check` contains any value, the submission is rejected immediately.

### 3. Password Reset Flow (OTP Based)
- **Flow**: User requests reset at `/forgot-password/` by providing Email or Mobile Number.
- **Delivery**: A 6-digit numeric OTP is generated and delivered to the registered email in the background.
- **Validity**: 15 minutes.
- **Completion**: On successful reset, user is redirected to `/login/?mobile=<mobile_number>` where their login mobile username is displayed and pre-filled in the form.

---

## 7. Developer Command Cheat Sheet

### 🐍 Python & Django Backend Commands

```bash
# 1. Navigate to the BackEnd directory
cd BackEnd

# 2. Install required Python packages
pip install -r requirements.txt

# 3. Run system health check
python manage.py check

# 4. Run migrations (Preserves existing SQLite production data)
python manage.py migrate

# 5. Compile multi-language translation catalogs
python manage.py compilemessages

# 6. Collect static files (For production deployment)
python manage.py collectstatic --noinput

# 7. Start local development server
python manage.py runserver 0.0.0.0:8000

# 8. Test production settings locally
python manage.py runserver --settings=VRACADEMYHUB.settings.production
```

### 📱 Flutter CRM Commands

```bash
# 1. Navigate to Flutter project directory
cd "Front End\vr_academy_crm"

# 2. Get dependencies
flutter pub get

# 3. Run static analyzer (Must pass with 0 issues)
flutter analyze

# 4. Run on Chrome (Web)
flutter run -d chrome

# 5. Run on connected Android device / Emulator
flutter run -d android

# 6. Build Release APK
flutter build apk --release
```

### 🐙 Git Version Control Commands

```bash
# Check status
git status

# Stage changes
git add .

# Commit with a descriptive message
git commit -m "Your commit message"

# Push to GitHub repository (main branch)
git push origin main

# Pull latest updates from remote
git pull origin main
```

---

## 8. Production Deployment, Nginx & Gunicorn Guide

### 1. Gunicorn Systemd Service (`/etc/systemd/system/vracademyhub.service`)

```ini
[Unit]
Description=Gunicorn daemon for VR Academy Hub
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/vracademyhub/BackEnd
Environment="DJANGO_SETTINGS_MODULE=VRACADEMYHUB.settings.production"
ExecStart=/var/www/vracademyhub/BackEnd/venv/bin/gunicorn \
          --workers 3 \
          --bind 127.0.0.1:8000 \
          --timeout 120 \
          VRACADEMYHUB.wsgi:application

[Install]
WantedBy=multi-user.target
```

### 2. Nginx Server Block Configuration (`/etc/nginx/sites-available/vracademyhub`)

```nginx
server {
    listen 80;
    server_name vracademyhub.com www.vracademyhub.com 72.60.96.41;

    client_max_body_size 100M;

    # Static files
    location /static/ {
        alias /var/www/vracademyhub_static/;
        expires 30d;
        access_log off;
    }

    # Media files (User uploads)
    location /media/ {
        alias /var/www/vracademyhub_media/;
        expires 30d;
        access_log off;
    }

    # Proxy all dynamic requests to Django Gunicorn
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Useful Server Management Commands

```bash
# Reload & restart Gunicorn
sudo systemctl daemon-reload
sudo systemctl restart vracademyhub
sudo systemctl status vracademyhub

# Test & reload Nginx
sudo nginx -t
sudo systemctl reload nginx

# Check live application error logs
tail -f /var/www/vracademyhub/BackEnd/info.log

# Renew SSL Certificate (Let's Encrypt)
sudo certbot --nginx -d vracademyhub.com -d www.vracademyhub.com
```

---

## 9. Important Development Directives & Rules

1. **Production SQLite Integrity**:
   - `BackEnd/db.sqlite3` contains **live production data**. Never delete or run destructive operations without creating a timestamped backup first:
     ```bash
     cp db.sqlite3 "db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
     ```
2. **Dynamic Configuration Architecture**:
   - Avoid hardcoded values in templates, views, or Flutter screens. Always use settings variables, choices endpoints, or database lookups.
3. **User Authentication Key**:
   - `CustomUser` does **not** have a `username` field. Always refer to `mobile_number` for authentication, user lookups, and admin ordering.
4. **Email Background Threading**:
   - Always dispatch SMTP emails asynchronously (`threading.Thread(target=..., daemon=True).start()`) to prevent blocking HTTP request/response lifecycles.
5. **Code Verification Standard**:
   - Before pushing code, always verify:
     1. `python manage.py check` -> 0 issues.
     2. `flutter analyze` -> 0 errors, 0 warnings.
