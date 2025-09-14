import argparse, subprocess, sys, datetime, pathlib

BATCH_MAP = {
    "p1": ["tests/test_checkboxes.py"],
    "p2": ["tests/test_dropdown.py"]
}


def run_batch(batch: str, out_root: pathlib.Path) -> int:
    out_dir = out_root / batch
    out_dir.mkdir(parents=True, exist_ok=True)
    junit = out_dir / f"results_{batch}.xml"
    html = out_dir / f"report_{batch}.html"
    cmd = [sys.executable, "-m", "pytest", *BATCH_MAP[batch],
           f"--junitxml={junit}", f"--html={html}", "--self-contained-html", "-q"]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--batch", choices=["p1", "p2", "all"], required=True)
    p.add_argument("--out", default=f"artifacts/{datetime.date.today().isoformat()}")
    a = p.parse_args()
    out_root = pathlib.Path(a.out)
    batches = ["p1", "p2"] if a.batch == "all" else [a.batch]
    rc = 0
    for b in batches:
        rc = rc or run_batch(b, out_root)
    print("Artifacts at:", out_root.resolve());
    sys.exit(rc)


if __name__ == "__main__":
    main()
