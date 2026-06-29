output "developer_group_arn" {
  value = aws_iam_group.developer.arn
}

output "developer_policy_arn" {
  value = aws_iam_policy.developer.arn
}

output "terraform_state_bucket" {
  value = local.state_bucket_name
}
