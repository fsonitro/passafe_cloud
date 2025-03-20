# PasSafe - Secure Password Manager

<p align="center">
  <img src="passafe/static/images/passafe_fav.png" width="150" alt="PasSafe Logo">
</p>

PasSafe is a secure, open-source password manager application built with Django that helps users store, manage, and generate strong passwords with military-grade encryption.

## Features

### Core Functionality
- **Secure Password Storage**: Store passwords using AES-256 bit encryption
- **Password Generator**: Create strong, customizable passwords
- **Folder Organization**: Organize passwords into folders for better management
- **Search**: Quickly find entries across your vault
- **Copy to Clipboard**: Easily copy usernames and passwords to clipboard

### Security Features
- **Military-Grade Encryption**: AES-256 encryption for all sensitive data
- **Two-Factor Authentication**: Additional security with TOTP-based MFA
- **Secure PIN**: Requires a PIN alongside password for vault access
- **Auto-Lock**: Automatically locks the vault after period of inactivity
- **Session Management**: Monitor login activity across devices

### User Experience
- **Responsive Design**: Works on desktop and mobile devices
- **Dark/Light Theme**: Choose your preferred visual theme
- **Dashboard Overview**: Get insights into your password security
- **Password Health Check**: Identify weak or reused passwords

## Technologies Used

- **Backend**: Django 5.1+, Python 3.11+
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Security**: PyOTP (for 2FA), AES-256 encryption

## Installation

### Prerequisites
- Python 3.11 or higher
- PostgreSQL
- pip

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/passafe.git
   cd passafe
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure the database**
   - Create a PostgreSQL database
   - Update database settings in `passafe/settings.py`

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and navigate to `http://localhost:8000`

## Usage

### Registration & Login
1. Create an account with your email, password, and secure PIN
2. Enable Two-Factor Authentication for enhanced security
3. Log in using your credentials and PIN

### Managing Passwords
1. Create folders to organize your passwords
2. Add new password entries with usernames, passwords, and associated websites
3. Use the built-in password generator to create strong passwords
4. Search for passwords using the search bar
5. View or copy passwords as needed

### Security Best Practices
1. Use a strong master password and PIN
2. Enable Two-Factor Authentication
3. Regularly check your account activity
4. Export your vault periodically for backup

## Security Architecture

PasSafe employs a multi-layered security approach:

1. **Authentication Layer**:
   - Username/password authentication
   - Secure 8-digit PIN
   - Optional TOTP-based Two-Factor Authentication

2. **Encryption Layer**:
   - AES-256 bit encryption for all sensitive data
   - Encryption keys derived using PBKDF2 with high iteration counts
   - Unique salt for each user

3. **Session Security**:
   - Secure session storage
   - Session timeout for inactivity
   - Login activity monitoring

## Development

### Project Structure
```
passafe/
├── accounts/          # User authentication and account management
├── hub/               # Dashboard and main interface
├── password_vault/    # Password storage and management
├── password_generator/ # Password generation utilities
├── search/            # Search functionality
├── static/            # Static assets (CSS, JS, images)
├── templates/         # Base HTML templates
└── passafe/           # Project settings and configuration
```

## Acknowledgements

- [Django](https://www.djangoproject.com/) - The web framework used
- [Bootstrap](https://getbootstrap.com/) - Frontend component library
- [Font Awesome](https://fontawesome.com/) - Icons used throughout the application
