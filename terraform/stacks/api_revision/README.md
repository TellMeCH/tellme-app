# TellMe Infrastructure & Network Architecture

## Overview

This document provides a detailed network diagram and description of the TellMe infrastructure. The architecture is designed with a serverless-first approach on Google Cloud Platform (GCP) and Cloudflare, prioritizing security controls, data integrity, and high availability to support ISO 27001 and SOC 2 compliance.

## Network Diagram

The following diagram illustrates the boundary definitions, network zones, security controls, and data flows within the environment.

```mermaid
graph TD
    subgraph User_Zone [External Zone: Public Internet]
        EndUser[End Users]
        Devs[Developers - BYOD w/ Kandji MDM]
    end

    subgraph Identity_Layer [Identity & Access Layer]
        Firebase[Firebase Authentication]
        IAM[GCP IAM & Workload Identity Federation]
    end

    subgraph Edge_Zone [Edge Layer: Cloudflare]
        CFW[Cloudflare Worker - Frontend]
    end

    subgraph GCP_Boundary [GCP Security Boundary]
        LB[Global External HTTPs Load Balancer]
        CA[Cloud Armour WAF - DDoS & Threat Protection]
        SSL[Managed SSL Certificate - TLS 1.2+]
    end

    subgraph GCP_API_Mgmt [API Management Layer]
        AGW[API Gateway]
    end

    subgraph GCP_Compute [Application Layer - Region: europe-west6]
        CloudRun[Cloud Run Service - Backend API]
        FW[Firewall - Deny Public SSH]
    end

    subgraph GCP_Data_Storage [Data & Services Layer]
        SQL[(Cloud SQL - PostgreSQL 17)]
        GCS[Cloud Storage - Media & Call Buckets]
        Tasks[Cloud Tasks - Call/Summary/Ticket Queues]
        Secrets[Secret Manager - App Settings]
    end

    %% Data Flows
    EndUser -- "1. Auth Request" --> Firebase
    EndUser -- "2. HTTPS / Firebase Token" --> CFW
    CFW -- "3. API Call (TLS 1.2+)" --> LB
    LB -- "4. Inspects Traffic" --> CA
    LB -- "5. Routes to" --> AGW
    AGW -- "6. Authenticated Invoke" --> CloudRun
    
    CloudRun -- "7. Internal Connection" --> SQL
    CloudRun -- "7. IAM Access" --> GCS
    CloudRun -- "7. IAM Access" --> Tasks
    CloudRun -- "7. IAM Access" --> Secrets

    Devs -- "CI/CD & Management" --> IAM
    IAM -- "OIDC / WIF" --> CloudRun
```

## Architectural Components & Security Controls

### 1. Network Zones & Boundaries

* **External Zone**: Includes end-users and company developers. Developers operate under a "lightweight" BYOD scheme, with security compliance enforced by the **Kandji MDM** platform.
* **Edge Layer**: The application frontend is hosted on **Cloudflare Workers**, providing a globally distributed entry point that minimizes latency.
* **GCP Security Boundary**: All backend traffic is funneled through a **Global External HTTP(S) Load Balancer**. Entry is protected by **Cloud Armour**, which serves as a Web Application Firewall (WAF) to block SQL injection, Cross-Site Scripting (XSS), and malicious IP ranges.
* **Application Layer**: The backend logic is fully containerized and hosted on **Cloud Run (Gen2)** within the `europe-west6` region.

### 2. Security Controls & Redundancy

* **Encryption**: All external communications are encrypted using **TLS 1.2+**. The Load Balancer enforces security headers, including **HSTS**, **X-Content-Type-Options** (nosniff), and **X-Frame-Options** (DENY).
* **Access Control**: User identity is managed via **Firebase Authentication**. Internal service access is strictly governed by **GCP IAM roles**, ensuring that the backend service account has the minimum necessary permissions to access databases, buckets, and secrets.
* **Network Hardening**: To comply with audit requirements, a high-priority firewall rule explicitly **denies public SSH access** (Port 22) across the project.
* **Data Availability & Redundancy**:
  * **Cloud SQL (PostgreSQL 17)**: Configured for high availability (REGIONAL) with automatic failover. Automated daily backups are retained for 30 days, and Point-in-Time Recovery (PITR) is enabled.
  * **Cloud Storage**: Buckets for media and call processing have **versioning enabled** and lifecycle rules to manage data retention.

### 3. Data Flows

* **Request Pipeline**: Upon successful authentication with Firebase, requests from the Cloudflare-hosted frontend reach the GCP Load Balancer. After WAF inspection by Cloud Armour, the **API Gateway** routes authorized requests to the Cloud Run backend.
* **Resource Integration**: The Cloud Run service communicates internally with:
  * **Cloud SQL** via a secure instance connection.
  * **Cloud Tasks** for asynchronous processing of calls, summaries, and tickets.
  * **Secret Manager** for retrieving sensitive environment settings and credentials.
* **Developer/CI Flow**: GitHub Actions utilizes **Workload Identity Federation** to securely deploy infrastructure and code without long-lived secrets.