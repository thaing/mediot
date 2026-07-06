variable "region" { default = "us-east-1" }
variable "cluster_name" { default = "mediot-cluster" }
variable "node_instance_type" { default = "t3.medium" }
variable "node_count" { default = 1 }
variable "developer_iam_arn" {
  description = "ARN of the Developer IAM user or role for EKS cluster access"
  type        = string
  default     = "arn:aws:iam::697957957974:user/mediot"
}
