# IAM for medIoT Developer access on GCP

# --- Custom IAM Role ---
resource "google_project_iam_custom_role" "mediot_developer" {
  role_id     = "mediotDeveloper"
  title       = "medIoT Developer"
  description = "Least-privilege permissions to run terraform apply on medIoT GCP infrastructure"
  project     = var.project_id

  permissions = [
    # VPC / Networking
    "compute.networks.create",
    "compute.networks.delete",
    "compute.networks.get",
    "compute.networks.updatePolicy",
    "compute.subnetworks.create",
    "compute.subnetworks.delete",
    "compute.subnetworks.get",
    "compute.subnetworks.use",
    # Firewall
    "compute.firewalls.create",
    "compute.firewalls.delete",
    "compute.firewalls.get",
    "compute.globalOperations.get",
    # GKE
    "container.clusters.create",
    "container.clusters.delete",
    "container.clusters.get",
    "container.clusters.update",
    "container.operations.get",
    # Cloud SQL
    "cloudsql.instances.create",
    "cloudsql.instances.delete",
    "cloudsql.instances.get",
    "cloudsql.databases.create",
    "cloudsql.databases.delete",
    "cloudsql.users.create",
    "cloudsql.users.delete",
    # Service Accounts (read-only — cannot create/delete SAs or change policy)
    "iam.serviceAccounts.get",
    "iam.serviceAccounts.list",
    # Cloud Storage (Terraform state)
    "storage.buckets.create",
    "storage.buckets.delete",
    "storage.buckets.get",
    "storage.objects.create",
    "storage.objects.delete",
    "storage.objects.get",
    # Project-level read
    "resourcemanager.projects.get",
  ]
}

# --- Bind role to developer members at project level ---
resource "google_project_iam_binding" "developer" {
  project = var.project_id
  role    = google_project_iam_custom_role.mediot_developer.id
  members = var.developer_members

  # Skip if no members configured yet
  count = length(var.developer_members) > 0 ? 1 : 0
}

# --- GCS backend for Terraform state ---
resource "google_storage_bucket" "terraform_state" {
  name          = "${var.project_id}-mediot-tfstate"
  location      = var.region
  force_destroy = false

  versioning {
    enabled = true
  }

  # Prevent accidental public exposure
  public_access_prevention = "enforced"
}
