#!/usr/bin/env python3
"""Device simulator — generates randomized vitals and POSTs to medIoT API."""

import argparse
import os
import random
import sys
import time

import requests


def random_walk_vital(min_val: int, max_val: int, current: int) -> int:
    step = random.randint(-3, 3)
    return max(min_val, min(max_val, current + step))


def build_payload(
    device_id: str, hr: int, spo2: int, bp_sys: int, bp_dia: int, bat: int
) -> dict:
    return {
        "ts": int(time.time()),
        "d_id": device_id,
        "hr": hr,
        "spo2": spo2,
        "bp_sys": bp_sys,
        "bp_dia": bp_dia,
        "bat": bat,
    }


def main():
    parser = argparse.ArgumentParser(description="medIoT device simulator")
    parser.add_argument(
        "--api-url",
        default=os.environ.get("API_URL", "http://localhost:8000"),
    )
    parser.add_argument("--api-key", default=os.environ.get("API_KEY", ""))
    parser.add_argument(
        "--device-id",
        required=True,
        help="Device identifier (required, e.g. HM-001)",
    )
    parser.add_argument(
        "--interval", type=float, default=1.0, help="Seconds between readings"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Readings before battery drops 1 percent",
    )
    parser.add_argument("--start-battery", type=int, default=100)
    args = parser.parse_args()

    if not args.api_key:
        print("ERROR: API_KEY is required. Set --api-key or API_KEY env var.")
        sys.exit(1)

    api_url = args.api_url.rstrip("/")
    endpoint = f"{api_url}/api/v1/readings/"

    battery = args.start_battery
    hr = 80
    spo2 = 98
    bp_sys = 120
    bp_dia = 80
    count = 0

    print(f"Simulator started: device={args.device_id}, interval={args.interval}s")
    print(f"POST → {endpoint}")

    try:
        while battery > 0:
            # Random walk vital signs
            hr = random_walk_vital(60, 100, hr)
            spo2 = random_walk_vital(95, 100, spo2)
            bp_sys = random_walk_vital(110, 140, bp_sys)
            bp_dia = random_walk_vital(70, 90, bp_dia)

            # Battery decrement
            if count > 0 and count % args.batch_size == 0:
                battery -= 1

            payload = build_payload(
                args.device_id, hr, spo2, bp_sys, bp_dia, battery
            )

            try:
                resp = requests.post(
                    endpoint,
                    json=payload,
                    headers={"X-API-Key": args.api_key},
                    timeout=5,
                )
                if resp.status_code == 202:
                    print(
                        f"[{count+1:5d}] bat={battery:3d}% "
                        f"hr={hr:3d} spo2={spo2}% "
                        f"bp={bp_sys}/{bp_dia} → {resp.status_code}"
                    )
                else:
                    print(
                        f"[{count+1:5d}] ERROR {resp.status_code}: {resp.text[:80]}"
                    )
            except requests.RequestException as e:
                print(f"[{count+1:5d}] CONNECTION ERROR: {e}")

            count += 1
            time.sleep(args.interval)

    except KeyboardInterrupt:
        print(f"\nSimulator stopped. Sent {count} readings, battery={battery}%")
    else:
        print(f"\nBattery depleted. Sent {count} readings.")


if __name__ == "__main__":
    main()
