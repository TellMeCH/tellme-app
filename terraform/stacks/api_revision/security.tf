provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Cloud Armour Security Policy with EU geo-restriction
resource "google_compute_security_policy" "api_security_policy" {
  name        = "tellme-api-security-policy"
  project     = var.project_id
  description = "Security policy for TellMe API with DDoS protection and WAF rules"


  # Block requests not targeting the expected domain (e.g. direct-IP scanners)
  rule {
    action   = "deny(403)"
    priority = "100"
    match {
      expr {
        expression = "!has(request.headers['host']) || request.headers['host'] != '${var.api_domain}'"
      }
    }
    description = "Block direct-IP requests that bypass the domain (scanners, bots)"
  }

  # Block requests to paths outside known application namespaces
  # Allowlist: /api/, /processing/, /admin, /health/, /ws/audiohook
  # This stops internet scanners (zgrab, l9scan, etc.) from reaching Cloud Run
  rule {
    action   = "deny(403)"
    priority = "300"
    match {
      expr {
        expression = <<-EOF
          !request.path.startsWith('/api/v1/') &&
          !request.path.startsWith('/processing/v1/') &&
          !request.path.startsWith('/admin') &&
          !request.path.startsWith('/health/') &&
          !request.path.startsWith('/ws/audiohook')
        EOF
      }
    }
    description = "Block requests to unknown paths (path allowlist)"
  }

  # Block known malicious IPs
  rule {
    action   = "deny(403)"
    priority = "200"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = [
          "185.220.100.0/22",
          "198.98.48.0/20",
          "23.129.64.0/18"
        ]
      }
    }
    description = "Block known malicious IP ranges"
  }

  # /processing/v1/start rate limit — stricter, as this is the token-issuance gate
  rule {
    action   = "throttle"
    priority = "1050"
    match {
      expr {
        expression = "request.path.matches('/processing/v1/start.*')"
      }
    }
    description = "Strict rate limiting for ephemeral token issuance endpoint"

    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"

      rate_limit_threshold {
        count        = 10
        interval_sec = 60
      }
    }
  }

  # Processing endpoints rate limit
  rule {
    action   = "throttle"
    priority = "1100"
    match {
      expr {
        expression = "request.path.matches('/processing/v1/.*')"
      }
    }
    description = "Rate limiting for processing endpoints"

    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"

      rate_limit_threshold {
        count        = 50
        interval_sec = 60
      }
    }
  }

  # General API rate limiting
  rule {
    action   = "throttle"
    priority = "1150"
    match {
      expr {
        expression = "request.path.matches('/api/.*')"
      }
    }
    description = "General API rate limiting"

    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"
      enforce_on_key = "IP"

      rate_limit_threshold {
        count        = 300
        interval_sec = 60
      }
    }
  }


  # XSS Protection
  rule {
    action   = "deny(403)"
    priority = "1300"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "Block cross-site scripting attempts"
  }

  # LFI Protection
  rule {
    action   = "deny(403)"
    priority = "1350"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('lfi-stable')"
      }
    }
    description = "Block local file inclusion attempts"
  }

  # RCE Protection
  rule {
    action   = "deny(403)"
    priority = "1360"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('rce-stable')"
      }
    }
    description = "Block remote code execution attempts"
  }

  # Block large request bodies (Uses Content-Length header)
  rule {
    action   = "deny(403)"
    priority = "1400"
    match {
      expr {
        # logic: has content-length AND length > 10MB AND NOT processing endpoint
        expression = "has(request.headers['content-length']) && int(request.headers['content-length']) > 10485760 && !request.path.matches('/processing/v1/queue.*')"
      }
    }
    description = "Block requests with large bodies (except processing endpoints)"
  }

  # Block suspicious user agents
  rule {
    action   = "deny(403)"
    priority = "1500"
    match {
      expr {
        expression = <<-EOF
          has(request.headers['user-agent']) &&
          request.headers['user-agent'].lower().matches('.*sqlmap.*|.*nikto.*|.*nessus.*|.*masscan.*|.*gobuster.*|.*dirb.*|.*burp.*|.*zgrab.*|.*l9scan.*|.*censys.*|.*scrapy.*|.*gptbot.*|.*semrushbot.*|.*ahrefsbot.*|.*mj12bot.*')
        EOF
      }
    }
    description = "Block requests from known scanning tools"
  }

  # Allow only specific HTTP methods
  rule {
    action   = "deny(403)"
    priority = "1600"
    match {
      expr {
        expression = "!(request.method.matches('GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD'))"
      }
    }
    description = "Block unsupported HTTP methods"
  }

  # Block requests without proper headers (FIXED: Returns 403 instead of 400)
  rule {
    action   = "deny(403)"
    priority = "1700"
    match {
      expr {
        expression = <<-EOF
          request.path.matches('/api/.*') &&
          request.method.matches('POST|PUT|PATCH') &&
          !request.method.matches('OPTIONS') &&
          (!has(request.headers['content-type']) ||
           !request.headers['content-type'].matches('application/json.*|multipart/form-data.*'))
        EOF
      }
    }
    description = "Require proper Content-Type for API requests"
  }

  # SPECIAL BYPASS: Allow /admin to bypass ONLY SQLi checks (after all other WAF rules)
  # Admin traffic still gets protected by XSS, LFI, RCE, rate limiting, etc.
  # Only SQLi is bypassed due to false positives on IAP OAuth flow
  # This provides better defense in depth than bypassing all WAF rules
  rule {
    action   = "allow"
    priority = "1800"
    match {
      expr {
        expression = "request.path.matches('/admin/.*') || request.path.matches('/admin')"
      }
    }
    description = "Bypass SQLi checks for IAP-protected admin (after other WAF checks applied)"
  }

  # GENERAL SQLi: Block SQL injection for all traffic (admin already bypassed above)
  rule {
    action   = "deny(403)"
    priority = "1900"
    match {
      expr {
        expression = "evaluatePreconfiguredWaf('sqli-v33-stable')"
      }
    }
    description = "Block SQL injection attempts (admin traffic already allowed above)"
  }

  # DEFAULT ALLOW
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule"
  }

  # Enable adaptive protection for DDoS
  adaptive_protection_config {
    layer_7_ddos_defense_config {
      enable          = true
      rule_visibility = "STANDARD"
    }
  }
}

# Cloudflare Origin Certificate for the Load Balancer.
# Issued by Cloudflare (SSL/TLS → Origin Server → Create Certificate, 15-year validity).
# Replaces google_compute_managed_ssl_certificate whose HTTP-01 ACME renewal is
# blocked by Cloudflare's orange-cloud proxy. name_prefix ensures a unique name on
# each replacement since self-managed certs are immutable in GCP.
resource "google_compute_ssl_certificate" "api_ssl_cert" {
  name_prefix = "tellme-api-ssl-cert-"
  project     = var.project_id
  certificate = var.cf_origin_cert
  private_key = var.cf_origin_key

  lifecycle {
    create_before_destroy = true
  }
}

# Backend service pointing directly to Cloud Run (via Serverless NEG).
# Previously routed through the API Gateway (ESPv2). Removed in favour of direct
# Cloud Run routing so that all backends use Serverless NEGs, enabling
# INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER on Cloud Run (blocks public internet access).
# Firebase JWT validation is handled by Django's FirebaseAuthentication class.
resource "google_compute_backend_service" "api_backend" {
  name                            = "tellme-api-backend"
  project                         = var.project_id
  description                     = "Backend service for TellMe — direct Cloud Run Serverless NEG"
  connection_draining_timeout_sec = 300
  enable_cdn                      = false
  load_balancing_scheme           = "EXTERNAL_MANAGED"
  protocol                        = "HTTPS"

  security_policy = google_compute_security_policy.api_security_policy.id

  # Pointing directly to Cloud Run via Serverless NEG
  backend {
    group = google_compute_region_network_endpoint_group.cloud_run_neg.id
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }

  custom_request_headers = [
    "X-Forwarded-Proto: https"
  ]
}

# IAP Configuration for /admin endpoints
# Note: OAuth client must be created manually once in GCP Console
# 1. Go to: APIs & Services > Credentials
# 2. Create OAuth 2.0 Client ID
# 3. Application type: Web application
# 4. Name: "TellMe Admin IAP Client"
# 5. Add redirect URI: https://iap.googleapis.com/v1/oauth/clientIds/YOUR_CLIENT_ID:handleRedirect
# 6. Copy the Client ID and Client Secret
# 7. Store them as GitHub secrets: IAP_CLIENT_ID and IAP_CLIENT_SECRET

# Provision the IAP service account
# This creates: service-PROJECT_NUMBER@gcp-sa-iap.iam.gserviceaccount.com
resource "google_project_service_identity" "iap_sa" {
  provider = google-beta
  project  = var.project_id
  service  = "iap.googleapis.com"
}

# Serverless NEG for Cloud Run (IAP Backend)
resource "google_compute_region_network_endpoint_group" "cloud_run_neg" {
  provider              = google-beta
  name                  = "tellme-cloud-run-neg"
  project               = var.project_id
  region                = var.region
  network_endpoint_type = "SERVERLESS"

  cloud_run {
    service = var.service_name
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Backend service for Cloud Run with IAP enabled
resource "google_compute_backend_service" "admin_backend" {
  name                            = "tellme-admin-backend"
  project                         = var.project_id
  description                     = "Backend service for TellMe Admin with IAP"
  connection_draining_timeout_sec = 300
  enable_cdn                      = false
  load_balancing_scheme           = "EXTERNAL_MANAGED"
  protocol                        = "HTTPS"

  security_policy = google_compute_security_policy.api_security_policy.id

  # Pointing to Cloud Run via Serverless NEG
  backend {
    group = google_compute_region_network_endpoint_group.cloud_run_neg.id
  }

  # Enable IAP
  iap {
    enabled              = true
    oauth2_client_id     = var.iap_client_id
    oauth2_client_secret = var.iap_client_secret
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }

  custom_request_headers = [
    "X-Forwarded-Proto: https"
  ]
}


# Grant IAP access to specified members
resource "google_iap_web_backend_service_iam_binding" "admin_iap_access" {
  project             = var.project_id
  web_backend_service = google_compute_backend_service.admin_backend.name
  role                = "roles/iap.httpsResourceAccessor"
  members             = var.iap_allowed_members
}


# URL Map for the Load Balancer
resource "google_compute_url_map" "api_url_map" {
  name        = "tellme-api-url-map"
  project     = var.project_id
  description = "URL map for TellMe API with security headers"

  host_rule {
    hosts        = [var.api_domain]
    path_matcher = "allpaths"
  }

  path_matcher {
    name = "allpaths"

    # Default route to API Gateway
    default_route_action {
      weighted_backend_services {
        backend_service = google_compute_backend_service.api_backend.id
        weight          = 100
      }
    }

    # Route /admin traffic to IAP-protected Cloud Run backend
    path_rule {
      paths = ["/admin", "/admin/*"]
      route_action {
        weighted_backend_services {
          backend_service = google_compute_backend_service.admin_backend.id
          weight          = 100
        }
      }
    }

    # All other paths fall through to api_backend (direct Cloud Run Serverless NEG)
    path_rule {
      paths = ["/*"]
      route_action {
        weighted_backend_services {
          backend_service = google_compute_backend_service.api_backend.id
          weight          = 100
        }
      }
    }
  }

  # Default route action (Fallback)
  # This top-level default applies if the Host header doesn't match
  default_route_action {
    weighted_backend_services {
      backend_service = google_compute_backend_service.api_backend.id
      weight          = 100
    }
  }

  # These headers will now apply to ALL responses (both path_matcher and default)
  header_action {
    response_headers_to_add {
      header_name  = "Strict-Transport-Security"
      header_value = "max-age=31536000; includeSubDomains; preload"
      replace      = true
    }
    response_headers_to_add {
      header_name  = "X-Content-Type-Options"
      header_value = "nosniff"
      replace      = true
    }
    response_headers_to_add {
      header_name  = "X-Frame-Options"
      header_value = "DENY"
      replace      = true
    }
    response_headers_to_add {
      header_name  = "X-XSS-Protection"
      header_value = "1; mode=block"
      replace      = true
    }
    response_headers_to_add {
      header_name  = "Referrer-Policy"
      header_value = "strict-origin-when-cross-origin"
      replace      = true
    }
  }
}

# Target HTTPS Proxy
resource "google_compute_target_https_proxy" "api_https_proxy" {
  name             = "tellme-api-https-proxy"
  project          = var.project_id
  url_map          = google_compute_url_map.api_url_map.id
  ssl_certificates = [google_compute_ssl_certificate.api_ssl_cert.id]
  ssl_policy       = google_compute_ssl_policy.api_ssl_policy.id
}

# SSL Policy for enhanced security
resource "google_compute_ssl_policy" "api_ssl_policy" {
  name            = "tellme-api-ssl-policy"
  project         = var.project_id
  profile         = "MODERN"
  min_tls_version = "TLS_1_2"
}

# Static Global IP for Forwarding Rule
resource "google_compute_global_address" "api_ip" {
  name    = "tellme-api-ip"
  project = var.project_id
}

# Global Forwarding Rule (Entry point)
resource "google_compute_global_forwarding_rule" "api_forwarding_rule" {
  name                  = "tellme-api-forwarding-rule"
  project               = var.project_id
  target                = google_compute_target_https_proxy.api_https_proxy.id
  port_range            = "443"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address = google_compute_global_address.api_ip.id

  depends_on = [google_compute_target_https_proxy.api_https_proxy, google_compute_global_address.api_ip]
}

# Redirect HTTP to HTTPS
resource "google_compute_url_map" "api_http_redirect" {
  name    = "tellme-api-http-redirect"
  project = var.project_id

  default_url_redirect {
    https_redirect = true
    strip_query    = false
  }
}

resource "google_compute_target_http_proxy" "api_http_proxy" {
  name    = "tellme-api-http-proxy"
  project = var.project_id
  url_map = google_compute_url_map.api_http_redirect.id
}

resource "google_compute_global_forwarding_rule" "api_http_forwarding_rule" {
  name                  = "tellme-api-http-forwarding-rule"
  project               = var.project_id
  target                = google_compute_target_http_proxy.api_http_proxy.id
  port_range            = "80"
  load_balancing_scheme = "EXTERNAL_MANAGED"
}

# The Complete Flow:
# 1. Customer arrives at api.tell-me.ch (thanks to Cloudflare DNS)
# 2. Neon sign (Forwarding Rule) directs them to the IP address
# 3. Fancy doorman (HTTPS Proxy) checks their SSL credentials
# 4. Bouncer (Cloud Armour) inspects every request for WAF, rate limiting, and DDoS threats
# 5. Seating chart (URL Map) decides which kitchen (Backend Service):
#    - /admin/** → IAP-protected Cloud Run backend (Google account auth required)
#    - Everything else → api_backend (direct Cloud Run Serverless NEG)
# 6. Cloud Run only accepts requests from the Load Balancer (INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER)
#    so the direct Cloud Run URL is unreachable from the public internet
# 7. Django handles all application-level authentication (Firebase JWT, ephemeral tokens, processing key)