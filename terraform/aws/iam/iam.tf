# IAM for medIoT Developer access

data "aws_caller_identity" "current" {}

locals {
  state_bucket_name = var.s3_backend_bucket != "" ? var.s3_backend_bucket : "mediot-tfstate"
}

# --- IAM Group ---
resource "aws_iam_group" "developer" {
  name = "Developer"
}

# --- Least-privilege managed policy ---
resource "aws_iam_policy" "developer" {
  name        = "mediot-Developer-terraform"
  description = "Permissions to run terraform apply on medIoT AWS infrastructure"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # ── VPC ──
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateVpc", "ec2:DeleteVpc", "ec2:DescribeVpcs", "ec2:ModifyVpcAttribute",
          "ec2:CreateSubnet", "ec2:DeleteSubnet", "ec2:DescribeSubnets",
          "ec2:CreateInternetGateway", "ec2:DeleteInternetGateway", "ec2:AttachInternetGateway", "ec2:DetachInternetGateway",
          "ec2:CreateNatGateway", "ec2:DeleteNatGateway", "ec2:DescribeNatGateways",
          "ec2:AllocateAddress", "ec2:ReleaseAddress", "ec2:DescribeAddresses",
          "ec2:CreateRouteTable", "ec2:DeleteRouteTable", "ec2:CreateRoute", "ec2:DeleteRoute",
          "ec2:AssociateRouteTable", "ec2:DisassociateRouteTable",
          "ec2:DescribeRouteTables", "ec2:DescribeAvailabilityZones",
        ]
        Resource = "*"
      },
      # ── Security Groups ──
      {
        Effect = "Allow"
        Action = [
          "ec2:CreateSecurityGroup", "ec2:DeleteSecurityGroup",
          "ec2:AuthorizeSecurityGroupIngress", "ec2:RevokeSecurityGroupIngress",
          "ec2:AuthorizeSecurityGroupEgress", "ec2:RevokeSecurityGroupEgress",
          "ec2:DescribeSecurityGroups", "ec2:DescribeSecurityGroupRules",
        ]
        Resource = "*"
      },
      # ── EKS ──
      {
        Effect = "Allow"
        Action = [
          "eks:CreateCluster", "eks:DeleteCluster", "eks:DescribeCluster",
          "eks:CreateNodegroup", "eks:DeleteNodegroup", "eks:DescribeNodegroup",
          "eks:ListClusters", "eks:ListNodegroups",
        ]
        Resource = "*"
      },
      # ── IAM (roles only — no user/group/policy management) ──
      {
        Effect = "Allow"
        Action = [
          "iam:CreateRole", "iam:DeleteRole", "iam:GetRole",
          "iam:PassRole", "iam:ListRoles", "iam:ListRolePolicies",
          "iam:AttachRolePolicy", "iam:DetachRolePolicy",
          "iam:ListAttachedRolePolicies", "iam:GetRolePolicy",
        ]
        Resource = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/mediot-*"
      },
      # ── IAM instance profiles (needed by EKS node groups) ──
      {
        Effect = "Allow"
        Action = [
          "iam:CreateInstanceProfile", "iam:DeleteInstanceProfile",
          "iam:GetInstanceProfile", "iam:AddRoleToInstanceProfile",
          "iam:RemoveRoleFromInstanceProfile", "iam:ListInstanceProfiles",
        ]
        Resource = "*"
      },
      # ── RDS ──
      {
        Effect = "Allow"
        Action = [
          "rds:CreateDBInstance", "rds:DeleteDBInstance", "rds:DescribeDBInstances",
          "rds:ModifyDBInstance", "rds:CreateDBSubnetGroup", "rds:DeleteDBSubnetGroup",
          "rds:DescribeDBSubnetGroups", "rds:ListTagsForResource",
        ]
        Resource = "*"
      },
      # ── ECR (for pushing container images) ──
      {
        Effect = "Allow"
        Action = [
          "ecr:CreateRepository", "ecr:DescribeRepositories",
          "ecr:GetAuthorizationToken", "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload", "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload", "ecr:PutImage",
        ]
        Resource = "*"
      },
      # ── S3 (Terraform state) ──
      {
        Effect = "Allow"
        Action = [
          "s3:CreateBucket", "s3:DeleteBucket", "s3:ListBucket",
          "s3:GetObject", "s3:PutObject", "s3:DeleteObject",
          "s3:GetBucketVersioning", "s3:PutBucketVersioning",
        ]
        Resource = [
          "arn:aws:s3:::${local.state_bucket_name}",
          "arn:aws:s3:::${local.state_bucket_name}/*",
        ]
      },
      # ── Deny sensitive IAM actions ──
      {
        Effect = "Deny"
        Action = [
          "iam:CreateUser", "iam:DeleteUser", "iam:CreateGroup", "iam:DeleteGroup",
          "iam:CreatePolicy", "iam:DeletePolicy", "iam:AttachUserPolicy",
          "organizations:*", "billing:*", "account:*", "iam:CreateAccountAlias",
        ]
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_group_policy_attachment" "developer" {
  group      = aws_iam_group.developer.name
  policy_arn = aws_iam_policy.developer.arn
}

resource "aws_iam_group_policy_attachment" "developer_login" {
  count      = var.attach_login_policy ? 1 : 0
  group      = aws_iam_group.developer.name
  policy_arn = "arn:aws:iam::aws:policy/SignInLocalDevelopmentAccess"
}

# --- Add users to group ---
resource "aws_iam_user_group_membership" "developer" {
  for_each = toset(var.developer_users)
  user     = each.key
  groups   = [aws_iam_group.developer.name]
}

# --- S3 backend for Terraform state ---
resource "aws_s3_bucket" "terraform_state" {
  bucket = local.state_bucket_name
}

resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
