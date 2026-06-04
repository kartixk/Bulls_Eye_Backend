from __future__ import annotations
from core.types import Signal


def format_signal(s: Signal) -> str:
    emoji = "🟢" if s["action"] == "BUY" else "🔴"
    lines = [
        f"{emoji} *{s['action']}* `{s['instrument']}`  ({s['confidence']:.0f}%)",
        f"Entry: `{s['entry_price']}`",
    ]
    if s.get("target_price"):
        lines.append(f"Target: `{s['target_price']}`")
    if s.get("stop_loss"):
        lines.append(f"Stop:   `{s['stop_loss']}`")
    if s["kind"] == "FNO":
        lines.append(f"Strike: `{s.get('strike_price')}` exp `{s.get('expiry_date')}`")
    if s.get("rationale"):
        lines.append(f"_{s['rationale']}_")
    return "\n".join(lines)
