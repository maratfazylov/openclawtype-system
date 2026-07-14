"""Reset the stage 05 SWE demo to the expected buggy starting point."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VK = ROOT / "connectors" / "vk.py"
BRIDGE = ROOT / "scripts" / "vk_langgraph_bridge.py"
FIXTURE_DIR = ROOT / "demo_fixtures" / "swe_stage_05"
VK_BEFORE = FIXTURE_DIR / "vk.py.before"
BRIDGE_BEFORE = FIXTURE_DIR / "vk_langgraph_bridge.py.before"


def main() -> int:
    if not VK_BEFORE.exists() or not BRIDGE_BEFORE.exists():
        raise RuntimeError(f"Missing SWE demo fixtures in {FIXTURE_DIR}")

    shutil.copyfile(VK_BEFORE, VK)
    shutil.copyfile(BRIDGE_BEFORE, BRIDGE)
    print("✓ restored connectors/vk.py")
    print("✓ restored scripts/vk_langgraph_bridge.py")

    vk_source = VK.read_text()
    bridge_source = BRIDGE.read_text()
    ok = True

    if "def split_vk_message" in vk_source or "split_vk_message" in vk_source:
        print("! connectors/vk.py already contains split helper; stage 05 may already be solved")
        ok = False
    else:
        print("✓ connectors/vk.py has no split helper yet")

    if "reply[:3500]" in bridge_source:
        print("✓ bridge still truncates long replies; demo defect is present")
    else:
        print("! bridge no longer contains reply[:3500]; demo defect may already be solved")
        ok = False

    print()
    print("Stage 05 expected task:")
    print("- add VK message chunking with <=3500 chars per chunk")
    print("- avoid empty chunks")
    print("- preserve order and full text")
    print("- call messages.send once per chunk")
    print("- use a distinct random_id for each chunk")
    print("- add unit tests without real VK network")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
