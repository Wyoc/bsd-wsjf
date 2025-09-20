# WSJF Excel Generator

A full-stack web application that generates Excel files for WSJF (Weighted Shortest Job First) prioritization methodology used in Agile/SAFe frameworks.

## Project Structure

```
bsd-wsjf/
├── backend/          # Python FastAPI backend
├── frontend/         # TypeScript React frontend  
├── docs/             # Documentation
├── docker-compose.yml
├── Makefile
└── README.md
```

## Technology Stack

- **Backend**: Python 3.11+ with FastAPI framework
- **Frontend**: TypeScript 5+ with React 18
- **Database**: DuckDB
- **Excel Generation**: pandas + xlsxwriter
- **Build Tools**: Vite for frontend, uv for backend
- **Containerization**: Docker & Docker Compose

## Development

Use the Makefile for common development tasks:

```bash
make setup     # Initial project setup
make dev       # Start development environment
make test      # Run tests
make build     # Build for production
make clean     # Clean build artifacts
```

## WSJF Formula

```
WSJF Score = (Business Value + Time Criticality + Risk Reduction) / Job Size
```

Where each component is scored 1-10.