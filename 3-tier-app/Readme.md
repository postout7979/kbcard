![image](https://github.com/user-attachments/assets/606b24d3-f470-4b50-b606-192790fbc6fc)


구성 요소

VM 서비스 MySQL 8

- VM 환경 설정 - cloud-init
- VM 서비스 로드밸런서 - 3306포트 및 22포트 노출

TKG 클러스터

- Backend-App (API)
    - msql 연결 정보를 포함한 secret(host, user, db_name, password)
    - 5000 포트로 로드밸런서 노출
    - API 서버 1개 pod
- Frontend-App (UI)
    - API 서비스 IP:Port를 포함한 Secret
    - 5000번 포트로 로드밸런서 노출
    - GUI 기반의 1개 pod 노출

---

## Supervisor CP IP로 로그인 혹은 vSphere Namespace로 로그인

```yaml
kubectl vsphere login --server https://10.10.152.1 --insecure-skip-tls-verify --vsphere-username=cis@vsphere.local --tanzu-kubernetes-cluster-namespace kbcard
```

---

## Database DB 배포

namespace에 사용 가능한 storageclass를 확인합니다.

```yaml
kubectl describe ns kbcard
```

```yaml
Name:         kbcard
Labels:       kubernetes.io/metadata.name=kbcard
              vSphereClusterID=domain-c9
Annotations:  ls_id-0: dd8e9131-d0e4-4b07-be2c-4c003995c82b
              ncp/extpoolid: domain-c9:4817a1c1-55bc-46da-a54d-de40dcb765ac-ippool-10-10-153-1-10-10-153-254
              ncp/router_id: t1_01d25708-7975-436f-a556-19751fac9e7e_rtr
              ncp/snat_ip: 10.10.153.4
              ncp/subnet-0: 10.244.1.16/28
              vmware-system-resource-pool: resgroup-3395
              vmware-system-vm-folder: group-v3396
Status:       Active

Resource Quotas
  Name:                                                              kbcard-storagequota
  Resource                                                           Used   Hard
  --------                                                           ---    ---
  tanzu-storage-policy.storageclass.storage.k8s.io/requests.storage  320Gi  9223372036854775807
```

사용 가능한 vmclass 타입을 확인합니다.

```yaml
kubectl get vmclass -n kbcard
```

```yaml
NAME                  CPU   MEMORY
best-effort-2xlarge   8     64Gi
best-effort-4xlarge   16    128Gi
best-effort-8xlarge   32    128Gi
best-effort-large     4     16Gi
best-effort-medium    2     8Gi
best-effort-small     2     4Gi
best-effort-xlarge    4     32Gi
best-effort-xsmall    2     2Gi
```

사용 가능한 virtualmachineimage를 확인합니다.

```yaml
kubectl get virtualmachineimages -n kbcard
```

```yaml
NAME                    DISPLAY NAME                  IMAGE VERSION   OS NAME         OS VERSION   HARDWARE VERSION   CAPABILITIES
vmi-d3429e7257eb61a17   noble-server-cloudimg-amd64                   ubuntu64Guest                10
```

### mysql-db.yaml

```yaml
apiVersion: vmoperator.vmware.com/v1alpha1
kind: VirtualMachine
metadata:
  labels:
    vm.name: db-vm
  name: mysql-db
  namespace: kbcard
spec:
  imageName: vmi-7360314ef0704e0bf
  className: best-effort-medium
  powerState: poweredOn
  storageClass: tanzu-storage-policy
  networkInterfaces:
  - networkName: vks-workload-01
    networkType: vsphere-distributed
  vmMetadata:
    transport: CloudInit
    secretName: my-vm-bootstrap-data
---
apiVersion: v1
kind: Secret
metadata:
  name: my-vm-bootstrap-data
  namespace: kbcard
stringData:
  user-data: |
    #cloud-config
    ssh_pwauth: true

    groups:
      - admingroup: [root,sys]

    users:
      - name: devuser
        gecos: Dev S. Ops
        lock_passwd: false
        # mkpasswd -m sha-512 VMware1!
        passwd: $6$uQvh5Md4UBQM79d0$d7CszB7mrxaS3ewUvJ12lWz1g6qldsp1aZZ0SPbBO1YQq3yKPzeoZ7G8CNv319/9sgD7e2WbY2BqgDnJBMC.z.
        sudo: ALL=(ALL) NOPASSWD:ALL
        groups: sudo, users, admin
        shell: /bin/bash
        ssh_pwauth: True
    chpasswd:
      list: |
        root:VMware1!
        devuser:VMware1!
      expire: false

    write_files:
      - content: |
           ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
        append: true
        path: alteruser.txt

      - content: |
           CREATE USER 'devops'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
           CREATE DATABASE demo;
           GRANT ALL PRIVILEGES ON demo.* TO 'devops'@'%';

           CREATE TABLE demo.user (
             id INTEGER PRIMARY KEY AUTO_INCREMENT,
             username varchar(255) NOT NULL,
             password varchar(255) NOT NULL,
             UNIQUE (username)
           );

           CREATE TABLE demo.entry (
             id INTEGER PRIMARY KEY AUTO_INCREMENT,
             author_id INTEGER NOT NULL,
             created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
             title varchar(255) NOT NULL,
             body varchar(5400) NOT NULL,
             FOREIGN KEY (author_id) REFERENCES user (id)
           );

           INSERT INTO demo.user (username,password) VALUES('admin','admin');
           INSERT INTO demo.entry (author_id,title,body) VALUES(1,"Welcome to the request page, this is the first entry This entry is owned by Jeremy and can only be modified by him. You can create your own post by registering and logging in!");

        append: true
        path: init.sql

    runcmd:
      - sudo hostname mysql-db
      - sudo apt update
      - sudo apt -y install mysql-server
      - sudo systemctl start mysql.service
      - sudo mysql < alteruser.txt
      - mysql -u root -ppassword < init.sql
      - sudo sed -i '0,/bind-address/s//#bind-address/' /etc/mysql/mysql.conf.d/mysqld.cnf
      - sudo systemctl restart mysql.service
---
apiVersion: vmoperator.vmware.com/v1alpha1
kind: VirtualMachineService
metadata:
  name: mysql-db
  namespace: kbcard
spec:
  ports:
  - name: ssh
    port: 22
    protocol: TCP
    targetPort: 22
  - name: mysql
    port: 3306
    protocol: TCP
    targetPort: 3306
  selector:
    vm.name: db-vm
  type: LoadBalancer
```

DB VM 배포를 진행합니다.

```yaml
kubectl apply -f mysql-db.yaml -n kbcard
```

mysql DB VM의 service IP를 확인합니다.

- Backend APP 배포 시, mysql DB의 external IP 주소를 사용합니다.

```yaml
kubectl get virtualmachineservice mysql-db -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

-

---

## TKG Cluster로 Context 이동

tanzu kubernetes cluster로 사용자 lab context를 이동합니다.

```yaml
kubectx lab01
```

```yaml
kubectl config current-context
```

# BackendAPP

```yaml
kubectl create namespace 3ta
kubectl label namespace 3ta pod-security.kubernetes.io/enforce=privileged
```

backend app yaml 파일을 생성합니다.

- mysql-db VM의 loadBalancer IP 주소를 base64 encoding한 값으로 data.mysql_host: 항목에 추가합니다.

```yaml
echo -n "{mysql-db VM loadBalancer IP}" | base64 -w0
```

```yaml
cat << EOF > backend-app.yaml
apiVersion: v1
kind: Secret
metadata:  
  name: backend-app-secret
  namespace: 3ta
type: Opaque
data:
  mysql_user: ZGV2b3Bz
  db_passwd: cGFzc3dvcmQ=
  # mysql-db VM에 대한 IP 주소를 encoding 후 값을 추가합니다.  
  mysql_host: <BASE64_ENCODED_IP_FOR_mysql-db>
  db_name: ZGVtbw==

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-app-deployment
  namespace: 3ta
  labels:
    app: backend-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend-app
  template:
    metadata:
      labels:
        app: backend-app
    spec:
      containers:
        - name: backend-app
          image: postout7979/developer-utilities-backend
          ports:
            - containerPort: 5000
          env:
          - name: MYSQL_HOST
            valueFrom:
              secretKeyRef:
                name: backend-app-secret
                key: mysql_host
                optional: false
          - name: MYSQL_USER
            valueFrom:
              secretKeyRef:
                name: backend-app-secret
                key: mysql_user
                optional: false 
          - name: DB_PASSWORD
            valueFrom:
              secretKeyRef:
                name: backend-app-secret
                key: db_passwd
                optional: false 
          - name: DB_NAME
            valueFrom:
              secretKeyRef:
                name: backend-app-secret
                key: db_name
                optional: false 
#      imagePullSecrets:
#      - name: docker-hub-creds
---
apiVersion: v1
kind: Service
metadata:
  name: backend-app-service
  namespace: 3ta
spec:
  selector:
    app: backend-app
  ports:
    - name: web-app-port
      protocol: TCP
      port: 5000
      targetPort: 5000
  type: LoadBalancer
EOF
```

앱 배포를 진행합니다.

```yaml
kubectl apply -f backend-app.yaml
```

배포된 앱 및 서비스를 확인합니다.

```bash
kubectl get po,svc -n 3ta
```

---

## Frontend APP

- backend app service의 external IP 주소를 base64 encoding한 다음 data.api_url에 값을 변경합니다.

```bash
kubectl get -n 3ta svc backend-app-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}
```

```yaml
# echo -n "{backed-app external IP:Port}" | base64 -w0
echo -n "10.10.152.18:5000" | base64 -w0
```

```yaml
cat << EOF > frontend-app.yaml
apiVersion: v1
kind: Secret
metadata:  
  name: frontend-app-secret
  namespace: 3ta
type: Opaque
data:
  api_url: <BASE64_ENCODED_IP:PORT_FOR_backend-app-service>

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-app-deployment
  namespace: 3ta
  labels:
    app: frontend-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend-app
  template:
    metadata:
      labels:
        app: frontend-app
    spec:
      containers:
        - name: frontend-app
          image: postout7979/developer-utilities-frontend
          ports:
            - containerPort: 5000
          env:
          - name: API_URL
            valueFrom:
              secretKeyRef:
                name: frontend-app-secret
                key: api_url
                optional: false 
#      imagePullSecrets:
#      - name: docker-hub-creds
---

apiVersion: v1
kind: Service
metadata:
  name: frontend-app-service
  namespace: 3ta
spec:
  selector:
    app: frontend-app
  ports:
    - name: web-app-port
      protocol: TCP
      port: 5000
      targetPort: 5000
  type: LoadBalancer
EOF
```

app 배포를 진행합니다.

```yaml
kubectl apply -f frontend-app.yaml
```

배포된 앱 및 서비스를 확인합니다.

```yaml
 kubectl get po,svc -n 3ta
```

-
