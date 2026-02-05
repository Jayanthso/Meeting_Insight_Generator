# Backend/F_llm.py
# -------------------------------------------------
# 100% FREE
# 100% offline
# No transformers
# No torch
# Streamlit-Cloud safe
# Production stable
# -------------------------------------------------

import re
import nltk
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

nltk.download("punkt", quiet=True)


# =================================================
# -------- TEXT NORMALIZATION (CRITICAL FIX) -------
# =================================================

def normalize_text(text: str) -> str:
    """
    Whisper returns 1 long paragraph.
    NLP needs sentence-per-line format.
    """
    sentences = nltk.sent_tokenize(text)
    return "\n".join(sentences)


# =================================================
# ---------------- SUMMARY -------------------------
# =================================================

def summarize(text: str, sentences_count: int = 4) -> str:
    """
    Lightweight extractive summary using LSA.
    Works offline. No models required.
    """
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()

    summary = summarizer(parser.document, sentences_count)

    return " ".join(str(s) for s in summary)


# =================================================
# --------------- ACTION ITEMS ---------------------
# =================================================

def extract_actions(text: str):
    """
    Returns structured actions:
    [
        {"task": "...", "owner": "..."}
    ]
    """

    actions = []

    action_verbs = [
        "will", "must", "should",
        "start", "prepare", "draft",
        "deliver", "complete", "finish",
        "send", "update", "create",
        "submit", "plan"
    ]

    for line in text.split("\n"):
        sentence = line.strip()

        if not sentence:
            continue

        lower = sentence.lower()

        # detect action sentence
        if not any(v in lower for v in action_verbs):
            continue

        # -------- owner detection --------
        owner = "Unassigned"

        # Pattern 1: "Rahul will prepare..."
        m = re.match(r"^([A-Z][a-zA-Z]+)\s+(will|must|should|to|can|starts?|prepares?|drafts?|delivers?)", sentence)
        if m:
            owner = m.group(1)

        # Pattern 2: "Meera, can you draft..."
        if owner == "Unassigned":
            m = re.match(r"^([A-Z][a-zA-Z]+),", sentence)
            if m:
                owner = m.group(1)

        # Pattern 3: "Arjun’s team..."
        if owner == "Unassigned":
            m = re.match(r"^([A-Z][a-zA-Z]+)['’]s", sentence)
            if m:
                owner = m.group(1)

        # remove speaker prefix like "Priya:"
        if ":" in sentence:
            sentence = sentence.split(":", 1)[1].strip()

        task = sentence.strip()

        actions.append({
            "task": task,
            "owner": owner
        })

    return actions


# =================================================
# ---------------- DECISIONS -----------------------
# =================================================

def extract_decisions(text: str):
    keywords = [
        "decided",
        "approved",
        "confirmed",
        "deadline",
        "must",
        "finalized"
    ]

    decisions = []

    for line in text.split("\n"):
        if any(k in line.lower() for k in keywords):
            decisions.append(line.strip())

    return decisions


# =================================================
# --------------- KEY POINTS -----------------------
# =================================================

def extract_key_points(text: str):
    """
    First 5 meaningful sentences.
    """
    lines = [l.strip() for l in text.split("\n") if len(l.strip()) > 40]
    return lines[:5]


# =================================================
# ---------------- MAIN API ------------------------
# =================================================

def generate_insights(transcript: str, title="", meeting_type="discussion"):
    """
    Main function called by Streamlit / FastAPI
    """

    transcript = normalize_text(transcript)  # ⭐ MOST IMPORTANT STEP

    return {
        "summary": summarize(transcript),
        "key_points": extract_key_points(transcript),
        "decisions": extract_decisions(transcript),
        "action_items": extract_actions(transcript)
    }
