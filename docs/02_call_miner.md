# Application Data Model

The Django app `call_miner` is meant to organize and serve the data model shown below:


## Core Models

### Organization
- **Purpose**: Multi-tenant container for users and data
- **Key Features**:
  - Configurable transcription method (Deepgram)
  - Configurable enrichment method (OpenAI, Groq, Google GenAI)
  - User and topic limits
  - API key management
  - Conversation trend analysis

### User
- **Purpose**: Custom user model with Firebase integration
- **Key Features**:
  - Email-based authentication
  - Multiple auth types: password, Google, Microsoft
  - Automatic Firebase user management
  - Email verification and onboarding

### Employee System
- **Employee**: Base class linking users to organizations with roles
- **Analyst**: Employee with topic management permissions (no conversation access)
- **Agent**: Employee who can participate in conversations
  - Hierarchical relationships (managers/subordinates)
  - Conversation statistics and trend analysis
  - Automatic summary generation

### Conversation Management
- **Customer**: Organization-specific customer entities with external IDs
  - All-summaries endpoint includes customers with at least 1 conversation
  - Default summary period: eternity (full customer history)
  - Conversation count and revenue aggregations for ordering
- **Conversation**: Call records with rich metadata
  - Audio path, transcript, sentiment (0-5 scale)
  - Token usage tracking
  - AI-generated summaries and titles
  - Topic and suggested topic associations
  - Ordered by date descending (most recent first) for meta-summarization

### Topic System
- **Topic**: Semantic labels for call categorization
  - Organization-specific with descriptions
  - Conversation statistics and trend analysis
  - Automatic summary generation
- **SuggestedTopic**: AI-generated topic candidates
  - Approval workflow to convert to Topics
  - Conversation tracking during approval process

## Advanced Features

### Summary System
- **PeriodSummary**: Automated summary generation for configurable time periods
  - Weekly, monthly, quarterly, and eternity (full history) aggregations
  - Automatic refresh based on conversation volume changes
  - Generic relation system for any model type
  - Default settings:
    - **Topics**: Quarterly summaries with rolling window
    - **Customers**: Eternity (full history) summaries for comprehensive customer view
    - **Agents**: Monthly summaries (currently disabled in trigger pipeline)

### Analytics Capabilities
All core entities (Agent, Customer, Topic, Organization) inherit:
- **ConversationStatsAbstractModel**: Real-time conversation counts and date ranges
- **ConversationTrendMixin**: Trend analysis with daily/weekly/monthly granularity
- **MetaSummaryAbstractModel**: Intelligent summary caching and refresh logic

### API Management
- **OrganizationAPIKey**: Secure API key system
  - SHA-256 hashed storage
  - 90-day expiration
  - Maximum 3 keys per organization
  - Named keys for easy management
- **EphemeralProcessingToken**: Short-lived tokens for call recording ingestion
  - SHA-256 hashed storage (same scheme as OrganizationAPIKey)
  - 15-minute TTL; issued by `GET /processing/v1/start/` in exchange for a valid API key
  - Used to authenticate `/processing/v1/queue/` and `/ws/audiohook/` requests
  - Expired tokens are purged on every deployment via the `purge_ephemeral_tokens` management command

## Key Relationships
- Users can be employees in multiple organizations (via Employee model)
- Agents have hierarchical relationships (manager/subordinate)
- Conversations link customers, agents, and topics within organizations
- Period summaries provide cached analytics for any model instance
- Suggested topics can be promoted to full topics with conversation history preservation