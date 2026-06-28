terraform {
  required_providers {
    google = { source = "hashicorp/google", version = "~> 5.0" }
  }
  required_version = ">= 1.5"
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# VPC
resource "google_compute_network" "mediot" {
  name                    = "mediot-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "mediot" {
  name          = "mediot-subnet"
  network       = google_compute_network.mediot.id
  region        = var.region
  ip_cidr_range = "10.0.0.0/16"
}

# GKE
resource "google_container_cluster" "mediot" {
  name     = var.cluster_name
  location = var.region
  network  = google_compute_network.mediot.name
  subnetwork = google_compute_subnetwork.mediot.name
  initial_node_count = var.node_count
  node_config {
    machine_type = var.node_machine_type
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]
  }
}

# Cloud SQL
resource "google_sql_database_instance" "postgres" {
  name             = "mediot-postgres"
  database_version = "POSTGRES_16"
  region           = var.region
  settings {
    tier              = var.db_tier
    disk_size         = 20
    availability_type = "ZONAL"
    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.mediot.id
    }
  }
  deletion_protection = false
}

resource "google_sql_database" "mediot" {
  name     = var.db_name
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "mediot" {
  name     = var.db_username
  instance = google_sql_database_instance.postgres.name
  password = var.db_password
}

# Firewall for GKE → Cloud SQL
resource "google_compute_firewall" "allow_http" {
  name    = "mediot-allow-http"
  network = google_compute_network.mediot.name
  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }
  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_firewall" "allow_gke_to_sql" {
  name    = "mediot-gke-to-sql"
  network = google_compute_network.mediot.name
  allow {
    protocol = "tcp"
    ports    = ["5432"]
  }
  source_ranges = [google_compute_subnetwork.mediot.ip_cidr_range]
}
