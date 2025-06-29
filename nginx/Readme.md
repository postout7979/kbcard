### APP 배포 및 서비스 L4 연결

namespace을 생성하고, 권한을 부여합니다.

```bash
kubectl create ns nginx
kubectl label --overwrite ns nginx pod-security.kubernetes.io/enforce=privileged
```

```yaml
mkdir nginx
cd nginx
```

Deployment yaml 파일을 작성합니다.

```yaml
cat << EOF > deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx
  namespace: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hello
  template:
    metadata:
      labels:
        app: hello
        tier: frontend
    spec:
      containers:
      - name: nginx
        image: "nginxdemos/hello"
EOF
```

deployment.yaml을 적용합니다.

```yaml
kubectl apply -f deployment.yaml
```

배포된 생성 항목을 확인합니다.

```bash
kubectl get deployment,replicasets,pod -n nginx
```

배포된 deployment, replicasets, pod 상세 정보를 확인합니다.

```bash
kubectl describe deployment -n nginx
```

```bash
Name:                   nginx
Namespace:              nginx
CreationTimestamp:      Thu, 19 Jun 2025 01:40:32 +0000
Labels:                 <none>
Annotations:            deployment.kubernetes.io/revision: 1
Selector:               app=hello
Replicas:               2 desired | 2 updated | 2 total | 2 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=hello
           tier=frontend
  Containers:
   nginx:
    Image:        nginxdemos/hello
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:       <none>
  Volumes:        <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
OldReplicaSets:  <none>
NewReplicaSet:   nginx-579bd96b44 (2/2 replicas created)
Events:
  Type    Reason             Age    From                   Message
  ----    ------             ----   ----                   -------
  Normal  ScalingReplicaSet  4m17s  deployment-controller  Scaled up replica set nginx-579bd96b44 to 2
```

```bash
kubectl describe replicasets -n nginx
```

```bash
Name:           nginx-579bd96b44
Namespace:      nginx
Selector:       app=hello,pod-template-hash=579bd96b44
Labels:         app=hello
                pod-template-hash=579bd96b44
                tier=frontend
Annotations:    deployment.kubernetes.io/desired-replicas: 2
                deployment.kubernetes.io/max-replicas: 3
                deployment.kubernetes.io/revision: 1
Controlled By:  Deployment/nginx
Replicas:       2 current / 2 desired
Pods Status:    2 Running / 0 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  Labels:  app=hello
           pod-template-hash=579bd96b44
           tier=frontend
  Containers:
   nginx:
    Image:        nginxdemos/hello
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:       <none>
  Volumes:        <none>
Events:
  Type    Reason            Age    From                   Message
  ----    ------            ----   ----                   -------
  Normal  SuccessfulCreate  4m54s  replicaset-controller  Created pod: nginx-579bd96b44-f6vlx
  Normal  SuccessfulCreate  4m54s  replicaset-controller  Created pod: nginx-579bd96b44-dlck7
```

```bash
kubectl describe pod -n nginx
```

```bash
Name:             nginx-579bd96b44-f6vlx
Namespace:        nginx
Priority:         0
Service Account:  default
Node:             lab01-np01-w8xp9-s78qj-47g9t/10.244.1.37
Start Time:       Thu, 19 Jun 2025 01:40:31 +0000
Labels:           app=hello
                  pod-template-hash=579bd96b44
                  tier=frontend
Annotations:      <none>
Status:           Running
IP:               172.19.1.10
IPs:
  IP:           172.19.1.10
Controlled By:  ReplicaSet/nginx-579bd96b44
Containers:
  nginx:
    Container ID:   containerd://13a5ccd905b1573aedc24707a52408fbf9d86a6caa7b44ff9fd69d63e9a70605
    Image:          nginxdemos/hello
    Image ID:       docker.io/nginxdemos/hello@sha256:27984e326bb77db2c9e1c669ee63fd1dc6708b9ed2c1315b81e30b1eef75f947
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Thu, 19 Jun 2025 01:40:38 +0000
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-v4swx (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
Volumes:
  kube-api-access-v4swx:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:
  Type    Reason     Age    From               Message
  ----    ------     ----   ----               -------
  Normal  Pulling    5m18s  kubelet            Pulling image "nginxdemos/hello"
  Normal  Scheduled  5m18s  default-scheduler  Successfully assigned nginx/nginx-579bd96b44-f6vlx to lab01-np01-w8xp9-s78qj-47g9t
  Normal  Pulled     5m12s  kubelet            Successfully pulled image "nginxdemos/hello" in 5.881s (5.881s including waiting). Image size: 20987104 bytes.
  Normal  Created    5m12s  kubelet            Created container nginx
  Normal  Started    5m12s  kubelet            Started container nginx

```

type: ClusterIP 서비스 yaml 파일을 생성합니다.

```yaml
cat << EOF > service.yaml
kind: Service
apiVersion: v1
metadata:
  name: nginx
  namespace: nginx
spec:
  selector:
    app: hello
    tier: frontend
  ports:
  - protocol: "TCP"
    port: 80
  type: ClusterIP
EOF
```

service.yaml을 적용합니다.

```yaml
kubectl apply -f service.yaml
```

서비스 배포 상태를 확인합니다.

```bash
kubectl get svc -n nginx
```

```yaml
NAME    TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
nginx   ClusterIP   172.20.0.188   <none>        80/TCP    2m51s
```

배포된 서비스 상세 정보를 확인합니다.

```bash
Name:              nginx
Namespace:         nginx
Labels:            <none>
Annotations:       <none>
Selector:          app=hello,tier=frontend
Type:              ClusterIP
IP Family Policy:  SingleStack
IP Families:       IPv4
IP:                172.20.0.188
IPs:               172.20.0.188
Port:              <unset>  80/TCP
TargetPort:        80/TCP
Endpoints:         172.19.1.10:80,172.19.2.10:80
Session Affinity:  None
Events:            <none>
```

L7 서비스를 위한 Ingress yaml 파일을 생성합니다.

```yaml
cat << EOF > ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ing-nginx
  namespace: nginx
spec:
  rules:
  - host: lab01.ing.tanzu.lab
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
EOF
```

```yaml
kubectl apply -f ingress.yaml
```

-
