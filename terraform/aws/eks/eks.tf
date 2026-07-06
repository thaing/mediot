# medIoT AWS — EKS cluster and node group

data "aws_vpc" "mediot" {
  tags = { Name = "mediot-vpc" }
}

data "aws_subnets" "public" {
  filter {
    name   = "tag:Name"
    values = ["mediot-public-0", "mediot-public-1"]
  }
}

data "aws_subnets" "private" {
  filter {
    name   = "tag:Name"
    values = ["mediot-private-0", "mediot-private-1"]
  }
}

# EKS cluster IAM role
resource "aws_iam_role" "eks_cluster" {
  name = "mediot-eks-cluster"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster" {
  role       = aws_iam_role.eks_cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# EKS cluster
resource "aws_eks_cluster" "mediot" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn
  vpc_config {
    subnet_ids = concat(data.aws_subnets.public.ids, data.aws_subnets.private.ids)
  }
  access_config {
    authentication_mode = "API_AND_CONFIG_MAP"
  }
  depends_on = [aws_iam_role_policy_attachment.eks_cluster]
}

# EKS node group IAM role
resource "aws_iam_role" "eks_node" {
  name = "mediot-eks-node"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_node" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "eks_cni" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "ecr_read" {
  role       = aws_iam_role.eks_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# Inline policy: allow ESO to read secrets from Secrets Manager
resource "aws_iam_role_policy" "eks_node_secrets" {
  name = "mediot-secrets-read"
  role = aws_iam_role.eks_node.name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = ["secretsmanager:GetSecretValue", "secretsmanager:DescribeSecret"]
      Resource = "*"
    }]
  })
}

# EKS node group
resource "aws_eks_node_group" "mediot" {
  cluster_name    = aws_eks_cluster.mediot.name
  node_group_name = "mediot-nodes"
  node_role_arn   = aws_iam_role.eks_node.arn
  subnet_ids      = data.aws_subnets.public.ids
  instance_types  = [var.node_instance_type]
  scaling_config {
    desired_size = var.node_count
    min_size     = 1
    max_size     = 4
  }
  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node,
    aws_iam_role_policy_attachment.eks_cni,
    aws_iam_role_policy_attachment.ecr_read,
  ]
}

# EKS access entry — grant Developer IAM user kubectl access
resource "aws_eks_access_entry" "developer" {
  cluster_name  = aws_eks_cluster.mediot.name
  principal_arn = var.developer_iam_arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "developer_admin" {
  cluster_name  = aws_eks_cluster.mediot.name
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
  principal_arn = var.developer_iam_arn
  access_scope {
    type = "cluster"
  }
}
