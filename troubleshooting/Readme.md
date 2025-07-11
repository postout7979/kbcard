## 이 애플리케이션은 장애를 유발하도록 설정되어 있습니다.

ACME Fitness APP을 배포 합니다.
이 애플리케이션의 git link: https://github.com/postout7979/troubleshooting


```bash
mkdir git
cd git

sudo apt install gh -y

git clone https://github.com/postout7979/troubleshooting.git
```

```bash
cd troubleshooting/kubernetes-manifests
```

```bash
kubectl create ns acme-fitness
```

```bash
kubectl apply -f . -n acme-fitness
```

### 권한 문제 - Pod가 배포되지 않는 경우

```bash
# namespace에 pod-security 상승
kubectl label --overwrite ns acme-fitness pod-security.kubernetes.io/enforce=privileged

# Deployment 재시작
kubectl rollout restart deployment -n acme-fitness
```

## CreateContainerConfigError

```bash
kubectl create secret generic cart-redis-pass --from-literal=password=acmefitness -n acme-fitness

kubectl create secret generic catalog-mongo-pass --from-literal=password=acmefitness -n acme-fitness

kubectl create secret generic order-postgres-pass --from-literal=password=acmefitness -n acme-fitness

kubectl create secret generic users-mongo-pass --from-literal=password=acmefitness -n acme-fitness
kubectl create secret generic users-redis-pass --from-literal=password=acmefitness -n acme-fitness
```

### ContainerCreating

catalog-db-total.yaml

```bash
      volumes:
        - name: mongodata
          emptyDir: {}
        - name: mongo-initdb
          configMap:
            name: catalog-init-db-config
      ---
      volumes:
        - name: mongodata
          emptyDir: {}
        - name: mongo-initdb
          configMap:
            name: catalog-initdb-config
```

-

## ImagePullBackOff 혹은 ErrImagePull

cart-redis-total.yaml

```bash
    spec:
      containers:
        - name: cart-redis
          image: tkgs-harbor.tanzu.lab/library/redis:v5
---
    spec:
      containers:
        - name: cart-redis
          image: tkgs-harbor.tanzu.lab/library/redis:latest
```

-

users-

user-mongo-

- 어떤 문제….

```bash

```

### LoadBalancer EXTERNAL-IP pending

- 잘못된 대역의 static IP 설정으로 인한 pending 발생

```bash
  type: LoadBalancer
  loadBalancerIP: 172.18.106.101
---
  type: LoadBalancer
  ~~loadBalancerIP: 172.18.106.101~~
```

## CrashLoopBackOff

pos-

- point-of-sales-total.yaml 내의 container에서 다른 구성 요소와 연결되는 value 값 문제

```bash

```

## CrashLoopBackOff

```bash
# 신규 스케줄링을 노드에 차단
kubectl cordon [node name] # 모든 노드를 cordon 진행

# 스케줄링이 가능하도록 cordon 해제
kubectl uncordon [node name]
```

busybox app 배포 진행

```bash
kubectl apply -f busybox.yaml
```

-

<aside>
💡

users: ***eric, dwight, han, or phoebe***

***password for these users is 'vmware1!'***

</aside>

-
