# Suna Ultra - Kubernetes Deployment

Production-grade Kubernetes manifests for deploying Suna Ultra at scale.

## Prerequisites

- Kubernetes 1.24+
- kubectl configured
- At least 8GB RAM per node
- 50GB storage available
- Ingress controller (nginx)
- cert-manager (for TLS)

## Quick Start

### 1️⃣ Create Namespace

```bash
kubectl apply -f namespace.yaml
```

### 2️⃣ Configure Secrets

Edit `secrets.yaml` with your actual values:

```bash
# Generate secrets
openssl rand -hex 32  # SECRET_KEY
openssl rand -hex 16  # DB_PASSWORD
```

Or create from command line:

```bash
kubectl create secret generic suna-secrets \
  --namespace=suna-ultra \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-xxx \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32) \
  --from-literal=DB_PASSWORD=$(openssl rand -hex 16) \
  --from-literal=SUPABASE_URL=https://xxx.supabase.co \
  --from-literal=SUPABASE_ANON_KEY=eyJ... \
  --from-literal=SUPABASE_SERVICE_ROLE_KEY=eyJ... \
  --from-literal=SUPABASE_JWT_SECRET=xxx
```

### 3️⃣ Deploy Infrastructure

```bash
# ConfigMap
kubectl apply -f configmap.yaml

# Storage
kubectl apply -f redis/pvc.yaml
kubectl apply -f postgres/pvc.yaml

# Databases
kubectl apply -f redis/deployment.yaml
kubectl apply -f redis/service.yaml
kubectl apply -f postgres/deployment.yaml
kubectl apply -f postgres/service.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n suna-ultra --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n suna-ultra --timeout=300s
```

### 4️⃣ Deploy Application

```bash
# Backend
kubectl apply -f backend/deployment.yaml
kubectl apply -f backend/service.yaml
kubectl apply -f backend/hpa.yaml

# Workers
kubectl apply -f worker/deployment.yaml
kubectl apply -f worker/hpa.yaml

# Wait for application to be ready
kubectl wait --for=condition=ready pod -l app=suna-backend -n suna-ultra --timeout=300s
```

### 5️⃣ Configure Ingress

Edit `ingress.yaml` and set your domain:

```yaml
spec:
  tls:
  - hosts:
    - suna.yourdomain.com
  rules:
  - host: suna.yourdomain.com
```

Apply ingress:

```bash
kubectl apply -f ingress.yaml
```

### 6️⃣ Verify Deployment

```bash
# Check all resources
kubectl get all -n suna-ultra

# Check pod status
kubectl get pods -n suna-ultra

# Check logs
kubectl logs -n suna-ultra -l app=suna-backend --tail=50

# Port forward for testing
kubectl port-forward -n suna-ultra svc/suna-backend 8000:8000
```

Access at: http://localhost:8000/health

## Architecture

### Services

```
┌─────────────┐
│   Ingress   │ (HTTPS, Rate Limiting)
└──────┬──────┘
       │
┌──────▼──────┐
│   Backend   │ (2-10 pods, HPA)
└──────┬──────┘
       │
  ┌────┴────┐
  │         │
┌─▼─┐   ┌──▼───┐
│DB │   │Redis │
└───┘   └──────┘
  │         │
  │    ┌────▼────┐
  │    │ Workers │ (2-8 pods, HPA)
  │    └─────────┘
  │
┌─▼─────────┐
│ PostgreSQL│
│    PVC    │
└───────────┘
```

### Components

- **backend**: FastAPI application (2-10 replicas)
- **worker**: Dramatiq background workers (2-8 replicas)
- **postgres**: PostgreSQL 15 with persistent storage
- **redis**: Redis 7 with persistent storage
- **ingress**: NGINX ingress with TLS

## Configuration

### Resource Requests/Limits

#### Backend

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

#### Worker

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### Auto-scaling

#### Backend HPA

- Min: 2 replicas
- Max: 10 replicas
- CPU target: 70%
- Memory target: 80%

#### Worker HPA

- Min: 2 replicas
- Max: 8 replicas
- CPU target: 75%
- Memory target: 85%

### Storage

#### PostgreSQL PVC

- Size: 20Gi
- Access: ReadWriteOnce
- StorageClass: standard

#### Redis PVC

- Size: 10Gi
- Access: ReadWriteOnce
- StorageClass: standard

## Operations

### Scaling

#### Manual Scaling

```bash
# Scale backend
kubectl scale deployment suna-backend -n suna-ultra --replicas=5

# Scale workers
kubectl scale deployment suna-worker -n suna-ultra --replicas=4
```

#### Auto-scaling

Edit HPA configuration:

```bash
kubectl edit hpa suna-backend-hpa -n suna-ultra
```

### Updates

#### Rolling Update

```bash
# Update backend image
kubectl set image deployment/suna-backend \
  backend=suna-ultra/backend:v2.0 \
  -n suna-ultra

# Check rollout status
kubectl rollout status deployment/suna-backend -n suna-ultra

# Rollback if needed
kubectl rollout undo deployment/suna-backend -n suna-ultra
```

### Monitoring

#### Pod Status

```bash
# All pods
kubectl get pods -n suna-ultra -o wide

# Watch pods
kubectl get pods -n suna-ultra -w

# Pod details
kubectl describe pod <pod-name> -n suna-ultra
```

#### Logs

```bash
# Recent logs
kubectl logs -n suna-ultra -l app=suna-backend --tail=100

# Follow logs
kubectl logs -n suna-ultra -l app=suna-backend -f

# Previous container logs
kubectl logs -n suna-ultra <pod-name> --previous
```

#### Events

```bash
kubectl get events -n suna-ultra --sort-by='.lastTimestamp'
```

#### Resource Usage

```bash
# Node usage
kubectl top nodes

# Pod usage
kubectl top pods -n suna-ultra

# Container usage
kubectl top pod <pod-name> -n suna-ultra --containers
```

### Health Checks

```bash
# Backend health
kubectl exec -n suna-ultra deployment/suna-backend -- curl -f http://localhost:8000/health

# PostgreSQL
kubectl exec -n suna-ultra deployment/postgres -- pg_isready -U suna

# Redis
kubectl exec -n suna-ultra deployment/redis -- redis-cli ping
```

## Backup & Restore

### PostgreSQL Backup

```bash
# Create backup
kubectl exec -n suna-ultra deployment/postgres -- \
  pg_dump -U suna suna_ultra > backup-$(date +%Y%m%d).sql

# Schedule with CronJob
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
  namespace: suna-ultra
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:15-alpine
            command:
            - sh
            - -c
            - pg_dump -h postgres-service -U suna suna_ultra | gzip > /backup/db-\$(date +%Y%m%d-%H%M%S).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: suna-secrets
                  key: DB_PASSWORD
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
EOF
```

### PostgreSQL Restore

```bash
# Restore from backup
kubectl exec -i -n suna-ultra deployment/postgres -- \
  psql -U suna suna_ultra < backup-20240101.sql
```

### Redis Backup

```bash
# Trigger BGSAVE
kubectl exec -n suna-ultra deployment/redis -- redis-cli BGSAVE

# Copy dump.rdb
kubectl cp suna-ultra/redis-pod:/data/dump.rdb ./redis-backup.rdb
```

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n suna-ultra

# Describe pod
kubectl describe pod <pod-name> -n suna-ultra

# Check events
kubectl get events -n suna-ultra

# Check logs
kubectl logs <pod-name> -n suna-ultra
```

### Common Issues

#### ImagePullBackOff

```bash
# Check image name
kubectl describe pod <pod-name> -n suna-ultra | grep Image

# Update image
kubectl set image deployment/suna-backend backend=correct-image:tag -n suna-ultra
```

#### CrashLoopBackOff

```bash
# Check logs
kubectl logs <pod-name> -n suna-ultra --previous

# Check configuration
kubectl get configmap suna-config -n suna-ultra -o yaml
kubectl get secret suna-secrets -n suna-ultra -o yaml
```

#### Pending Pods

```bash
# Check resources
kubectl describe node

# Check PVC status
kubectl get pvc -n suna-ultra

# Check events
kubectl get events -n suna-ultra | grep Pending
```

### Database Connection Issues

```bash
# Test PostgreSQL
kubectl exec -n suna-ultra deployment/postgres -- \
  psql -U suna -d suna_ultra -c "SELECT version();"

# Test Redis
kubectl exec -n suna-ultra deployment/redis -- \
  redis-cli ping

# Check service DNS
kubectl exec -n suna-ultra deployment/suna-backend -- \
  nslookup postgres-service
```

## Security

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: suna-network-policy
  namespace: suna-ultra
spec:
  podSelector:
    matchLabels:
      app: suna-backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

### RBAC

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: suna-role
  namespace: suna-ultra
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: suna-rolebinding
  namespace: suna-ultra
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: suna-role
subjects:
- kind: ServiceAccount
  name: default
  namespace: suna-ultra
```

### Pod Security

```yaml
# Add to deployment spec
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: backend
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
```

## Monitoring & Observability

### Prometheus Metrics

```yaml
apiVersion: v1
kind: Service
metadata:
  name: suna-backend-metrics
  namespace: suna-ultra
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8000"
    prometheus.io/path: "/metrics"
spec:
  selector:
    app: suna-backend
  ports:
  - port: 8000
    targetPort: 8000
```

### Grafana Dashboard

Import dashboard for monitoring:
- Pod CPU/Memory usage
- Request rate and latency
- Error rates
- Queue lengths (Redis)

## Advanced Configuration

### Multiple Environments

```bash
# Staging
kubectl apply -k overlays/staging/

# Production
kubectl apply -k overlays/production/
```

### Custom Storage Classes

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-ssd
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
  replication-type: regional-pd
```

Update PVC:

```yaml
spec:
  storageClassName: fast-ssd
```

### External Secrets

Use external-secrets operator:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: suna-secrets
  namespace: suna-ultra
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: suna-secrets
  data:
  - secretKey: ANTHROPIC_API_KEY
    remoteRef:
      key: suna/anthropic-key
```

## Production Checklist

- [ ] Set appropriate resource limits
- [ ] Configure HPA thresholds
- [ ] Set up persistent storage
- [ ] Configure ingress and TLS
- [ ] Set up monitoring and alerts
- [ ] Configure backups
- [ ] Implement network policies
- [ ] Set up RBAC
- [ ] Configure pod security policies
- [ ] Set up log aggregation
- [ ] Document runbooks
- [ ] Test disaster recovery

## Support

- Documentation: [/docs](../../docs/)
- Issues: [GitHub Issues](https://github.com/Danthemainman1/suna-enhanced/issues)
- Discord: [Join Community](https://discord.gg/RvFhXUdZ9H)

## License

Apache License 2.0 - See [LICENSE](../../LICENSE)
