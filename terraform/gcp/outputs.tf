output "cluster_endpoint" { value = google_container_cluster.mediot.endpoint }
output "cluster_name" { value = google_container_cluster.mediot.name }
output "db_connection_name" { value = google_sql_database_instance.postgres.connection_name }
output "db_private_ip" { value = google_sql_database_instance.postgres.private_ip_address }
