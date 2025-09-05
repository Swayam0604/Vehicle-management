# 🚗 Vehicle Management System

A comprehensive Django-based Vehicle Management System with **role-based access control**, **OTP email verification**, and **extensive testing**.

-----

## 🌐 **Live Demo**

**🔗 Live Application**: [https://swayam0604.pythonanywhere.com](https://swayam0604.pythonanywhere.com)

**Test the application with different user roles:**
- Register as SuperAdmin/Admin/User to experience role-based access
- Complete OTP email verification process
- Explore CRUD operations based on your role permissions

-----

## 🔹 **Features**

### **Vehicle Management**

  - **CRUD Operations** for Vehicles with fields:
      - Vehicle Number (Alpha-numeric, unique)
      - Vehicle Type (Two, Three, Four wheelers)
      - Vehicle Model
      - Vehicle Description
      - Timestamps (created\_at, updated\_at)

### **User Management & Authentication**

  - **Custom User Model** with role-based permissions
  - **OTP Email Verification** for account activation
  - **Dual Login System** - Username or Email
  - **Role-Based Access Control**:
      - **SuperAdmin** → Full CRUD access (Create, Read, Update, Delete)
      - **Admin** → Edit + View access (Read, Update)
      - **User** → View only access (Read)

### **Security & UI**

  - **Email OTP verification** for secure registration
  - **Session-based authentication**
  - **Bootstrap 5** responsive UI
  - **Role-based template rendering**
  - **Custom permission messages**

-----

## ⚙️ **Tech Stack**

  - **Backend**: Python 3.x, Django 5.x
  - **Database**: SQLite (development/production)
  - **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
  - **Deployment**: PythonAnywhere
  - **Testing**: Django TestCase, OOP-based testing
  - **Email**: Django SMTP backend
  - **Version Control**: Git

-----

## 🚀 **Setup Instructions**

### **1. Clone and Setup Environment**

```bash
git clone https://github.com/Swayam0604/Vehicle-management.git
cd vehicle_mgmt
python -m venv vehicle_mgmt_env
source vehicle_mgmt_env/bin/activate # On Windows: vehicle_mgmt_env\Scripts\activate
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Configure Email Settings**

Update `settings.py` with your email configuration:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email@gmail.com'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

### **4. Database Setup**

```bash
python manage.py makemigrations
python manage.py migrate
```

### **5. Create SuperUser (Optional)**

```bash
python manage.py createsuperuser
```

### **6. Run Development Server**

```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

-----

## 🌍 **Deployment**

### **Live Deployment on PythonAnywhere**

The application is successfully deployed on PythonAnywhere with the following configuration:

### **Deployment Steps:**
1. **Upload project files** to PythonAnywhere
2. **Setup virtual environment** and install dependencies
3. **Configure static files mapping**:
   - URL: `/static/`
   - Directory: `/home/Swayam0604/vehicle_mgmt/vehicle_mgmt/staticfiles/`
4. **Run database migrations**: `python manage.py migrate`
5. **Collect static files**: `python manage.py collectstatic`
6. **Configure WSGI file** for Django application
7. **Set up email backend** for OTP verification

### **Production Settings:**
- **Static Files**: Served via PythonAnywhere's static file mapping
- **Database**: SQLite database for simplicity
- **Email Service**: Gmail SMTP for OTP delivery
- **Security**: CSRF protection and secure session management

### **Access the Live Application:**
Visit [https://swayam0604.pythonanywhere.com](https://swayam0604.pythonanywhere.com) to interact with the deployed vehicle management system.

-----

## 📂 **Project Structure**

```
vehicle_mgmt/
├── manage.py
├── requirements.txt
├── README.md
├── static/css/styles.css # Custom styling
├── templates/pages/ # Global templates
│ ├── base.html
│ ├── home.html
│ └── about.html
├── users/ # Authentication app
│ ├── models.py # CustomUser model
│ ├── views.py # Auth views + OTP
│ ├── forms.py # Registration & Login forms
│ ├── tests.py # 24 comprehensive tests ✅
│ ├── templates/users/
│ │ ├── login.html
│ │ ├── register.html
│ │ └── verify_otp.html
│ └── urls.py
├── vehicles/ # Vehicle management app
│ ├── models.py # Vehicle model
│ ├── views.py # CRUD views with permissions
│ ├── forms.py # Vehicle form
│ ├── tests.py # 30 comprehensive tests ✅
│ ├── templates/vehicles/
│ │ ├── base.html
│ │ ├── list.html # Vehicle dashboard
│ │ ├── detail.html
│ │ ├── form.html
│ │ └── delete.html
│ └── urls.py
└── vehicle_mgmt/ # Main project
├── settings.py
├── urls.py
├── views.py # Home & About views
└── wsgi.py
```

-----

## 🧪 **Testing Strategy**

### **Comprehensive Test Suite**
- **40 Tests Total** using **Object-Oriented Programming** principles
- **Users App**: Authentication, registration, OTP verification, role management
- **Vehicles App**: CRUD operations, role-based permissions, model validation
- **Full Coverage**: Models, views, forms, permissions, and security features

### **Test Categories**
- **Model Testing**: CustomUser roles, Vehicle constraints, field validation
- **Authentication Flows**: Register → OTP → Login → Logout workflows
- **Permission Testing**: Role-based access control (SuperAdmin/Admin/User)
- **Form Validation**: Registration forms, login forms, vehicle forms
- **Security Testing**: OTP verification, inactive user handling, CSRF protection

### **Run Tests**

```bash
# Run all tests
python manage.py test --verbosity=2

# Run specific app tests
python manage.py test users
python manage.py test vehicles
```

-----

## 👥 **User Roles & Permissions**

| Role           | Vehicle List | Vehicle Detail | Add Vehicle | Edit Vehicle | Delete Vehicle |
|----------------|--------------|----------------|-------------|--------------|----------------|
| **SuperAdmin** |      ✅     |       ✅       |      ✅     |     ✅      |       ✅      |
| **Admin**      |      ✅     |       ✅       |      ❌     |     ✅      |       ❌      |
| **User**       |      ✅     |       ✅       |      ❌     |     ❌      |       ❌      |

-----

## 📖 **Usage Workflow**

### **For New Users**

1.  **Register** → Enter username, email, role, password
2.  **Email Verification** → Receive OTP via email
3.  **Activate Account** → Enter 6-digit OTP
4.  **Login** → Use username/email + password
5.  **Access Dashboard** → View vehicles based on role

### **For SuperAdmins**

  - Full vehicle management capabilities
  - Add new vehicles with all details
  - Edit existing vehicle information
  - Delete vehicles from system
  - View comprehensive vehicle statistics

### **For Admins**

  - View and edit existing vehicles
  - Cannot add or delete vehicles
  - Access to vehicle details and modifications

### **For Users**

  - View-only access to vehicle list
  - Browse vehicle details
  - Search and filter capabilities

-----

## 🔐 **Security Features**

  - **OTP Email Verification** with attempt limiting
  - **Role-based access control** at view level
  - **Session management** with automatic timeouts
  - **CSRF protection** on all forms
  - **Input validation** and sanitization
  - **Custom error messages** for better UX

-----

## 📊 **Key Features Implemented**

✅ **Complete CRUD** with role restrictions
✅ **Email OTP verification** system
✅ **Dual login** (username or email)
✅ **Role-based UI** rendering
✅ **Responsive design** with Bootstrap
✅ **Comprehensive testing** (54+ tests)
✅ **SQLite database** integration
✅ **Custom user model** with roles
✅ **Object-oriented** code architecture
✅ **Production deployment** on PythonAnywhere

-----

## 🛠️ **Development**

### **Adding New Features**

1.  Create feature branch
2.  Write tests first (TDD approach)
3.  Implement functionality
4.  Run test suite
5.  Update documentation

### **Database Schema**

  - **CustomUser**: Extends Django's User with role field
  - **Vehicle**: Core vehicle entity with type constraints
  - **Relationships**: User-agnostic vehicle management

-----

## 📝 **License**

This project is developed for educational purposes as part of a Django development assessment.

-----

## 🤝 **Contributing**

1.  Fork the repository
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

-----

**📧 Contact**: [Your Email]
**🔗 Repository**: [https://github.com/Swayam0604/Vehicle-management.git](https://github.com/Swayam0604/Vehicle-management.git)
**🌐 Live Demo**: [https://swayam0604.pythonanywhere.com](https://swayam0604.pythonanywhere.com)

-----

### **`requirements.txt`**

```
Django>=5.0,<6.0
sqlparse>=0.4.2
asgiref>=3.5,<4
pytz>=2021.1
```