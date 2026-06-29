# medIoT AWS — RDS PostgreSQL

data "aws_vpc" "mediot" {
  tags = { Name = "mediot-vpc" }
}

data "aws_subnets" "private" {
  filter {
    name   = "tag:Name"
    values = ["mediot-private-0", "mediot-private-1"]
  }
}

# RDS security group — allows inbound from VPC CIDR (survives EKS deletion)
resource "aws_security_group" "rds" {
  name   = "mediot-rds-sg"
  vpc_id = data.aws_vpc.mediot.id
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.mediot.cidr_block]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = { Name = "mediot-rds-sg" }
}

# RDS subnet group — private subnets for DB isolation
resource "aws_db_subnet_group" "mediot" {
  name       = "mediot-db-subnet"
  subnet_ids = data.aws_subnets.private.ids
}

resource "aws_db_instance" "postgres" {
  identifier              = "mediot-postgres"
  engine                  = "postgres"
  engine_version          = "16"
  instance_class          = var.db_instance_class
  allocated_storage       = 20
  db_name                 = var.db_name
  username                = var.db_username
  password                = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.mediot.name
  vpc_security_group_ids  = [aws_security_group.rds.id]
  publicly_accessible     = false
  skip_final_snapshot     = false
  deletion_protection     = true
}
