# Development Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Make (optional, for convenience commands)

## Quick Start

1. Clone the repository
2. Run initial setup:
   ```bash
   make setup
   ```
3. Start development environment:
   ```bash
   make dev
   ```

This will start both backend (http://localhost:8000) and frontend (http://localhost:3000) services.

## Development Workflow

### Backend Development

```bash
# Start backend only
make dev-backend

# Run tests
make test-backend

# Run linting
make lint-backend

# Install new dependencies
cd backend && uv add <package-name>
```

### Frontend Development

```bash
# Start frontend only
make dev-frontend

# Run tests
make test-frontend

# Run linting
make lint-frontend

# Install new dependencies
cd frontend && npm install <package-name>
```

## Project Structure

```
bsd-wsjf/
├── backend/
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration and utilities
│   │   ├── models/       # Data models
│   │   └── services/     # Business logic
│   ├── tests/            # Backend tests
│   └── pyproject.toml    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   ├── services/     # API clients
│   │   └── types/        # TypeScript types
│   └── package.json      # Node.js dependencies
└── docker-compose.yml    # Development containers
```

## Code Style

### Backend (Python)
- Use Black for formatting
- Use isort for import sorting
- Use flake8 for linting
- Use mypy for type checking
- Follow PEP 8 guidelines

### Frontend (TypeScript/React)
- Use ESLint for linting
- Use Prettier for formatting
- Follow React best practices
- Use functional components with hooks

## Testing

- Backend: pytest with async support
- Frontend: Vitest (when configured)
- Integration tests with Docker containers

## Environment Variables

Copy `.env.example` files and modify as needed:

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```