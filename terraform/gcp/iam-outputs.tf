output "developer_role_id" {
  value = google_project_iam_custom_role.mediot_developer.role_id
}

output "terraform_state_bucket" {
  value = google_storage_bucket.terraform_state.name
}
