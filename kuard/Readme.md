### APP 배포 및 서비스 L4 연결

namespace을 생성하고, 권한을 부여합니다.

```bash
kubectl create ns kuard
kubectl label --overwrite ns kuard pod-security.kubernetes.io/enforce=privileged
```

```yaml
mkdir kuard
cd kuard
```

Deployment yaml 파일을 작성합니다.

```yaml

cat << EOF > deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: kuard
  name: kuard
  namespace: kuard
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kuard
  template:
    metadata:
      labels:
        app: kuard
    spec:
      containers:
      - image: gcr.io/kuar-demo/kuard-amd64:1
        name: kuard
EOF
```

배포된 생성 항목을 확인합니다.

```bash
kubectl get deployment,replicasets,pod -n kuard
```

배포된 deployment, replicasets, pod 상세 정보를 확인합니다.

```bash
kubectl describe deployment -n kuard
```

```bash
Name:                   kuard
Namespace:              kuard
CreationTimestamp:      Wed, 18 Jun 2025 07:39:39 +0000
Labels:                 app=kuard
Annotations:            deployment.kubernetes.io/revision: 2
Selector:               app=kuard
Replicas:               1 desired | 1 updated | 1 total | 1 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=kuard
  Containers:
   kuard:
    Image:        gcr.io/kuar-demo/kuard-amd64:1
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
OldReplicaSets:  kuard-5cf6f6768d (0/0 replicas created)
NewReplicaSet:   kuard-68ddc8dccf (1/1 replicas created)
```

```bash
kubectl describe replicasets -n kuard
```

```bash
Name:           kuard-5cf6f6768d
Namespace:      kuard
Selector:       app=kuard,pod-template-hash=5cf6f6768d
Labels:         app=kuard
                pod-template-hash=5cf6f6768d
Annotations:    deployment.kubernetes.io/desired-replicas: 1
                deployment.kubernetes.io/max-replicas: 2
                deployment.kubernetes.io/revision: 1
Controlled By:  Deployment/kuard
Replicas:       0 current / 0 desired
Pods Status:    0 Running / 0 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  Labels:  app=kuard
           pod-template-hash=5cf6f6768d
  Containers:
   kuard:
    Image:        gcr.io/kuar-demo/kuard-amd64:blue
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:       <none>
  Volumes:        <none>
Events:           <none>

Name:           kuard-68ddc8dccf
Namespace:      kuard
Selector:       app=kuard,pod-template-hash=68ddc8dccf
Labels:         app=kuard
                pod-template-hash=68ddc8dccf
Annotations:    deployment.kubernetes.io/desired-replicas: 1
                deployment.kubernetes.io/max-replicas: 2
                deployment.kubernetes.io/revision: 2
Controlled By:  Deployment/kuard
Replicas:       1 current / 1 desired
Pods Status:    1 Running / 0 Waiting / 0 Succeeded / 0 Failed
Pod Template:
  Labels:  app=kuard
           pod-template-hash=68ddc8dccf
  Containers:
   kuard:
    Image:        gcr.io/kuar-demo/kuard-amd64:1
    Port:         <none>
    Host Port:    <none>
    Environment:  <none>
    Mounts:       <none>
  Volumes:        <none>
Events:           <none>
```

```bash
kubectl describe pod -n kuard
```

```bash

Name:             kuard-68ddc8dccf-ml5r9
Namespace:        kuard
Priority:         0
Service Account:  default
Node:             lab01-np01-w8xp9-s78qj-pfzrc/10.244.1.36
Start Time:       Wed, 18 Jun 2025 07:44:47 +0000
Labels:           app=kuard
                  pod-template-hash=68ddc8dccf
Annotations:      <none>
Status:           Running
IP:               172.19.3.7
IPs:
  IP:           172.19.3.7
Controlled By:  ReplicaSet/kuard-68ddc8dccf
Containers:
  kuard:
    Container ID:   containerd://1c59478866a2a119c2408d26c48884e5e5b39689a795a29bef59d39ac1e59bb7
    Image:          gcr.io/kuar-demo/kuard-amd64:1
    Image ID:       gcr.io/kuar-demo/kuard-amd64@sha256:bd17153e9a3319f401acc7a27759243f37d422c06cbbf01cb3e1f54bbbfe14f4
    Port:           <none>
    Host Port:      <none>
    State:          Running
      Started:      Wed, 18 Jun 2025 07:44:51 +0000
    Ready:          True
    Restart Count:  0
    Environment:    <none>
    Mounts:
      /var/run/secrets/kubernetes.io/serviceaccount from kube-api-access-9z88s (ro)
Conditions:
  Type                        Status
  PodReadyToStartContainers   True
  Initialized                 True
  Ready                       True
  ContainersReady             True
  PodScheduled                True
Volumes:
  kube-api-access-9z88s:
    Type:                    Projected (a volume that contains injected data from multiple sources)
    TokenExpirationSeconds:  3607
    ConfigMapName:           kube-root-ca.crt
    ConfigMapOptional:       <nil>
    DownwardAPI:             true
QoS Class:                   BestEffort
Node-Selectors:              <none>
Tolerations:                 node.kubernetes.io/not-ready:NoExecute op=Exists for 300s
                             node.kubernetes.io/unreachable:NoExecute op=Exists for 300s
Events:                      <none>
```

type: LoadBalancer 서비스 yaml 파일을 생성합니다.

```yaml
cat << EOF > service.yaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app: kuard
  name: kuard
  namespace: default
spec:
  ports:
  - port: 80
    protocol: TCP
    targetPort: 8080
  selector:
    app: kuard
  sessionAffinity: None
  type: LoadBalancer
EOF
```

할당된 로드밸런서의 external IP 주소를 확인합니다.

```bash
kubectl get svc -n kuard
```

배포된 서비스 상세 정보를 확인합니다.

```bash
$ kubectl describe svc kuard -n kuard
Name:                     kuard
Namespace:                kuard
Labels:                   app=kuard
Annotations:              <none>
Selector:                 app=kuard
Type:                     LoadBalancer
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       172.20.1.254
IPs:                      172.20.1.254
LoadBalancer Ingress:     10.10.152.15
Port:                     <unset>  80/TCP
TargetPort:               8080/TCP
NodePort:                 <unset>  32346/TCP
Endpoints:                172.19.3.7:8080
Session Affinity:         None
External Traffic Policy:  Cluster
Events:
  Type     Reason                  Age                From                Message
  ----     ------                  ----               ----                -------
  Warning  SyncLoadBalancerFailed  15m (x2 over 16m)  service-controller  Error syncing load balancer: failed to ensure load balancer: VirtualMachineService IP not found
  Normal   EnsuringLoadBalancer    15m (x3 over 16m)  service-controller  Ensuring load balancer
  Normal   EnsuredLoadBalancer     15m                service-controller  Ensured load balancer
```

Deployment를 수정하여, replica 수를 3개로 변경합니다.
