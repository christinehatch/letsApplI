from __future__ import annotations

from pathlib import Path

THRESHOLD = 700
ORCH_THRESHOLD = 3
PATTERNS = ("resolve_content", "build_spans", "interpretation", "hydration")


def _count_orchestration_endpoints(text: str) -> int:
    count = 0
    for block in text.split("\n@app."):
        if "def " not in block:
            continue
        lower = block.lower()
        if any(p in lower for p in PATTERNS):
            count += 1
    return count


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    bridge_path = repo_root / "bridge_server.py"
    if not bridge_path.exists():
        print("Architecture guard failed: bridge_server.py not found.")
        return

    text = bridge_path.read_text(encoding="utf-8")
    lines = len(text.splitlines())
    orch_endpoints = _count_orchestration_endpoints(text)

    if lines > THRESHOLD or orch_endpoints > ORCH_THRESHOLD:
        print("⚠️ Architecture Guard Triggered\n")
        print(f"bridge_server.py is {lines} lines.")
        print("This exceeds the architecture threshold.\n")
        print("Recommended action:")
        print("Introduce service layer:\n")
        print("services/")
        print("    job_view_service.py")
        print("    interpretation_service.py")
        print("    discovery_service.py")
        print("\nbridge_server should only contain API routing.")
        print(f"\nOrchestration endpoint matches: {orch_endpoints}")
        return

    print("Architecture guard check passed.")


if __name__ == "__main__":
    main()
