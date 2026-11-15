"""依次运行全部方法，用于试点与全量。"""

import argparse
import subprocess
import sys

METHODS = ["direct", "cot", "self_consistency", "self_refine", "debate", "mas"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--per-level", type=int, default=None)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    for method in METHODS:
        cmd = [sys.executable, "scripts/run_eval.py", method,
               "--workers", str(args.workers)]
        if args.per_level:
            cmd += ["--per-level", str(args.per_level)]
        print(f"运行 {method}", flush=True)
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
