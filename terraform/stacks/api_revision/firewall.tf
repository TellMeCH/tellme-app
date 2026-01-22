# ==============================================================================
# Firewall Rules (Drata Compliance - Denial of Public SSH)
# ==============================================================================
# GCP automatically creates a default VPC network with "default-allow-ssh" rule
# that allows SSH from 0.0.0.0/0 (entire internet) with priority 65534.
#
# Since we use serverless architecture (Cloud Run, Cloud SQL) with no compute
# instances, we create a higher-priority DENY rule to block public SSH access.
#
# This rule takes precedence over the default-allow-ssh rule and ensures Drata
# compliance without affecting our application (which doesn't use SSH).
# ==============================================================================

# Explicitly deny SSH from public internet (overrides GCP default-allow-ssh)
resource "google_compute_firewall" "deny_public_ssh" {
  name        = "deny-public-ssh"
  network     = "default"
  project     = var.project_id
  priority    = 65533  # Higher priority (lower number) than default-allow-ssh (65534)

  deny {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]

  description = "Explicitly deny SSH from public internet for Drata compliance (overrides default-allow-ssh)"
}
