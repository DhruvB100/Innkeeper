# Innkeeper - Federated Social Platform

A federated social media platform where multiple independent servers (nodes) can connect and share content with each other.

## What is this?

Innkeeper lets users on different servers communicate with each other, similar to how email works across different providers. Each "node" is an independent server, but users can follow people on other nodes and see their posts.

## Tech Stack

- **Backend**: Django, Django REST Framework, PostgreSQL
- **Frontend**: React.js
- **Auth**: JWT tokens
- **Testing**: Postman, Selenium
- **CI/CD**: GitHub Actions
- **Deployment**: Heroku

## Setup

### Backend

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (copy .env.example to .env):
```bash
cp .env.example .env
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the server:
```bash
python manage.py runserver
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the dev server:
```bash
npm start
```

## API Endpoints

- `POST /api/auth/login/` - Login and get JWT token
- `POST /api/auth/register/` - Create new account
- `GET /api/posts/` - Get all posts
- `POST /api/posts/` - Create a post
- `GET /api/posts/<id>/` - Get a specific post
- `POST /api/posts/<id>/like/` - Like/unlike a post
- `GET /api/authors/` - Get all authors
- `POST /api/authors/<id>/follow/` - Follow an author
- `GET /api/inbox/` - Get inbox (for federation)
- `POST /api/inbox/` - Send to inbox (for federation)

## Federation

The federation system works using an inbox/outbox pattern. When a user creates a post, it goes to their outbox. Remote nodes can pull from the outbox, or we push posts to remote users' inboxes.

## Notes

This was built as a group project for CMPUT 404. There are probably some rough edges but the core functionality works.
