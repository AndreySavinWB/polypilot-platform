"""Unified event ranking — Simplicity Filter (default) or legacy Priority Agent."""

from __future__ import annotations

import os

from src.agents import priority, simplicity

RANK_MODES = ("simple", "priority")


def get_rank_mode() -> str:
    mode = (os.getenv("PP_RANK_MODE") or "simple").strip().lower()
    return mode if mode in RANK_MODES else "simple"


def score_event(event, use_llm=False):
    if get_rank_mode() == "priority":
        return priority.score_event(event, use_llm=use_llm)
    return simplicity.score_event(event)


def scan_and_rank(events, top_n=10, min_decision=None, use_llm_top_k=0):
    mode = get_rank_mode()
    if mode == "priority":
        if min_decision is None:
            min_decision = "watchlist"
        return priority.scan_and_rank(
            events,
            top_n=top_n,
            min_decision=min_decision,
            use_llm_top_k=use_llm_top_k,
        )

    if min_decision is None:
        min_decision = "accepted"
    return simplicity.scan_and_rank(
        events,
        top_n=top_n,
        min_decision=min_decision,
        use_llm_top_k=0,
    )
