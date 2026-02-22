# TellMe Infrastructure & Network Architecture

## Overview

This document provides a detailed network diagram and description of the TellMe infrastructure. The architecture is designed with a serverless-first approach on Google Cloud Platform (GCP) and Cloudflare, prioritizing security controls, data integrity, and high availability to support ISO 27001 and SOC 2 compliance.

## Network Diagram

The following diagram illustrates the boundary definitions, network zones, security controls, and data flows within the environment.

```mermaid
graph TB
    subgraph User_Zone [Public Internet]
        EndUser[End Users]
        AdminUser[App Superusers]
        Devs[Developers - BYOD w/ MDM]
    end

    subgraph Edge_Zone [Edge Layer: Cloudflare]
        CFW[Cloudflare Worker<br/>Static Frontend]
    end

    subgraph Identity_Layer [ID & Access Management]
        Firebase[Firebase Auth<br/>API Users]
        GoogleIAP[Google IAP<br/>App Superusers]
        IAM[GCP IAM & WIF<br/>CI/CD]
    end

    subgraph GCP_Boundary [GCP Security Perimeter]
        SSL[Managed SSL Cert<br/>TLS 1.2+]
        LB[Global HTTPS Load Balancer<br/>Path-Based URL Routing]
        CA[Cloud Armour WAF<br/>Multi-Layer Protection]
    end

    subgraph Routing_Layer [Request Routing Layer]
        AGW[API Gateway Backend<br/>/api/**, /health, /schema]
        IAPBackend[IAP Backend Service<br/>/admin, /admin/**]
        ProcBackend[Processing Direct Backend<br/>/processing/v1/queue, /ws/audiohook]
    end

    subgraph GCP_Compute [App Layer - europe-west6]
        CloudRun[Cloud Run Service<br/>Django Application]
    end

    subgraph GCP_Data [Data & Services Layer]
        SQL[(Cloud SQL<br/>PostgreSQL 17)]
        GCS[Cloud Storage<br/>Media & Calls]
        Tasks[Cloud Tasks<br/>Processing Queues]
        Secrets[Secret Manager<br/>Config & Creds]
    end

    %% User flows
    EndUser --> Firebase
    EndUser --> CFW
    AdminUser --> GoogleIAP
    Devs --> IAM

    %% API path
    CFW --> SSL
    SSL --> LB
    LB --> CA
    CA -."/api/** traffic".-> AGW
    AGW --> CloudRun

    %% Admin path
    AdminUser --> SSL
    CA -."/admin/** traffic".-> IAPBackend
    IAPBackend --> GoogleIAP
    IAPBackend --> CloudRun

    %% Processing direct path (bypasses API Gateway)
    CA -."/processing/v1/queue
    /ws/audiohook traffic".-> ProcBackend
    ProcBackend --> CloudRun

    %% CI/CD path
    IAM -.WIF OIDC.-> CloudRun

    %% Data access
    CloudRun --> SQL
    CloudRun --> GCS
    CloudRun --> Tasks
    CloudRun --> Secrets

    %% Styling
    style CA fill:#ffebee
    style AGW fill:#f3e5f5
    style IAPBackend fill:#fff3e0
    style ProcBackend fill:#e8eaf6
    style LB fill:#e1f5ff
    style CloudRun fill:#e8f5e9
```

## Architectural Components & Security Controls

### 1. Network Zones & Boundaries

* **External Zone**: Includes end-users and company developers. Developers operate under a "lightweight" BYOD scheme, with security compliance enforced by a **Mobile Device Management (MDM)** platform.
* **Edge Layer**: The application frontend is hosted on **Cloudflare Workers**, providing a globally distributed entry point that minimizes latency.
* **GCP Security Boundary**: All backend traffic is funneled through a **Global External HTTP(S) Load Balancer**. Entry is protected by **Cloud Armour**, which serves as a Web Application Firewall (WAF) to block SQL injection, Cross-Site Scripting (XSS), and malicious IP ranges.
* **Application Layer**: The backend logic is fully containerized and hosted on **Cloud Run (Gen2)** within the `europe-west6` region.

### 2. Security Controls & Redundancy

* **Encryption**: All external communications are encrypted using **TLS 1.2+**. The Load Balancer enforces security headers, including **HSTS**, **X-Content-Type-Options** (nosniff), and **X-Frame-Options** (DENY).
* **Access Control**:
  * **API Access**: User identity for API endpoints is managed via **Firebase Authentication**. The API Gateway validates Firebase JWTs before routing requests to Cloud Run.
  * **Admin Access**: The Django admin interface (`/admin`) is protected by **Google Identity-Aware Proxy (IAP)**, which requires Google account authentication and IAM role membership (`roles/iap.httpsResourceAccessor`). This provides enterprise-grade access control with centralized identity management.
  * **Service Access**: Internal service access is strictly governed by **GCP IAM roles**, ensuring that the backend service account has the minimum necessary permissions to access databases, buckets, and secrets.
* **Web Application Firewall**: **Cloud Armour** provides layered protection with distinct security policies for API and admin traffic:
  * **API Traffic Protection** (`/api/**`): Full WAF rule enforcement including SQLi, XSS, LFI, RCE, rate limiting, malicious IP blocking, and suspicious user agent detection
  * **Processing Traffic Protection** (`/processing/v1/queue`, `/ws/audiohook`): Same Cloud Armour security policy applies via the `processing_direct_backend` Backend Service. `/processing/v1/start` has an additional dedicated rate-limit rule (10 req/min per IP, priority 1050) to prevent ephemeral token generation abuse.
  * **Admin Traffic Protection** (`/admin/**`): Applies all WAF rules **except** SQL injection detection, which is bypassed to prevent false positives on Google IAP's OAuth callback tokens. Admin traffic is still protected by:
    - IP blocking and rate limiting (Priority 200-1150)
    - XSS protection (Priority 1300)
    - LFI protection (Priority 1350)
    - RCE protection (Priority 1360)
    - Large body checks, user agent filtering, HTTP method validation (Priority 1400-1700)
    - **Defense in depth**: IAP authentication + WAF (minus SQLi) + Django security
  * **Adaptive DDoS Protection**: Layer 7 DDoS defense enabled with automatic threat detection and mitigation
* **Network Hardening**: To comply with audit requirements, a high-priority firewall rule explicitly **denies public SSH access** (Port 22) across the project.
* **Data Availability & Redundancy**:
  * **Cloud SQL (PostgreSQL 17)**: Configured for high availability (REGIONAL) with automatic failover. Automated daily backups are retained for 30 days, and Point-in-Time Recovery (PITR) is enabled.
  * **Cloud Storage**: Buckets for media and call processing have **versioning enabled** and lifecycle rules to manage data retention.

### 3. Data Flows

The architecture implements three distinct routing paths based on the request type:

#### API Request Pipeline (/api/**)
* **Authentication**: Users authenticate via **Firebase Authentication** and obtain a Firebase token.
* **Request Flow**: Authenticated requests from the Cloudflare-hosted frontend reach the GCP Load Balancer.
* **Security Inspection**: After WAF inspection by Cloud Armour, the **Load Balancer** routes `/api/**` traffic to the **API Gateway**.
* **Token Validation**: The API Gateway validates the Firebase JWT before invoking the Cloud Run backend.

#### Admin Request Pipeline (/admin, /admin/**)
* **Authentication**: Admin users authenticate via **Google IAP (Identity-Aware Proxy)** using their Google accounts.
* **Request Flow**: Admin requests reach the GCP Load Balancer at the `/admin` path.
* **Layered Security Inspection**: Cloud Armour applies multiple WAF protection layers:
  1. IP blocking and rate limiting checks
  2. XSS, LFI, and RCE attack detection
  3. Large body, user agent, and HTTP method validation
  4. **SQLi checks bypassed** (Priority 1800) to prevent false positives on IAP OAuth tokens
* **Routing**: The **Load Balancer** routes `/admin/**` traffic to the **IAP Backend Service**.
* **IAP Verification**: IAP validates the user's Google identity and checks IAM permissions (`roles/iap.httpsResourceAccessor`) before allowing direct access to Cloud Run.
* **Bypass API Gateway**: Admin traffic bypasses the API Gateway entirely, going directly from IAP to Cloud Run.
* **Security Model**: Multi-layer defense combining IAP authentication, selective WAF protection, and Django's built-in security controls.

#### Processing Request Pipeline (/processing/v1/queue, /ws/audiohook)
* **Token Exchange**: Customer servers first call `GET /processing/v1/start` with their long-lived **Organization API Key** to receive a short-lived **ephemeral session token** (15-minute TTL).
* **Request Flow**: The customer server uses the ephemeral token (`X-TellMe-Session-Token: Bearer <token>`) to authenticate audio upload (`POST /processing/v1/queue`) or WebSocket streaming (`/ws/audiohook`) requests.
* **Security Inspection**: Cloud Armour applies the same WAF policy via the `processing_direct_backend` Backend Service (no API Gateway involvement — required for WebSocket support and to keep long-lived API keys off hot paths).
* **Routing**: The Load Balancer routes these paths directly to Cloud Run, bypassing the API Gateway entirely. Cloud Run validates the ephemeral token against Cloud SQL and processes the audio.
* **Cloud Run Ingress**: Set to `INGRESS_TRAFFIC_LOAD_BALANCER` to prevent direct Cloud Run URL bypass.

#### Resource Integration
The Cloud Run service communicates internally with:
  * **Cloud SQL** via a secure instance connection.
  * **Cloud Tasks** for asynchronous processing of calls, summaries, and tickets.
  * **Secret Manager** for retrieving sensitive environment settings and credentials.

#### Developer/CI Flow
GitHub Actions utilizes **Workload Identity Federation** to securely deploy infrastructure and code without long-lived secrets.