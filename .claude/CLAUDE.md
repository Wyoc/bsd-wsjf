
# CLAUDE.md - WSJF Excel Generator Project Specification

## Executive Summary

Create a full-stack web application that generates Excel files for WSJF (Weighted Shortest Job First) prioritization methodology used in Agile/SAFe frameworks. The application allows teams to manage, prioritize, and export functional subjects for Program Increments.

## Key Definitions

### WSJF (Weighted Shortest Job First)
A prioritization model used in SAFe (Scaled Agile Framework) that calculates priority using the formula:
```
WSJF Score = (Business Value + Time Criticality + Risk Reduction) / Job Size
```

### Components
- **Business Value**: Economic value delivered to the business (1-10 scale)
- **Time Criticality**: Urgency and time sensitivity of the feature (1-10 scale)
- **Risk Reduction**: Mitigation of risks or opportunity enablement (1-10 scale)
- **Job Size**: Effort required to complete the work (1-10 scale)
- **Program Increment (PI)**: Fixed timebox for planning, building, and validating (e.g., PI18)

## Project Phases

### Phase 1: Project Initialization and Architecture
**Objective**: Set up project foundation and define technical architecture

#### Step 1.1: Define Project Structure
- Create root project directory
- Establish backend/frontend separation
- Define configuration management approach
- Set up version control (git)

#### Step 1.2: Technology Stack Selection
- **Backend**: Python 3.11+ with FastAPI framework
- **Frontend**: TypeScript 5+ with React 18
- **Database**:  Duckdb
- **Excel Generation**: pandas + xlsxwriter
- **Build Tools**: Vite for frontend, uv for backend
- **Containerization**: Docker & Docker Compose
- **Makefile**: All the relevant commende should run with a makefile

#### Step 1.3: Development Environment Setup
- Configure IDE/editor settings
- Set up linting and formatting rules
- Establish coding standards
- Create development documentation

### Phase 2: Backend Development
**Objective**: Build RESTful API with Excel generation capabilities

#### Step 2.1: API Design
- Design REST endpoints structure
- Define request/response schemas
- Plan error handling strategy
- Document API specifications (OpenAPI/Swagger)

#### Step 2.2: Data Model Implementation
- Create WSJF item model with validation rules
- Implement status enumeration (New, In Progress, Blocked, Completed, Cancelled)
- Define batch operations model
- Add calculation methods for WSJF scoring

#### Step 2.3: Core Functionality
- CRUD operations for WSJF items
- WSJF score calculation engine
- Priority ranking algorithm
- Batch import/export capabilities

#### Step 2.4: Excel Generation Module
- Excel file creation with xlsxwriter
- Formatting and styling implementation
- Data validation rules
- Conditional formatting for high-priority items
- Formula integration for dynamic calculations

#### Step 2.5: API Endpoints Implementation
Required endpoints:
- `GET /api/items` - Retrieve all WSJF items
- `POST /api/items` - Create new item
- `PUT /api/items/{id}` - Update existing item
- `DELETE /api/items/{id}` - Remove item
- `POST /api/items/batch` - Bulk create items
- `GET /api/export/excel` - Generate and download Excel file
- `GET /api/sample-data` - Generate demo data

### Phase 3: Frontend Development
**Objective**: Build responsive TypeScript/React user interface

#### Step 3.1: Project Setup
- Initialize React project with Vite
- Configure TypeScript settings
- Set up Tailwind CSS for styling
- Install required dependencies

#### Step 3.2: Type System Design
- Create TypeScript interfaces for WSJF items
- Define enumerations for status values
- Type API responses and requests
- Implement strict type checking

#### Step 3.3: Component Architecture
Core components to develop:
- **WSJFForm**: Item creation/editing form with validation
- **WSJFTable**: Data grid with sorting and filtering
- **ExportButton**: Excel download functionality
- **ScoreCalculator**: Real-time WSJF score display
- **StatusBadge**: Visual status indicators

#### Step 3.4: State Management
- Implement React hooks for local state
- Create custom hooks for data fetching
- Handle loading and error states
- Implement optimistic UI updates

#### Step 3.5: API Integration Layer
- Create axios-based API client
- Implement error handling and retry logic
- Add request/response interceptors
- Configure CORS handling

#### Step 3.6: User Interface Features
- Responsive design for mobile/desktop
- Real-time WSJF score calculation
- Inline editing capabilities
- Drag-and-drop prioritization
- Toast notifications for user feedback
- Keyboard shortcuts for power users

### Phase 4: Integration and Testing
**Objective**: Ensure system reliability and performance

#### Step 4.1: Integration Testing
- API endpoint testing with pytest
- Frontend component testing with Jest
- End-to-end testing with Cypress
- Cross-browser compatibility testing

#### Step 4.2: Performance Optimization
- Backend query optimization
- Frontend bundle size reduction
- Lazy loading implementation
- Caching strategy implementation

#### Step 4.3: Security Implementation
- Input validation and sanitization
- CORS configuration
- Rate limiting
- Authentication preparation (for future)

### Phase 5: Excel File Specifications
**Objective**: Define Excel output format and features

#### Step 5.1: Worksheet Structure
- Single worksheet named "WSJF {PI}"
- Frozen header row
- Auto-filter enabled
- Print-ready formatting

#### Step 5.2: Column Definitions
1. **ID**: Sequential identifier
2. **Subject**: Feature/requirement name
3. **Description**: Detailed explanation
4. **Business Value**: Score 1-10
5. **Time Criticality**: Score 1-10
6. **Risk Reduction**: Score 1-10
7. **Job Size**: Score 1-10
8. **WSJF Score**: Calculated value
9. **Priority**: Rank based on WSJF score
10. **Status**: Current state
11. **Owner**: Responsible person
12. **Team**: Assigned team
13. **Program Increment**: PI identifier
14. **Created Date**: Timestamp

#### Step 5.3: Excel Formatting Rules
- Header row: Blue background (#4472C4), white text, bold
- High priority items: Yellow highlight (#FFE699)
- Data validation: Scores limited to 1-10
- Status dropdown: Predefined values
- Column widths: Auto-adjusted for content
- Number formatting: WSJF score with 2 decimal places

### Phase 6: Deployment Preparation
**Objective**: Ready application for production deployment

#### Step 6.1: Containerization
- Create Dockerfile for backend
- Create Dockerfile for frontend
- Configure docker-compose for local development
- Set up nginx reverse proxy

#### Step 6.2: Environment Configuration
- Development environment variables
- Staging configuration
- Production settings
- Secret management approach

#### Step 6.3: CI/CD Pipeline
- Automated testing on commit
- Build verification
- Container registry push
- Deployment automation

### Phase 7: Documentation and Handover
**Objective**: Ensure maintainability and knowledge transfer

#### Step 7.1: Technical Documentation
- API documentation with examples
- Database schema documentation
- Architecture decision records
- Deployment guide

#### Step 7.2: User Documentation
- User manual with screenshots
- Video tutorials for key features
- FAQ section
- Troubleshooting guide

#### Step 7.3: Developer Documentation
- Setup instructions
- Development workflow
- Contributing guidelines
- Code style guide

## Success Criteria

### Functional Requirements
- ✅ Create, read, update, delete WSJF items
- ✅ Automatic WSJF score calculation
- ✅ Priority ranking based on scores
- ✅ Excel export with formatting
- ✅ Batch operations support
- ✅ Status tracking capability
- ✅ Team and owner assignment

### Non-Functional Requirements
- ✅ Response time < 1 second for standard operations
- ✅ Support 100+ concurrent users
- ✅ Excel generation for 1000+ items
- ✅ Mobile-responsive design
- ✅ 99.9% uptime target
- ✅ Cross-browser compatibility (Chrome, Firefox, Safari, Edge)

### Quality Metrics
- Code coverage > 80%
- Lighthouse performance score > 90
- Zero critical security vulnerabilities
- Load time < 3 seconds
- Accessibility WCAG 2.1 AA compliant
