"""
Download the latest AngelOne scrip master and update data/nifty100.json tokens.
Run once whenever you see "Symbol token not found" errors from the API.

    python scripts/refresh_tokens.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

SCRIP_MASTER_URL = (
    "https://margincalculator.angelone.in/OpenAPI_File/files/OpenAPIScripMaster.json"
)
NIFTY100_PATH = Path(__file__).parent.parent / "data" / "nifty100.json"


def fetch_scrip_master() -> list[dict]:
    print("Downloading AngelOne scrip master (this may take a moment)…")
    with urllib.request.urlopen(SCRIP_MASTER_URL, timeout=60) as r:
        data = json.loads(r.read())
    print(f"  Downloaded {len(data):,} entries")
    return data


def build_lookup(scrip_master: list[dict]) -> dict[tuple[str, str], str]:
    """Return {(exch_seg, symbol): token} for fast look-up."""
    return {
        (entry["exch_seg"], entry["symbol"]): entry["token"]
        for entry in scrip_master
        if "exch_seg" in entry and "symbol" in entry and "token" in entry
    }


def refresh_tokens() -> dict:
    """Refresh tokens in nifty100.json from the AngelOne scrip master.
    Returns a summary dict — safe to call from the scheduler."""
    import logging
    log = logging.getLogger(__name__)
    try:
        scrip_master = fetch_scrip_master()
        lookup = build_lookup(scrip_master)
        instruments: list[dict] = json.loads(NIFTY100_PATH.read_text())
        updated, missing = 0, []
        for inst in instruments:
            key = (inst["exchange"], inst["tradingsymbol"])
            token = lookup.get(key)
            if token:
                if inst["symboltoken"] != token:
                    log.info("token refresh: %s %s -> %s", inst["name"], inst["symboltoken"], token)
                    inst["symboltoken"] = token
                    updated += 1
            else:
                missing.append(inst["name"])
        NIFTY100_PATH.write_text(json.dumps(instruments, indent=2))
        log.info("token refresh done: %d updated, %d missing", updated, len(missing))
        if missing:
            log.warning("token refresh: no scrip master entry for %s", missing)
        return {"updated": updated, "missing": missing}
    except Exception as exc:
        logging.getLogger(__name__).error("token refresh failed: %s", exc)
        return {"error": str(exc)}


def main() -> None:
    result = refresh_tokens()
    updated = result.get("updated", 0)
    missing = result.get("missing", [])
    print(f"\nDone: {updated} token(s) updated.")
    if missing:
        print(f"WARNING: could not find tokens for: {', '.join(missing)}")
        print("  These symbols may have been renamed — check AngelOne scrip master manually.")


if __name__ == "__main__":
    main()
