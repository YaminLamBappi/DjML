# Django ML Project

A Django-based machine learning project with a dynamic notification system and real-time updates.

## Features

- Real-time notification system
- Dynamic ML model training notifications
- Interactive fluid canvas background
- Responsive morphing grid layout
- Authentication and user-specific notifications

## Prerequisites

- Python 3.10+
- MySQL 5.7+
- pip (Python package installer)

## Setup

1. Clone the repository
```bash
git clone <your-repo-url>
cd django_ml
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Configure environment variables
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Set up local settings
```bash
cp django_ml/local_settings.example.py django_ml/local_settings.py
# Edit local_settings.py with your configuration
```

6. Set up the database
```bash
python manage.py migrate
```

7. Create a superuser (optional)
```bash
python manage.py createsuperuser
```

8. Run the development server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ to see the application.

## Development

### Project Structure

- `machine_learning/` - Main Django app
  - `static/` - Static files (CSS, JS)
  - `templates/` - HTML templates
  - `views.py` - View functions
  - `models.py` - Database models
  - `notification_utils.py` - Notification system utilities

### Working with Notifications

The project includes a dynamic notification system that:
- Generates ML training updates
- Provides real-time feedback
- Supports multiple notification types
- Handles user-specific and global notifications

### Static Files

Static files are served from `machine_learning/static/`. During development, ensure:
1. DEBUG is True for static file serving
2. Run `python manage.py collectstatic` if needed
3. Use {% static %} template tag for static file URLs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.