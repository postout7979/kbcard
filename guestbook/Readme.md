## Guestbook Application

```bash
# namespace를 생성합니다.
kubectl create namespace guestbook
kubectl label --overwrite ns guestbook pod-security.kubernetes.io/enforce=privileged

```

## Guestbook yaml 파일 생성

```yaml
cat << EOF > redis-leader-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-leader-deployment
  namespace: guestbook
spec:
  selector:
    matchLabels:
      app: redis
      role: leader
      tier: backend
  replicas: 1
  template:
    metadata:
      labels:
        app: redis
        role: leader
        tier: backend
    spec:
      containers:
      - name: leader
        image: redis:6.0.5
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-leader-data
          mountPath: /data
      volumes: 
      - name: redis-leader-data
        persistentVolumeClaim:
          claimName: redis-leader-pvc
EOF
```

```yaml

cat << EOF > redis-leader-pvc.yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: redis-leader-pvc
  namespace: guestbook
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: tanzu-storage-policy
  resources:
    requests:
      storage: 2Gi
EOF
```

```yaml
cat << EOF > redis-follower-pvc.yaml
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: redis-follower-pvc
  namespace: guestbook
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: tanzu-storage-policy
  resources:
    requests:
      storage: 2Gi
EOF
```

```yaml
cat << EOF > redis-follower-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-follower-deployment
  namespace: guestbook
  labels:
    app: redis
spec:
  selector:
    matchLabels:
      app: redis
      role: follower
      tier: backend
  replicas: 1
  template:
    metadata:
      labels:
        app: redis
        role: follower
        tier: backend
    spec:
      containers:
      - name: follower
        image: us-docker.pkg.dev/google-samples/containers/gke/gb-redis-follower:v2
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
        env:
        - name: GET_HOSTS_FROM
          value: dns
        ports:
        - containerPort: 6379
        volumeMounts:
        - name: redis-follower-data
          mountPath: /data
      volumes: 
      - name: redis-follower-data
        persistentVolumeClaim:
          claimName: redis-follower-pvc
EOF
```

```yaml
cat << EOF > redis-leader-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-leader
  namespace: guestbook
  labels:
    app: redis
    role: leader
    tier: backend
spec:
  ports:
  - port: 6379
    targetPort: 6379
  selector:
    app: redis
    role: leader
    tier: backend
EOF
```

```yaml
cat << EOF > redis-follower-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: redis-follower
  namespace: guestbook
  labels:
    app: redis
    role: follower
    tier: backend
spec:
  ports:
  - port: 6379
  selector:
    app: redis
    role: follower
    tier: backend
EOF

```

```yaml
cat << EOF > guestbook-frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: guestbook-frontend-deployment
  namespace: guestbook
spec:
  selector:
    matchLabels:
      app: guestbook
      tier: frontend
  replicas: 3
  template:
    metadata:
      labels:
        app: guestbook
        tier: frontend
    spec:
      containers:
      - name: php-redis
        image: us-docker.pkg.dev/google-samples/containers/gke/gb-frontend:v5
        resources:
          requests:
            cpu: 100m
            memory: 100Mi
        env:
        - name: GET_HOSTS_FROM
          value: dns
        ports:
        - containerPort: 80
EOF
```

```yaml

cat << EOF > guestbook-frontend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: guestbook-frontend
  namespace: guestbook
  labels:
    app: guestbook
    tier: frontend
spec:
  type: LoadBalancer
  ports:
  - port: 80
  selector:
    app: guestbook
    tier: frontend
EOF

```

모든 yaml 파일을 적용합니다.

```bash
kubectl apply -f .
```

배포 구성 요소를 확인합니다.

```bash
kubectl get po,svc -n guestbook
```

-
