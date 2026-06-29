output "cluster_endpoint" { value = aws_eks_cluster.mediot.endpoint }
output "cluster_name" { value = aws_eks_cluster.mediot.name }
output "cluster_security_group_id" { value = aws_eks_cluster.mediot.vpc_config[0].cluster_security_group_id }
