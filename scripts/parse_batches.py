import xml.etree.ElementTree as ET
import pathlib, json, sys


def parse_junit(xml_path: pathlib.Path):
    root = ET.parse(xml_path).getroot()
    suites = [root] if root.tag == "testsuite" else root.findall("testsuite")
    total = passed = failed = skipped = 0
    for s in suites:
        t = int(s.attrib.get("tests", 0))
        f = int(s.attrib.get("failures", 0)) + int(s.attrib.get("error", 0))
        sk = int(s.attrib.get("skipped", 0))
        p = t - f - sk
        total += t;
        passed += p;
        failed += f;
        skipped += sk
    return {"total": total, "passed": passed, "failed": failed, "skipped": skipped}


def main():
    root_dir = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path("artifacts")
    per_batch = {}
    for batch_dir in sorted(p for p in root_dir.iterdir() if p.is_dir()):
        xmls = list(batch_dir.glob("results_*.xml"))
        if xmls:
            per_batch[batch_dir.name] = parse_junit(xmls[0])
    overall = {
        "total": sum(v["total"] for v in per_batch.values()),
        "passed": sum(v["passed"] for v in per_batch.values()),
        "failed": sum(v["failed"] for v in per_batch.values()),
        "skipped": sum(v["skipped"] for v in per_batch.values()),
    }
    overall["pass_rate_pct"] = round((overall["passed"] / overall["total"]) * 100, 2) if overall["total"] else 0.0
    out = {"batches": per_batch, "overall": overall}
    out_path = root_dir / "summary.json"
    out_path.write_text(json.dumps(out, indent=2))
    print(out_path.read_text())


if __name__ == "__main__":
    main()
