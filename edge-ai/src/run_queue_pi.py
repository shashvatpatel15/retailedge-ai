#!/usr/bin/env python3
"""
Standalone RetailEdge AI Queue Monitoring Runner for Raspberry Pi 3 B+.
Headless, ultra-lightweight execution with live console telemetry.
"""

import sys
import time
import signal
import argparse
from pathlib import Path

# Add edge-ai/src to python path
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from engine.queue_engine import QueueEngine


def main():
    parser = argparse.ArgumentParser(description="RetailEdge AI - Raspberry Pi Queue Monitor")
    parser.add_argument(
        "-s", "--source",
        type=str,
        default=None,
        help="Camera source: device index (e.g. 0), stream URL (e.g. http://IP:8080/video), video file, or 'mock'"
    )
    args = parser.parse_args()

    print("==================================================")
    print("  RetailEdge AI - Raspberry Pi 3 B+ Queue Engine  ")
    print("==================================================")
    print("Initializing lightweight edge vision runtime...")

    engine = QueueEngine(camera_source=args.source)

    # Graceful shutdown handler
    def handle_signal(sig, frame):
        print("\n\nShutting down RetailEdge Queue AI gracefully...")
        engine.stop()

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    import threading
    engine_thread = threading.Thread(
        target=engine.run,
        kwargs={"display": False},
        daemon=True
    )
    engine_thread.start()

    print("\n[AI Active] Monitoring Billing Queue. Press Ctrl+C to stop.\n")
    print("-" * 75)
    print(f"{'Time':<10} | {'FPS':<6} | {'Inference':<10} | {'Tracked':<8} | {'Queue':<6} | {'Avg Wait':<9} | {'Alert':<6}")
    print("-" * 75)

    try:
        while engine.running:
            snap = engine.get_snapshot()
            timestamp_str = time.strftime("%H:%M:%S", time.localtime(snap["timestamp"]))
            alert_str = "ALERT!" if snap["alert"] else "OK"
            avg_wait_str = f"{snap['average_wait']:.1f}s"
            inf_str = f"{snap['inference_time_ms']:.1f}ms"
            fps_str = f"{snap['fps']:.1f}"

            print(
                f"{timestamp_str:<10} | "
                f"{fps_str:<6} | "
                f"{inf_str:<10} | "
                f"{snap['tracked_people']:<8} | "
                f"{snap['queue_length']:<6} | "
                f"{avg_wait_str:<9} | "
                f"{alert_str:<6}"
            )
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        engine.stop()
        engine_thread.join(timeout=2.0)
        print("\nEngine stopped cleanly.")


if __name__ == "__main__":
    main()