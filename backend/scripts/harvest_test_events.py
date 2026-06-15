"""Сканировать Polymarket → Simplicity Filter / Priority → полный анализ топ-N."""

import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from src.agents.event_ranking import get_rank_mode, scan_and_rank
from src.agents.pipeline import analyze_event
from src.agents.pie import run_pie
from src.services.llm import has_llm_key
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


def classify_event(event, priority):
    tags = []
    decision = (priority or {}).get("decision")
    if decision == "accepted":
        tags.append("hot")
    if decision == "watchlist":
        tags.append("watchlist")
    if decision == "rejected":
        tags.append("rejected")

    simple_category = (priority or {}).get("simpleCategory")
    if simple_category and simple_category not in ("other", "hold_politics_macro", "hold_weather"):
        tags.append(simple_category)

    rubric = (priority or {}).get("rubric") or {}
    liq = rubric.get("liquidity") or {}
    if isinstance(liq, dict) and liq.get("score", 100) < 4:
        tags.append("low_liquidity")

    markets_count = int(event.get("marketsCount") or 0)
    if markets_count > 1:
        tags.append("multi_market")

    if not tags:
        tags.append("standard")
    return tags


def main():
    load_env()
    scan_limit = int(os.getenv("PP_SCAN_LIMIT", "300"))
    top_n = int(os.getenv("PP_TOP_N", "10"))

    print("LLM enabled:", has_llm_key(), "| provider:", os.getenv("LLM_PROVIDER"), "| model:", os.getenv("LLM_MODEL") or os.getenv("OPENAI_MODEL"))
    print("Rank mode:", get_rank_mode())
    print(f"Scanning up to {scan_limit} active Polymarket events...")

    pool = scan_active_events(max_events=scan_limit)
    print(f"Fetched {len(pool)} events from Polymarket")

    ranking = scan_and_rank(pool, top_n=top_n, use_llm_top_k=20 if get_rank_mode() == "priority" else 0)
    scan_label = "Simplicity scan" if get_rank_mode() == "simple" else "Priority scan"
    print(
        scan_label + ":",
        f"scanned={ranking['scannedTotal']}",
        f"passedGates={ranking['passedGates']}",
        f"accepted={ranking['accepted']}",
        f"watchlist={ranking['watchlist']}",
        f"rejected={ranking['rejected']}",
        f"top={len(ranking['top'])}",
    )

    output_dir = os.path.join(ROOT, "data")
    os.makedirs(output_dir, exist_ok=True)

    scan_path = os.path.join(output_dir, "priority_scan.json")
    with open(scan_path, "w", encoding="utf-8") as handle:
        json.dump(ranking, handle, ensure_ascii=False, indent=2)

    dataset = []
    for index, row in enumerate(ranking["top"], start=1):
        event = row["event"]
        priority = row["priority"]
        print(f"Analyzing #{index} [score={priority.get('score')}] {event.get('title')}")
        pipeline_package = run_pie(event, priority_result=priority)
        analysis = analyze_event(event, priority_result=priority)
        dataset.append(
            {
                "testNo": index,
                "tags": classify_event(event, priority),
                "event": event,
                "pipelinePackage": pipeline_package,
                "analysis": analysis,
            }
        )

    events_path = os.path.join(output_dir, "test_events.json")
    summary_path = os.path.join(output_dir, "test_events_summary.json")

    with open(events_path, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "count": len(dataset),
                "scanMeta": {
                    "scannedTotal": ranking["scannedTotal"],
                    "weights": ranking["weights"],
                    "rubricVersion": ranking["rubricVersion"],
                },
                "items": dataset,
            },
            handle,
            ensure_ascii=False,
            indent=2,
        )

    summary = [
        {
            "testNo": item["testNo"],
            "id": item["event"].get("id"),
            "title": item["event"].get("title"),
            "tags": item["tags"],
            "priorityScore": (item["analysis"].get("priority") or {}).get("score"),
            "priorityDecision": (item["analysis"].get("priority") or {}).get("decision"),
            "priorityRank": (item["analysis"].get("priority") or {}).get("rank"),
            "riskLevel": (
                (item.get("pipelinePackage") or {}).get("risk") or {}
            ).get("riskLevel")
            or (item["analysis"].get("riskOfficer") or {}).get("riskLevel"),
            "pipelineStatus": (item.get("pipelinePackage") or {}).get("pipelineStatus"),
            "titleRu": ((item.get("pipelinePackage") or {}).get("normalizedEvent") or {}).get("titleRu"),
            "eventType": ((item.get("pipelinePackage") or {}).get("eventClassification") or {}).get("eventType"),
            "ppVerdict": (item["analysis"].get("verdict") or {}).get("ppVerdict", "")[:120],
            "confidence": (item["analysis"].get("verdict") or {}).get("confidence"),
            "sourceUrl": item["event"].get("sourceUrl"),
        }
        for item in dataset
    ]
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)

    print(f"Saved {len(dataset)} events to {events_path}")
    print(f"Priority scan report: {scan_path}")
    for row in summary:
        print(
            f"#{row['testNo']} [{row['priorityDecision']} {row['priorityScore']}] "
            f"{row['title']}"
        )

    sync_script = os.path.join(os.path.dirname(__file__), "sync_live_to_mvp.py")
    if os.path.exists(sync_script):
        subprocess.run([sys.executable, sync_script], cwd=ROOT, check=False)


if __name__ == "__main__":
    main()
