# medIoT — Installation Guide

Complete deployment instructions for the medIoT platform on AWS and GCP.

## Prerequisites

- **Terraform >= 1.5** — [Install](https://developer.hashicorp.com/terraform/downloads)
- **kubectl** — [Install](https://kubernetes.io/docs/tasks/tools/)
- **AWS CLI** (`aws`) or **gcloud CLI** (`gcloud`) — depending on target cloud
- **Docker** — for building container images
- **Minikube** — for local K8s testing (optional: verify images and manifests before cloud deploy)
- **Domain name** (optional) — for Ingress TLS

### kubectl context switching

Each platform creates its own kubectl context. List and switch between them:

```bash
kubectl config get-contexts          # see all contexts
kubectl config current-context        # which one is active

# Switch
kubectl config use-context minikube                           # local
kubectl config use-context arn:aws:eks:us-east-1:697957957974:cluster/mediot-cluster  # AWS
kubectl config use-context gke_PROJECT_us-central1_mediot-cluster                     # GCP
```

Contexts are created by `minikube start`, `aws eks update-kubeconfig`, and `gcloud container clusters get-credentials`. No setup needed beyond those commands.

---

## Local Development

No cloud resources needed. Uses SQLite, no Kafka, no Kubernetes.

### 1. Start the API

```bash
uvicorn src.app.main:app --port 8000 --reload
```

Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs).

### 2. Run the device simulator

```bash
# Default: device HM-2790, 1 reading/sec, starts at 100% battery
python scripts/simulator.py --api-key change-me-device-api-key

# Custom settings
python scripts/simulator.py --api-key change-me-device-api-key --device-id MY-DEVICE-01 --interval 0.5 --start-battery 50

# See all options
python scripts/simulator.py --help
```

POSTs randomized vitals to `/api/v1/readings/` every second. Battery drops 1% per 100 readings. Exits at 0%.

### 3. Start the frontend

```bash
cd frontend && npm install && npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Dev server proxies `/api` to port 8000.

---

## Minikube Testing

Verify all containers, manifests, and the full K8s topology before deploying to the cloud. Runs everything locally — no AWS or GCP needed.

### 1. Start Minikube

```bash
minikube start --cpus=4 --memory=8192
minikube addons enable ingress
```

### 2. Build images into Minikube's Docker

Point your shell at Minikube's Docker daemon, then build all images:

```bash
eval $(minikube docker-env)

docker build -t mediot-api:latest -f Dockerfile.api .
docker build -t mediot-worker:latest -f Dockerfile.worker .
docker build -t mediot-frontend:latest -f Dockerfile.frontend .
```

Images are now available inside the cluster — no registry needed.

### 3. Adjust manifests for local images

Replace ECR URIs with local image names (Minikube pulls from its own Docker):

```bash
cd k8s
sed -i 's|697957957974.dkr.ecr.us-east-1.amazonaws.com/mediot-api:latest|mediot-api:latest|' api-deployment.yaml
sed -i 's|697957957974.dkr.ecr.us-east-1.amazonaws.com/mediot-worker:latest|mediot-worker:latest|' worker-deployment.yaml
sed -i 's|697957957974.dkr.ecr.us-east-1.amazonaws.com/mediot-frontend:latest|mediot-frontend:latest|' frontend-deployment.yaml
```

Also make `imagePullPolicy: Never` (Minikube won't try to pull from a registry):

```bash
sed -i 's|imagePullPolicy: IfNotPresent|imagePullPolicy: Never|' api-deployment.yaml
sed -i 's|imagePullPolicy: IfNotPresent|imagePullPolicy: Never|' worker-deployment.yaml
sed -i 's|imagePullPolicy: IfNotPresent|imagePullPolicy: Never|' frontend-deployment.yaml
```

### 4. Update ConfigMap for local DB

Edit `k8s/configmap.yaml` — point at SQLite:

```yaml
KAFKA_BROKER: "kafka-service.mediot.svc.cluster.local:9092"
DATABASE_HOST: ""            # not used for SQLite
DATABASE_PORT: ""
DATABASE_NAME: ""
```

Edit `k8s/secret.yaml` — use SQLite + fill in placeholder secrets:

```yaml
DATABASE_URL: "sqlite:////app/mediot.db"
API_KEY: "change-me-device-api-key"
JWT_SECRET: "change-me-jwt-secret-at-least-32-characters"
```

### 5. Deploy

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/
```

### 6. Verify

```bash
# Wait for all pods
kubectl get pods -n mediot -w

# Expose the frontend
minikube service frontend-service -n mediot

# Or use ingress (after minikube addons enable ingress)
minikube ip
curl -H "Host: mediot.local" http://$(minikube ip)/api/docs
```

### 7. Clean up

```bash
kubectl delete -f k8s/
minikube stop
```

### 8. Revert manifests for cloud deployment

```bash
cd k8s
git checkout -- .
```

---

## AWS Deployment

### 1. Configure AWS credentials (admin)

```bash
aws configure
# Use admin credentials to create IAM resources
```

### 2. Create Developer IAM group (admin credentials)

```bash
cd terraform/aws/iam
terraform init
terraform apply -var='developer_users=["YOUR_USERNAME"]'
```

Add your IAM user to the Developer group, then switch to those credentials:

```bash
aws configure  # switch to Developer user credentials
```

### 3. Provision networking (VPC, subnets)

```bash
cd terraform/aws
terraform init
terraform apply
```

### 4. Provision EKS cluster

```bash
cd terraform/aws/eks
terraform init
terraform apply
```

### 5. Provision RDS PostgreSQL

```bash
cd terraform/aws/rds
terraform init
terraform apply -var='db_password=YourSecurePassword123!'
```

**Provisioned resources:** VPC (172.32.0.0/16), public subnets, IGW, EKS cluster (t3.medium nodes), RDS PostgreSQL (db.t3.micro, deletion-protected)

> **Cost tip:** Destroy EKS when not in use (`cd terraform/aws/eks && terraform destroy`). RDS in private subnets survives independently thanks to `deletion_protection = true`.

### 6. Configure kubectl

```bash
aws eks update-kubeconfig --region us-east-1 --name mediot-cluster
kubectl get nodes
```

### 7. Create secrets in AWS Secrets Manager

Create each secret manually (Developer group has `secretsmanager:*` permissions):

```bash
DB_PASSWORD=$(cd terraform/aws/rds && terraform output -raw db_password)
DB_HOST=$(cd terraform/aws/rds && terraform output -raw db_host)

aws secretsmanager create-secret --name mediot/database_url \
  --secret-string "postgresql://mediot_admin:${DB_PASSWORD}@${DB_HOST}:5432/mediot"

aws secretsmanager create-secret --name mediot/api_key \
  --secret-string "your-strong-device-api-key"

aws secretsmanager create-secret --name mediot/jwt_secret \
  --secret-string "$(openssl rand -base64 32)"

# OAuth secrets (optional — create only if using social login)
aws secretsmanager create-secret --name mediot/oauth_google_client_id --secret-string "..."
# ... (repeat for all OAuth secrets visible in k8s/secret.yaml)
```

### 8. Create K8s secret from AWS Secrets Manager

No file needed — values are fetched from Secrets Manager and piped straight into K8s:

```bash
kubectl -n mediot create secret generic mediot-secrets \
  --from-literal=DATABASE_URL="$(aws secretsmanager get-secret-value --secret-id mediot/database_url --query SecretString --output text)" \
  --from-literal=API_KEY="$(aws secretsmanager get-secret-value --secret-id mediot/api_key --query SecretString --output text)" \
  --from-literal=JWT_SECRET="$(aws secretsmanager get-secret-value --secret-id mediot/jwt_secret --query SecretString --output text)" \
  --from-literal=OAUTH_GOOGLE_CLIENT_ID="$(aws secretsmanager get-secret-value --secret-id mediot/oauth_google_client_id --query SecretString --output text)" \
  --from-literal=OAUTH_GOOGLE_CLIENT_SECRET="$(aws secretsmanager get-secret-value --secret-id mediot/oauth_google_client_secret --query SecretString --output text)" \
  --from-literal=OAUTH_APPLE_CLIENT_ID="$(aws secretsmanager get-secret-value --secret-id mediot/oauth_apple_client_id --query SecretString --output text)" \
  --from-literal=OAUTH_APPLE_CLIENT_SECRET="$(aws secretsmanager get-secret-value --secret-id mediot/oauth_apple_client_secret --query SecretString --output text)" \
  --from-literal=OAUTH_FACEBOOK_CLIENT_ID="$(aws secretsmanager get-secret-value --secret-id mediot/oauth_facebook_client_id --query SecretString --output text)" \
  --from-literal=OAUTH_FACEBOOK_CLIENT_SECRET="$(aws secretsmanager get-secret-value --secret-id mediot/oauth_facebook_client_secret --query SecretString --output text)" \
  --dry-run=client -o yaml | kubectl apply -f -
```

> `k8s/secret.yaml` is a reference template — never applied in cloud deployments.

### 9. Build and push container images

```bash
# API
docker build -t mediot-api:latest -f Dockerfile.api .
aws ecr create-repository --repository-name mediot-api
docker tag mediot-api:latest <aws-account>.dkr.ecr.us-east-1.amazonaws.com/mediot-api:latest
docker push <aws-account>.dkr.ecr.us-east-1.amazonaws.com/mediot-api:latest

# Worker
docker build -t mediot-worker:latest -f Dockerfile.worker .
aws ecr create-repository --repository-name mediot-worker
docker tag mediot-worker:latest <aws-account>.dkr.ecr.us-east-1.amazonaws.com/mediot-worker:latest
docker push <aws-account>.dkr.ecr.us-east-1.amazonaws.com/mediot-worker:latest

# Frontend
docker build -t mediot-frontend:latest -f Dockerfile.frontend .
aws ecr create-repository --repository-name mediot-frontend
docker tag mediot-frontend:latest <aws-account>.dkr.ecr.us-east-1.amazonaws.com/mediot-frontend:latest
docker push <aws-account>.dkr.ecr.us-east-1.amazonaws.com/mediot-frontend:latest
```

### 10. Update ConfigMap

Edit `k8s/configmap.yaml` and replace `DATABASE_HOST` with the RDS endpoint from the `db_host` Terraform output.

### 11. Deploy to Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/kafka-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### 10. Verify deployment

```bash
kubectl get pods -n mediot
kubectl get ingress -n mediot
# Access the application at the Ingress address
```

---

## GCP Deployment

### 1. Configure gcloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable container.googleapis.com sqladmin.googleapis.com
```

### 2. Initialize and apply Terraform

```bash
cd terraform/gcp
terraform init
terraform plan -var="project_id=YOUR_PROJECT_ID" -var="db_password=YourSecurePassword123!"
terraform apply -var="project_id=YOUR_PROJECT_ID" -var="db_password=YourSecurePassword123!"
```

**Provisioned resources:** VPC, subnet, GKE cluster (2 e2-medium nodes), Cloud SQL PostgreSQL (db-f1-micro), firewall rules

### 3. Configure kubectl

```bash
gcloud container clusters get-credentials mediot-cluster --region us-central1
kubectl get nodes
```

### 4. Create secrets in GCP Secret Manager

```bash
DB_PASSWORD=YourSecurePassword123!
DB_PRIVATE_IP=$(cd terraform/gcp && terraform output -raw db_private_ip 2>/dev/null || echo "YOUR_DB_IP")

echo -n "postgresql://mediot_admin:${DB_PASSWORD}@${DB_PRIVATE_IP}:5432/mediot" | \
  gcloud secrets create mediot-database-url --data-file=-

echo -n "your-strong-device-api-key" | gcloud secrets create mediot-api-key --data-file=-
echo -n "$(openssl rand -base64 32)" | gcloud secrets create mediot-jwt-secret --data-file=-
# ... create remaining OAuth secrets as needed
```

### 5. Create K8s secret from GCP Secret Manager

No file needed — values fetched from Secret Manager straight into K8s:

```bash
kubectl -n mediot create secret generic mediot-secrets \
  --from-literal=DATABASE_URL="$(gcloud secrets versions access latest --secret=mediot-database-url)" \
  --from-literal=API_KEY="$(gcloud secrets versions access latest --secret=mediot-api-key)" \
  --from-literal=JWT_SECRET="$(gcloud secrets versions access latest --secret=mediot-jwt-secret)" \
  --dry-run=client -o yaml | kubectl apply -f -
```

> `k8s/secret.yaml` is a reference template — never applied in cloud deployments.

### 6. Build and push container images (GCP)

```bash
docker build -t gcr.io/YOUR_PROJECT_ID/mediot-api:latest -f Dockerfile.api .
docker push gcr.io/YOUR_PROJECT_ID/mediot-api:latest

docker build -t gcr.io/YOUR_PROJECT_ID/mediot-worker:latest -f Dockerfile.worker .
docker push gcr.io/YOUR_PROJECT_ID/mediot-worker:latest

docker build -t gcr.io/YOUR_PROJECT_ID/mediot-frontend:latest -f Dockerfile.frontend .
docker push gcr.io/YOUR_PROJECT_ID/mediot-frontend:latest
```

### 7. Update ConfigMap

Edit `k8s/configmap.yaml` — replace `DATABASE_HOST` with the Cloud SQL private IP.

### 8. Deploy to Kubernetes

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/kafka-deployment.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### 9. Verify deployment

```bash
kubectl get pods -n mediot
kubectl get svc -n mediot  # get external IP for Ingress
```

---

## Post-Deployment Verification

### Run the device simulator

```bash
export API_URL=http://<INGRESS_ADDRESS>
export API_KEY=<your-api-key-from-k8s-secret>
python scripts/simulator.py
```

### Check the API

```bash
curl -H "X-API-Key: your-key" http://<INGRESS_ADDRESS>/api/v1/readings/ -d '{"ts":1782561130,"d_id":"HM-2790","hr":78,"spo2":97,"bp_sys":122,"bp_dia":81,"bat":86}'
```

### Open the frontend

Navigate to the Ingress URL, sign in with a social provider, and verify real-time dashboard charts render.
