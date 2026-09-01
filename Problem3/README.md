# Problem 3: Zero-Trust KubeArmor Policy for Wisecow

Applies a KubeArmor runtime security policy to the Wisecow workload from Problem 1,
enforcing a zero-trust posture: only the processes the app actually needs can run;
everything else (shells, package managers, download tools, sensitive file reads)
is explicitly blocked.

## What I did

1. Installed KubeArmor on the same `kind` cluster used in Problem 1.
2. Wrote a `KubeArmorPolicy` targeting pods labeled `app: wisecow` in the `wisecow` namespace.
3. The policy **blocks**: [policy *action* is set to Block; actual enforcement is
   audit-only in this Kind setup — see note below]
   - Interactive shells (`/bin/bash`, `/bin/sh`) — prevents an attacker (or anyone via `kubectl exec`) from getting a shell inside the container.
   - Package managers (`apt`, `apt-get`) and download tools (`curl`, `wget`) — prevents installing or pulling in extra tools at runtime.
   - Reads of sensitive files (`/etc/shadow`, `/etc/passwd`).
4. Applied the policy and captured a real policy violation by attempting a blocked action. [attempting an action the policy is configured to block — the attempt succeeded and was logged, not prevented, due to the Kind/LSM limitation below]


## Why this is "zero trust"

The wisecow container's only real job is running `wisecow.sh`, which itself calls `fortune`, `cowsay`, and `ncat`. It never needs a shell, a package manager, or the ability to read system credential files at runtime. Rather than trusting the container to "behave," this policy explicitly denies exactly the actions an attacker would take after gaining any foothold (spawn a shell, install tools, read secrets) — the app can only do what it was built to do, nothing more.

## Files

- [`wisecow-zero-trust-policy.yaml`](./wisecow-zero-trust-policy.yaml) — the policy


## Proof of Work

---
**1. KubeArmor installed and running**
---
<img width="524" height="284" alt="image" src="https://github.com/user-attachments/assets/489bf824-69c2-42c2-b5bd-268788f52559" />

---
**2. Policy applied successfully**
---
<img width="503" height="53" alt="image" src="https://github.com/user-attachments/assets/922bb00e-3aa4-4b95-811d-04be2399f916" />

---
**3. Policy violation — **
---
<img width="234" height="64" alt="image" src="https://github.com/user-attachments/assets/c28e15f4-ea19-4b37-b8d6-7d2224369e12" />

---
**4. Live violation log from `karmor logs`**
---

```
$ karmor logs -n wisecow
== Alert / <timestamp> ==
ContainerName: wisecow
ContainerID: c922a7e357d233ad1ae062cdb1bfae8814ab07c79f16e961832422c4d38bfc2d
ContainerImage: docker.io/mubashraiftikhar10/wisecow:4d86c59@sha256:3dbfb494fb0840fc9a213b3c8668e2c784aa5c24086b2b48745c17dc54825b95
Type: MatchedPolicy
PolicyName: wisecow-zero-trust-policy
Severity: 8
Source: /usr/bin/whoami
Resource: /etc/passwd
Operation: File
Action: Audit (Block)
Data: syscall=SYS_OPENAT fd=-100 flags=O_RDONLY|O_CLOEXEC
EventData: map[Fd:-100 Flags:O_RDONLY|O_CLOEXEC Syscall:SYS_OPENAT]
Enforcer: eBPF Monitor
```
## Note on KubeArmor Enforcement

KubeArmor is deployed and the zero-trust policy is applied. It successfully
**detects** violations (see screenshot/logs — `Action: Audit (Block)`), but it
doesn't actually **block** them.

This is because KubeArmor needs a Linux security feature (called an **LSM** —
like AppArmor or BPF-LSM) to enforce policies, not just watch them. I checked
and found:

- The EC2 host has AppArmor enabled, but it doesn't carry over into the Kind
  node (Kind runs nodes as containers, not real VMs).
- The Kind node image doesn't even have the tool (`apparmor_parser`) needed to
  use AppArmor.
- Confirmed with `karmor probe`, which showed no active LSM inside the node.

So this is a limitation of running Kind in this setup, not a mistake in the
policy itself. The policy works correctly — it just can't fully enforce without
a real VM or bare-metal node.
