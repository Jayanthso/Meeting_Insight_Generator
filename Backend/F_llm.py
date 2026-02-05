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
def summarize(text, sentences=4):
    """
    Cleaner extractive summary.
    Removes very short/noisy lines first.
    """

    # remove short lines + noise
    cleaned = "\n".join(
        l.strip() for l in text.split("\n")
        if len(l.strip()) > 30
    )

    parser = PlaintextParser.from_string(cleaned, Tokenizer("english"))
    summarizer = LsaSummarizer()

    summary = summarizer(parser.document, sentences)

    result = " ".join(str(s) for s in summary)

    # fallback safety
    if len(result) < 40:
        return cleaned[:400]

    return result


# =========================================================
# KEY POINTS
# =========================================================
def extract_key_points(text):
    seen = set()
    points = []

    for l in text.split("\n"):
        l = l.strip()
        if len(l) > 40 and l not in seen:
            points.append(l)
            seen.add(l)

    return points[:6]



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
def extract_actions(text):
    actions = []

    pattern = r"""
        ^(?:[A-Z][a-z]+)?      # optional owner
        [,:]?\s*
        (.*?\b(?:will|must|should|please|by|prepare|send|deliver|update|start)\b.*)
    """

    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 15:
            continue

        m = re.search(pattern, line, re.IGNORECASE | re.VERBOSE)
        if not m:
            continue

        task = m.group(1)

        # detect owner
        owner_match = re.match(r"^([A-Z][a-z]+)", line)
        owner = owner_match.group(1) if owner_match else "Unassigned"

        actions.append({
            "task": task.strip(),
            "owner": owner
        })

    return actions[:10]   # cap noise

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

