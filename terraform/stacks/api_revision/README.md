# TellMe Infrastructure & Network Architecture

## Overview

This document provides a detailed network diagram and description of the TellMe infrastructure. The architecture is designed with a serverless-first approach on Google Cloud Platform (GCP) and Cloudflare, prioritizing security controls, data integrity, and high availability to support ISO 27001 and SOC 2 compliance.

## Network Diagram

The following diagram illustrates the boundary definitions, network zones, security controls, and data flows within the environment.

```mermaid
graph TD
    subgraph User_Zone [External Zone: Public Internet]
        EndUser[End Users]
        AdminUser[Admin Users]
        Devs[Developers - BYOD w/ Kandji MDM]
    end

    subgraph Identity_Layer [Identity & Access Layer]
        Firebase[Firebase Authentication]
        GoogleIAP[Google IAP - OAuth2]
        IAM[GCP IAM & Workload Identity Federation]
    end

    subgraph Edge_Zone [Edge Layer: Cloudflare]
        CFW[Cloudflare Worker - Frontend]
    end

    subgraph GCP_Boundary [GCP Security Boundary]
        LB[Global External HTTPs Load Balancer<br/>URL Map - Path-based Routing]
        CA[Cloud Armour WAF - DDoS & Threat Protection]
        SSL[Managed SSL Certificate - TLS 1.2+]
    end

    subgraph GCP_API_Mgmt [API Management Layer]
        AGW[API Gateway<br/>Handles: /api/**, /health, /schema]
    end

    subgraph GCP_IAP_Layer [IAP Layer]
        IAPBackend[IAP Backend Service<br/>Handles: /admin, /admin/**]
    end

    subgraph GCP_Compute [Application Layer - Region: europe-west6]
        CloudRun[Cloud Run Service - Backend API<br/>Django Application]
        FW[Firewall - Deny Public SSH]
    end

    subgraph GCP_Data_Storage [Data & Services Layer]
        SQL[(Cloud SQL - PostgreSQL 17)]
        GCS[Cloud Storage - Media & Call Buckets]
        Tasks[Cloud Tasks - Call/Summary/Ticket Queues]
        Secrets[Secret Manager - App Settings]
    end

    %% API Data Flows
    EndUser -- "1. Auth Request" --> Firebase
    EndUser -- "2. HTTPS / Firebase Token" --> CFW
    CFW -- "3. API Call (TLS 1.2+)" --> LB
    LB -- "4. WAF Inspection" --> CA
    LB -- "5a. /api/** → API Gateway" --> AGW
    AGW -- "6a. Firebase JWT Validation" --> CloudRun

    %% Admin Data Flows
    AdminUser -- "1. Google Login" --> GoogleIAP
    AdminUser -- "2. /admin Request (TLS 1.2+)" --> LB
    LB -- "4. WAF Inspection" --> CA
    LB -- "5b. /admin/** → IAP Backend" --> IAPBackend
    IAPBackend -- "6b. IAP Auth Check" --> GoogleIAP
    IAPBackend -- "7b. Direct Invoke" --> CloudRun

    %% Internal Connections
    CloudRun -- "8. Internal Connection" --> SQL
    CloudRun -- "8. IAM Access" --> GCS
    CloudRun -- "8. IAM Access" --> Tasks
    CloudRun -- "8. IAM Access" --> Secrets

    %% CI/CD Flow
    Devs -- "CI/CD & Management" --> IAM
    IAM -- "OIDC / WIF" --> CloudRun

    %% Styling
    style LB fill:#e1f5ff
    style IAPBackend fill:#fff3e0
    style AGW fill:#f3e5f5
```

## Architectural Components & Security Controls

### 1. Network Zones & Boundaries

* **External Zone**: Includes end-users and company developers. Developers operate under a "lightweight" BYOD scheme, with security compliance enforced by the **Kandji MDM** platform.
* **Edge Layer**: The application frontend is hosted on **Cloudflare Workers**, providing a globally distributed entry point that minimizes latency.
* **GCP Security Boundary**: All backend traffic is funneled through a **Global External HTTP(S) Load Balancer**. Entry is protected by **Cloud Armour**, which serves as a Web Application Firewall (WAF) to block SQL injection, Cross-Site Scripting (XSS), and malicious IP ranges.
* **Application Layer**: The backend logic is fully containerized and hosted on **Cloud Run (Gen2)** within the `europe-west6` region.

### 2. Security Controls & Redundancy

* **Encryption**: All external communications are encrypted using **TLS 1.2+**. The Load Balancer enforces security headers, including **HSTS**, **X-Content-Type-Options** (nosniff), and **X-Frame-Options** (DENY).
* **Access Control**:
  * **API Access**: User identity for API endpoints is managed via **Firebase Authentication**. The API Gateway validates Firebase JWTs before routing requests to Cloud Run.
  * **Admin Access**: The Django admin interface (`/admin`) is protected by **Google Identity-Aware Proxy (IAP)**, which requires Google account authentication and IAM role membership (`roles/iap.httpsResourceAccessor`). This provides enterprise-grade access control with centralized identity management.
  * **Service Access**: Internal service access is strictly governed by **GCP IAM roles**, ensuring that the backend service account has the minimum necessary permissions to access databases, buckets, and secrets.
* **Web Application Firewall**: **Cloud Armour** protects both API and admin traffic against common threats including:
  * SQL injection and XSS attacks
  * Local file inclusion (LFI) and remote code execution (RCE)
  * DDoS attacks with adaptive protection
  * Rate limiting per endpoint type
  * Malicious IP blocking and suspicious user agent detection
* **Network Hardening**: To comply with audit requirements, a high-priority firewall rule explicitly **denies public SSH access** (Port 22) across the project.
* **Data Availability & Redundancy**:
  * **Cloud SQL (PostgreSQL 17)**: Configured for high availability (REGIONAL) with automatic failover. Automated daily backups are retained for 30 days, and Point-in-Time Recovery (PITR) is enabled.
  * **Cloud Storage**: Buckets for media and call processing have **versioning enabled** and lifecycle rules to manage data retention.

### 3. Data Flows

The architecture implements two distinct routing paths based on the request type:

#### API Request Pipeline (/api/**)
* **Authentication**: Users authenticate via **Firebase Authentication** and obtain a Firebase token.
* **Request Flow**: Authenticated requests from the Cloudflare-hosted frontend reach the GCP Load Balancer.
* **Security Inspection**: After WAF inspection by Cloud Armour, the **Load Balancer** routes `/api/**` traffic to the **API Gateway**.
* **Token Validation**: The API Gateway validates the Firebase JWT before invoking the Cloud Run backend.

#### Admin Request Pipeline (/admin, /admin/**)
* **Authentication**: Admin users authenticate via **Google IAP (Identity-Aware Proxy)** using their Google accounts.
* **Request Flow**: Admin requests reach the GCP Load Balancer at the `/admin` path.
* **Security Inspection**: After WAF inspection by Cloud Armour, the **Load Balancer** routes `/admin/**` traffic to the **IAP Backend Service**.
* **IAP Verification**: IAP validates the user's Google identity and checks IAM permissions (`roles/iap.httpsResourceAccessor`) before allowing direct access to Cloud Run.
* **Bypass API Gateway**: Admin traffic bypasses the API Gateway entirely, going directly from IAP to Cloud Run.

#### Resource Integration
The Cloud Run service communicates internally with:
  * **Cloud SQL** via a secure instance connection.
  * **Cloud Tasks** for asynchronous processing of calls, summaries, and tickets.
  * **Secret Manager** for retrieving sensitive environment settings and credentials.

#### Developer/CI Flow
GitHub Actions utilizes **Workload Identity Federation** to securely deploy infrastructure and code without long-lived secrets.