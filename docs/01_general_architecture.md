# General Architecture

The application is built upon the components shown below:

![General Architecture](images/General_Architecture.drawio.svg)

## System Overview

TellMe is a Django-based AI call analysis platform designed for multi-tenant customer support operations. The system transforms call recordings into actionable insights through AI-powered processing pipelines.

## Core Components

### Django Applications

#### call_miner
REST API serving call data to frontend clients. Provides:
- Multi-tenant data model with organizations, users, customers, and conversations
- Role-based access control (Analysts vs Agents)
- Conversation statistics and trend analysis
- Automated summary caching with PeriodSummary model
- API key management for external integrations
- Full-text search across customers and conversations

#### call_processing
AI processing pipeline for incoming calls:
- Audio transcription (Deepgram)
- Topic association and suggestion
- Churn analysis and sentiment scoring
- Conversation summarization
- Meta-summarization with intelligent transcript/summary selection
- Asynchronous task orchestration via Google Cloud Tasks

### Technology Stack

#### Backend
- **Framework**: Django 5.1.2 with Django REST Framework
- **Database**: PostgreSQL with psycopg2-binary
- **Authentication**: Firebase Admin SDK with custom authentication backend
- **AI/ML**: OpenAI, Groq, Google GenAI via LiteLLM
- **Observability**: Langfuse for LLM tracing and monitoring

#### Infrastructure
- **Cloud Platform**: Google Cloud Platform
  - Cloud Run for container deployment
  - Cloud Tasks for async job processing
  - Secret Manager for configuration
  - Cloud Storage for audio files
- **Containerization**: Docker with multi-stage builds
- **Dependency Management**: uv for fast Python package management

#### Local Development
- Docker Compose orchestrating:
  - PostgreSQL database
  - Firebase Authentication emulator
  - Cloud Tasks emulator
  - GCP Storage emulator

## Key Features

### Multi-Tenancy
- Organization-level data isolation
- Per-organization LLM provider configuration
- Separate API keys and usage tracking
- Configurable transcription and enrichment methods

### AI-Powered Analysis
- Automatic call transcription and summarization
- Intelligent topic detection and categorization
- Sentiment analysis and churn prediction
- Full history customer summaries (eternity period)
- Token-optimized meta-summarization choosing between transcripts and summaries

### Scalability & Performance
- Asynchronous processing via Cloud Tasks
- Cached summaries with smart refresh logic
- Pagination and cursor-based ordering
- Database query optimization with select_related/prefetch_related

### Security
- Firebase authentication with role-based permissions
- SHA-256 hashed API keys with expiration
- Organization-scoped data access
- Multi-factor authentication support via Firebase

## Deployment Environments

### Development (dev)
- Local Docker Compose setup
- Firebase emulator for auth
- Local PostgreSQL instance
- `.env` file configuration

### Staging
- Cloud Run deployment
- Shared Firebase project
- GCP Secret Manager for secrets
- Separate database instance

### Production (prod)
- Cloud Run with autoscaling
- Production Firebase project
- Encrypted secrets via Secret Manager
- High-availability database configuration