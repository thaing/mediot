variable "region" { default = "us-east-1" }
variable "cluster_name" { default = "mediot-cluster" }
variable "node_instance_type" { default = "t3.medium" }
variable "node_count" { default = 2 }
variable "db_instance_class" { default = "db.t3.micro" }
variable "db_name" { default = "mediot" }
variable "db_username" { default = "mediot_admin" }
variable "db_password" { sensitive = true }
