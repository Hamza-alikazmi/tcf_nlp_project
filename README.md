# TCF NLP Project

A comprehensive FastAPI-based web application for managing student affairs, complaints, and applications with NLP-powered intelligent complaint analysis and routing.

## About

TCF NLP Project is a full-featured student management system designed for educational institutions. It combines modern web technologies with natural language processing to intelligently categorize, prioritize, and analyze student complaints while managing registrations, fee applications, and scholarship programs.

## Features

### Complaint Management System
- **Intelligent Complaint Routing**: Automatically detects complaint departments (IT, HR, Admin, Fee) using NLP and keyword matching
- **Sentiment Analysis**: Analyzes complaint tone using VADER sentiment analysis
- **Priority Detection**: Automatically classifies complaints as HIGH, NORMAL, or LOW priority
- **Complaint Tracking**: Comprehensive tracking from submission to resolution with status updates
- **Similarity Matching**: Semantic search for similar complaints using sentence transformers

### Student Management
- **Student Registration**: Streamlined registration process for new students and alumni
- **Fee Applications**: Manage fee exemption/assistance applications with document uploads
- **Scholarship Management**: Track scholarship applications and approvals
- **Student Profiles**: Maintain comprehensive student records with contact information

### Access Control & Authentication
- **Role-Based Access**: Multiple user roles including Student, Alumni, Admin, Fee Staff, Scholarship Staff, and Super Admin
- **JWT Authentication**: Secure token-based authentication system
- **Password Security**: Bcrypt-based password hashing

### Web Dashboard
- **Admin Dashboard**: Manage users, view system logs, and monitor applications
- **Student Dashboard**: Access personal information and track applications
- **Alumni Dashboard**: Alumni-specific features and resources
- **Role-Specific Views**: Customized interfaces for different user roles

## Tech Stack

- **Backend**: FastAPI
- **Database**: MongoDB with MongoEngine ODM
- **Authentication**: JWT tokens
- **NLP/ML**: Sentence Transformers, Scikit-learn, VADER Sentiment Analysis
- **Frontend**: Jinja2 templating, HTML5, JavaScript
- **Container**: Docker & Docker Compose
- **Server**: Uvicorn

## Quick Start

### Prerequisites

- Python 3.8+
- MongoDB instance (local or cloud)
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Hamza-alikazmi/tcf_nlp_project.git
   cd tcf_nlp_project
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env  # If available
   ```
   Set required environment variables in `.env`:
   ```
   MONGO_URL=mongodb://localhost:27017  # or your MongoDB connection string
   ```

5. **Run the application**
   ```bash
   uvicorn app:app --reload
   ```
   Access the application at `http://localhost:8000`

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f
   ```

3. **Stop the application**
   ```bash
   docker-compose down
   ```

## Usage

### Web Interface

The application provides a web-based interface accessible at the root URL:
- **Public Pages**: Index, About, Contact, Guide
- **Authentication**: Login and signup pages
- **Dashboards**: Role-specific dashboards after authentication
- **Forms**: Fee applications, scholarship applications, student registration

### API Endpoints

The application exposes REST API endpoints for programmatic access. Access the interactive API documentation at `/docs` (Swagger UI) or `/redoc` (ReDoc) after starting the server.

### Example: Submitting a Complaint

```bash
curl -X POST http://localhost:8000/api/complaints \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The WiFi in the lab is not working",
    "contact": "user@example.com"
  }'
```

The system will automatically:
1. Detect the department (IT in this case)
2. Analyze sentiment
3. Determine priority level
4. Generate a unique complaint ID
5. Store in MongoDB

## Project Structure

```
tcf_nlp_project/
├── app.py                    # Main FastAPI application
├── database.py              # MongoDB connection management
├── models.py                # MongoDB document schemas and Pydantic models
├── database/                # Database files (SQLite backups)
├── static/                  # Static assets (CSS, JavaScript)
│   └── script.js           # Client-side scripts
├── templates/              # Jinja2 HTML templates
│   ├── index.html          # Home page
│   ├── login.html          # Login page
│   ├── dashboard.html      # Student dashboard
│   ├── admin-dashboard.html # Admin dashboard
│   ├── fee-form.html       # Fee application form
│   ├── scholarship-form.html # Scholarship application form
│   └── ...
├── uploads/                # User uploaded files
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker image configuration
├── docker-compose.yml      # Docker Compose orchestration
└── .env                    # Environment variables (not in repo)
```

## Configuration

### Environment Variables

Create a `.env` file in the project root with:

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017

# JWT Security (change in production)
SECRET_KEY=TCF_SUPER_SECRET_KEY_2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Database Models

The application supports the following main entities:

- **User**: Users with roles (student, alumni, admin, etc.)
- **Complaint**: Complaint records with NLP analysis
- **StudentRegistration**: Student profile and registration data
- **FeeApplication**: Fee assistance/exemption applications
- **ScholarshipApplication**: Scholarship application records
- **QueryTicket**: Help desk ticket system

## Key Features Explained

### Smart Complaint Analysis

The system uses a multi-layered approach for complaint understanding:

1. **Department Detection**: Keyword matching + semantic similarity using embeddings
2. **Sentiment Analysis**: VADER sentiment analyzer to understand tone
3. **Priority Classification**: Based on keywords and sentiment scores
4. **Complaint Matching**: Finds similar complaints for categorization

### Role-Based Access Control

Different user roles have different capabilities:

- **Student**: Submit complaints, apply for fees/scholarships, view own data
- **Alumni**: Access alumni-specific features and resources
- **Admin**: Full system access, user management
- **Fee Staff**: Manage fee applications and approvals
- **Scholarship Staff**: Handle scholarship applications
- **Super Admin**: System administration and configuration

## Development

### Running Tests

```bash
pytest tests/
```

### Code Structure

- **API Routes**: Defined directly in `app.py`
- **Database Layer**: `database.py` and `models.py`
- **Frontend**: Jinja2 templates in `templates/` with JavaScript in `static/`

### Adding New Features

1. Define MongoDB models in `models.py`
2. Create API endpoints in `app.py`
3. Add corresponding HTML templates in `templates/`
4. Add any client-side logic to `static/script.js`

## Troubleshooting

### MongoDB Connection Issues

```
Error: MONGO_URL is not set in the environment variables
```
**Solution**: Ensure `MONGO_URL` is set in `.env` and MongoDB is running.

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### Missing Dependencies

```bash
pip install --upgrade -r requirements.txt
```

## Support & Documentation

### Getting Help

- **Documentation**: Check the `templates/guide.html` for user guides
- **Issues**: Report issues on [GitHub Issues](https://github.com/Hamza-alikazmi/tcf_nlp_project/issues)
- **Contact**: Use the Contact form in the application

### API Documentation

- **Swagger UI**: Available at `/docs` after starting the server
- **ReDoc**: Available at `/redoc` after starting the server

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For detailed contribution guidelines, see the [CONTRIBUTING](CONTRIBUTING.md) file (if available).

## Maintainers

**Hamza Alikazmi** - Project Creator and Maintainer

For more information, visit [GitHub Profile](https://github.com/Hamza-alikazmi)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG](CHANGELOG.md) for version history and updates.

---

## Quick Reference

### Common Commands

```bash
# Start development server
uvicorn app:app --reload

# Access Swagger UI
http://localhost:8000/docs

# Run with Docker
docker-compose up

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

### Useful Links

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc
- **MongoDB Compass**: For database administration
- **GitHub Repository**: https://github.com/Hamza-alikazmi/tcf_nlp_project

---

For questions or issues, please open an issue on GitHub or contact the maintainers.
