variable "region" {
  description = "AWS region for the IAM resources"
  type        = string
  default     = "us-east-1"
}

variable "developer_users" {
  description = "IAM usernames to add to the Developer group"
  type        = list(string)
  default     = []
}

variable "s3_backend_bucket" {
  description = "S3 bucket for Terraform state (auto-created if empty)"
  type        = string
  default     = ""
}

variable "attach_login_policy" {
  description = "Attach SignInLocalDevelopmentAccess (custom policy) to Developer group"
  type        = bool
  default     = false
}
