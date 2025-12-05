provider "google-beta" {
  project = var.project_id
  region  = var.gateway_region
}

# Cloud Armour Security Policy with EU geo-restriction
resource "google_compute_security_policy" "api_security_policy" {
  name        = "tellme-api-security-policy"
  project     = var.project_id
  description = "Security policy for TellMe API with EU geo-restriction, DDoS protection and WAF rules"

  # BLOCK NON-EUROPEAN TRAFFIC FIRST (so EU traffic continues to other rules)
  rule {
    action   = "deny_403"
    priority = "100"
    match {
      expr {
        expression = "!origin.region_code.matches('AT|BE|BG|HR|CY|CZ|DK|EE|FI|FR|DE|GR|HU|IE|IT|LV|LT|LU|MT|NL|PL|PT|RO|SK|SI|ES|SE|CH|NO|IS|LI|GB')"
      }
    }
    description = "Block traffic from outside Europe"
  }

  # Block known malicious IPs and bot networks (within EU)
  rule {
    action   = "deny_403"
    priority = "200"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = [
          "185.220.100.0/22",  # Known Tor exit nodes range
          "198.98.48.0/20",    # Known malicious ranges
          "23.129.64.0/18"     # Common bot networks
        ]
      }
    }
    description = "Block known malicious IP ranges"
  }

  # Enhanced rate limiting for processing endpoints (handles large files)
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

  # SQL Injection Protection
  rule {
    action   = "deny_403"
    priority = "1200"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('sqli-stable')"
      }
    }
    description = "Block SQL injection attempts"
  }

  # XSS Protection
  rule {
    action   = "deny_403"
    priority = "1300"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('xss-stable')"
      }
    }
    description = "Block cross-site scripting attempts"
  }

  # Local File Inclusion (LFI) Protection
  rule {
    action   = "deny_403"
    priority = "1350"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('lfi-stable')"
      }
    }
    description = "Block local file inclusion attempts"
  }

  # Remote Code Execution (RCE) Protection
  rule {
    action   = "deny_403"
    priority = "1360"
    match {
      expr {
        expression = "evaluatePreconfiguredExpr('rce-stable')"
      }
    }
    description = "Block remote code execution attempts"
  }

  # Block large request bodies (potential DoS) - except for processing endpoints
  rule {
    action   = "deny_413"
    priority = "1400"
    match {
      expr {
        expression = "request.body_size > 10485760 && !request.path.matches('/processing/v1/queue.*')"  # 10MB limit, except processing
      }
    }
    description = "Block requests with large bodies (except processing endpoints)"
  }

  # Block requests with suspicious user agents (CASE INSENSITIVE)
  rule {
    action   = "deny_403"
    priority = "1500"
    match {
      expr {
        expression = <<-EOF
          has(request.headers['user-agent']) &&
          request.headers['user-agent'][0].lower().matches('.*sqlmap.*|.*nikto.*|.*nessus.*|.*masscan.*|.*gobuster.*|.*dirb.*|.*burp.*')
        EOF
      }
    }
    description = "Block requests from known scanning tools"
  }

  # Allow only specific HTTP methods
  rule {
    action   = "deny_405"
    priority = "1600"
    match {
      expr {
        expression = "!(request.method.matches('GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD'))"
      }
    }
    description = "Block unsupported HTTP methods"
  }

  # Block requests without proper headers for API calls (excluding OPTIONS for CORS)
  rule {
    action   = "deny_400"
    priority = "1700"
    match {
      expr {
        expression = <<-EOF
          request.path.matches('/api/.*') &&
          request.method.matches('POST|PUT|PATCH') &&
          !request.method.matches('OPTIONS') &&
          (!has(request.headers['content-type']) ||
           !request.headers['content-type'][0].matches('application/json.*|multipart/form-data.*'))
        EOF
      }
    }
    description = "Require proper Content-Type for API requests (excluding CORS preflight)"
  }

  # DEFAULT RULE - ALLOW (traffic has passed all security checks)
  rule {
    action   = "allow"
    priority = "2147483647"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }
    description = "Default allow rule - traffic has passed all security checks"
  }

  # Enable adaptive protection for DDoS
  adaptive_protection_config {
    layer_7_ddos_defense_config {
      enable          = true
      rule_visibility = "STANDARD"
    }
  }
}

# SSL Certificate for the Load Balancer
resource "google_compute_managed_ssl_certificate" "api_ssl_cert" {
  name    = "tellme-api-ssl-cert"
  project = var.project_id

  managed {
    domains = [var.api_domain]
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Backend service pointing to API Gateway (via Serverless NEG)
resource "google_compute_backend_service" "api_backend" {
  name                            = "tellme-api-backend"
  project                         = var.project_id
  description                     = "Backend service for TellMe API Gateway"
  connection_draining_timeout_sec = 300
  enable_cdn                      = false
  load_balancing_scheme           = "EXTERNAL_MANAGED"
  protocol                        = "HTTPS"
  port_name                       = "https"
  timeout_sec                     = 30

  security_policy = google_compute_security_policy.api_security_policy.id

  # Pointing to API Gateway via Serverless NEG (no health checks needed)
  backend {
    group = google_compute_region_network_endpoint_group.api_gateway_neg.id
  }

  log_config {
    enable      = true
    sample_rate = 1.0
  }

  custom_request_headers = [
    "X-Forwarded-Proto: https",
    "X-Forwarded-For: {client_ip}",
    "X-Cloud-Trace-Context: {trace_id}"
  ]
}

# Serverless Network Endpoint Group for API Gateway
resource "google_compute_region_network_endpoint_group" "api_gateway_neg" {
  name                  = "tellme-api-gateway-neg"
  project               = var.project_id
  region                = var.gateway_region
  network_endpoint_type = "SERVERLESS"

  serverless_deployment {
    platform = "apigateway.googleapis.com"
    resource = google_api_gateway_gateway.gateway.gateway_id
  }

  lifecycle {
    create_before_destroy = true
  }
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

  # Default route action with security headers
  default_route_action {
    weighted_backend_services {
      backend_service = google_compute_backend_service.api_backend.id
      weight          = 100
    }

    # Add security headers
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
  ssl_certificates = [google_compute_managed_ssl_certificate.api_ssl_cert.id]
  ssl_policy       = google_compute_ssl_policy.api_ssl_policy.id
}

# SSL Policy for enhanced security (FIXED - removed custom_features with MODERN profile)
resource "google_compute_ssl_policy" "api_ssl_policy" {
  name            = "tellme-api-ssl-policy"
  project         = var.project_id
  profile         = "MODERN"
  min_tls_version = "TLS_1_2"
}

# Global Forwarding Rule (Entry point)
resource "google_compute_global_forwarding_rule" "api_forwarding_rule" {
  name                  = "tellme-api-forwarding-rule"
  project               = var.project_id
  target                = google_compute_target_https_proxy.api_https_proxy.id
  port_range            = "443"
  load_balancing_scheme = "EXTERNAL_MANAGED"

  depends_on = [google_compute_target_https_proxy.api_https_proxy]
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
#
#   1. Customer arrives at api.tell-me.ch (thanks to Cloudflare DNS)
#   2. Neon sign (Forwarding Rule) directs them to IP address
#   3. Fancy doorman (HTTPS Proxy) checks their SSL credentials
#   4. Seating chart (URL Map) decides which kitchen (Backend Service)
#   5. Kitchen manager (Backend Service) picks a chef from the list (NEG)
#   6. Chef (API Gateway) actually makes the food
#   7. Bouncer (Cloud Armour) kicks out troublemakers throughout