#!/usr/bin/env python3
"""
System Health Monitoring Script
--------------------------------
Checks CPU usage, memory usage, disk space, and running process count.
If any metric crosses its threshold, an ALERT is printed to the console
AND written to a log file, with a timestamp.

Usage:
    python3 system_health_monitor.py                # run once
    python3 system_health_monitor.py --watch 5       # run every 5 seconds, forever (Ctrl+C to stop)

Dependencies:
    pip install psutil --break-system-packages
"""

import argparse
import datetime
import os
import sys

try:
    import psutil
except ImportError:
    print("ERROR: 'psutil' is not installed. Run: pip install psutil --break-system-packages")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Configuration — thresholds are easy to tweak here
# ---------------------------------------------------------------------------
CPU_THRESHOLD_PERCENT = 80
MEMORY_THRESHOLD_PERCENT = 80
DISK_THRESHOLD_PERCENT = 80
DISK_PATH_TO_CHECK = "/"
PROCESS_COUNT_THRESHOLD = 300  # alert if more than this many processes are running

LOG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "health_monitor.log")


def timestamp():
    """Return a readable current timestamp string."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log_alert(message):
    """Print an alert to the console AND append it to the log file."""
    line = f"[{timestamp()}] ALERT: {message}"
    print(line)
    with open(LOG_FILE_PATH, "a") as f:
        f.write(line + "\n")


def log_info(message):
    """Print a normal (non-alert) status line to the console only."""
    print(f"[{timestamp()}] INFO:  {message}")


def check_cpu():
    """Check CPU usage % (averaged over 1 second) against the threshold."""
    usage = psutil.cpu_percent(interval=1)
    log_info(f"CPU usage: {usage}%")
    if usage > CPU_THRESHOLD_PERCENT:
        log_alert(f"CPU usage is {usage}%, which exceeds the {CPU_THRESHOLD_PERCENT}% threshold.")


def check_memory():
    """Check RAM usage % against the threshold."""
    mem = psutil.virtual_memory()
    log_info(f"Memory usage: {mem.percent}% (used {mem.used // (1024**2)}MB / total {mem.total // (1024**2)}MB)")
    if mem.percent > MEMORY_THRESHOLD_PERCENT:
        log_alert(f"Memory usage is {mem.percent}%, which exceeds the {MEMORY_THRESHOLD_PERCENT}% threshold.")


def check_disk():
    """Check disk usage % for the configured path against the threshold."""
    disk = psutil.disk_usage(DISK_PATH_TO_CHECK)
    log_info(f"Disk usage ({DISK_PATH_TO_CHECK}): {disk.percent}% (free {disk.free // (1024**3)}GB)")
    if disk.percent > DISK_THRESHOLD_PERCENT:
        log_alert(f"Disk usage on {DISK_PATH_TO_CHECK} is {disk.percent}%, "
                   f"which exceeds the {DISK_THRESHOLD_PERCENT}% threshold.")


def check_processes():
    """Check the total number of running processes against the threshold."""
    process_count = len(psutil.pids())
    log_info(f"Running processes: {process_count}")
    if process_count > PROCESS_COUNT_THRESHOLD:
        log_alert(f"Process count is {process_count}, which exceeds the {PROCESS_COUNT_THRESHOLD} threshold.")


def run_all_checks():
    print(f"\n--- Health check at {timestamp()} ---")
    check_cpu()
    check_memory()
    check_disk()
    check_processes()


def main():
    parser = argparse.ArgumentParser(description="Monitor Linux system health.")
    parser.add_argument(
        "--watch",
        type=int,
        metavar="SECONDS",
        help="Run continuously, checking every SECONDS seconds, until Ctrl+C.",
    )
    args = parser.parse_args()

    if args.watch:
        print(f"Watching system health every {args.watch}s. Press Ctrl+C to stop.")
        print(f"Alerts are logged to: {LOG_FILE_PATH}\n")
        try:
            import time
            while True:
                run_all_checks()
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nStopped by user.")
    else:
        run_all_checks()


if __name__ == "__main__":
    main()
