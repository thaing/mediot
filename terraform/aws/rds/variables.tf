variable "region" { default = "us-east-1" }
variable "db_instance_class" { default = "db.t3.micro" }
variable "db_name" { default = "mediot" }
variable "db_username" { default = "mediot_admin" }
variable "db_password" { sensitive = true }
