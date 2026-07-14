"""Check/reset the stage 05 SWE demo to the expected buggy starting point.

This script intentionally does not edit files. It verifies that the live demo
still contains the long-message defect the SWE agent is expected to fix.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VK = ROOT / "connectors" / "vk.py"
BRIDGE = ROOT / "scripts" / "vk_langgraph_bridge.py"


def main() -> int:
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
    print("- add unit tests without real VK network")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
