variable "developer_members" {
  description = "List of members to bind the Developer role to (e.g., ['user:dev@example.com', 'group:developers@example.com'])"
  type        = list(string)
  default     = []
}
