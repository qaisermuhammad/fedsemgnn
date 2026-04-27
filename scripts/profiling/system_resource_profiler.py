dataset_path = "workloads/sample_dataset3.json"



import time
import json
import os
import platform
import psutil
import subprocess
import threading
import sys
from datetime import datetime

DATASET_PATH = "workloads/sample_dataset3.json"
ALGORITHMS = [
    ("FedSemGNN",    [sys.executable, "main.py", "--algorithm", "FedSemGNN", "--steps", "5", "--override-num-nodes", "10"]),
    ("FlatFedPPO",   [sys.executable, "main.py", "--algorithm", "FlatFedPPO", "--steps", "5", "--override-num-nodes", "10"]),
    ("HierFedPPO",   [sys.executable, "main.py", "--algorithm", "HierFedPPO", "--steps", "5", "--override-num-nodes", "10"]),
    ("HSQF",         [sys.executable, "main.py", "--algorithm", "HSQF", "--steps", "5", "--override-num-nodes", "10"]),
    ("RandomPlacement", [sys.executable, "main.py", "--algorithm", "RandomPlacement", "--steps", "5", "--override-num-nodes", "10"]),
]

LOGS_DIR = "logs"
os.makedirs(LOGS_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
logfile_path = os.path.join(LOGS_DIR, f"system_resource_profile_{timestamp}.txt")

def log(msg):
    print(msg)
    with open(logfile_path, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

def print_system_info():
    log("System: {} {}".format(platform.system(), platform.release()))
    log("CPU: {}".format(platform.processor()))
    log("CPU Cores: {}".format(psutil.cpu_count(logical=True)))
    log("RAM (GB): {}".format(round(psutil.virtual_memory().total / (1024**3), 2)))

def print_dataset_info():
    if os.path.exists(DATASET_PATH):
        file_size = os.path.getsize(DATASET_PATH) / (1024**2)
        log(f"Dataset file size (MB): {round(file_size, 2)}")
        start = time.time()
        with open(DATASET_PATH, "r") as f:
            data = json.load(f)
        end = time.time()
        log(f"Dataset load time (seconds): {round(end - start, 4)}")
        log(f"Dataset keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
        # Node/component count (customize as needed)
        if isinstance(data, dict) and "nodes" in data:
            log(f"Node count: {len(data['nodes'])}")
        elif isinstance(data, list):
            log(f"Top-level list length: {len(data)}")
    else:
        log(f"Dataset file not found: {DATASET_PATH}")

def monitor_process(proc, interval=1):
    peak_mem = 0
    cpu_samples = []
    try:
        p = psutil.Process(proc.pid)
        while proc.poll() is None:
            mem = p.memory_info().rss / (1024**2)
            cpu = p.cpu_percent(interval=0.1)
            peak_mem = max(peak_mem, mem)
            cpu_samples.append(cpu)
            time.sleep(interval)
    except Exception:
        pass
    return peak_mem, cpu_samples

def profile_experiment():
    log("\n--- Per-Algorithm Experiment Profiling (10,000 nodes) ---")
    results = []
    for algoname, cmd in ALGORITHMS:
        log(f"\nRunning {algoname}...")
        start = time.time()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        peak_mem, cpu_samples = monitor_process(proc)
        stdout, stderr = proc.communicate()
        end = time.time()
        runtime = round(end - start, 2)
        avg_cpu = round(sum(cpu_samples)/len(cpu_samples), 2) if cpu_samples else 0.0
        log(f"{algoname} runtime (seconds): {runtime}")
        log(f"{algoname} peak memory usage (MB): {round(peak_mem, 2)}")
        log(f"{algoname} average CPU usage (%): {avg_cpu}")
        log(f"{algoname} exit code: {proc.returncode}")
        if proc.returncode == 0:
            log(f"{algoname} completed successfully")
        else:
            log(f"{algoname} failed (return code {proc.returncode})")
        # Optionally log stdout/stderr for debugging
        if stdout:
            log(f"--- STDOUT ---\n{stdout.decode(errors='replace')}")
        if stderr:
            log(f"--- STDERR ---\n{stderr.decode(errors='replace')}")
        # Check for metrics file (case-insensitive match)
        metrics_files = [
            f"results/{algoname}_metrics.csv",
            f"results/{algoname.lower()}_metrics.csv",
            f"results/{algoname.upper()}_metrics.csv"
        ]
        found = False
        for mf in metrics_files:
            if os.path.exists(mf):
                log(f"Metrics file found for {algoname}: {mf}")
                found = True
                break
        if not found:
            log(f"WARNING: Metrics file missing for {algoname}: tried {metrics_files}")
        results.append({
            "algorithm": algoname,
            "runtime_sec": runtime,
            "peak_mem_mb": round(peak_mem, 2),
            "avg_cpu": avg_cpu,
            "exit_code": proc.returncode
        })
    log("\nAll algorithms complete!")
    return results


if __name__ == "__main__":
    log("--- System Resource Profiler ---")
    print_system_info()
    log("\n--- Dataset Profiling ---")
    print_dataset_info()
    log("\nProfiling each algorithm for 10,000 nodes, 1,000 steps...")
    profile_experiment()
    log(f"\nResource profiling complete. See log file: {logfile_path}")

# Rename this file to system_resource_profiler.py for clarity.