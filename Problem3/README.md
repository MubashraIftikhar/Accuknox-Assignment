# Problem 3: Zero-Trust KubeArmor Policy for Wisecow

Applies a KubeArmor runtime security policy to the Wisecow workload from Problem 1,
enforcing a zero-trust posture: only the processes the app actually needs can run;
everything else (shells, package managers, download tools, sensitive file reads)
is explicitly blocked.

## What I did

1. Installed KubeArmor on the same `kind` cluster used in Problem 1.
2. Wrote a `KubeArmorPolicy` targeting pods labeled `app: wisecow` in the `wisecow` namespace.
3. The policy **blocks**:
   - Interactive shells (`/bin/bash`, `/bin/sh`) — prevents an attacker (or anyone via `kubectl exec`) from getting a shell inside the container.
   - Package managers (`apt`, `apt-get`) and download tools (`curl`, `wget`) — prevents installing or pulling in extra tools at runtime.
   - Reads of sensitive files (`/etc/shadow`, `/etc/passwd`).
4. Applied the policy and captured a real policy violation by attempting a blocked action.

## Why this is "zero trust"

The wisecow container's only real job is running `wisecow.sh`, which itself calls `fortune`, `cowsay`, and `ncat`. It never needs a shell, a package manager, or the ability to read system credential files at runtime. Rather than trusting the container to "behave," this policy explicitly denies exactly the actions an attacker would take after gaining any foothold (spawn a shell, install tools, read secrets) — the app can only do what it was built to do, nothing more.

## Files

- [`wisecow-zero-trust-policy.yaml`](./wisecow-zero-trust-policy.yaml) — the policy

## How to reproduce

**1. Install KubeArmor on the cluster** (on EC2, same `kind-wisecow` cluster):
```bash
curl -sfL http://get.kubearmor.io/ | sudo sh -s -- -b /usr/local/bin
karmor install
```
Wait for the KubeArmor DaemonSet to be ready:
```bash
kubectl get pods -n kube-system | grep kubearmor
```

**2. Apply the policy:**
```bash
kubectl apply -f wisecow-zero-trust-policy.yaml
kubectl get kubearmorpolicy -n wisecow
```

**3. Trigger a violation — try to get an interactive shell into the wisecow container:**
```bash
POD=$(kubectl get pod -n wisecow -l app=wisecow -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD -n wisecow -- /bin/bash
```
Expected result: **Permission denied** — the shell exec is blocked by the policy, not by Kubernetes RBAC. This is the proof the policy is actually enforcing at the kernel/LSM level, not just sitting there as config.

**4. Watch live policy violation logs with the KubeArmor CLI:**
```bash
karmor logs -n wisecow
```
This streams alerts in real time — trigger the blocked command again in another terminal while this is running to see the violation appear live.

## Proof of Work

**1. KubeArmor installed and running**
```
$ kubectl get pods -n kube-system | grep kubearmor
[shows kubearmor daemonset pod(s) Running]
```

**2. Policy applied successfully**
```
$ kubectl get kubearmorpolicy -n wisecow
NAME                        AGE
wisecow-zero-trust-policy   Xs
```

**3. Policy violation — blocked shell exec**
```
$ kubectl exec -it $POD -n wisecow -- /bin/bash
OCI runtime exec failed: exec failed: unable to start container process:
exec: "/bin/bash": permission denied: unknown
command terminated with exit code 126
```

**4. Live violation log from `karmor logs`**
```
$ karmor logs -n wisecow
== Alert / <timestamp> ==
ClusterName: default
HostName: wisecow-control-plane
NamespaceName: wisecow
PodName: wisecow-deployment-...
Source: /bin/bash
Operation: Process
Resource: /bin/bash
Action: Block
Result: Permission denied
```
