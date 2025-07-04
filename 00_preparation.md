
### TKG cluster

- lab01 - user A
- lab02 - user B
- lab03 - user C

```bash
# TKG cluster name을 할당 받은 lab number로 변경하여 사용
kubectl vsphere login --server https://172.18.105.5 --insecure-skip-tls-verify --vsphere-username=guest@vsphere.local --tanzu-kubernetes-cluster-namespace kbcard --tanzu-kubernetes-cluster-name lab01
```

```bash
# 모든 context 정보를 확인합니다.
kubectl config get-contexts

# 현재 위치한 context를 확인합니다.
kubectl config current-context

# 원하는 context로 이동합니다.
kubectl config use-context [namespace]

# kubectx 명령어를 사용해서 context를 이동할 수 있습니다.
kubectx [namespace]

```

---

Tanzu Package 일부는 사전에 사용하는 클러스터에 구성이 되어 있습니다.

- cert-manager, contour, external-dns

## Tanzu Package 배포(lab01, lab02, lab03 사전 설치 진행됨.)

### Carvel tool 설치

```bash
# carvel 설치 스크립트를 다운로드 후 실행합니다.
wget -O- https://carvel.dev/install.sh > install.sh
sudo bash install.sh
```

```bash
# 설치된 도구 중 imgpkg 도구를 사용하여, 표준 패키지 리스트를 확인합니다.
imgpkg version
imgpkg tag list -i projects.registry.vmware.com/tkg/packages/standard/repo
```

### Tanzu Package repository 추가

```bash
# package repository를 추가 정의
tanzu package repository add standard-repo --url projects.registry.vmware.com/tkg/packages/standard/repo:v2025.6.18 -n tkg-system

# 현재 가용한 패키지 리스트를 확인
tanzu package available list -n tkg-system
```

TKGs에서 지원 항목

![Untitled](https://prod-files-secure.s3.us-west-2.amazonaws.com/cc60dda1-95a9-4322-bb8c-248e45010633/7f00d4de-a6d7-434c-b2e5-9d0de6ad76a3/Untitled.png)

[Cert-manager](https://www.notion.so/Cert-manager-2163d2a98aa880609502d6b55890240d?pvs=21)

[contour](https://www.notion.so/contour-2163d2a98aa880968690e0defd0c3214?pvs=21)

---

## Cluster 배포(사전 배포 완료)

cluster.yaml

```yaml
apiVersion: cluster.x-k8s.io/v1beta1
kind: Cluster
metadata:
  annotations:
  labels:
  name: demo
  namespace: kbcard
spec:
  clusterNetwork:
    pods:
      cidrBlocks:
      - 10.5.0.0/20
    serviceDomain: cluster.local
    services:
      cidrBlocks:
      - 10.100.0.0/20
  topology:
    class: builtin-generic-v3.3.0
    controlPlane:
      replicas: 1
    variables:
    - name: osConfiguration
      value:
        trust:
          additionalTrustedCAs:
          - caCert:
              secretRef:
                key: harbor.tanzu.lab
                name: lab01-user-trusted-ca-secret
    - name: vmClass
      value: best-effort-medium
    - name: storageClass
      value: tanzu-storage-policy
    - name: vsphereOptions
      value:
        persistentVolumes:
          availableStorageClasses:
          - tanzu-storage-policy
          defaultStorageClass: tanzu-storage-policy
#          availableVolumeSnapshotClasses:
#          - tanzu-storage-policy
#          defaultVolumeSnapshotClass: tanzu-storage-policy
    - name: volumes
      value:
      - capacity: 40Gi
        mountPath: /var/lib/containerd
        name: containerd-override
        storageClass: tanzu-storage-policy
      - capacity: 40Gi
        mountPath: /var/lib/kubelet
        name: kubelet-override
        storageClass: tanzu-storage-policy
    - name: kubernetes
      value:
        certificateRotation:
          enabled: true
          renewalDaysBeforeExpiry: 90
    version: v1.31.4+vmware.1-fips
    workers:
      machineDeployments:
      - class: node-pool
        name: np01
        replicas: 3
        variables:
          overrides:
          - name: vmClass
            value: best-effort-medium
```

trusted-certificate

```yaml
apiVersion: v1
data:
  # 하기 name은 TKC yaml 배포파일에서 인증서 이름으로 동일하게 사용됩니다. 이름과 인증서 base64 인코딩 된 값을 붙여 넣습니다.
  harbor.tanzu.lab: TFMwdExTMUNSVWRKVGlCRFJWSlVTVVpKUTBGVVJTMHRMUzB0Q2sxSlNVWnNla05EUVRNclowRjNTVUpCWjBsVll6aHZXakZDZUU5T1ZFVlBTa04xU0ZkUVREaERWMng2UjNrNGQwUlJXVXBMYjFwSmFIWmpUa0ZSUlV3S1FsRkJkMVZVUlV4TlFXdEhRVEZWUlVKb1RVTlJNRFI0UkVSQlMwSm5UbFpDUVdkTlFURkNSbE42UlZGTlFUUkhRVEZWUlVKM2QwaFJiVlp3VTIxc2RRcGFla1ZRVFVFd1IwRXhWVVZEWjNkSFZtc3hNMWxZU214TlVrVjNSSGRaUkZaUlVVUkVRV2hKV1ZoS2FXSXpTa1JSVkVGbFJuY3dlVTVVUVhsTlZHTjNDazVxVFRWT1JHUmhSbmN3ZWs1VVFYbE5WRlYzVG1wTk5VNUVaR0ZOUm10NFEzcEJTa0puVGxaQ1FWbFVRV3RPVDAxUmQzZERaMWxFVmxGUlNVUkJUbEVLVWxWemVFVkVRVTlDWjA1V1FrRmpUVUl3U214aFZYQndZbTFqZUVSNlFVNUNaMDVXUWtGdlRVSnNXazVrTWtaNVdsUkZXazFDWTBkQk1WVkZRWGQzVVFwaFIwWjVXVzA1ZVV4dVVtaGlibkF4VEcxNGFGbHFRME5CYVVsM1JGRlpTa3R2V2tsb2RtTk9RVkZGUWtKUlFVUm5aMGxRUVVSRFEwRm5iME5uWjBsQ0NrRkxNbUZFSzIxelIyZG9hVk0wWlhjMGRESTRXVk4wT0hsMFVrOWlNMmxUY1Radk56WXdORFJYTmpaMldtdzNVVU51WWtsc1UweHBUWHB0WW1oYWJpc0taMEo2WXpJMWNEZEtZVTFTV1hKalUxRldVSGhFVWtoRFFUWlNSVFZCVm1oTVoyVkZOR05rVEV3M1JXWktXWFJwYjNOVE9IRldkekZ6VVZwTWNDOVJWZ3BqZVcwclUyMHJkblJ6WlZKTFJYSjJSRkYyWlVsSlZVVldTMFU0ZEZVelNteHhOelIwVTAxMlZtbHlSakZoVVZCeVMwUkJORmsxWVd4cVUxZzNMeTl3Q25JclNWSnhRWHBaYTJWVGMyNTFRek15V2prelMyRjZiVGhMY0dOMGVrVTRRbFkxYURCS2JHOVhWWFU1UlVsbVFtUkZUbHBzZFZkTFJ6bGlaM1p3ZFZJS1V6QnFTRzFuV2twVmFXOWxOalY1YzBobk5reFhORzU2YWsxSFNucE9jMHN2Tm5JdlRsZzBRbVppY2pKS01tTlBZVVpXU0VKWlR6WnBNMkpoWkdsU1JncHROR1p3TTFKbFJGUnlhVmRPVURSaWNFSjRORUZZUkdFdmFuTXhabHBIWlZWVGF6UktWVWRaUjFsdGExQk1TMll5Y1RVNWFDOHlNMWg1TkhsemJrOVdDbWR0TW5WeVlYQTVZVmRsVjNRNVQwbEpkR1pLVjNsMFpHczNheXRNWjJkTE1tSlpZa0poVTBOb05WRnVUVVZ4VDJNdlZtOW9hMlJ6Um1WaGMxWjZiWG9LUTJKSFowVTRLMmhCVG01VVZYSXJZVVozZUM5Q2VWUTFNR1JpVDJkSVVFRkZieTl2VVhKRlpESk5abFJ3WVdKRVlWcElXV1JPT1dWQ01GQk9Tak5zTWdwQk5WRktkM1ZwUzFONFZuWm5iVUUyV1dGS1ZqRTNlbXhhWm1zd2VtMUphVzF1V2k5a2IySlJlVkJ2YkdKWFNrWkxXU3RMVGxkdlFuWnhka0ZtWlZCWkNuZzNNVVF4YlVGa1RteEpjRlF3VFRVMVJVRXdVbU5hZGtkWmNDOHlaWHBCY0hoeGJUazNPWEJCT0VOMGFFUkhiR2xMZFdWWFJWQTJPV3RyWlhZMWJqQUtNM28yZFdsTFV5dFJTVnBQU0hSaVVrZFFOMFZFTTNGa01YcG1jVVkxZERGM2NURkxkSFV4YlVSTkwyeEJaMDFDUVVGSGFsaDZRbVJOUW5OSFFURlZaQXBGVVZGVlRVSkxRMFZIYUdoamJVcDJZMmsxTUZsWE5UWmtVelZ6V1ZkSmQwaFJXVVJXVWpCUFFrSlpSVVpRU214aVEyRjVjaXN5VldKMmIyTkpVbFY1Q2xWMk9IcHBNRWhZVFVJNFIwRXhWV1JKZDFGWlRVSmhRVVpDTUZrelZIZENLMFpuZW1zelRrTnVSblpuV0Nzdk1GUlllblZOUVRCSFExTnhSMU5KWWpNS1JGRkZRa04zVlVGQk5FbERRVkZCZG1RMlZDc3ZiM2N4YzA1VVVFdERVME5rZDIxMFEyMTJTMlpRTDJOYWEyY3hWMkZZYm01U2FqQlVZbnB0YW0xNU9BcGhhblJSYmxCVGFtcEdhRk5yTW1KUlZXbHpNM2hZSzI0ME9GWjFOakk1UlRsRlFWVlhSVXBxWVhkRVUxUmFLelUzZEM5SGFUSjJiVXRXWTBodFZTOU9DbGR4TTFKd0sxbFBVR2w1WTNWbWJGTkxlVGN5T0RBeGFWVkNkVXByYmt4cGFUaHpiMEkwVlRoUEsxWTNkakEzVUZGblN6QTBTVUp2UzBjNVkyZENVazhLUlZSSU1HTnFjMGRMUjJaVWVYUnZNbFk1Y2pSYVRsSTRURUk1VFd4RmFVMTVRVU54ZEc5UVowZHJSV1Z6YUZkRE5VMVpRVkoyVW1ZemMzaDZPV05GVFFwd2NWaERWVU0yZWpjMlNVbDBkRU5rU1RBMEwyRjBhWEE1Y2l0Q2NEVnNNbkUyVDBOSGFtYzFhMHRGYTB0c1JVTlhSVWRSVEZsWE5HRlJZbWRqWkcwMUNtbE1TazVzZFVwYU1FWlRPVTVFZG1kSFdGaFhRM0JUUlhwak56YzVZWEZhTm1NMlNFOWpWekJ6U3pKRU5rdEtVako1ZG1sS2VGQjNUbE16ZG5wa2QzVUtTVkJ5TDJaSVJXWk5TR3MxTlhwSFVsQjRVM0V4Wmt4QlZXZ3ZURnBCU2pSa01pdEpXRVk1YW1WaFJEVm5OV3R6ZUhCNFNERkNSMVYwUzBGYU55dEdNd3BpTW05d2VYbFBjbXQ0UzJGVWJGVTFSRXBFVUZrM01sSjZkek0zV2s5aVdXazVSRk5yWnl0VmRFUktObnBVSzBsT1R6UnFTVzlKTTNSSlpUbG1aa1JMQ2xkbVJISjVXVzVwVEVkcU5YUnJNVnBWWkc1WFRrZG1VMmR1U25GV05VOHJNSFpyWXpsalUwNVROMGRCTURFcmRFVmFjRUoyUzAwM2NETlZiVzlGUVVFS1drcEJibVJ1TVRkMGVuQTRNbGRqVmt0aWVVMUZORlJ2TkhkVlkwVnlkVzFuVjBReFMxSkhaVTAyV0V3MlNGUnVibEJTUXpCQ1VqaEdWMUp1ZW5OVmRncGxiMEZTTUhSQlUxRnhaRU5vYTJKRFZITkhUSGxtTDFkeGNFUnRjMGswZEhsMGJHOU9Wa2RMWTBGek5EUnFMMWRwUWk4eFZWQmtUVWhCUFQwS0xTMHRMUzFGVGtRZ1EwVlNWRWxHU1VOQlZFVXRMUzB0TFFvSw==
kind: Secret
metadata:
  # {tkc name}-user-trusted-ca-secret & tkc name은 tkc yaml 배포파일에서 지정한 이름으로 사용합니다. -user.. 이후 구문은 고정 값입니다.
  name: demo-user-trusted-ca-secret
  # vsphere namespace: TKC yaml 파일에서 지정한 vSphere namespace 대상 이름입니다.
  namespace: kbcard
type: Opaque
```

-
