variable "project_id" {}
variable "region" { default = "us-central1" }
variable "cluster_name" { default = "mediot-cluster" }
variable "node_machine_type" { default = "e2-medium" }
variable "node_count" { default = 2 }
variable "db_tier" { default = "db-f1-micro" }
variable "db_name" { default = "mediot" }
variable "db_username" { default = "mediot_admin" }
variable "db_password" { sensitive = true }
