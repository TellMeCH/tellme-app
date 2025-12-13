provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Cloud Armour Security Policy with EU geo-restriction
resource "google_compute_security_policy" "api_security_policy" {
  name        = "tellme-api-security-policy"
  project     = var.project_id
  description = "Security policy for TellMe API with EU geo-restriction, DDoS protection and WAF rules"

  # ALLOW GITHUB ACTIONS RUNNERS
  # GitHub Actions IP ranges from https://api.github.com/meta (actions field)
  # Note: Update periodically to maintain current list
  rule {
    action   = "allow"
    priority = "50"
    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = [
          # GitHub Actions IPv4 ranges (partial list - major ranges)
          "4.148.0.0/16", "4.149.0.0/17", "4.150.0.0/17", "4.151.0.0/16",
          "4.152.0.0/15", "4.154.0.0/15", "4.156.0.0/15", "4.175.0.0/16",
          "4.180.0.0/16", "4.207.0.0/16", "4.208.0.0/15", "4.210.0.0/16",
          "4.227.0.0/16", "4.231.0.0/16", "4.236.0.0/16", "4.242.0.0/16",
          "4.245.0.0/16", "4.246.0.0/16", "4.249.0.0/16", "4.255.0.0/16",
          "9.93.0.0/18", "9.93.64.0/20", "9.93.80.0/20", "9.93.96.0/21",
          "9.93.104.0/21", "9.93.112.0/21", "9.93.120.0/21", "9.93.128.0/18",
          "13.64.0.0/11", "13.104.0.0/14", "20.20.0.0/16", "20.21.0.0/16",
          "20.26.0.0/16", "20.29.0.0/16", "20.33.0.0/16", "20.38.0.0/16",
          "20.42.0.0/16", "20.45.0.0/16", "20.49.0.0/16", "20.51.0.0/16",
          "20.57.0.0/16", "20.59.0.0/16", "20.65.0.0/16", "20.72.0.0/16",
          "20.83.0.0/16", "20.84.0.0/16", "20.96.0.0/12", "20.112.0.0/13",
          "20.120.0.0/14", "20.124.0.0/16", "20.125.0.0/16", "20.135.0.0/16",
          "20.150.0.0/15", "20.157.0.0/16", "20.189.0.0/16", "20.190.0.0/15",
          "20.192.0.0/10", "23.96.0.0/13", "40.64.0.0/10", "48.208.0.0/12",
          "52.96.0.0/12", "52.112.0.0/14", "52.184.0.0/13", "52.224.0.0/11",
          "57.128.0.0/9"
        ]
      }
    }
    description = "Allow GitHub Actions runners from all regions"
  }

  # BLOCK NON-EUROPEAN TRAFFIC
  rule {
    action   = "deny(403)"
    priority = "100"
    match {
      expr {
        expression = "!origin.region_code.matches('AT|BE|BG|HR|CY|CZ|DK|EE|FI|FR|DE|GR|HU|IE|IT|LV|LT|LU|MT|NL|PL|PT|RO|SK|SI|ES|SE|CH|NO|IS|LI|GB')"
      }
    }
    description = "Block traffic from outside Europe"
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

  # SQL Injection
  rule {
    action   = "deny(403)"
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
          request.headers['user-agent'].lower().matches('.*sqlmap.*|.*nikto.*|.*nessus.*|.*masscan.*|.*gobuster.*|.*dirb.*|.*burp.*')
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
    "X-Forwarded-Proto: https"
  ]
}

# Serverless Network Endpoint Group for API Gateway
resource "google_compute_region_network_endpoint_group" "api_gateway_neg" {
  provider              = google-beta
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

    default_route_action {
      weighted_backend_services {
        backend_service = google_compute_backend_service.api_backend.id
        weight          = 100
      }
    }

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
  ssl_certificates = [google_compute_managed_ssl_certificate.api_ssl_cert.id]
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
# 2. Neon sign (Forwarding Rule) directs them to IP address
# 3. Fancy doorman (HTTPS Proxy) checks their SSL credentials
# 4. Seating chart (URL Map) decides which kitchen (Backend Service)
# 5. Kitchen manager (Backend Service) picks a chef from the list (NEG)
# 6. Chef (API Gateway) actually makes the food
# 7. Bouncer (Cloud Armour) kicks out troublemakers throughout