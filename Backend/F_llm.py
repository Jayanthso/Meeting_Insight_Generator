# =========================================================
# Backend/F_llm.py
# Production-grade Meeting Insight Engine
# No external LLM / No heavy dependencies
# Uses: nltk + sumy + regex only
# =========================================================

import re
import nltk

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


# ---------------------------------------------------------
# Download once (safe if already present)
# ---------------------------------------------------------
nltk.download("punkt", quiet=True)


# =========================================================
# TEXT NORMALIZATION
# Fix Whisper output + improves all downstream quality
# =========================================================
def normalize_text(text: str) -> str:
    sentences = nltk.sent_tokenize(text)

    clean = []

    for s in sentences:
        s = s.strip()

        # remove filler noise
        s = re.sub(r"\b(um|uh|you know|like|basically|okay)\b", "", s, flags=re.I)

        if len(s) > 10:
            clean.append(s)

    # remove duplicates while preserving order
    return "\n".join(dict.fromkeys(clean))


# =========================================================
# SUMMARY (LSA extractive — fast + stable)
# =========================================================
def summarize(text: str, sentences_count: int = 4) -> str:
    """
    Extractive summary using Sumy LSA
    Works better if we summarize only first part of meeting
    """

    lines = text.split("\n")

    # summarize only first 60% (meetings put key info early)
    partial = "\n".join(lines[: int(len(lines) * 0.6)])

    parser = PlaintextParser.from_string(partial, Tokenizer("english"))
    summarizer = LsaSummarizer()

    summary = summarizer(parser.document, sentences_count)

    return " ".join(str(s) for s in summary)


# =========================================================
# KEY POINTS
# =========================================================
def extract_key_points(text: str, limit: int = 6):
    lines = [
        l.strip()
        for l in text.split("\n")
        if 40 < len(l.strip()) < 200
    ]
    return lines[:limit]


# =========================================================
# DECISIONS
# =========================================================
def extract_decisions(text: str):
    decision_keywords = [
        "decided",
        "agreed",
        "approved",
        "confirmed",
        "finalized",
        "selected",
        "deadline",
        "must deliver",
    ]

    results = []

    for l in text.split("\n"):
        lower = l.lower()
        if any(k in lower for k in decision_keywords):
            results.append(l.strip())

    return results


# =========================================================
# ACTION ITEMS (structured)
# returns:
# [{"task": "...", "owner": "...", "deadline": "..."}]
# =========================================================
def extract_actions(text: str):
    verb_regex = r"\b(start|prepare|draft|deliver|complete|send|update|submit|finish|create|build|test)\b"
    deadline_regex = r"\b(by|before|on)\s+[A-Za-z0-9 ,]+\b"

    actions = []

    for line in text.split("\n"):
        s = line.strip()

        if not s:
            continue

        lower = s.lower()

        # must contain action verb
        if not re.search(verb_regex, lower):
            continue

        # -------- owner detection --------
        owner = "Unassigned"

        m = re.match(r"^([A-Z][a-zA-Z]+)", s)
        if m:
            owner = m.group(1)

        # -------- deadline detection --------
        deadline = ""
        d = re.search(deadline_regex, lower)
        if d:
            deadline = d.group(0)

        # remove speaker labels
        if ":" in s:
            s = s.split(":", 1)[1].strip()

        actions.append({
            "task": s,
            "owner": owner,
            "deadline": deadline
        })

    return actions


# =========================================================
# UTIL
# =========================================================
def unique(items):
    seen = set()
    out = []

    for i in items:
        key = str(i)
        if key not in seen:
            out.append(i)
            seen.add(key)

    return out


# =========================================================
# MAIN PIPELINE
# =========================================================
def generate_insights(transcript, title="", meeting_type="discussion"):
    """
    Main public function used by Streamlit/FastAPI
    """

    if not transcript or len(transcript) < 20:
        return {
            "summary": "",
            "key_points": [],
            "decisions": [],
            "action_items": []
        }

    text = normalize_text(transcript)

    summary = summarize(text)
    key_points = unique(extract_key_points(text))
    decisions = unique(extract_decisions(text))
    actions = unique(extract_actions(text))

    # small meeting-type tuning
    if meeting_type == "standup":
        key_points = key_points[:3]

    return {
        "summary": summary,
        "key_points": key_points,
        "decisions": decisions,
        "action_items": actions
    }
