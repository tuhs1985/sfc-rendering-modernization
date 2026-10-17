"""Bounded, process-filtered PresentMon console capture; never touches SFC."""
import argparse
import csv
import json
import math
import queue
import subprocess
import threading
import time
import uuid
from pathlib import Path


def analyze_csv(path, target_pid):
    groups = {}
    rows = 0
    with open(path, encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = {name.casefold(): name for name in (reader.fieldnames or [])}
        if len(fields) != len(reader.fieldnames or []):
            raise ValueError("Ambiguous duplicate PresentMon columns")
        required = {"processid", "swapchainaddress", "msbetweenpresents"}
        if not required.issubset(fields):
            raise ValueError("PresentMon v1 columns missing; native coverage unqualified")
        for row in reader:
            if int(row[fields["processid"]]) != target_pid:
                raise ValueError("Unexpected process in PID-filtered capture")
            value = float(row[fields["msbetweenpresents"]])
            if not math.isfinite(value) or value < 0:
                raise ValueError("Invalid presentation interval")
            rows += 1
            # First frame can legitimately have no predecessor.
            if value:
                groups.setdefault(row[fields["swapchainaddress"]], []).append(value)
    if not groups:
        raise ValueError("No positive presentation intervals; coverage unqualified")
    result = {}
    for chain, values in groups.items():
        values.sort()
        result[chain] = {"intervals": len(values), "mean_ms": sum(values) / len(values),
                         "p95_ms": values[math.ceil(.95 * len(values)) - 1],
                         "max_ms": values[-1]}
    return {"rows": rows, "swap_chains": result}


def capture(command, output, seconds, hard_bytes=64 * 1024 * 1024, guard_seconds=10,
            stop_file=None):
    """Pipe backpressure plus a strict writer cap; only terminate our child."""
    output = Path(output)
    stderr_path = output.with_suffix(output.suffix + ".stderr.txt")
    summary_path = output.with_suffix(output.suffix + ".capture.json")
    if any(p.exists() for p in (output, stderr_path, summary_path)):
        raise FileExistsError("Use fresh output paths; evidence is never overwritten")
    output.parent.mkdir(parents=True, exist_ok=True)
    events = queue.Queue(maxsize=128)
    stop = threading.Event()
    process = None
    workers = []
    counts = [0, 0]
    failure = None
    began = time.monotonic()

    def read_pipe(pipe, index):
        try:
            while not stop.is_set():
                line = pipe.readline(8193)
                item = (index, line)
                while not stop.is_set():
                    try:
                        events.put(item, timeout=.1)
                        break
                    except queue.Full:
                        pass
                if not line:
                    break
        except OSError:
            pass

    try:
        with output.open("xb") as stdout_file, stderr_path.open("xb") as stderr_file:
            process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE,
                                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            for index, pipe in enumerate((process.stdout, process.stderr)):
                worker = threading.Thread(target=read_pipe, args=(pipe, index), daemon=True)
                worker.start()
                workers.append(worker)
            finished = set()
            while len(finished) < 2:
                if stop_file and Path(stop_file).exists():
                    raise RuntimeError("Collector cancellation requested")
                if time.monotonic() - began > seconds + guard_seconds:
                    raise TimeoutError("Collector wall-time guard reached")
                try:
                    index, line = events.get(timeout=.1)
                except queue.Empty:
                    continue
                if not line:
                    finished.add(index)
                    continue
                cap = hard_bytes if index == 0 else 65536
                if len(line) > 8192 or counts[index] + len(line) > cap:
                    raise ValueError("Collector output/line limit reached")
                (stdout_file if index == 0 else stderr_file).write(line)
                counts[index] += len(line)
            process.wait(timeout=2)
            if process.returncode:
                raise RuntimeError(f"Collector exit code {process.returncode}")
    except Exception as error:
        failure = str(error)
    finally:
        stop.set()
        if process:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
            for worker in workers:
                worker.join(timeout=1)
            process.stdout.close()
            process.stderr.close()
    result = {"complete": failure is None, "error": failure, "command": command,
              "stdout_bytes": counts[0], "stderr_bytes": counts[1],
              "elapsed_seconds": time.monotonic() - began,
              "exit_code": process.returncode if process else None}
    with summary_path.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", type=Path)
    parser.add_argument("--pid", required=True, type=int)
    parser.add_argument("--seconds", type=int)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--analyze-only", action="store_true")
    parser.add_argument("--analysis-output", type=Path)
    parser.add_argument("--stop-file", type=Path)
    args = parser.parse_args()
    if args.analyze_only:
        if args.pid <= 0:
            parser.error("Positive PID required")
        result = {"analysis": analyze_csv(args.output, args.pid),
                  "source": str(args.output), "pid": args.pid,
                  "adjudication": "reanalysis-only; original collector result preserved"}
        if args.analysis_output:
            with args.analysis_output.open("x", encoding="utf-8") as stream:
                json.dump(result, stream, indent=2)
        print(json.dumps(result, indent=2))
        return 0
    if not args.tool or args.seconds is None or args.pid <= 0 or not 1 <= args.seconds <= 2100:
        parser.error("Positive PID and 1..2100 seconds required")
    command = [str(args.tool.resolve()), "--process_id", str(args.pid),
               "--timed", str(args.seconds), "--terminate_after_timed",
               "--v1_metrics", "--output_stdout", "--no_console_stats",
               "--session_name", "SFCM1_" + uuid.uuid4().hex]
    result = capture(command, args.output, args.seconds, stop_file=args.stop_file)
    if not result["complete"]:
        # A terminated ETW consumer can leave its named session behind. Clean
        # only our unique session; never terminate someone else's capture.
        cleanup = subprocess.Popen([str(args.tool.resolve()), "--session_name", command[-1],
                                    "--terminate_existing_session"],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        try:
            cleanup.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cleanup.kill()
            cleanup.wait(timeout=3)
        result["owned_session_cleanup_exit"] = cleanup.returncode
    if result["complete"]:
        try:
            result["analysis"] = analyze_csv(args.output, args.pid)
        except (ValueError, KeyError) as error:
            result["complete"] = False
            result["error"] = str(error)
    # Analysis goes to stdout; capture metadata remains the collector's own result.
    print(json.dumps(result, indent=2))
    return 0 if result["complete"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
