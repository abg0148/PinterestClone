# Pinterest Clone

A full-featured Pinterest clone built with Flask and PostgreSQL, featuring a modern UI and comprehensive pin management system.

## Features

- **User Management**
  - User registration and authentication
  - Profile management with customizable avatars
  - Default board creation for new users

- **Board Management**
  - Create, edit, and delete boards
  - Public and friends-only comment settings
  - Soft deletion support for data integrity

- **Pin System**
  - Create pins with images (URL or file upload)
  - Repin functionality
  - Tag-based organization
  - Source page tracking
  - Comprehensive pin deletion handling (cascade to repins)

- **Social Features**
  - Follow boards through streams
  - Like and comment on pins
  - Friend system
  - Activity feed

- **UI/UX**
  - Modern, responsive design
  - Pinterest-style masonry layout
  - Intuitive navigation
  - Real-time feedback

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-Login
- **Image Storage**: File system / URL based

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd PinterestClone
   ```

2. **Set Up Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create PostgreSQL Database**
   ```bash
   createdb pinterest_clone_dev
   ```

5. **Generate Secret Key**
   ```python
   python -c "import secrets; print(secrets.token_hex(16))"
   ```

6. **Configure Environment**
   Create a `.env` file in the project root:
   ```bash
   FLASK_ENV=development
   SECRET_KEY=<generated-secret-key>
   DATABASE_URL=postgresql://<username>:<password>@localhost/pinterest_clone_dev
   ```

7. **Initialize Database**
   ```bash
   flask init-db
   ```

8. **Run the Application**
   ```bash
   flask run
   ```
   The application will be available at `http://localhost:5000`

## Project Structure

```
PinterestClone/
├── app/
│   ├── models/         # Database models
│   ├── routes/         # Route handlers
│   ├── templates/      # Jinja2 templates
│   ├── static/         # Static files (CSS, JS)
│   └── __init__.py     # App initialization
├── migrations/         # Database migrations
├── tests/             # Test suite
├── requirements.txt    # Project dependencies
└── README.md          # This file
```

## Version History

- **v3.0** - Current version with complete UI implementation and enhanced deletion logic
- **v2.0** - Added social features and improved board management
- **v1.0** - Initial release with basic pin and board functionality

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
