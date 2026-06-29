# medIoT AWS — VPC and networking foundation

terraform {
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
  required_version = ">= 1.5"

  backend "s3" {
    bucket  = "mediot-tfstate"
    key     = "main/terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }
}

provider "aws" { region = var.region }

data "aws_availability_zones" "available" { state = "available" }

# VPC
resource "aws_vpc" "mediot" {
  cidr_block           = "172.32.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "mediot-vpc" }
}

# Subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.mediot.id
  cidr_block              = "172.32.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "mediot-public-${count.index}" }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.mediot.id
  cidr_block        = "172.32.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]
  tags = { Name = "mediot-private-${count.index}" }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.mediot.id
  tags = { Name = "mediot-igw" }
}

# Route tables
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.mediot.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
