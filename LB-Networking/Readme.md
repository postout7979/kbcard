## Default LB  - Supervisor Control Plane LB Networking

- Supervisor Management 활성화를 위해서 최초 환경 설정에서 Load Balancer(vSphere 8: HAProxy, Avi LB, vSphere 9: HAProxy, Avi LB, Embedded Foundation LB)를 제공합니다.
- 이 로드밸런서는 Supervisor 및 TKC의 kubenetes control API를 위한 VIP를 제공하며, 모든 영역에서의 애플리케이션을 위한 기본 로드 밸런서로 운영됩니다.
- Avi LB로 배포 시, Default IPAM Profile에 설정된 1개 대역의 VIP Network만을 사용하게 됨으로 최초 구축 시, 클러스터의 확장성을 고려한 IP 대역 및 서브넷 설정을 고려할 필요가 있습니다.

## Additional LB - Dedicated Application LB Networking

- TKC 내에서 사용자는 기본 환경 설정과 분리된 네트워크로부터 VIP 연결을 허용하거나, 기본 로드 밸런서와 다른 제품의 로드 밸런서를 사용하기 위해서 추가 로드 밸런서를 구성할 수 있습니다.
- Avi LB는 TKC 내에 AKO(Avi Kubernetes Operator) 배포를 통해서, Avi LB로의 로드 밸런서 네트워크 사용을 배치할 수 있도록 지원합니다.

---

namespace을 생성합니다.

```yaml

kubectl create ns kuard
kubectl label --overwrite ns kuard pod-security.kubernetes.io/enforce=privileged
```

ako와 일치하는 label을 namespace에 추가합니다.

```yaml
kubectl label --overwrite ns kuard avi=red
```

label이 잘 추가된 것을 확인합니다.

```yaml
$ kubectl describe ns kuard
Name:         kuard
Labels:       avi=red
              kubernetes.io/metadata.name=kuard
              pod-security.kubernetes.io/enforce=privileged
Annotations:  <none>
Status:       Active

No resource quota.

No LimitRange resource.
viadmin@cis-jumphost:~/.../ako$
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
  loadBalancerClass: ako.vmware.com/avi-lb
EOF
```

할당된 로드밸런서의 external IP 주소를 확인합니다.

```bash
kubectl get svc -n kuard
```

---

## AviInfraSetting

- Avi AKO는 동일 avi controller에 대한 다른 네트워크 엔진 그룹을 사용할 수 있도록, 추가 CRD를 제공하고 있습니다.

aviinfrasetting.yaml

```yaml
apiVersion: ako.vmware.com/v1beta1
kind: AviInfraSetting
metadata:
  name: my-infrasetting
spec:
  seGroup:
    name: sub-group
  network:
    vipNetworks:
      - networkName: vks-datapath-02
        cidr: 172.18.109.0/24
    enableRhi: false
      #    nodeNetworks:
      #      - networkName: 2051
      #        cidr: 10.200.51.0/24
```

aviinfrasetting.yam을 적용합니다.

```yaml
kubectl apply -f aviinfrasetting.yaml
```

기존 ako를 사용하도록 설정한 namespace에 annotation을 추가하여 L4 로드밸런서 서비스를 제공 받을 수 있습니다.

```yaml
metadata:
  annotations:
    aviinfrasetting.ako.vmware.com/name: "my-infrasetting"
```

아래와 같이 annotation 및 label이 추가되어 있습니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  annotations:
    aviinfrasetting.ako.vmware.com/name: my-infrasetting
  creationTimestamp: "2025-06-29T07:30:58Z"
  labels:
    avi: red
    kubernetes.io/metadata.name: kuard
  name: kuard
  resourceVersion: "102619"
  uid: ffeb5fe2-8f71-4054-a5b2-839c095536bb
spec:
  finalizers:
  - kubernetes
status:
  phase: Active
```

service을 생성합니다.

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
  loadBalancerClass: ako.vmware.com/avi-lb
EOF
```

아래와 같이 신규 172.18.109.x 대역의 VIP를 사용하는 것을 확인할 수 있습니다.

```yaml
$ k get svc -n kuard
NAME    TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
kuard   LoadBalancer   10.100.12.253   172.18.109.64   80:30430/TCP   112s
```

-
