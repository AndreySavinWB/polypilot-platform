"""Quick Simplicity Filter scan (no LLM)."""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.agents.event_ranking import get_rank_mode, scan_and_rank
from src.services.polymarket import scan_active_events


def load_env():
    env_path = os.path.join(ROOT, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def main():
    load_env()
    os.environ.setdefault("PP_RANK_MODE", "simple")
    scan_limit = int(os.getenv("PP_SCAN_LIMIT", "300"))
    top_n = int(os.getenv("PP_TOP_N", "10"))

    print("Rank mode:", get_rank_mode())
    pool = scan_active_events(max_events=scan_limit)
    print(f"Fetched {len(pool)} events")

    ranking = scan_and_rank(pool, top_n=top_n)
    print(
        f"accepted={ranking['accepted']} watchlist={ranking['watchlist']} "
        f"rejected={ranking['rejected']} top={len(ranking['top'])}"
    )
    for row in ranking["top"]:
        p = row["priority"]
        print(
            f"  [{p['score']}] {p.get('categoryLabel')} · "
            f"{row['event'].get('title')}"
        )

    out = os.path.join(ROOT, "data", "simplicity_scan_preview.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "topTitles": [
                    {
                        "title": r["event"].get("title"),
                        "score": r["priority"]["score"],
                        "category": r["priority"].get("simpleCategory"),
                    }
                    for r in ranking["top"]
                ],
                **{k: ranking[k] for k in ("scannedTotal", "accepted", "watchlist", "rejected", "rubricVersion")},
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )
    print("Preview:", out)


if __name__ == "__main__":
    main()
