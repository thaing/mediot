output "cluster_endpoint" { value = aws_eks_cluster.mediot.endpoint }
output "cluster_name" { value = aws_eks_cluster.mediot.name }
output "db_host" { value = aws_db_instance.postgres.address }
output "db_port" { value = aws_db_instance.postgres.port }
