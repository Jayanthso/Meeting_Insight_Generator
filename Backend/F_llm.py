from transformers import pipeline
import re
import nltk

# -------------------------------------------------
# ONE-TIME downloads only (safe)
# -------------------------------------------------
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")


from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer


# =================================================
# TEXT CLEANING (shared by all extractors)
# =================================================

def clean_text(text: str) -> str:
    """Remove speaker labels and noise"""
    lines = []

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        # remove "Priya (PM):"
        line = re.sub(r"^[A-Za-z\s]+\([^)]*\):", "", line)

        # remove "Priya:"
        line = re.sub(r"^[A-Za-z\s]+:", "", line)

        lines.append(line.strip())

    return "\n".join(lines)


# =================================================
# SUMMARY (LSA + fallback)
# =================================================

def summarize(text: str, sentences: int = 4):
    text = clean_text(text)

    if len(text) < 80:
        return text

    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, sentences)

        result = " ".join(str(s) for s in summary)

        # fallback if empty
        if not result.strip():
            raise ValueError

        return result

    except:
        # fallback → first few sentences
        parts = re.split(r'[.!?]', text)
        return ". ".join(parts[:sentences]).strip()


# =================================================
# ACTION ITEMS (stronger heuristics)
# =================================================

def extract_actions(text: str):

    text = clean_text(text)

    actions = []
    seen = set()

    action_patterns = [
        r"([A-Z][a-zA-Z]+)\s+(will|must|to|can|should)\s+(.*)",
        r"([A-Z][a-zA-Z]+),\s*(.*)",
        r"([A-Z][a-zA-Z]+)['’]s\s+(team\s+)?(.*)",
    ]

    keywords = [
        "start", "prepare", "draft", "deliver", "send",
        "share", "create", "finish", "complete", "update",
        "escalate", "plan", "review", "test"
    ]

    for line in text.split("\n"):
        l = line.strip()

        if not l:
            continue

        lower = l.lower()

        if not any(k in lower for k in keywords):
            continue

        owner = "Unassigned"
        task = l

        for pat in action_patterns:
            m = re.match(pat, l)
            if m:
                owner = m.group(1)
                task = l.replace(owner, "", 1).strip()
                break

        task = re.sub(r"(?i)action item[:\-]?", "", task).strip()

        key = (task, owner)
        if key in seen:
            continue
        seen.add(key)

        actions.append({
            "task": task,
            "owner": owner
        })

    return actions


# =================================================
# DECISIONS
# =================================================

def extract_decisions(text):
    text = clean_text(text)

    keywords = [
        "decided", "approved", "confirmed",
        "finalized", "deadline", "must"
    ]

    results = []

    for l in text.split("\n"):
        if any(k in l.lower() for k in keywords):
            results.append(l.strip())

    return list(dict.fromkeys(results))  # remove duplicates


# =================================================
# KEY POINTS
# =================================================

def extract_key_points(text):
    text = clean_text(text)

    lines = [
        l.strip()
        for l in text.split("\n")
        if len(l.strip()) > 40
    ]

    return lines[:6]


# =================================================
# MAIN ENTRY
# =================================================

def generate_insights(transcript, title="", meeting_type="discussion"):

    transcript = transcript.strip()

    return {
        "summary": summarize(transcript, 4),
        "key_points": extract_key_points(transcript),
        "decisions": extract_decisions(transcript),
        "action_items": extract_actions(transcript)
    }
