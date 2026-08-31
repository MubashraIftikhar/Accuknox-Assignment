# Problem 2: System Health Monitoring + Application Health Checker

Two scripts written in Python, covering objectives #1 and #4 from the problem statement.

## What I did

1. **System Health Monitoring Script** (`system_health_monitor.py`)
   Checks CPU usage, memory usage, disk usage, and running process count against configurable thresholds (default 80%). Prints `INFO` for normal readings and `ALERT` when a threshold is crossed — both to the console and to `health_monitor.log`. Supports a `--watch` mode to run continuously.

2. **Application Health Checker** (`app_health_checker.py`)
   Sends an HTTP(S) request to a given URL and classifies it as `UP` (2xx/3xx status) or `DOWN` (4xx/5xx, timeout, connection error, or SSL error). Logs every check to `app_health.log`. Tested against my live Wisecow deployment from Problem 1 (`https://wisecow.local:8443`).

## Repo structure

```
Problem2/
├── system_health_monitor.py
└── app_health_checker.py
```

## How to run

```bash
pip install psutil requests --break-system-packages

# System health check — single run
python3 system_health_monitor.py

# System health check — continuous, every 5s
python3 system_health_monitor.py --watch 5

# Application health check
python3 app_health_checker.py https://wisecow.local:8443 --insecure
```

## Proof of Work

**1. Normal run — all metrics under threshold**
```
$ python3 system_health_monitor.py
--- Health check at 2026-08-31 16:37:11 ---
[2026-08-31 16:37:12] INFO:  CPU usage: 9.7%
[2026-08-31 16:37:12] INFO:  Memory usage: 53.4% (used 1018MB / total 1905MB)
[2026-08-31 16:37:12] INFO:  Disk usage (/): 42.5% (free 10GB)
[2026-08-31 16:37:12] INFO:  Running processes: 170
```

**2. Alert correctly fires when CPU is pushed to 100%**
```
$ for i in $(seq 1 $(nproc)); do (while true; do :; done) & done
$ python3 system_health_monitor.py
[...] INFO:  CPU usage: 100.0%
[...] ALERT: CPU usage is 100.0%, which exceeds the 80% threshold.
$ kill $(jobs -p)
```
Confirms threshold logic actually triggers, not just prints numbers.

**3. Alert written to log file, not just console**
```
$ cat health_monitor.log
[2026-08-31 16:4x:xx] ALERT: CPU usage is 100.0%, which exceeds the 80% threshold.
```

**4. Application Health Checker correctly detects DOWN**
```
$ python3 app_health_checker.py https://wisecow.local:8443 --insecure
[2026-08-31 16:41:41] https://wisecow.local:8443 -> DOWN (Connection error (host unreachable / refused))
```
(App was unreachable at this point because the `kubectl port-forward` tunnel to the ingress controller wasn't active — proves the script correctly reports DOWN rather than falsely reporting UP.)

**5. Application Health Checker correctly detects UP**
```
$ kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8443:443 &
$ echo "127.0.0.1 wisecow.local" | sudo tee -a /etc/hosts
$ python3 app_health_checker.py https://wisecow.local:8443 --insecure
[...] https://wisecow.local:8443 -> UP (HTTP 200)
```
Same app, same URL, only difference is the tunnel being active — confirms the UP/DOWN classification is accurate in both directions, not hardcoded.
