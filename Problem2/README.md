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
---
**1. Normal run — all metrics under threshold**
---
<img width="805" height="277" alt="WhatsApp Image 2026-08-31 at 9 37 34 PM" src="https://github.com/user-attachments/assets/4b9f85d0-2811-446a-b7e8-62304fd2e843" />

---
**2. Alert correctly fires when CPU is pushed to 100%**
---
<img width="769" height="417" alt="WhatsApp Image 2026-08-31 at 9 41 03 PM" src="https://github.com/user-attachments/assets/c8105af7-b9d0-47f9-bde3-5039dfd0fcd8" />
Confirms threshold logic actually triggers, not just prints numbers.

---
**3. Alert written to log file, not just console**
---
<img width="802" height="135" alt="WhatsApp Image 2026-08-31 at 9 41 24 PM" src="https://github.com/user-attachments/assets/baedf12d-2aef-4826-b2a4-536e3e2869ed" />

---
**4. Application Health Checker correctly detects DOWN**
---
<img width="1150" height="190" alt="WhatsApp Image 2026-08-31 at 9 41 59 PM" src="https://github.com/user-attachments/assets/6e6341d7-2faf-4444-ab40-1fe0e95db772" />

(App was unreachable at this point because the `kubectl port-forward` tunnel to the ingress controller wasn't active — proves the script correctly reports DOWN rather than falsely reporting UP.)
---
**5. Application Health Checker correctly detects UP**
---
<img width="1141" height="259" alt="WhatsApp Image 2026-08-31 at 9 45 01 PM" src="https://github.com/user-attachments/assets/549ebdd8-77cb-46bc-bd20-6cc8676b158f" />


Same app, same URL, only difference is the tunnel being active — confirms the UP/DOWN classification is accurate in both directions, not hardcoded.
